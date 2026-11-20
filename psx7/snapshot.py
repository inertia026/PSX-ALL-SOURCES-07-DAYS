"""Stage 0: fetch everything once and freeze it.

Agents only ever read this snapshot. Its SHA-256 fingerprint is part of every
agent cache key, so the same snapshot always replays the same answers.
"""
from __future__ import annotations

import re
from datetime import date, datetime, timedelta, timezone

import yaml

from . import sources
from .util import CONFIG_DIR, RUNS_DIR, r2, read_json, settings, sha256, write_json

MACRO_WORDS = [
    "SBP", "State Bank", "policy rate", "interest rate", "monetary policy", "IMF", "rupee", "PKR",
    "inflation", "CPI", "oil price", "Brent", "crude", "budget", "KSE-100", "KSE100", "PSX",
    "stock market", "foreign investors", "FIPI", "remittances", "current account", "reserves",
    "T-bill", "PIB", "circular debt", "Moody", "Fitch", "S&P", "GDP", "tax",
]
NAME_DROP = r"\b(the|limited|ltd|company|co|corporation|pakistan|\(pakistan\)|of)\b"


def run_dir(as_of: str):
    return RUNS_DIR / as_of


def _aliases() -> tuple[dict, set]:
    data = yaml.safe_load((CONFIG_DIR / "aliases.yaml").read_text(encoding="utf-8")) or {}
    return data.get("aliases", {}) or {}, set(data.get("ticker_word_blocklist", []) or [])


def match_patterns(symbol: str, name: str) -> list[re.Pattern]:
    aliases, block = _aliases()
    words = set(aliases.get(symbol, []))
    core = re.sub(r"\s+", " ", re.sub(NAME_DROP, " ", name, flags=re.I)).strip(" .&")
    if len(core) >= 6:
        words.add(core)
    pats = [re.compile(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", re.I) for w in sorted(words)]
    if symbol not in block and len(symbol) >= 3:
        pats.append(re.compile(r"(?<![A-Za-z])" + re.escape(symbol) + r"(?![A-Za-z])"))  # case-sensitive
    return pats


def breadth_last_days(history: dict[str, list[dict]], n: int) -> list[dict]:
    """Advancers / decliners / traded value for the whole market, last n days."""
    days = sorted({r["date"] for rows in history.values() for r in rows})[-n:]
    agg = {d: {"date": d, "advancers": 0, "decliners": 0, "unchanged": 0, "traded_value_pkr_m": 0.0}
           for d in days}
    for rows in history.values():
        for r in rows[-(n + 2):]:
            a = agg.get(r["date"])
            if a is None or not r["ldcp"] or not r["volume"]:
                continue
            a["traded_value_pkr_m"] += r["close"] * r["volume"] / 1e6
            key = "advancers" if r["close"] > r["ldcp"] else "decliners" if r["close"] < r["ldcp"] else "unchanged"
            a[key] += 1
    for a in agg.values():
        a["traded_value_pkr_m"] = r2(a["traded_value_pkr_m"], 1)
    return [agg[d] for d in days]


def market_proxy(history: dict[str, list[dict]], members: list[dict]) -> list[dict]:
    """Free-float-weighted KSE-100 proxy built from constituent closes.

    PSX does not offer free index history to scripts, so we rebuild it:
    daily return = sum(ff_shares * close_prev * ret) / sum(ff_shares * close_prev).
    """
    ff = {m["symbol"]: m["free_float_shares"] or 0 for m in members}
    closes: dict[str, dict[str, float]] = {}
    for s in ff:
        for row in history.get(s, []):
            closes.setdefault(row["date"], {})[s] = row["close"]
    days = sorted(closes)
    level, out = 100.0, [{"date": days[0], "level": 100.0}] if days else []
    for prev, cur in zip(days, days[1:]):
        num = den = 0.0
        for s, c in closes[cur].items():
            p = closes[prev].get(s)
            if p:
                w = ff[s] * p
                num += w * (c / p - 1)
                den += w
        level *= 1 + (num / den if den else 0)
        out.append({"date": cur, "level": r2(level, 4)})
    return out


def build(requested: date, refresh: bool = False, log=print) -> dict:
    cfg = settings()
    # resolve the actual last trading day first (cheap: walks back a few files)
    as_of, _ = sources.load_history(requested, 1, log=lambda *_: None)
    out_dir = run_dir(as_of) / "snapshot"
    snap_path = out_dir / "snapshot.json"
    if snap_path.exists() and not refresh:
        log(f"Snapshot for {as_of} already exists; reusing it (use --refresh to rebuild).")
        return read_json(snap_path)

    log(f"Building snapshot as of {as_of} (requested {requested.isoformat()})")
    _, history = sources.load_history(date.fromisoformat(as_of), cfg["history"]["trading_days"], log=log)

    log("Fetching KSE-100 constituents ...")
    members = [m for m in sources.kse100_constituents() if m["symbol"] in history]
    for m in members:
        last = history[m["symbol"]][-1]
        m["close"] = last["close"]
        m["free_float_mcap"] = r2((m["free_float_shares"] or 0) * last["close"], 0)
    members.sort(key=lambda m: (-(m["free_float_mcap"] or 0), m["symbol"]))
    universe = sorted(m["symbol"] for m in members[: cfg["universe"]["size"]])
    log(f"Universe (top {len(universe)} by free-float market cap): {', '.join(universe)}")

    companies, errors = {}, []
    for i, s in enumerate(universe, 1):
        c = sources.company_page(s)
        if "error" in c:
            errors.append(f"company page {s}: {c['error']}")
        companies[s] = c
        if i % 10 == 0:
            log(f"  company pages: {i}/{len(universe)}")

    log("Fetching news feeds ...")
    news, news_err = sources.fetch_news(log=log)
    errors += news_err
    cutoff = (date.fromisoformat(as_of) - timedelta(days=cfg["news"]["lookback_days"])).isoformat()
    news = [n for n in news if n["published_utc"][:10] > cutoff]

    names = {m["symbol"]: m["name"] for m in members}
    stock_news: dict[str, list[dict]] = {s: [] for s in universe}
    macro: list[dict] = []
    macro_re = re.compile("|".join(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])" for w in MACRO_WORDS), re.I)
    pats = {s: match_patterns(s, names[s]) for s in universe}
    for n in news:
        text = f"{n['title']} {n['summary']}"
        for s in universe:
            if any(p.search(text) for p in pats[s]):
                stock_news[s].append(n)
        if macro_re.search(n["title"]):
            macro.append(n)
    k = cfg["news"]["max_items_per_stock"]
    for s in universe:
        stock_news[s] = [dict(n, id=f"N-{s}-{i}") for i, n in enumerate(stock_news[s][:k], 1)]
    macro = [dict(n, id=f"MAC-{i}") for i, n in enumerate(macro[: cfg["news"]["max_macro_items"]], 1)]

    breadth = breadth_last_days(history, 5)

    keep = ("date", "open", "high", "low", "close", "volume", "ldcp", "ex_marker")
    snap = {
        "as_of": as_of,
        "window": sources.next_trading_days(date.fromisoformat(as_of), cfg["horizon"]["trading_days"]),
        "universe": universe,
        "members": [{k2: m[k2] for k2 in ("symbol", "name", "free_float_shares", "free_float_mcap",
                                          "index_weight_pct", "close")} for m in members],
        "prices": {s: [{k2: r[k2] for k2 in keep} for r in history[s]] for s in universe},
        "sector_code": {s: history[s][-1]["sector_code"] for s in universe},
        "companies": companies,
        "market_proxy": market_proxy(history, members),
        "breadth_5d": breadth,
        "stock_news": stock_news,
        "macro_news": macro,
        "fipi_lipi": sources.manual_fipi_lipi(),
        "social": None,          # filled by the optional social-collector agent
        "source_errors": sorted(errors),
    }
    snap["fingerprint"] = sha256({k2: v for k2, v in snap.items() if k2 != "fingerprint"})
    snap["meta"] = {"fetched_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "note": "meta is excluded from the fingerprint"}
    write_json(snap_path, snap)
    log(f"Snapshot saved: {snap_path}  fingerprint {snap['fingerprint'][:12]}")
    return snap


def attach_social(as_of: str, social: dict) -> dict:
    """Add the social-collector's output and re-fingerprint (done once, before agents run)."""
    path = run_dir(as_of) / "snapshot" / "snapshot.json"
    snap = read_json(path)
    snap["social"] = social
    snap["fingerprint"] = sha256({k: v for k, v in snap.items() if k not in ("fingerprint", "meta")})
    write_json(path, snap)
    return snap
