"""Stage 1 (Python part): Market and Fundamentals analysts + evidence packs.

These two roles from the reference flow are pure rules: zero tokens, fully
repeatable. Each signal gets an evidence ID that later agents must cite.
"""
from __future__ import annotations

from datetime import date
from statistics import median

from . import indicators as ind
from .util import r2, settings


def _sig(out: list, prefix: str, text: str, pts: int) -> None:
    out.append({"id": f"{prefix}{len(out) + 1}", "text": text, "points": pts})


# ----------------------------------------------------------------- market analyst
def market_analyst(sym: str, rows: list[dict], proxy: list[dict], adjustments: list[dict] | None = None) -> dict:
    closes = [r["close"] for r in rows]
    highs = [r["high"] or r["close"] for r in rows]
    lows = [r["low"] or r["close"] for r in rows]
    vols = [r["volume"] for r in rows]
    c = closes[-1]
    p_lv = {p["date"]: p["level"] for p in proxy}
    mkt = [p_lv[r["date"]] for r in rows if r["date"] in p_lv]

    sma20, sma50, sma200 = ind.sma(closes, 20), ind.sma(closes, 50), ind.sma(closes, 200)
    rsi = ind.rsi(closes)
    macd = ind.macd(closes)
    atr = ind.atr(highs, lows, closes)
    ret5, ret20 = ind.pct_change(closes, 5), ind.pct_change(closes, 20)
    m5, m20 = ind.pct_change(mkt, 5), ind.pct_change(mkt, 20)
    vr = (ind.sma(vols, 5) / ind.sma(vols, 20)) if ind.sma(vols, 20) else None
    tv20 = sum(a * b for a, b in zip(closes[-20:], vols[-20:])) / min(20, len(closes))
    hi52, lo52 = max(highs[-250:]), min(lows[-250:])
    pos52 = (c - lo52) / (hi52 - lo52) if hi52 > lo52 else None
    recent_days = {r["date"] for r in rows[-20:]}
    ex_recent = [a for a in (adjustments or []) if a["date"] in recent_days]
    sup20, res20 = min(lows[-20:]), max(highs[-20:])

    pre, s = f"M-{sym}-", []
    if sma20:
        _sig(s, pre, f"Close {c:.2f} is {'above' if c > sma20 else 'below'} 20-day average {sma20:.2f}",
             10 if c > sma20 else -10)
    if sma50:
        _sig(s, pre, f"Close is {'above' if c > sma50 else 'below'} 50-day average {sma50:.2f}",
             10 if c > sma50 else -10)
    if sma20 and sma50:
        _sig(s, pre, f"20-day average is {'above' if sma20 > sma50 else 'below'} 50-day average (short-term trend {'up' if sma20 > sma50 else 'down'})",
             10 if sma20 > sma50 else -10)
    if sma200:
        _sig(s, pre, f"Close is {'above' if c > sma200 else 'below'} 200-day average {sma200:.2f}",
             5 if c > sma200 else -5)
    if rsi is not None:
        if rsi > 75:
            t, p = "overbought, pullback risk", -10
        elif rsi >= 55:
            t, p = "positive momentum", 10
        elif rsi >= 45:
            t, p = "neutral momentum", 0
        elif rsi >= 30:
            t, p = "weak momentum", -5
        else:
            t, p = "oversold, bounce possible", 5
        _sig(s, pre, f"RSI(14) {rsi:.1f}: {t}", p)
    if macd:
        _sig(s, pre, f"MACD histogram {macd[2]:+.2f} ({'bullish' if macd[2] > 0 else 'bearish'} crossover side)",
             10 if macd[2] > 0 else -10)
    if ret5 is not None and m5 is not None:
        rel = ret5 - m5
        _sig(s, pre, f"5-day return {ret5:+.1f}% vs market {m5:+.1f}% (relative {rel:+.1f} pts)",
             10 if rel > 2 else -10 if rel < -2 else 0)
    if ret20 is not None and m20 is not None:
        rel = ret20 - m20
        _sig(s, pre, f"20-day return {ret20:+.1f}% vs market {m20:+.1f}% (relative {rel:+.1f} pts)",
             10 if rel > 5 else -10 if rel < -5 else 0)
    if vr is not None and ret5 is not None:
        p = (10 if ret5 > 0 else -10) if vr > 1.5 else 0
        _sig(s, pre, f"5-day volume is {vr:.2f}x the 20-day average"
             + (f" on a {'rising' if ret5 > 0 else 'falling'} price" if vr > 1.5 else ""), p)
    if pos52 is not None:
        p = 5 if pos52 > 0.9 else -5 if pos52 < 0.1 else 0
        _sig(s, pre, f"Price sits at {pos52 * 100:.0f}% of its 52-week range ({lo52:.2f} to {hi52:.2f})", p)
    _sig(s, pre, f"20-day support {sup20:.2f}, resistance {res20:.2f}", 0)
    if ex_recent:
        _sig(s, pre, "Dividend/bonus/rights adjustment on " + ", ".join(f"{a['date']} (x{a['factor']})" for a in ex_recent)
             + ": earlier prices adjusted, so the ex-date drop is not counted as a fall", 0)

    score = max(-100, min(100, sum(x["points"] for x in s)))
    return {
        "score": score, "signals": s,
        "facts": {"close": r2(c), "atr": r2(atr), "atr_pct": r2(atr / c * 100 if atr and c else None),
                  "sma20": r2(sma20), "sma50": r2(sma50), "rsi14": r2(rsi, 1),
                  "ret5_pct": r2(ret5), "ret20_pct": r2(ret20), "mkt_ret5_pct": r2(m5),
                  "vol_ratio_5_20": r2(vr), "avg_traded_value_pkr_m": r2(tv20 / 1e6, 1),
                  "support20": r2(sup20), "resistance20": r2(res20), "ex_marker_recent": [a["date"] for a in ex_recent]},
    }


# ----------------------------------------------------------------- fundamentals analyst
def _yoy_quarter(q: dict) -> tuple[str, float] | None:
    periods, eps = q.get("periods", []), q.get("rows", {}).get("EPS", [])
    if not periods or not eps:
        return None
    latest = periods[0]
    parts = latest.split()
    if len(parts) != 2 or not parts[1].isdigit():
        return None
    prior = f"{parts[0]} {int(parts[1]) - 1}"
    if prior in periods:
        a, b = eps[0], eps[periods.index(prior)]
        if a is not None and b not in (None, 0):
            return latest, (a / b - 1) * 100 * (1 if b > 0 else -1)
    return None


def fundamentals_analyst(sym: str, comp: dict, pe_median: float | None, as_of: str) -> dict:
    pre, s, catalysts = f"F-{sym}-", [], []
    if comp.get("error"):
        _sig(s, pre, f"Company page unavailable ({comp['error']}); fundamentals not scored", 0)
        return {"score": 0, "signals": s, "catalysts": catalysts, "facts": {}}
    st = comp.get("stats", {})
    pe = st.get("pe_ratio")
    if pe is not None and pe > 0 and pe_median:
        rel = pe / pe_median
        p = 15 if rel < 0.8 else -10 if rel > 1.2 else 0
        _sig(s, pre, f"P/E (TTM) {pe:.2f} vs top-30 median {pe_median:.2f} ({'cheaper' if rel < 1 else 'dearer'} by {abs(1 - rel) * 100:.0f}%)", p)
    elif pe is not None and pe <= 0:
        _sig(s, pre, "Negative trailing earnings (P/E not meaningful)", -10)
    rat = comp.get("ratios", {}).get("rows", {})
    eg = (rat.get("EPS Growth (%)") or [None])[0]
    if eg is not None:
        _sig(s, pre, f"Latest annual EPS growth {eg:+.1f}%", 10 if eg > 15 else -10 if eg < 0 else 0)
    npm = rat.get("Net Profit Margin (%)") or []
    if len(npm) >= 2 and None not in npm[:2]:
        d = npm[0] - npm[1]
        _sig(s, pre, f"Net margin {npm[0]:.1f}% vs {npm[1]:.1f}% a year earlier", 5 if d > 2 else -5 if d < -2 else 0)
    q = _yoy_quarter(comp.get("financials", {}).get("quarterly", {}))
    if q:
        _sig(s, pre, f"{q[0]} EPS {q[1]:+.1f}% vs same quarter last year", 10 if q[1] > 15 else -10 if q[1] < -10 else 0)
    yc = st.get("1-year_change")
    if yc is not None:
        _sig(s, pre, f"1-year price change {yc:+.1f}%", 0)

    a_date = date.fromisoformat(as_of)
    for a in comp.get("announcements", []):
        age = (a_date - date.fromisoformat(a["date"])).days
        t = a["title"].lower()
        if a["kind"] == "board_meetings" and 0 <= age <= 14 and "board meeting" in t:
            catalysts.append({"id": f"{pre}C{len(catalysts) + 1}", "date": a["date"],
                              "text": f"Board meeting notice ({a['date']}): results or payout may land in the window"})
        elif a["kind"] == "financial_results" and 0 <= age <= 7:
            catalysts.append({"id": f"{pre}C{len(catalysts) + 1}", "date": a["date"],
                              "text": f"Financial results published {a['date']}: {a['title'][:80]}"})
        elif a["kind"] == "others" and 0 <= age <= 7:
            catalysts.append({"id": f"{pre}C{len(catalysts) + 1}", "date": a["date"],
                              "text": f"Announcement {a['date']}: {a['title'][:90]}"})
    catalysts = catalysts[:5]
    score = max(-100, min(100, sum(x["points"] for x in s)))
    return {"score": score, "signals": s, "catalysts": catalysts,
            "facts": {"pe_ttm": pe, "eps_growth_annual_pct": eg, "free_float_pct": comp.get("free_float_pct"),
                      "sector": comp.get("sector")}}


# ----------------------------------------------------------------- run both + packs
def run(snap: dict) -> dict:
    """Returns {symbol: pack}. Pack = everything later agents need, compact."""
    pes = [snap["companies"][s].get("stats", {}).get("pe_ratio") for s in snap["universe"]]
    pes = [p for p in pes if p is not None and p > 0]
    pe_med = median(pes) if pes else None
    packs = {}
    names = {m["symbol"]: m["name"] for m in snap["members"]}
    for s in snap["universe"]:
        m = market_analyst(s, snap["prices"][s], snap["market_proxy"], snap.get("price_adjustments", {}).get(s))
        f = fundamentals_analyst(s, snap["companies"][s], pe_med, snap["as_of"])
        quant = round(0.6 * m["score"] + 0.4 * f["score"], 1)
        packs[s] = {
            "symbol": s, "name": names.get(s, s),
            "sector": f["facts"].get("sector") or snap["sector_code"].get(s),
            "market": m, "fundamentals": f,
            "quant_score": quant,
            "news": snap["stock_news"].get(s, []),
        }
    # volatility cap: the move estimate uses at most atr_cap_mult x the top-30 median ATR%
    atrs = [p["market"]["facts"]["atr_pct"] for p in packs.values() if p["market"]["facts"]["atr_pct"]]
    cap = median(atrs) * settings()["scoring"]["atr_cap_mult"] if atrs else None
    for p in packs.values():
        a = p["market"]["facts"]["atr_pct"]
        p["market"]["facts"]["atr_pct_capped"] = r2(min(a, cap)) if (a and cap) else a
    return packs


def compact_pack(p: dict, extra: dict | None = None) -> dict:
    """The ~300-token version agents read: ids + short text, no raw prices."""
    mf = p["market"]["facts"]
    out = {
        "symbol": p["symbol"], "name": p["name"], "sector": p["sector"],
        "close": mf["close"], "atr_pct": mf["atr_pct"], "avg_traded_value_pkr_m": mf["avg_traded_value_pkr_m"],
        "market_score": p["market"]["score"], "fundamental_score": p["fundamentals"]["score"],
        "quant_score": p["quant_score"],
        "evidence": [{"id": x["id"], "text": x["text"]} for x in p["market"]["signals"] + p["fundamentals"]["signals"]]
                    + [{"id": c["id"], "text": c["text"]} for c in p["fundamentals"]["catalysts"]],
    }
    if extra:
        out.update(extra)
    return out

