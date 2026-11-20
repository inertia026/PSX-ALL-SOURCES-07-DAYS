"""Hybrid score and ranking: pure formula, so the order is fully repeatable.

expected_move_% = direction_sign x conviction_mult x ATR%(14) x sqrt(5) x move_k
hybrid_score    = expected_move_% x (1 - risk_penalty) - liquidity_penalty
order           = hybrid_score desc, quant_score desc, ticker A->Z
"""
from __future__ import annotations

import math

from .util import r2, settings


def expected_move(atr_pct: float | None, direction: str, conviction: str) -> float:
    sc = settings()["scoring"]
    if not atr_pct:
        return 0.0
    return sc["direction_sign"].get(direction, 0) * sc["conviction_mult"].get(conviction, 0) \
        * atr_pct * math.sqrt(settings()["horizon"]["trading_days"]) * sc["move_k"]


def levels(facts: dict, direction: str, conviction: str) -> dict:
    """Entry/target/stop from volatility (Python, not the LLM)."""
    c, atr = facts.get("close"), facts.get("atr")
    mv = expected_move(facts.get("atr_pct"), direction, conviction)
    if not c or not atr:
        return {"expected_move_pct": r2(mv)}
    out = {"entry_ref": r2(c), "expected_move_pct": r2(mv), "target": r2(c * (1 + mv / 100))}
    if direction == "up":
        out["stop"] = r2(c - 1.2 * atr)
    elif direction == "down":
        out["note"] = "Short selling is limited on PSX; a 'down' call means avoid/reduce."
        out["stop"] = r2(c + 1.2 * atr)
    return out


def rank(ctx) -> list[dict]:
    from .stages import risk_consensus  # local import avoids a cycle

    cfg = settings()
    pm, rm, tr = ctx.stage("portfolio_manager"), ctx.stage("research_manager"), ctx.stage("trader")
    liq_min = cfg["liquidity"]["min_avg_traded_value_pkr"] / 1e6
    rows = []
    for s in ctx.snap["universe"]:
        p, f = ctx.packs[s], ctx.packs[s]["market"]["facts"]
        rc = risk_consensus(ctx, s)
        v = pm.get(s) or {"final_direction": rm.get(s, {}).get("direction", "flat"),
                          "final_conviction": rc["conviction_after_risk"], "flag": "none", "reason": ""}
        mv = expected_move(f["atr_pct"], v["final_direction"], v["final_conviction"])
        illiquid = (f["avg_traded_value_pkr_m"] or 0) < liq_min
        hybrid = mv * (1 - cfg["scoring"]["risk_penalty"][rc["risk_rating"]]) \
            - (cfg["liquidity"]["penalty_pct_points"] if illiquid else 0)
        rows.append({
            "symbol": s, "name": p["name"], "sector": p["sector"], "close": f["close"],
            "final_direction": v["final_direction"], "final_conviction": v["final_conviction"],
            "risk_rating": rc["risk_rating"], "flag": v.get("flag", "none"), "pm_reason": v.get("reason", ""),
            "expected_move_pct": r2(mv), "hybrid_score": r2(hybrid, 3), "quant_score": p["quant_score"],
            "market_score": p["market"]["score"], "fundamental_score": p["fundamentals"]["score"],
            "illiquid": illiquid, "atr_pct": f["atr_pct"],
            "winner": rm.get(s, {}).get("winner"), "setup": tr.get(s, {}).get("setup"),
            "deciding_points": [d["text"] for d in rm.get(s, {}).get("deciding_points", [])],
            "levels": levels(f, v["final_direction"], v["final_conviction"]),
        })
    rows.sort(key=lambda r: (-r["hybrid_score"], -r["quant_score"], r["symbol"]))
    for i, r in enumerate(rows, 1):
        r["rank"] = i
        r["top"] = i <= cfg["scoring"]["top_n"]
    return rows
