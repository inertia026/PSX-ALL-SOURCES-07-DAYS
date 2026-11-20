"""Structured Bull vs Bear debate: menus and scoring (pure Python, zero tokens).

Agents never write free-text arguments. Python splits each stock's evidence into
a bull menu and a bear menu. Round 1: each side picks its strongest IDs with a
weight. Round 2: each side rebuts opponent picks with a reason from a fixed list.
Python then scores the debate and proposes direction + conviction for the
Research Manager to accept or adjust by one step.
"""
from __future__ import annotations

from .util import r2, settings

WEIGHTS = ["weak", "moderate", "strong"]
REBUTTAL_REASONS = ["stale", "outweighed_by", "not_5day_relevant", "mechanical", "weak_signal"]
DIR_ORDER = ["down", "flat", "up"]
CONV_ORDER = ["low", "medium", "high"]


def menus(ctx, sym: str) -> dict[str, list[dict]]:
    """Evidence each side may argue from, in a fixed order. Every item: {id, text}."""
    p = ctx.packs[sym]
    bull, bear = [], []
    for x in p["market"]["signals"] + p["fundamentals"]["signals"]:
        item = {"id": x["id"], "text": x["text"]}
        if x["points"] > 0:
            bull.append(item)
        elif x["points"] < 0:
            bear.append(item)
    for c in p["fundamentals"]["catalysts"]:          # events cut both ways
        bull.append({"id": c["id"], "text": c["text"]})
        bear.append({"id": c["id"], "text": c["text"]})
    news = ctx.stage("news")
    titles = {n["id"]: n["title"] for n in p["news"]}
    for it in news.get("stocks", {}).get(sym, {}).get("items", []):
        item = {"id": it["id"], "text": f"News ({it['impact']} impact): {titles.get(it['id'], '')}"}
        (bull if it["tone"] == "positive" else bear if it["tone"] == "negative" else []).append(item)
    for d in news.get("macro", {}).get("drivers", []):
        if d.get("id"):
            item = {"id": d["id"], "text": f"Macro: {d['text']}"}
            (bull if d["tone"] == "positive" else bear if d["tone"] == "negative" else []).append(item)
    s = ctx.stage("sentiment").get(sym)
    if s and s.get("mood") in ("bullish", "bearish"):
        item = {"id": f"SENT-{sym}", "text": f"Crowd mood {s['mood']} ({s['strength']})"}
        (bull if s["mood"] == "bullish" else bear).append(item)
    social = ctx.stage("social") or ctx.snap.get("social") or {}
    for it in social.get("items", []):
        if it.get("symbol") == sym and it.get("tone") in ("positive", "negative"):
            item = {"id": it["id"], "text": f"Social: {it['text']}"}
            (bull if it["tone"] == "positive" else bear).append(item)
    return {"bull": bull, "bear": bear}


def evidence_text(ctx, sym: str) -> dict[str, str]:
    m = menus(ctx, sym)
    out = {x["id"]: x["text"] for x in m["bull"] + m["bear"]}
    p = ctx.packs[sym]
    out.update({x["id"]: x["text"] for x in p["market"]["signals"] + p["fundamentals"]["signals"]})
    return out


def _step(order: list[str], value: str, delta: int) -> str:
    return order[max(0, min(len(order) - 1, order.index(value) + delta))]


def tally(ctx, sym: str) -> dict:
    """Score the debate. Deterministic given the agents' picks and rebuttals."""
    cfg = settings()["debate"]
    w = cfg["weights"]
    r1, r2_ = ctx.stage("debate_r1").get(sym, {}), ctx.stage("debate_r2").get(sym, {})
    text = evidence_text(ctx, sym)
    sides = {}
    for side, opp in (("bull", "bear"), ("bear", "bull")):
        rebs = {rb["target"]: rb for rb in r2_.get(opp, {}).get("rebuttals", [])}
        pts, total = [], 0.0
        for pk in r1.get(side, {}).get("picks", []):
            base = w[pk["weight"]]
            rb = rebs.get(pk["id"])
            factor = 1.0
            if rb:
                factor = cfg["outweighed_factor"] if (rb["reason"] == "outweighed_by" and rb.get("effective")) \
                    else cfg["rebutted_factor"]
            total += base * factor
            pts.append({"id": pk["id"], "text": text.get(pk["id"], ""), "weight": pk["weight"],
                        "rebuttal": rb["reason"] if rb else None, "rebuttal_by": rb.get("by") if rb else None,
                        "counted": r2(base * factor, 2)})
        sides[side] = {"points": pts, "total": r2(total, 2)}
    net = round(sides["bull"]["total"] - sides["bear"]["total"], 2)
    thr = cfg["direction_threshold"]
    direction = "up" if net >= thr else "down" if net <= -thr else "flat"
    ct = cfg["conviction_thresholds"]
    conviction = "high" if abs(net) >= ct["high"] else "medium" if abs(net) >= ct["medium"] else "low"
    quant = ctx.packs[sym]["quant_score"]
    disagree = (direction == "up" and quant < 0) or (direction == "down" and quant > 0)
    if disagree and cfg.get("quant_disagree_downgrade", True):
        conviction = _step(CONV_ORDER, conviction, -1)
    winner = "bull" if net >= thr else "bear" if net <= -thr else "draw"
    return {"bull": sides["bull"], "bear": sides["bear"], "net": net, "quant_score": quant,
            "quant_disagrees": disagree,
            "proposal": {"winner": winner, "direction": direction, "conviction": conviction}}


def clamp_override(proposal: dict, direction: str, conviction: str) -> tuple[str, str, list[str]]:
    """Research Manager may move direction and conviction at most one step from the proposal."""
    notes = []
    pd, pc = proposal["direction"], proposal["conviction"]
    di = DIR_ORDER.index(direction) - DIR_ORDER.index(pd)
    if abs(di) > 1:
        direction = _step(DIR_ORDER, pd, 1 if di > 0 else -1)
        notes.append(f"direction clamped to {direction}")
    ci = CONV_ORDER.index(conviction) - CONV_ORDER.index(pc)
    if abs(ci) > 1:
        conviction = _step(CONV_ORDER, pc, 1 if ci > 0 else -1)
        notes.append(f"conviction clamped to {conviction}")
    return direction, conviction, notes
