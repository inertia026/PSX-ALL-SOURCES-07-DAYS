"""Walk-forward backtest of the Python market signals (zero tokens).

For every week in the past N trading days and every liquid KSE-100 member it
computes the live Market Analyst score (the real `analysts.market_analyst`
code, on the same 260-day window a live run sees) plus a set of raw candidate
features, and the stock's next-5-day return relative to the KSE-100 proxy.

A signal is useful only if it ranks next week's relative returns correctly,
week after week. Reported per signal:
  - mean weekly IC (Spearman rank correlation with next-5-day excess return)
  - t-stat of the weekly ICs and the share of weeks with IC > 0
  - top-20% minus bottom-20% next-5-day excess return
  - the same IC on the first and second half of the period (stability check)

Limits: KSE-100 members are today's list (survivorship bias); fundamentals,
news and agents are not backtested (no point-in-time history).
"""
from __future__ import annotations

import math
import statistics as st
from datetime import date

from . import analysts, sources
from . import indicators as ind
from .snapshot import market_proxy
from .util import RUNS_DIR, r2, read_json, settings, write_json

OUT = RUNS_DIR / "backtest"
LOOKBACK = 260           # rows a live run gives the Market Analyst
WARMUP = 200             # need a 200-day average before the first test week
H = 5                    # forecast horizon (trading days)
CLIP = 20.0              # clip 5-day excess returns at +/-20% for averages: a few unadjusted splits
                         # or data errors (e.g. +1600%) would otherwise swamp the means


def clip(x: float) -> float:
    return max(-CLIP, min(CLIP, x))


# ------------------------------------------------------------------ stats
def ranks(xs: list[float]) -> list[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    r, i = [0.0] * len(xs), 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            r[order[k]] = (i + j) / 2
        i = j + 1
    return r


def spearman(a: list[float], b: list[float]) -> float | None:
    if len(a) < 5 or len(set(a)) < 2 or len(set(b)) < 2:
        return None
    ra, rb = ranks(a), ranks(b)
    ma, mb = st.mean(ra), st.mean(rb)
    num = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    den = math.sqrt(sum((x - ma) ** 2 for x in ra) * sum((y - mb) ** 2 for y in rb))
    return num / den if den else None


# ------------------------------------------------------------------ features
def features(rows: list[dict], proxy_lv: dict[str, float]) -> dict[str, float | None]:
    """Raw candidate features from adjusted rows (oldest -> newest), as of the last row."""
    c = [r["close"] for r in rows]
    v = [r["volume"] for r in rows]
    mkt = [proxy_lv[r["date"]] for r in rows if r["date"] in proxy_lv]
    last = c[-1]

    def rel(n):
        a, b = ind.pct_change(c, n), ind.pct_change(mkt, n)
        return None if a is None or b is None else a - b

    s20, s50, s200 = ind.sma(c, 20), ind.sma(c, 50), ind.sma(c, 200)
    m = ind.macd(c)
    a = ind.atr([r["high"] or r["close"] for r in rows], [r["low"] or r["close"] for r in rows], c)
    vr = (ind.sma(v, 5) / ind.sma(v, 20)) if ind.sma(v, 20) else None
    r5 = ind.pct_change(c, 5)
    hi, lo = max(c[-250:]), min(c[-250:])
    return {
        "rel_ret_1d": rel(1), "rel_ret_5d": rel(5), "rel_ret_20d": rel(20), "rel_ret_60d": rel(60),
        "rsi14": ind.rsi(c),
        "dist_sma20_pct": (last / s20 - 1) * 100 if s20 else None,
        "dist_sma50_pct": (last / s50 - 1) * 100 if s50 else None,
        "dist_sma200_pct": (last / s200 - 1) * 100 if s200 else None,
        "trend_sma20_vs_50_pct": (s20 / s50 - 1) * 100 if s20 and s50 else None,
        "macd_hist_pct": m[2] / last * 100 if m else None,
        "volume_ratio_5_20": vr,
        "volume_x_direction": (vr - 1) * (1 if r5 and r5 > 0 else -1) if vr and r5 is not None else None,
        "pos_52w": (last - lo) / (hi - lo) if hi > lo else None,
        "atr_pct": a / last * 100 if a else None,
        "volatility_20d": ind.stdev_returns(c, 20),
    }


# ------------------------------------------------------------------ data
def load(to: date, n_days: int, log=print):
    _, hist = sources.load_history(to, n_days, log=log)
    snaps = sorted(p for p in RUNS_DIR.glob("*/snapshot/snapshot.json"))
    if snaps:
        members = read_json(snaps[-1])["members"]
    else:
        members = [m for m in sources.kse100_constituents() if m["symbol"] in hist]
    adj = {}
    for m in members:
        if m["symbol"] in hist:
            adj[m["symbol"]], _ = sources.adjust_history(hist[m["symbol"]])
    members = [m for m in members if m["symbol"] in adj]
    return adj, members, market_proxy(adj, members)


# ------------------------------------------------------------------ run
def observations(adj: dict, proxy: list[dict], min_tv_pkr_m: float, log=print) -> list[dict]:
    plv = {p["date"]: p["level"] for p in proxy}
    days = [p["date"] for p in proxy]
    idx = {d: i for i, d in enumerate(days)}
    # test dates: every 5th trading day counting back from the last date with a full forward window
    tests = days[WARMUP: len(days) - H][::-1][::H][::-1]
    pos = {s: {r["date"]: i for i, r in enumerate(rows)} for s, rows in adj.items()}
    obs = []
    for k, d in enumerate(tests):
        d_end = days[idx[d] + H]
        mret = (plv[d_end] / plv[d] - 1) * 100
        for s in sorted(adj):
            i, rows = pos[s].get(d), adj[s]
            j = pos[s].get(d_end)
            if i is None or j is None or i < WARMUP:
                continue
            win = rows[max(0, i + 1 - LOOKBACK): i + 1]
            tv = sum(r["close"] * r["volume"] for r in win[-20:]) / 20 / 1e6
            if tv < min_tv_pkr_m:
                continue
            fwd = (rows[j]["close"] / rows[i]["close"] - 1) * 100
            ma = analysts.market_analyst(s, win, proxy)
            o = {"date": d, "symbol": s, "fwd_ret_pct": fwd, "fwd_excess_pct": fwd - mret,
                 "market_score": ma["score"], **features(win, plv)}
            obs.append(o)
        if (k + 1) % 20 == 0:
            log(f"  backtest weeks: {k + 1}/{len(tests)}")
    return obs


def evaluate(obs: list[dict], key: str, target: str = "fwd_excess_pct") -> dict:
    weeks = sorted({o["date"] for o in obs})
    ics, spreads = [], []
    for w in weeks:
        g = [o for o in obs if o["date"] == w and o.get(key) is not None]
        ic = spearman([o[key] for o in g], [o[target] for o in g])
        if ic is None:
            continue
        ics.append((w, ic))
        g.sort(key=lambda o: o[key])
        q = max(1, len(g) // 5)
        spreads.append(st.mean(clip(o[target]) for o in g[-q:]) - st.mean(clip(o[target]) for o in g[:q]))
    if len(ics) < 4:
        return {"signal": key, "weeks": len(ics)}
    vals = [x for _, x in ics]
    half = len(vals) // 2
    sd = st.stdev(vals)
    return {"signal": key, "weeks": len(vals), "mean_ic": r2(st.mean(vals), 4),
            "t_stat": r2(st.mean(vals) / sd * math.sqrt(len(vals)) if sd else None),
            "pct_weeks_positive": r2(100 * sum(x > 0 for x in vals) / len(vals), 1),
            "top_minus_bottom_pct": r2(st.mean(spreads), 3),
            "ic_first_half": r2(st.mean(vals[:half]), 4), "ic_second_half": r2(st.mean(vals[half:]), 4)}


def buckets(obs: list[dict], key: str, n: int = 5) -> list[dict]:
    """Average next-5-day outcome per score bucket (pooled), for calibrating the expected move."""
    g = sorted((o for o in obs if o.get(key) is not None), key=lambda o: o[key])
    out, size = [], len(g) // n
    for b in range(n):
        part = g[b * size: (b + 1) * size if b < n - 1 else len(g)]
        out.append({"bucket": b + 1, "from": r2(part[0][key]), "to": r2(part[-1][key]), "n": len(part),
                    "avg_fwd_excess_pct": r2(st.mean(clip(o["fwd_excess_pct"]) for o in part), 3),
                    "median_fwd_excess_pct": r2(st.median(o["fwd_excess_pct"] for o in part), 3),
                    "pct_beat_market": r2(100 * sum(o["fwd_excess_pct"] > 0 for o in part) / len(part), 1),
                    "avg_abs_fwd_pct": r2(st.mean(abs(clip(o["fwd_ret_pct"])) for o in part), 3)})
    return out


def run(to: date, n_days: int = 760, log=print) -> dict:
    cfg = settings()
    adj, members, proxy = load(to, n_days, log=log)
    log(f"Backtest: {len(adj)} KSE-100 members, {len(proxy)} trading days")
    obs = observations(adj, proxy, cfg["liquidity"]["min_avg_traded_value_pkr"] / 1e6, log=log)
    keys = [k for k in obs[0] if k not in ("date", "symbol", "fwd_ret_pct", "fwd_excess_pct")] if obs else []
    res = {"to": proxy[-1]["date"] if proxy else None, "from": obs[0]["date"] if obs else None,
           "members": len(adj), "observations": len(obs), "weeks": len({o["date"] for o in obs}),
           "signals": sorted((evaluate(obs, k) for k in keys), key=lambda r: -(r.get("mean_ic") or -9)),
           "market_score_buckets": buckets(obs, "market_score")}
    OUT.mkdir(parents=True, exist_ok=True)
    write_json(OUT / "backtest.json", res)
    (OUT / "backtest.md").write_text(markdown(res), encoding="utf-8")
    log(f"Backtest written: {OUT / 'backtest.md'}")
    return res


def markdown(res: dict) -> str:
    L = ["# Backtest of the Python market signals", "",
         f"Weekly walk-forward from **{res['from']}** to **{res['to']}**: {res['weeks']} weeks, "
         f"{res['members']} KSE-100 members (liquid ones only), {res['observations']} stock-weeks.",
         "Target: next-5-day return **relative to the KSE-100 proxy**. Zero tokens. "
         f"Averages clip returns at ±{CLIP:.0f}% so a few data errors cannot dominate.", "",
         "IC = rank correlation between the signal and next week's relative return, averaged over weeks. "
         "|t| ≥ 2 is a reasonably steady effect; positive IC means 'higher value, better next week'.", "",
         "| Signal | Mean IC | t-stat | Weeks IC > 0 | Top 20% − bottom 20% | IC 1st half | IC 2nd half |",
         "|---|---|---|---|---|---|---|"]
    for s in res["signals"]:
        if "mean_ic" not in s:
            continue
        name = f"**{s['signal']}**" if s["signal"] == "market_score" else s["signal"]
        L.append(f"| {name} | {s['mean_ic']:+.3f} | {s['t_stat']:+.2f} | {s['pct_weeks_positive']}% | "
                 f"{s['top_minus_bottom_pct']:+.2f}% | {s['ic_first_half']:+.3f} | {s['ic_second_half']:+.3f} |")
    L += ["", "## Market score buckets (pooled)", "",
          "| Bucket | Score range | Stock-weeks | Avg next-5d vs market | Median vs market | Beat market | Avg size of move |", "|---|---|---|---|---|---|---|"]
    for b in res["market_score_buckets"]:
        L.append(f"| {b['bucket']} | {b['from']:+.0f} to {b['to']:+.0f} | {b['n']} | {b['avg_fwd_excess_pct']:+.2f}% | "
                 f"{b['median_fwd_excess_pct']:+.2f}% | {b['pct_beat_market']}% | {b['avg_abs_fwd_pct']:.2f}% |")
    L += ["", "_Limits: today's KSE-100 list is used for the whole period (survivorship bias). Fundamentals, news "
          "and agents are not backtested._", ""]
    return "\n".join(L)
