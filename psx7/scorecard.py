"""Score earlier runs once their 5-day window has closed. Price data only, zero tokens."""
from __future__ import annotations

from datetime import date

from . import sources
from .util import RUNS_DIR, Http, r2, read_json, write_json


def closes_on(d: str, http: Http) -> dict[str, float]:
    text = sources.eod_file(date.fromisoformat(d), http, date.today())
    return {r["symbol"]: r["close"] for r in sources.parse_eod_text(text)} if text else {}


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
    http = Http()
    end_close, end_day = {}, None
    for d in reversed(window):            # last trading day inside the window with a file
        end_close = closes_on(d, http)
        if end_close:
            end_day = d
            break
    start_close = closes_on(run_as_of, http)
    if not end_close or not start_close:
        log(f"  scorecard {run_as_of}: price files missing, will retry next run")
        return None
    rows = []
    for r in ranking["rows"]:
        s = r["symbol"]
        if s in end_close and start_close.get(s):
            ret = (end_close[s] / start_close[s] - 1) * 100
            rows.append({"symbol": s, "rank": r["rank"], "direction": r["final_direction"],
                         "hybrid_score": r["hybrid_score"], "actual_ret_pct": r2(ret), "hit": hit(r["final_direction"], ret)})
    snap = read_json(run / "snapshot" / "snapshot.json")
    num = den = 0.0
    for m in snap["members"]:
        s0, s1 = start_close.get(m["symbol"]), end_close.get(m["symbol"])
        if s0 and s1 and m["free_float_shares"]:
            w = m["free_float_shares"] * s0
            num += w * (s1 / s0 - 1)
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
