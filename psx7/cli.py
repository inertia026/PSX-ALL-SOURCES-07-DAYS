"""Command line. A run is driven from Claude Code (see .claude/skills/psx-run/SKILL.md):

    python -m psx7 snapshot [--date YYYY-MM-DD] [--refresh]   # Stage 0 + Python analysts + scorecard
    python -m psx7 step                                       # repeat: prints agent jobs to run, or DONE
    python -m psx7 finish                                     # ranking + reports
    python -m psx7 backtest [--days 760]                    # walk-forward test of Python signals
    python -m psx7 pdf                                        # large-font PDF of the latest run
    python -m psx7 status | sync-agents
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import date

from . import analysts, backtest, pdf_report, report, scorecard, snapshot, stages
from .util import ROOT, RUNS_DIR, read_json, settings, write_json

AGENT_MODEL_KEY = {
    "social-collector": "social_collector", "news-analyst": "news", "sentiment-analyst": "sentiment",
    "bull-researcher": "bull", "bear-researcher": "bear", "research-manager": "research_manager",
    "trader": "trader", "risk-aggressive": "risk", "risk-neutral": "risk", "risk-conservative": "risk",
    "portfolio-manager": "portfolio_manager", "run-narrator": "narrative",
}


def latest_run() -> str:
    runs = sorted(p.name for p in RUNS_DIR.iterdir() if p.is_dir() and (p / "snapshot").exists()) if RUNS_DIR.exists() else []
    if not runs:
        sys.exit("No run found. Start with: python -m psx7 snapshot")
    return runs[-1]


def cmd_snapshot(a) -> None:
    req = date.fromisoformat(a.date) if a.date else date.today()
    snap = snapshot.build(req, refresh=a.refresh)
    run = RUNS_DIR / snap["as_of"]
    print("Scoring earlier runs whose window has closed ...")
    scorecard.update_all(snap["as_of"])
    packs = analysts.run(snap)
    write_json(run / "analysts.json", packs)
    print(f"Market + Fundamentals analysts (Python) done for {len(packs)} stocks.")
    if not (run / "state.json").exists() or a.refresh:
        write_json(run / "state.json", {"stage": 0})
    print(f"RUN {snap['as_of']}  window {snap['window'][0]}..{snap['window'][-1]}")
    print("Next: python -m psx7 step")


def cmd_step(a) -> None:
    as_of = a.as_of or latest_run()
    run = RUNS_DIR / as_of
    state = read_json(run / "state.json")
    all_st = stages.all_stages()
    ctx = stages.Ctx(run)
    while state["stage"] < len(all_st):
        st = all_st[state["stage"]]
        if not st.enabled(ctx):
            state["stage"] += 1
            continue
        pending = stages.prepare(run, st, ctx, state)
        pending, msgs = stages.collect(run, st, ctx, state)
        for m in msgs:
            print("NOTE", m)
        if pending:
            write_json(run / "state.json", state)
            print(f"STAGE {st.name} ({state['stage'] + 1}/{len(all_st)}): {len(pending)} agent job(s) to run")
            for j in pending:
                inp, _ = stages.job_paths(run, st, j)
                model = settings()["models"].get(AGENT_MODEL_KEY.get(j["agent"], ""), "?")
                print(f"JOB {j['agent']} {model} {inp.relative_to(ROOT).as_posix()}")
            print("After all jobs finish, run: python -m psx7 step")
            return
        merged = stages.finalize(run, st, ctx)
        if st.name == "social":
            snapshot.attach_social(as_of, merged)
        print(f"stage {st.name}: complete")
        state["stage"] += 1
        write_json(run / "state.json", state)
        ctx = stages.Ctx(run)
    write_json(run / "state.json", state)
    print("DONE all agent stages. Next: python -m psx7 finish")


def cmd_finish(a) -> None:
    as_of = a.as_of or latest_run()
    run = RUNS_DIR / as_of
    state = read_json(run / "state.json")
    if state["stage"] < len(stages.all_stages()):
        sys.exit("Agent stages not finished. Run: python -m psx7 step")
    meta = report.build(stages.Ctx(run), state)
    scorecard.write_markdown()
    pdf = pdf_report.build_pdf(run)
    print(f"Reports written to runs/{as_of}/ (ranking.md, ranking.html, {pdf.name}, how_it_worked.md, stocks/)")
    print(f"Agent calls {meta['agent_calls']}, replayed {meta['replayed']}, fallbacks {meta['fallbacks']}")


def cmd_pdf(a) -> None:
    as_of = a.as_of or latest_run()
    print(f"PDF written: {pdf_report.build_pdf(RUNS_DIR / as_of)}")


def cmd_backtest(a) -> None:
    to = date.fromisoformat(a.to) if a.to else date.today()
    res = backtest.run(to, a.days)
    ms = next((s for s in res["signals"] if s["signal"] == "market_score"), {})
    print(f"market_score: mean weekly IC {ms.get('mean_ic')}, t {ms.get('t_stat')}, "
          f"top-bottom {ms.get('top_minus_bottom_pct')}% over {res['weeks']} weeks")


def cmd_status(a) -> None:
    as_of = a.as_of or latest_run()
    st = read_json(RUNS_DIR / as_of / "state.json")
    names = [s.name for s in stages.all_stages()]
    print(f"Run {as_of}: stage {min(st['stage'] + 1, len(names))}/{len(names)} "
          f"({names[st['stage']] if st['stage'] < len(names) else 'all done'}); "
          f"agent calls {st.get('agent_calls', 0)}, replayed {st.get('replayed', 0)}, fallbacks {st.get('fallbacks', 0)}")


def cmd_sync_agents(a) -> None:
    models = settings()["models"]
    for agent, key in AGENT_MODEL_KEY.items():
        p = stages.AGENT_DIR / f"{agent}.md"
        if p.exists():
            t = p.read_text(encoding="utf-8")
            p.write_text(re.sub(r"(?m)^model: .*$", f"model: {models[key]}", t, count=1), encoding="utf-8")
    print("Agent model lines updated from config/settings.yaml")


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(prog="psx7")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("snapshot")
    s.add_argument("--date")
    s.add_argument("--refresh", action="store_true")
    for name in ("step", "finish", "status", "pdf"):
        sub.add_parser(name).add_argument("--as-of", dest="as_of")
    sub.add_parser("sync-agents")
    b = sub.add_parser("backtest")
    b.add_argument("--to")
    b.add_argument("--days", type=int, default=760)
    a = ap.parse_args(argv)
    {"snapshot": cmd_snapshot, "step": cmd_step, "finish": cmd_finish, "status": cmd_status, "pdf": cmd_pdf, "backtest": cmd_backtest,
     "sync-agents": cmd_sync_agents}[a.cmd](a)
