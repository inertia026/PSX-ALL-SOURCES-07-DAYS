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
NAME_SUFFIX = r"\b(the|limited|ltd\.?|company limited|\(pakistan\))\b"
FLOW_RE = re.compile(r"(?<![A-Za-z])(foreign investors?|foreign buying|foreign selling|foreign outflows?|"
                     r"foreign inflows?|FIPI|LIPI|overseas investors?)(?![A-Za-z])", re.I)


def run_dir(as_of: str):
    return RUNS_DIR / as_of


PK_CONTEXT = re.compile(r"(?<![A-Za-z])(Pakistan\w*|PSX|KSE|SBP|rupee|PKR|Karachi|Islamabad|Lahore|Punjab|Sindh)(?![A-Za-z])", re.I)


def _aliases() -> tuple[dict, set]:
    data = yaml.safe_load((CONFIG_DIR / "aliases.yaml").read_text(encoding="utf-8")) or {}
    return data.get("aliases", {}) or {}, set(data.get("ticker_word_blocklist", []) or [])


def _strict() -> set[str]:
    data = yaml.safe_load((CONFIG_DIR / "aliases.yaml").read_text(encoding="utf-8")) or {}
    return set(data.get("strict_aliases", []) or [])


class StrictPattern:
    """Matches an alias only when it is NOT preceded by another capitalised word.

    'Systems Limited posts profit' matches; 'Fujiyama Power Systems Limited' does not.
    """

    def __init__(self, w: str):
        self.w = w
        self.rx = re.compile(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", re.I)

    def search(self, text: str):
        for m in self.rx.finditer(text):
            before = text[: m.start()].rstrip()
            prev = before.split()[-1] if before.split() else ""
            if not (prev[:1].isupper() and prev.strip("\"'‘’(").isalpha()):
                return m
        return None


def _pat(w: str) -> re.Pattern:
    """ALL-CAPS names match case-sensitively (PPL, HBL); others ignore case."""
    flags = 0 if w.upper() == w else re.I
    return re.compile(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])", flags)


def core_name(name: str) -> str:
    return re.sub(r"\s+", " ", re.sub(NAME_SUFFIX, " ", name, flags=re.I)).strip(" .&,")


def match_patterns(symbol: str, name: str) -> list[re.Pattern]:
    """Patterns that identify a company in a headline.

    Aliases from config/aliases.yaml, the ticker (unless it is a common word), and the
    company name without 'Limited' etc., used only if it is 2+ words and matched
    case-sensitively (so 'Pakistan Petroleum' never matches 'petroleum levy').
    """
    aliases, block = _aliases()
    strict = _strict()
    pats = [StrictPattern(w) if w in strict else _pat(w) for w in sorted(set(aliases.get(symbol, [])))]
    core = core_name(name)
    if len(core.split()) >= 2:
        pats.append(re.compile(r"(?<![A-Za-z])" + re.escape(core) + r"(?![A-Za-z])"))
    if symbol not in block and len(symbol) >= 3:
        pats.append(re.compile(r"(?<![A-Za-z])" + re.escape(symbol) + r"(?![A-Za-z])"))
    return pats


def google_query(symbol: str, name: str, days: int) -> str:
    aliases, _ = _aliases()
    names = [w for w in aliases.get(symbol, []) if len(w) > 4][:3] or [core_name(name)]
    return " OR ".join(f'"{w}"' for w in names) + f" when:{days}d"


def collect_news(as_of: str, window_start: str, universe: list[str], names: dict[str, str],
                 log=print) -> tuple[dict, list, list, list]:
    """News for the window [as_of - lookback, window_start). Returns (stock, macro, flows, errors).

    Sources: RSS feeds (1-3 days deep) + Google News RSS search per company and for
    macro topics (about 14 days deep). Headlines are matched to companies by title.
    """
    cfg = settings()["news"]
    lo = (date.fromisoformat(as_of) - timedelta(days=cfg["lookback_days"])).isoformat()
    junk = re.compile("|".join(re.escape(j) for j in cfg.get("junk_title_patterns", [])) or "$^", re.I)
    in_window = lambda n: lo < n["published_utc"][:10] < window_start and not junk.search(n["title"])  # noqa: E731

    feed_items, errors = sources.fetch_news(log=log)
    pats = {s: match_patterns(s, names[s]) for s in universe}
    stock: dict[str, list[dict]] = {s: [] for s in universe}
    pool: list[dict] = [n for n in feed_items if in_window(n)]
    for n in pool:
        text = f"{n['title']} {n['summary']}"
        for s in universe:
            if any(p.search(text) for p in pats[s]):
                stock[s].append(n)

    macro_pool = list(pool)
    if cfg.get("google_news", True):
        http = sources.Http(delay=1.0)
        days = cfg["lookback_days"]
        log(f"  Google News search: {len(universe)} companies + {len(cfg.get('macro_queries', []))} macro topics ...")
        for s in universe:
            items, err = sources.google_news(google_query(s, names[s], days), http)
            if err:
                errors.append(err)
            for n in items:
                if in_window(n) and any(p.search(n["title"]) for p in pats[s]):
                    stock[s].append(n)
        for q in cfg.get("macro_queries", []):
            items, err = sources.google_news(f"{q} when:{days}d", http)
            if err:
                errors.append(err)
            macro_pool += [n for n in items if in_window(n) and PK_CONTEXT.search(n["title"])]

    def dedupe(items):
        seen, out = set(), []
        for n in sorted(items, key=lambda x: (x["published_utc"], x["title"]), reverse=True):
            k = re.sub(r"\W+", " ", n["title"].lower()).strip()
            if k not in seen:
                seen.add(k)
                out.append(n)
        return out

    k = cfg["max_items_per_stock"]
    stock = {s: [dict(n, id=f"N-{s}-{i}") for i, n in enumerate(dedupe(stock[s])[:k], 1)] for s in universe}
    macro_re = re.compile("|".join(r"(?<![A-Za-z])" + re.escape(w) + r"(?![A-Za-z])" for w in MACRO_WORDS), re.I)
    allm = dedupe(macro_pool)
    macro = [dict(n, id=f"MAC-{i}") for i, n in
             enumerate([n for n in allm if macro_re.search(n["title"])][: cfg["max_macro_items"]], 1)]
    flows = [dict(n, id=f"FL-{i}") for i, n in
             enumerate([n for n in allm if FLOW_RE.search(n["title"]) and PK_CONTEXT.search(n["title"])]
                       [: cfg.get("max_flow_items", 6)], 1)]
    return stock, macro, flows, errors


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

    window = sources.next_trading_days(date.fromisoformat(as_of), cfg["horizon"]["trading_days"])
    log("Fetching news ...")
    names = {m["symbol"]: m["name"] for m in members}
    stock_news, macro, flows, news_err = collect_news(as_of, window[0], universe, names, log=log)
    errors += news_err
    log(f"  news: {sum(1 for s in universe if stock_news[s])}/{len(universe)} companies with news, "
        f"{len(macro)} macro items, {len(flows)} flow mentions")

    warnings = []
    today = date.today()
    if (today - date.fromisoformat(as_of)).days > 4:
        warnings.append("Past date: KSE-100 members and free float are TODAY's, not as of this date "
                        "(PSX does not publish history). Results for past dates are approximate.")
    if window[0] == today.isoformat():
        warnings.append("Today's session is part of the 5-day window and may already be trading.")
    for w in warnings:
        log("WARNING " + w)

    adjusted, adj_events = {}, {}
    for s, rows in history.items():
        adjusted[s], ev = sources.adjust_history(rows)
        if s in universe and ev:
            adj_events[s] = ev
    breadth = breadth_last_days(history, 5)

    keep = ("date", "open", "high", "low", "close", "volume", "ldcp", "ex_marker")
    snap = {
        "as_of": as_of,
        "window": window,
        "universe": universe,
        "members": [{k2: m[k2] for k2 in ("symbol", "name", "free_float_shares", "free_float_mcap",
                                          "index_weight_pct", "close")} for m in members],
        "prices": {s: [{k2: r[k2] for k2 in keep} for r in adjusted[s]] for s in universe},
        "price_adjustments": adj_events,      # dividend/bonus/rights factors from PSX's own LDCP
        "sector_code": {s: history[s][-1]["sector_code"] for s in universe},
        "companies": companies,
        "market_proxy": market_proxy(adjusted, members),
        "breadth_5d": breadth,
        "stock_news": stock_news,
        "macro_news": macro,
        "flow_mentions": flows,       # headlines about foreign/local investor flows
        "fipi_lipi": sources.manual_fipi_lipi(),
        "social": None,          # filled by the optional social-collector agent
        "source_errors": sorted(errors),
        "warnings": warnings,
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
