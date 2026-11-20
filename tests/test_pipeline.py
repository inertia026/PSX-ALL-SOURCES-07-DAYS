"""End-to-end pipeline on SYNTHETIC data with FAKE agents (no network, no Claude).

Proves: stage order, validation + retry + fallback, replay cache, and that a
re-run produces a byte-identical ranking with zero agent calls.
"""
import random
from datetime import date, timedelta

import pytest

from psx7 import analysts, cli, report, scoring, snapshot, stages
from psx7.util import read_json, write_json

AS_OF = "2026-11-20"


def business_days(end: date, n: int) -> list[str]:
    out, d = [], end
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d -= timedelta(days=1)
    return out[::-1]


def synthetic_snapshot() -> dict:
    days = business_days(date.fromisoformat(AS_OF), 260)
    syms = [f"T{i:02d}" for i in range(1, 31)]
    history, members, companies, news = {}, [], {}, {}
    for i, s in enumerate(syms):
        rnd = random.Random(i)
        px, rows, drift = 100.0 + i, [], (i - 15) / 3000
        for d in days:
            o = px
            px = max(1.0, px * (1 + drift + rnd.gauss(0, 0.015)))
            rows.append({"date": d, "open": round(o, 2), "high": round(max(o, px) * 1.01, 2),
                         "low": round(min(o, px) * 0.99, 2), "close": round(px, 2),
                         "volume": float(100000 + rnd.randint(0, 50000)), "ldcp": round(o, 2),
                         "ex_marker": "XD" if (i == 3 and d == days[-3]) else "", "sector_code": f"08{i % 4}",
                         "symbol": s, "name": f"Test Co {i}"})
        history[s] = rows
        members.append({"symbol": s, "name": f"Test Co {i}", "free_float_shares": 1e6 * (31 - i),
                        "free_float_mcap": 1e6 * (31 - i) * px, "index_weight_pct": 1.0, "close": rows[-1]["close"]})
        companies[s] = {"sector": ["BANKS", "CEMENT", "FERTILIZER", "OIL & GAS"][i % 4],
                        "stats": {"pe_ratio": 4 + i % 9, "1-year_change": 10.0},
                        "ratios": {"rows": {"EPS Growth (%)": [i - 10.0], "Net Profit Margin (%)": [20.0, 18.0]}},
                        "financials": {"quarterly": {"periods": ["Q1 2027", "Q1 2026"], "rows": {"EPS": [2.0 + i / 10, 2.0]}}},
                        "announcements": [{"date": "2026-11-12", "kind": "board_meetings", "title": "NOTICE OF BOARD MEETING"}] if i % 5 == 0 else []}
        news[s] = [{"id": f"N-{s}-1", "title": f"Test Co {i} expands capacity", "summary": "synthetic",
                    "source": "test", "url": "https://example.com", "published_utc": "2026-11-19T10:00Z"}] if i % 3 == 0 else []
    snap = {"as_of": AS_OF, "window": ["2026-11-23", "2026-11-24", "2026-11-25", "2026-11-26", "2026-11-27"],
            "universe": syms, "members": members,
            "prices": {s: [{k: r[k] for k in ("date", "open", "high", "low", "close", "volume", "ldcp", "ex_marker")}
                           for r in history[s]] for s in syms},
            "sector_code": {s: history[s][-1]["sector_code"] for s in syms}, "companies": companies,
            "market_proxy": snapshot.market_proxy(history, members),
            "breadth_5d": snapshot.breadth_last_days(history, 5), "stock_news": news,
            "macro_news": [{"id": "MAC-1", "title": "SBP keeps policy rate unchanged", "summary": "synthetic",
                            "source": "test", "url": "", "published_utc": "2026-11-18T10:00Z"}],
            "fipi_lipi": None, "social": None, "source_errors": []}
    snap["fingerprint"] = snapshot.sha256(snap)
    return snap


def fake_agent(job: dict, packs: dict) -> dict:
    """Deterministic stand-in for a Claude subagent."""
    st, data, syms = job["stage"], job["data"], job["symbols"]
    ev = lambda s: packs[s]["market"]["signals"][0]["id"]  # noqa: E731
    q = lambda s: packs[s]["quant_score"]  # noqa: E731
    if st == "social":
        return {"result": {"market_mood": "neutral", "items": [{"symbol": "T01", "text": "Investors like T01", "tone": "positive", "source": "https://example.com"}]}}
    if st == "news" and job["job_id"] == "macro":
        return {"macro": {"macro_view": "neutral", "drivers": [{"text": "Rates on hold", "tone": "neutral", "cites": ["MAC-1"]}]}}
    if st == "news":
        return {"results": [{"symbol": s["symbol"], "news_view": "positive",
                             "items": [{"id": h["id"], "tone": "positive", "impact": "medium", "why": "capacity"} for h in s["headlines"]]}
                            for s in data["stocks"]]}
    if st == "sentiment":
        return {"results": [{"symbol": s["symbol"], "mood": "bullish" if (s["ret5_pct"] or 0) > 0 else "bearish",
                             "strength": "medium", "reasons": [{"text": "price action", "cites": []}]} for s in data["stocks"]]}
    if st.startswith("debate"):
        if st == "debate_r1":
            return {"results": [{"symbol": s, "side": data["side"], "points": [{"claim": "trend", "cites": [ev(s), "FAKE-ID"]}], "summary": "ok"} for s in syms]}
        return {"results": [{"symbol": s, "side": data["side"], "rebuttals": [{"target": 0, "response": "no", "cites": [ev(s)]}], "summary": "ok"} for s in syms]}
    if st == "research_manager":
        return {"results": [{"symbol": s, "winner": "bull" if q(s) > 0 else "bear",
                             "direction": "up" if q(s) > 10 else "down" if q(s) < -10 else "flat",
                             "conviction": "high" if abs(q(s)) > 40 else "medium", "deciding_points": [{"text": "x", "cites": [ev(s)]}]} for s in syms]}
    if st == "trader":
        return {"results": [{"symbol": s, "setup": "momentum", "invalidation": "close below support"} for s in syms]}
    if st.startswith("risk"):
        rating = {"aggressive": "low", "neutral": "medium", "conservative": "high"}[data["your_role"]]
        key = "argument" if st == "risk_r1" else "response"
        return {"results": [{"symbol": s, "risk_rating": rating, "conviction_adjust": 0, key: "fine", "cites": []} for s in syms]}
    if st == "portfolio_manager":
        return {"results": [{"symbol": s["symbol"], "final_direction": "up" if s["research_direction"] == "down" and s["symbol"] == "T05" else s["research_direction"],
                             "final_conviction": s["conviction_after_risk"], "flag": "none", "reason": "ok"} for s in data["stocks"]]}
    if st == "narrative":
        return {"result": {"summary_md": "Synthetic run summary."}}
    raise AssertionError(st)


@pytest.fixture
def repo(tmp_path, monkeypatch):
    runs, cache = tmp_path / "runs", tmp_path / "cache"
    for mod in (cli, snapshot):
        monkeypatch.setattr(mod, "RUNS_DIR", runs)
    monkeypatch.setattr(stages, "CACHE_DIR", cache)
    monkeypatch.setattr(stages, "ROOT", tmp_path)
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    return tmp_path


def setup_run(root):
    snap = synthetic_snapshot()
    run = root / "runs" / AS_OF
    write_json(run / "snapshot" / "snapshot.json", snap)
    write_json(run / "analysts.json", analysts.run(snap))
    write_json(run / "state.json", {"stage": 0})
    return run


def drive(root, run, capsys, break_once=None):
    """Loop `step` like the skill does, answering every JOB with the fake agent."""
    packs = read_json(run / "analysts.json")
    broken = set()
    for _ in range(60):
        cli.cmd_step(type("A", (), {"as_of": AS_OF})())
        out = capsys.readouterr().out
        if "DONE" in out:
            return out
        for line in out.splitlines():
            if line.startswith("JOB "):
                path = root / line.split()[3]
                job = read_json(path)
                target = root / job["output_path"]
                if break_once and job["job_id"] == break_once and job["job_id"] not in broken:
                    broken.add(job["job_id"])
                    target.write_text("not json", encoding="utf-8")
                else:
                    write_json(target, fake_agent(job, packs))
    raise AssertionError("pipeline did not finish")


def test_full_pipeline_and_replay(repo, capsys):
    run = setup_run(repo)
    drive(repo, run, capsys, break_once="batch01")
    state = read_json(run / "state.json")
    assert state["stage"] == len(stages.all_stages())
    assert state["agent_calls"] > 0 and state.get("fallbacks", 0) == 0
    ctx = stages.Ctx(run)
    # social output was frozen into the snapshot
    assert ctx.snap["social"]["items"][0]["id"] == "S-1"
    # invalid cite was dropped
    assert all("FAKE-ID" not in p["cites"] for v in ctx.stage("debate_r1").values() for p in v["bull"]["points"])
    # PM may not flip direction: T05 clamped to flat if research said down
    pm, rm = ctx.stage("portfolio_manager"), ctx.stage("research_manager")
    if rm["T05"]["direction"] == "down":
        assert pm["T05"]["final_direction"] == "flat" and pm["T05"]["clamp_notes"]
    meta = report.build(ctx, state)
    first = (run / "ranking.json").read_bytes()
    assert (run / "ranking.html").exists() and (run / "stocks" / "T01.md").exists()
    assert "How the strategy worked" in (run / "how_it_worked.md").read_text(encoding="utf-8")
    assert meta["agent_calls"] == state["agent_calls"]

    # ---- re-run from scratch on the same snapshot: everything replays, zero calls
    import shutil
    for d in ("jobs", "stages"):
        shutil.rmtree(run / d)
    snap = read_json(run / "snapshot" / "snapshot.json")
    snap["social"] = None
    write_json(run / "snapshot" / "snapshot.json", snap)
    write_json(run / "state.json", {"stage": 0})
    out = drive(repo, run, capsys)
    state2 = read_json(run / "state.json")
    assert state2.get("agent_calls", 0) == 0 and state2["replayed"] > 0
    assert "JOB " not in out
    report.build(stages.Ctx(run), state2)
    assert (run / "ranking.json").read_bytes() == first


def test_fallback_after_two_failures(repo, capsys):
    run = setup_run(repo)
    packs = read_json(run / "analysts.json")
    for _ in range(3):  # social job: answer garbage twice
        cli.cmd_step(type("A", (), {"as_of": AS_OF})())
        out = capsys.readouterr().out
        jobs = [ln for ln in out.splitlines() if ln.startswith("JOB ")]
        if not jobs or "social" not in jobs[0]:
            break
        job = read_json(repo / jobs[0].split()[3])
        (repo / job["output_path"]).write_text("{}", encoding="utf-8")
    assert read_json(run / "stages" / "social.json")["fallback"] is True
    assert packs  # silence unused


def test_ranking_formula_order():
    from psx7.util import settings
    s = settings()["scoring"]
    up_high = scoring.expected_move(2.0, "up", "high")
    up_low = scoring.expected_move(2.0, "up", "low")
    assert up_high == pytest.approx(2.0 * s["conviction_mult"]["high"] * 5 ** 0.5 * s["move_k"])
    assert up_high > up_low > 0 == scoring.expected_move(2.0, "flat", "high")
    assert scoring.expected_move(2.0, "down", "medium") < 0
