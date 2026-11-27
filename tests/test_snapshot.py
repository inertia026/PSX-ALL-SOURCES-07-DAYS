"""Stage 0 (snapshot), news filtering, price adjustment and scorecard, all offline.

Network functions are replaced by fakes, so this exercises the real build code
path that a live run uses, without touching PSX or Google.
"""
from datetime import date, timedelta
from pathlib import Path

import pytest

from psx7 import scorecard, snapshot, sources
from psx7.snapshot import match_patterns
from psx7.util import read_json, write_json

FX = Path(__file__).parent / "fixtures"
AS_OF = "2026-11-20"


def bdays(end: str, n: int) -> list[str]:
    out, d = [], date.fromisoformat(end)
    while len(out) < n:
        if d.weekday() < 5:
            out.append(d.isoformat())
        d -= timedelta(days=1)
    return out[::-1]


def fake_history(n_syms=35, n_days=260):
    days = bdays(AS_OF, n_days)
    hist = {}
    for i in range(n_syms):
        s = f"S{i:02d}"
        rows, px = [], 50.0 + i
        for j, d in enumerate(days):
            prev = px
            px = round(px * (1.002 if (i + j) % 3 else 0.997), 2)
            ldcp = prev
            ex = ""
            if s == "S01" and j == n_days - 10:     # 10% dividend on this day
                ldcp, px, ex = round(prev * 0.9, 2), round(prev * 0.9, 2), "XD"
            rows.append({"date": d, "symbol": s, "sector_code": f"08{i % 3}", "name": f"Sample {i}",
                         "ex_marker": ex, "open": prev, "high": max(prev, px) * 1.01, "low": min(prev, px) * 0.99,
                         "close": px, "volume": 1e6, "ldcp": ldcp})
        hist[s] = rows
    return hist


@pytest.fixture
def offline(tmp_path, monkeypatch):
    hist = fake_history()
    monkeypatch.setattr(snapshot, "RUNS_DIR", tmp_path / "runs")
    monkeypatch.setattr(sources, "load_history", lambda d, n, log=print: (AS_OF, hist))
    monkeypatch.setattr(sources, "kse100_constituents", lambda: [
        {"symbol": s, "name": f"Sample Company {s} Limited", "index_weight_pct": 1.0,
         "free_float_shares": 1e6 * (40 - int(s[1:])), "market_cap": 1.0} for s in hist])
    company = sources.parse_company((FX / "company_OGDC.html").read_text(encoding="utf-8"))
    monkeypatch.setattr(sources, "company_page", lambda s: company)
    monkeypatch.setattr(sources, "fetch_news", lambda log=print: ([
        {"source": "feed", "title": "Sample Company S03 wins big order", "url": "", "summary": "",
         "published_utc": "2026-11-19T08:00Z"},
        {"source": "feed", "title": "Sample Company S04 news AFTER the window starts", "url": "", "summary": "",
         "published_utc": "2026-11-24T08:00Z"},
    ], []))

    def fake_google(query, http):
        if "foreign" in query:
            return [{"source": "x", "title": "Foreign investors buy $20m at PSX", "url": "", "summary": "",
                     "published_utc": "2026-11-18T08:00Z"},
                    {"source": "x", "title": "Indian shares rise as foreign inflows jump", "url": "", "summary": "",
                     "published_utc": "2026-11-18T08:00Z"}], None
        if "S05" in query:
            return [{"source": "x", "title": "Sample Company S05 Stock Price and Competitors", "url": "", "summary": "",
                     "published_utc": "2026-11-18T08:00Z"},
                    {"source": "x", "title": "Sample Company S05 posts record profit", "url": "", "summary": "",
                     "published_utc": "2026-11-10T08:00Z"},
                    {"source": "x", "title": "Sample Company S05 old story", "url": "", "summary": "",
                     "published_utc": "2026-10-01T08:00Z"}], None
        return [], None
    monkeypatch.setattr(sources, "google_news", fake_google)
    monkeypatch.setattr(sources, "manual_fipi_lipi", lambda: None)
    return tmp_path


def test_snapshot_build_offline(offline):
    snap = snapshot.build(date(2026, 11, 21), log=lambda *_: None)
    assert snap["as_of"] == AS_OF and snap["window"][0] == "2026-11-23"
    assert len(snap["universe"]) == 30 and "S34" not in snap["universe"]      # smallest free float dropped
    titles = {s: [n["title"] for n in v] for s, v in snap["stock_news"].items()}
    assert titles["S03"] == ["Sample Company S03 wins big order"]
    assert titles["S04"] == []                                                # after window start: excluded
    assert titles["S05"] == ["Sample Company S05 posts record profit"]        # junk + too-old excluded
    assert [n["title"] for n in snap["flow_mentions"]] == ["Foreign investors buy $20m at PSX"]  # India dropped
    assert snap["price_adjustments"]["S01"][0]["factor"] == 0.9
    # adjusted history: no 10% "fall" on the ex-date
    rows = snap["prices"]["S01"]
    i = next(k for k, r in enumerate(rows) if r["ex_marker"] == "XD")
    assert abs(rows[i]["close"] / rows[i - 1]["close"] - 1) < 0.01
    # rebuilding with identical inputs gives an identical fingerprint
    again = snapshot.build(date(2026, 11, 21), refresh=True, log=lambda *_: None)
    assert again["fingerprint"] == snap["fingerprint"]


def test_reuses_existing_snapshot(offline):
    a = snapshot.build(date(2026, 11, 21), log=lambda *_: None)
    b = snapshot.build(date(2026, 11, 21), log=lambda *_: None)
    assert a == b


def test_matching_rules():
    ppl = match_patterns("PPL", "Pakistan Petroleum Limited")
    assert not any(p.search("Petrol price reduced; petroleum levy raised") for p in ppl)
    assert any(p.search("Pakistan Petroleum Limited credits dividend") for p in ppl)
    assert any(p.search("PPL profit rises") for p in ppl)
    psel = match_patterns("PSEL", "Pakistan Services Limited")
    assert not any(p.search("Pakistan services sector grows") for p in psel)
    sys_ = match_patterns("SYS", "Systems Limited")
    assert any(p.search("Systems Limited posts record profit") for p in sys_)
    assert not any(p.search("Shares of Fujiyama Power Systems Limited listed") for p in sys_)


def test_adjust_history_bonus():
    rows = [{"date": "d1", "open": 100, "high": 100, "low": 100, "close": 100, "ldcp": 100, "volume": 1},
            {"date": "d2", "open": 50, "high": 52, "low": 49, "close": 51, "ldcp": 50, "volume": 1, "ex_marker": "XB"}]
    adj, ev = sources.adjust_history(rows)
    assert ev[0]["factor"] == 0.5 and adj[0]["close"] == 50 and adj[1]["close"] == 51


def test_scorecard_without_snapshot(tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    monkeypatch.setattr(scorecard, "RUNS_DIR", runs)
    window = ["2026-11-23", "2026-11-24"]
    write_json(runs / "2026-11-20" / "ranking.json", {
        "window": window, "benchmark_members": [["A", 100, 10.0], ["B", 100, 10.0]],
        "rows": [{"symbol": "A", "rank": 1, "final_direction": "up", "hybrid_score": 2.0},
                 {"symbol": "B", "rank": 2, "final_direction": "down", "hybrid_score": -1.0}]})
    days = {"2026-11-23": {"A": (11.0, 10.0), "B": (9.0, 10.0)},
            "2026-11-24": {"A": (10.89, 9.9), "B": (9.0, 9.0)}}   # A: ex-dividend 0.10 on 24th
    monkeypatch.setattr(scorecard, "rows_on", lambda d, http: days.get(d, {}))
    res = scorecard.score_run("2026-11-20", "2026-11-27", log=lambda *_: None)
    a = next(r for r in res["rows"] if r["symbol"] == "A")
    assert a["actual_ret_pct"] == pytest.approx(21.0)       # 1.1 * 1.1, dividend not counted as a loss
    assert res["hit_rate_pct"] == 100.0 and res["kse100_proxy_ret_pct"] is not None
    scorecard.write_markdown()
    assert "2026-11-20" in (runs / "scorecard.md").read_text(encoding="utf-8")
    assert read_json(runs / "2026-11-20" / "scorecard.json")["n"] == 2


def test_pdf_report(tmp_path):
    from psx7 import pdf_report
    run = tmp_path / "2026-11-20"
    rows = [{"symbol": f"S{i:02d}", "name": f"Sample {i}", "sector": "BANKS", "rank": i + 1, "top": i < 5,
             "final_direction": ("up", "flat", "down")[i % 3], "final_conviction": "low", "risk_rating": "medium",
             "setup": "momentum", "expected_move_pct": 1.0, "hybrid_score": 0.5, "quant_score": 10.0,
             "flag": "caution" if i == 1 else "none", "illiquid": i == 2, "deciding_points": ["RSI ≥ 70 → *risk*"],
             "pm_reason": "ok", "levels": {"entry_ref": 10, "target": 11, "stop": 9}} for i in range(30)]
    write_json(run / "ranking.json", {"as_of": AS_OF, "window": ["2026-11-23", "2026-11-27"], "fingerprint": "ab" * 32, "rows": rows})
    write_json(run / "run_meta.json", {"agent_calls": 93, "fallbacks": 0, "prompt_version": "x", "missing_sources": []})
    (run / "how_it_worked.md").write_text("# t\n\n## Summary (agent narrative)\nskip\n\n## Stage 1: Analysts\n- **Market:** ok\n", encoding="utf-8")
    first = pdf_report.build_pdf(run).read_bytes()
    assert first.startswith(b"%PDF") and pdf_report.build_pdf(run).read_bytes() == first    # deterministic


def test_backtest_offline(tmp_path, monkeypatch):
    from psx7 import backtest
    hist = fake_history(n_syms=12, n_days=320)
    adj = {s: sources.adjust_history(r)[0] for s, r in hist.items()}
    members = [{"symbol": s, "free_float_shares": 1e6, "close": r[-1]["close"]} for s, r in adj.items()]
    monkeypatch.setattr(backtest, "OUT", tmp_path / "bt")
    monkeypatch.setattr(backtest, "load", lambda to, n, log=print: (adj, members, snapshot.market_proxy(adj, members)))
    a = backtest.run(date(2026, 11, 20), 320, log=lambda *_: None)
    assert a["weeks"] >= 20 and a["observations"] == a["weeks"] * 12
    ics = [s["mean_ic"] for s in a["signals"] if "mean_ic" in s]
    assert ics and all(-1 <= x <= 1 for x in ics) and len(a["market_score_buckets"]) == 5
    assert backtest.run(date(2026, 11, 20), 320, log=lambda *_: None) == a          # deterministic
    assert (tmp_path / "bt" / "backtest.md").exists()
