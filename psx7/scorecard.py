"""Score earlier runs once their 5-day window has closed. Price data only, zero tokens."""
from __future__ import annotations

from datetime import date

from . import sources
from .util import RUNS_DIR, Http, r2, read_json, write_json


def rows_on(d: str, http: Http) -> dict[str, tuple[float, float]]:
    """{symbol: (close, ldcp)} for one trading day (empty if market closed / no file)."""
    text = sources.eod_file(date.fromisoformat(d), http, date.today())
    return {r["symbol"]: (r["close"], r["ldcp"]) for r in sources.parse_eod_text(text)} if text else {}


def window_returns(window: list[str], today_as_of: str, http: Http) -> tuple[dict[str, float], str | None]:
    """Total return % per symbol over the window, chaining close/LDCP day by day.

    PSX's LDCP is the previous close adjusted for dividends/bonus/rights, so the
    chain counts an ex-date correctly instead of as a fall.
    """
    growth: dict[str, float] = {}
    last = None
    for d in window:
        if d > today_as_of:
            break
        day = rows_on(d, http)
        if not day:
            continue
        last = d
        for s, (c, l) in day.items():
            if c and l:
                growth[s] = growth.get(s, 1.0) * (c / l)
    return {s: (g - 1) * 100 for s, g in growth.items()}, last


def _ranks(xs: list[float]) -> list[float]:
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    rk = [0.0] * len(xs)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        for k in range(i, j + 1):
            rk[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return rk


def spearman(a: list[float], b: list[float]) -> float | None:
    if len(a) < 3:
        return None
    ra, rb = _ranks(a), _ranks(b)
    ma, mb = sum(ra) / len(ra), sum(rb) / len(rb)
    cov = sum((x - ma) * (y - mb) for x, y in zip(ra, rb))
    va = sum((x - ma) ** 2 for x in ra) ** 0.5
    vb = sum((y - mb) ** 2 for y in rb) ** 0.5
    return cov / (va * vb) if va and vb else None


def hit(direction: str, ret: float) -> bool:
    return ret > 0 if direction == "up" else ret < 0 if direction == "down" else abs(ret) <= 1.0


def score_run(run_as_of: str, today_as_of: str, log=print) -> dict | None:
    run = RUNS_DIR / run_as_of
    rk_path, sc_path = run / "ranking.json", run / "scorecard.json"
    if not rk_path.exists() or sc_path.exists():
        return None
    ranking = read_json(rk_path)
    window = ranking["window"]
    if window[-1] > today_as_of:
        return None  # window not finished yet
    rets, end_day = window_returns(window, today_as_of, Http())
    if not rets:
        log(f"  scorecard {run_as_of}: price files missing, will retry next run")
        return None
    rows = []
    for r in ranking["rows"]:
        s = r["symbol"]
        if s in rets:
            ret = rets[s]
            rows.append({"symbol": s, "rank": r["rank"], "direction": r["final_direction"],
                         "hybrid_score": r["hybrid_score"], "actual_ret_pct": r2(ret), "hit": hit(r["final_direction"], ret)})
    bench = ranking.get("benchmark_members")
    if bench is None:                      # older runs: fall back to the local snapshot if present
        sp = run / "snapshot" / "snapshot.json"
        bench = [[m["symbol"], m["free_float_shares"], m["close"]] for m in read_json(sp)["members"]] if sp.exists() else []
    num = den = 0.0
    for sym, ff, close in bench:
        if sym in rets and ff and close:
            w = ff * close
            num += w * rets[sym] / 100
            den += w
    top = [x for x in rows if x["rank"] <= 5]
    res = {
        "as_of": run_as_of, "window_end": end_day, "n": len(rows),
        "hit_rate_pct": r2(100 * sum(x["hit"] for x in rows) / len(rows)) if rows else None,
        "spearman_score_vs_return": r2(spearman([x["hybrid_score"] for x in rows], [x["actual_ret_pct"] for x in rows]), 3),
        "top5_avg_ret_pct": r2(sum(x["actual_ret_pct"] for x in top) / len(top)) if top else None,
        "kse100_proxy_ret_pct": r2(num / den * 100) if den else None,
        "rows": rows,
    }
    if res["top5_avg_ret_pct"] is not None and res["kse100_proxy_ret_pct"] is not None:
        res["top5_excess_pct"] = r2(res["top5_avg_ret_pct"] - res["kse100_proxy_ret_pct"])
    write_json(sc_path, res)
    log(f"  scored {run_as_of}: hit rate {res['hit_rate_pct']}%, top5 {res['top5_avg_ret_pct']}% vs KSE-100 proxy {res['kse100_proxy_ret_pct']}%")
    return res


def update_all(today_as_of: str, log=print) -> None:
    if not RUNS_DIR.exists():
        return
    for d in sorted(p.name for p in RUNS_DIR.iterdir() if p.is_dir() and p.name < today_as_of):
        score_run(d, today_as_of, log=log)
    write_markdown()


def write_markdown() -> None:
    cards = [read_json(p) for p in sorted(RUNS_DIR.glob("*/scorecard.json"))]
    lines = ["# Scorecard", "",
             "Each run is scored after its 5-trading-day window closes. Price data only; no Claude calls.", "",
             "| Run (as of) | Window end | Hit rate | Rank corr. | Top 5 avg | KSE-100 proxy | Top 5 excess |",
             "|---|---|---|---|---|---|---|"]
    for c in cards:
        lines.append(f"| {c['as_of']} | {c['window_end']} | {c['hit_rate_pct']}% | {c['spearman_score_vs_return']} | "
                     f"{c['top5_avg_ret_pct']}% | {c['kse100_proxy_ret_pct']}% | {c.get('top5_excess_pct')}% |")
    if cards:
        def avg(k):
            v = [c[k] for c in cards if c.get(k) is not None]
            return r2(sum(v) / len(v)) if v else None
        lines += ["", f"**Average over {len(cards)} run(s):** hit rate {avg('hit_rate_pct')}%, "
                  f"rank corr. {avg('spearman_score_vs_return')}, top-5 excess {avg('top5_excess_pct')}%."]
    else:
        lines += ["", "_No runs scored yet._"]
    (RUNS_DIR / "scorecard.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
