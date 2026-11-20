"""Reports, written by Python templates (zero tokens). One short narrative comes from an agent."""
from __future__ import annotations

import html
import re
from collections import Counter

from . import scoring
from .stages import risk_consensus
from .util import read_json, settings, write_json

DISCLAIMER = ("> **Not financial advice.** This is an automated research experiment. It can be wrong, "
              "uses free data that may be incomplete, and says nothing about your own situation.")


def _counts(values) -> str:
    c = Counter(v for v in values if v)
    return ", ".join(f"{k}: {n}" for k, n in sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))) or "none"


def _c(ids) -> str:
    return " ".join(f"`{i}`" for i in ids) if ids else "_(no cite)_"


def _lv(lv: dict) -> str:
    parts = [f"{k.replace('_', ' ')} {v}" for k, v in lv.items() if k != "note"]
    return ", ".join(parts) + (f". {lv['note']}" if lv.get("note") else "")


def _flag(r) -> str:
    return " ".join(x for x in ((r["flag"] if r["flag"] != "none" else ""), ("illiquid" if r["illiquid"] else "")) if x)


def _pct(x) -> str:
    return "n/a" if x is None else f"{x:+.2f}%"


def build(ctx, state: dict) -> dict:
    run, snap, cfg = ctx.run, ctx.snap, settings()
    rows = scoring.rank(ctx)
    write_json(run / "ranking.json", {"as_of": snap["as_of"], "window": snap["window"],
                                      "fingerprint": snap["fingerprint"], "rows": rows})
    news, sen, r1, r2_, rm, tr = (ctx.stage(n) for n in ("news", "sentiment", "debate_r1", "debate_r2",
                                                           "research_manager", "trader"))
    risk1, risk2, pm = ctx.stage("risk_r1"), ctx.stage("risk_r2"), ctx.stage("portfolio_manager")
    social = ctx.stage("social") or snap.get("social") or {}
    narrative = ctx.stage("narrative").get("summary_md", "_Narrative not generated._")
    missing = snap["source_errors"] + ([] if snap.get("fipi_lipi") else ["FIPI/LIPI flows (NCCPL blocks scripts; no manual file supplied)"])
    if not social.get("items"):
        missing.append("Social posts (collector off or found nothing)")

    # ---------------------------------------------------------- ranking.md
    head = [f"# PSX top-30 five-day ranking: as of {snap['as_of']}", "", DISCLAIMER, "",
            f"Window: **{snap['window'][0]} to {snap['window'][-1]}** (5 trading days). "
            f"Snapshot fingerprint `{snap['fingerprint'][:12]}`.", ""]
    tbl = ["| # | Ticker | Call | Conviction | Risk | Exp. 5d move | Score | Quant | Flag |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        star = "**" if r["top"] else ""
        tbl.append(f"| {r['rank']} | {star}{r['symbol']}{star} | {r['final_direction']} | {r['final_conviction']} | "
                   f"{r['risk_rating']} | {_pct(r['expected_move_pct'])} | {r['hybrid_score']:+.3f} | {r['quant_score']:+.0f} | "
                   f"{_flag(r)} |")
    top = ["", f"## Top {cfg['scoring']['top_n']}", ""]
    for r in rows[: cfg["scoring"]["top_n"]]:
        lv = r["levels"]
        top += [f"### {r['rank']}. {r['symbol']}: {r['name']}",
                f"- Call **{r['final_direction']}**, conviction **{r['final_conviction']}**, risk **{r['risk_rating']}**, setup *{r['setup']}*",
                f"- Expected 5-day move {_pct(r['expected_move_pct'])}: {_lv(lv)}",
                f"- Debate winner: {r['winner']}. Deciding points: " + ("; ".join(r["deciding_points"]) or "none"),
                f"- Portfolio Manager: {r['pm_reason'] or '-'}", f"- Full trail: [stocks/{r['symbol']}.md](stocks/{r['symbol']}.md)", ""]
    (run / "ranking.md").write_text("\n".join(head + tbl + top) + "\n", encoding="utf-8")

    # ---------------------------------------------------------- per-stock trail
    for r in rows:
        s, p = r["symbol"], ctx.packs[r["symbol"]]
        L = [f"# {s}: {p['name']}", "", DISCLAIMER, "", f"Sector: {p['sector']} · Close {r['close']} · Rank {r['rank']}/30", "",
             "## 1. Analysts", "", f"### Market (Python, score {p['market']['score']:+d})"]
        L += [f"- `{x['id']}` {x['text']} ({x['points']:+d})" for x in p["market"]["signals"]]
        L += ["", f"### Fundamentals (Python, score {p['fundamentals']['score']:+d})"]
        L += [f"- `{x['id']}` {x['text']} ({x['points']:+d})" for x in p["fundamentals"]["signals"]]
        L += [f"- `{c['id']}` catalyst: {c['text']}" for c in p["fundamentals"]["catalysts"]]
        ns = news.get("stocks", {}).get(s, {})
        titles = {n["id"]: (n["title"], n["url"]) for n in p["news"]}
        L += ["", f"### News (agent) view: {ns.get('news_view', 'none')}"]
        L += [f"- `{i['id']}` [{titles.get(i['id'], ('', ''))[0]}]({titles.get(i['id'], ('', ''))[1]}): {i['tone']}, {i['impact']} impact. {i['why']}"
              for i in ns.get("items", [])] or ["- No company news in the last 7 days."]
        sv = sen.get(s, {})
        L += ["", f"### Sentiment (agent): {sv.get('mood')} ({sv.get('strength')})"]
        L += [f"- {x['text']} {_c(x['cites'])}" for x in sv.get("reasons", [])]
        L += ["", "## 2. Bull vs Bear"]
        for side in ("bull", "bear"):
            a, b = r1.get(s, {}).get(side, {}), r2_.get(s, {}).get(side, {})
            L += ["", f"### {side.title()}: round 1", *[f"- {x['claim']} {_c(x['cites'])}" for x in a.get("points", [])],
                  f"- _Summary:_ {a.get('summary', '')}"]
            if b:
                L += [f"### {side.title()}: round 2 (rebuttals)",
                      *[f"- re point {x['target']}: {x['response']} {_c(x['cites'])}" for x in b.get("rebuttals", [])],
                      f"- _Summary:_ {b.get('summary', '')}"]
        v = rm.get(s, {})
        L += ["", "## 3. Research Manager → Trader",
              f"- Winner **{v.get('winner')}**, direction **{v.get('direction')}**, conviction **{v.get('conviction')}**",
              *[f"- {x['text']} {_c(x['cites'])}" for x in v.get("deciding_points", [])],
              f"- Trader setup *{tr.get(s, {}).get('setup')}*; invalid if: {tr.get(s, {}).get('invalidation')}",
              f"- Levels (Python, from ATR): {_lv(r['levels'])}", "", "## 4. Risk debate"]
        for role in ("aggressive", "neutral", "conservative"):
            a, b = risk1.get(s, {}).get(role, {}), risk2.get(s, {}).get(role, {})
            L.append(f"- **{role}**: r1 {a.get('risk_rating')} ({a.get('conviction_adjust', 0):+d}) {a.get('argument', '')}"
                     + (f" → r2 {b.get('risk_rating')} ({b.get('conviction_adjust', 0):+d}) {b.get('response', '')}" if b else ""))
        rc = risk_consensus(ctx, s)
        L += [f"- Consensus (median): risk **{rc['risk_rating']}**, conviction after risk **{rc['conviction_after_risk']}**",
              "", "## 5. Portfolio Manager",
              f"- Final **{r['final_direction']} / {r['final_conviction']}**, flag {r['flag']}. {r['pm_reason']}",
              *[f"- Clamp: {n}" for n in pm.get(s, {}).get("clamp_notes", [])],
              f"- Expected 5-day move {_pct(r['expected_move_pct'])}, hybrid score {r['hybrid_score']:+.3f}"]
        (run / "stocks").mkdir(exist_ok=True)
        (run / "stocks" / f"{s}.md").write_text("\n".join(L) + "\n", encoding="utf-8")

    # ---------------------------------------------------------- how_it_worked.md
    calls, replays, fb = state.get("agent_calls", 0), state.get("replayed", 0), state.get("fallbacks", 0)
    sc_prev = sorted(run.parent.glob("*/scorecard.json"))
    how = [f"# How the strategy worked: run as of {snap['as_of']}", "", DISCLAIMER, "",
           "## Summary (agent narrative)", "", narrative, "",
           "## Stage 0: Frozen snapshot",
           f"- As-of close: **{snap['as_of']}**; forecast window **{', '.join(snap['window'])}**",
           f"- Universe: top 30 KSE-100 by free-float market cap: {', '.join(snap['universe'])}",
           f"- Fingerprint `{snap['fingerprint']}`: every agent answer is cached against its exact input, so re-running replays identical results.",
           f"- Missing or blocked sources: {'; '.join(missing) or 'none'}", "",
           "## Stage 1: Analysts",
           f"- **Market (Python):** scores range {min(r['market_score'] for r in rows):+d} to {max(r['market_score'] for r in rows):+d}; "
           f"positive for {sum(r['market_score'] > 0 for r in rows)} of 30.",
           f"- **Fundamentals (Python):** positive for {sum(r['fundamental_score'] > 0 for r in rows)} of 30 (P/E vs peers, EPS growth, margins, catalysts).",
           f"- **News (agent):** {sum(1 for s in snap['universe'] if ctx.packs[s]['news'])} stocks had news in 7 days; "
           f"views: {_counts(v.get('news_view') for v in news.get('stocks', {}).values())}. Macro view: **{news.get('macro', {}).get('macro_view')}**.",
           *[f"  - Macro: {d['text']} ({d['tone']})" for d in news.get("macro", {}).get("drivers", [])],
           f"- **Sentiment (agent):** moods: {_counts(v.get('mood') for v in sen.values())}. Social market mood: {social.get('market_mood', 'not collected')}.",
           "- **Merge:** all four outputs combined into a compact evidence pack per stock with IDs (M-, F-, N-, MAC-, S-).", "",
           "## Stage 2: Bull vs Bear",
           f"- {cfg['debate']['research_rounds']} rounds per stock. Debate winners: {_counts(v.get('winner') for v in rm.values())}.", "",
           "## Stage 3: Research Manager → Trader",
           f"- Directions: {_counts(v.get('direction') for v in rm.values())}; convictions: {_counts(v.get('conviction') for v in rm.values())}.",
           f"- Trader setups: {_counts(v.get('setup') for v in tr.values())}. Targets and stops come from volatility (ATR), not from the agent.", "",
           "## Stage 4: Risk debate",
           f"- Aggressive, Neutral and Conservative, {cfg['debate']['risk_rounds']} rounds. Final risk (median of three): "
           f"{_counts(risk_consensus(ctx, s)['risk_rating'] for s in snap['universe'])}.", "",
           "## Stage 5: Portfolio Manager and ranking",
           f"- Final calls: {_counts(r['final_direction'] for r in rows)}; flags: {_counts(r['flag'] for r in rows if r['flag'] != 'none')}.",
           f"- PM rule clamps applied: {sum(len(v.get('clamp_notes', [])) for v in pm.values())}.",
           "- Ranking is the formula `expected move × (1 − risk penalty) − liquidity penalty`; ties by quant score then ticker. The PM cannot reorder.",
           f"- Top {cfg['scoring']['top_n']}: " + ", ".join(f"{r['symbol']} ({_pct(r['expected_move_pct'])})" for r in rows[: cfg['scoring']['top_n']]), "",
           "## Cost and repeatability",
           f"- Agent calls this run: **{calls}**; answers replayed from cache: **{replays}**; neutral fallbacks: **{fb}**.",
           "- Market and Fundamentals analysts, scoring, levels, reports and scorecard use **zero tokens** (Python).", ""]
    if sc_prev:
        last = read_json(sc_prev[-1])
        how += ["## Last scored run", f"- Run {last['as_of']}: hit rate {last['hit_rate_pct']}%, top 5 {last['top5_avg_ret_pct']}% "
                f"vs KSE-100 proxy {last['kse100_proxy_ret_pct']}%. See [scorecard](../scorecard.md).", ""]
    (run / "how_it_worked.md").write_text("\n".join(how) + "\n", encoding="utf-8")

    # ---------------------------------------------------------- HTML
    (run / "ranking.html").write_text(_html(snap, rows, narrative, how), encoding="utf-8")
    meta = {"as_of": snap["as_of"], "window": snap["window"], "fingerprint": snap["fingerprint"],
            "prompt_version": cfg["prompt_version"], "models": cfg["models"],
            "agent_calls": calls, "replayed": replays, "fallbacks": fb, "missing_sources": missing}
    write_json(run / "run_meta.json", meta)
    return meta


def _md_inline(s: str) -> str:
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`(.+?)`", r"<code>\1</code>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', s)
    return re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<em>\1</em>", s)


def _md(lines: list[str]) -> str:
    out, in_list = [], False
    for ln in "\n".join(lines).splitlines():
        if ln.startswith(("- ", "  - ")):
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_md_inline(ln.strip()[2:])}</li>")
            continue
        if in_list:
            out.append("</ul>")
            in_list = False
        if ln.startswith("#"):
            lvl = min(len(ln) - len(ln.lstrip("#")) + 1, 4)
            out.append(f"<h{lvl}>{_md_inline(ln.lstrip('#').strip())}</h{lvl}>")
        elif ln.startswith(">"):
            out.append(f"<p class=note>{_md_inline(ln.lstrip('> '))}</p>")
        elif ln.strip():
            out.append(f"<p>{_md_inline(ln)}</p>")
    if in_list:
        out.append("</ul>")
    return "\n".join(out)


def _html(snap, rows, narrative, how) -> str:
    color = {"up": "pos", "down": "neg", "flat": "flat"}
    trs = "\n".join(
        f"<tr class='{'top' if r['top'] else ''}'><td>{r['rank']}</td><td><a href='stocks/{r['symbol']}.md'>{r['symbol']}</a></td>"
        f"<td class='{color[r['final_direction']]}'>{r['final_direction']}</td><td>{r['final_conviction']}</td><td>{r['risk_rating']}</td>"
        f"<td class=num>{_pct(r['expected_move_pct'])}</td><td class=num>{r['hybrid_score']:+.3f}</td><td class=num>{r['quant_score']:+.0f}</td>"
        f"<td>{html.escape(_flag(r))}</td></tr>"
        for r in rows)
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>PSX 5-Day Ranking {snap['as_of']}</title><style>
:root{{--bg:#f7f8f7;--fg:#1d2321;--muted:#5d6763;--line:#d9dedb;--accent:#0f7a68;--pos:#0f7a3e;--neg:#b3261e;--card:#fff}}
@media (prefers-color-scheme:dark){{:root{{--bg:#121514;--fg:#e6ebe8;--muted:#9aa5a0;--line:#2c3330;--accent:#4fc1a9;--pos:#5fd38f;--neg:#ff8a80;--card:#1a1e1c}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,Segoe UI,sans-serif}}
main{{max-width:1000px;margin:0 auto;padding:24px 16px}}h1{{font-size:1.5rem}}a{{color:var(--accent)}}
.note{{border-left:3px solid var(--accent);padding:6px 12px;background:var(--card);color:var(--muted)}}
.wrap{{overflow-x:auto}}table{{border-collapse:collapse;width:100%;background:var(--card)}}
th,td{{padding:6px 8px;border-bottom:1px solid var(--line);text-align:left;white-space:nowrap}}th{{color:var(--muted);font-weight:600}}
.num{{text-align:right;font-variant-numeric:tabular-nums}}.pos{{color:var(--pos)}}.neg{{color:var(--neg)}}.flat{{color:var(--muted)}}
tr.top td{{font-weight:600}}code{{font-size:.85em}}</style></head><body><main>
<h1>PSX top-30 five-day ranking</h1>
<p class=note><strong>Not financial advice.</strong> Automated research experiment on free data. As of {snap['as_of']} close; window {snap['window'][0]} to {snap['window'][-1]}.</p>
<div class=wrap><table><thead><tr><th>#</th><th>Ticker</th><th>Call</th><th>Conviction</th><th>Risk</th><th class=num>Exp. 5d</th><th class=num>Score</th><th class=num>Quant</th><th>Flag</th></tr></thead>
<tbody>{trs}</tbody></table></div>
{_md(how)}
</main></body></html>
"""
