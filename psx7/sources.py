"""Free public data sources. Every function returns plain data and never guesses.

Working sources (checked 2026-11-20):
  * PSX daily market summary files  https://dps.psx.com.pk/download/mkt_summary/YYYY-MM-DD.Z
  * KSE-100 constituents + free float https://dps.psx.com.pk/indices/KSE100
  * Company pages                     https://dps.psx.com.pk/company/<SYMBOL>
  * News RSS: Business Recorder, Dawn (see config/settings.yaml)
Blocked for scripts (bot protection, we do NOT bypass): NCCPL FIPI/LIPI, Reddit,
PSX JSON endpoints (/timeseries, /company/payouts). FIPI/LIPI can be supplied by hand.
"""
from __future__ import annotations

import csv
import html
import time
import io
import re
import zipfile
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

from .util import CACHE_DIR, INPUTS_DIR, Http, holidays, r2, settings

PSX = "https://dps.psx.com.pk"
EOD_DIR = CACHE_DIR / "eod"
EX_SUFFIXES = ("XDXB", "XDXR", "XBXR", "XD", "XB", "XR")


# ----------------------------------------------------------------- calendar
def is_weekday(d: date) -> bool:
    return d.weekday() < 5


def next_trading_days(after: date, n: int) -> list[str]:
    """The n PSX trading days after `after` (weekends + config holidays skipped)."""
    out, d, hol = [], after, holidays()
    while len(out) < n:
        d += timedelta(days=1)
        if is_weekday(d) and d.isoformat() not in hol:
            out.append(d.isoformat())
    return out


# ----------------------------------------------------------------- daily EOD files
def parse_eod_text(text: str) -> list[dict]:
    rows = []
    for line in text.splitlines():
        p = line.split("|")
        if len(p) < 10 or "-" in p[1]:          # skip futures/derivatives (OGDC-CDEC etc.)
            continue
        try:
            name = p[3].strip()
            ex = next((s for s in EX_SUFFIXES if name.endswith(s)), "")
            rows.append({
                "date": datetime.strptime(p[0], "%d%b%Y").date().isoformat(),
                "symbol": p[1].strip(), "sector_code": p[2].strip(),
                "name": name[: len(name) - len(ex)].strip() if ex else name,
                "ex_marker": ex,
                "open": float(p[4] or 0), "high": float(p[5] or 0), "low": float(p[6] or 0),
                "close": float(p[7] or 0), "volume": float(p[8] or 0), "ldcp": float(p[9] or 0),
            })
        except ValueError:
            continue
    return rows


def eod_file(d: date, http: Http, today: date) -> str | None:
    """Text of the PSX daily file for date d, or None if the market was closed.

    Files are cached forever (past days never change). A missing file is only
    remembered as 'closed' for dates at least 3 days old, so a late upload is not
    mistaken for a holiday.
    """
    EOD_DIR.mkdir(parents=True, exist_ok=True)
    f, miss = EOD_DIR / f"{d.isoformat()}.lis", EOD_DIR / f"{d.isoformat()}.closed"
    if f.exists():
        return f.read_text(encoding="latin-1")
    if miss.exists():
        return None
    r = http.get(f"{PSX}/download/mkt_summary/{d.isoformat()}.Z")
    if r.status_code == 200 and r.content[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(r.content))
        text = z.read(z.namelist()[0]).decode("latin-1")
        f.write_text(text, encoding="latin-1")
        return text
    if r.status_code == 404 and (today - d).days >= 3:
        miss.write_text("closed\n")
    return None


def load_history(as_of: date, n_days: int, log=print) -> tuple[str, dict[str, list[dict]]]:
    """Walk back from as_of until n_days trading files are found.

    Returns (actual as-of trading date, {symbol: [rows oldest->newest]}).
    """
    http, today = Http(), date.today()
    d, found, by_sym = as_of, [], {}
    misses_in_a_row = 0
    while len(found) < n_days and misses_in_a_row < 15:
        if is_weekday(d):
            text = eod_file(d, http, today)
            if text:
                found.append(d.isoformat())
                misses_in_a_row = 0
                for row in parse_eod_text(text):
                    by_sym.setdefault(row["symbol"], []).append(row)
                if len(found) % 25 == 0:
                    log(f"  price files: {len(found)}/{n_days}")
            else:
                misses_in_a_row += 1
        d -= timedelta(days=1)
    if not found:
        raise RuntimeError("No PSX daily files found. Is dps.psx.com.pk reachable?")
    for rows in by_sym.values():
        rows.sort(key=lambda r: r["date"])
    return found[0], by_sym


# ----------------------------------------------------------------- KSE-100 constituents
def kse100_constituents() -> list[dict]:
    r = Http().get(f"{PSX}/indices/KSE100")
    r.raise_for_status()
    return parse_kse100(r.text)


def parse_kse100(page: str) -> list[dict]:
    soup = BeautifulSoup(page, "lxml")
    out = []
    for tr in soup.select("tbody.tbl__body tr"):
        td = tr.find_all("td")
        if len(td) < 11:
            continue
        def num(cell):
            v = cell.get("data-order") or cell.get_text(strip=True).replace(",", "").rstrip("%")
            try:
                return float(v)
            except ValueError:
                return None
        sym = (td[0].get("data-order") or td[0].get_text(strip=True)).strip()
        a = td[0].find("a")
        if a and a.get("href", "").startswith("/company/"):
            sym = a["href"].split("/company/")[1].strip()
        out.append({
            "symbol": sym, "name": td[1].get_text(strip=True),
            "index_weight_pct": num(td[6]), "free_float_shares": num(td[9]),
            "market_cap": num(td[10]),
        })
    return out


# ----------------------------------------------------------------- company page
def company_page(symbol: str) -> dict:
    r = Http().get(f"{PSX}/company/{symbol}")
    if r.status_code != 200:
        return {"error": f"HTTP {r.status_code}"}
    return parse_company(r.text)


def _num(s: str) -> float | None:
    s = s.strip().replace(",", "").replace("%", "")
    neg = s.startswith("(") and s.endswith(")")
    s = s.strip("()")
    try:
        return -float(s) if neg else float(s)
    except ValueError:
        return None


def _table(t) -> dict:
    rows = [[c.get_text(" ", strip=True) for c in r.find_all(["th", "td"])] for r in t.find_all("tr")]
    if not rows:
        return {}
    head = rows[0][1:]
    return {"periods": head, "rows": {r[0]: [_num(x) for x in r[1:]] for r in rows[1:] if r and r[0]}}


def parse_company(page: str) -> dict:
    soup = BeautifulSoup(page, "lxml")
    out: dict = {"stats": {}, "announcements": [], "financials": {}, "ratios": {}}
    sec = soup.select_one(".quote__sector")
    out["sector"] = sec.get_text(" ", strip=True) if sec else None
    # first stats block = regular market (later blocks are futures)
    for item in soup.select(".stats_item"):
        txt = item.get_text(" ", strip=True)
        if txt.startswith("Open") and "open" in out["stats"]:
            break
        m = re.match(r"(P/E Ratio \(TTM\)|1-Year Change|YTD Change|52-WEEK RANGE|LDCP|VAR|HAIRCUT)\W*(.*)", txt)
        if m:
            key, val = m.group(1), m.group(2)
            if key == "52-WEEK RANGE":
                nums = re.findall(r"[\d,]+\.\d+|[\d,]+", val)
                if len(nums) >= 2:
                    out["stats"]["low_52w"], out["stats"]["high_52w"] = _num(nums[0]), _num(nums[1])
            else:
                out["stats"][key.split(" (")[0].lower().replace(" ", "_").replace("/", "")] = _num(
                    re.sub(r"[^\d.,()\-%]", "", val))
        elif txt.startswith("Open"):
            out["stats"]["open"] = True
    out["stats"].pop("open", None)
    eq = soup.find(id="equity")
    if eq:
        t = eq.get_text(" | ", strip=True)
        m = re.search(r"Shares \| ([\d,]+)", t)
        out["shares"] = _num(m.group(1)) if m else None
        m = re.search(r"Free Float \| ([\d.]+)%", t)
        out["free_float_pct"] = _num(m.group(1)) if m else None
    ann = soup.find(id="announcements")
    tabs = ann.find_all("table") if ann else []
    kinds = ["financial_results", "board_meetings", "others"]
    for kind, tab in zip(kinds, tabs):
        for tr in tab.find_all("tr")[1:]:
            td = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
            if len(td) >= 2:
                try:
                    d = datetime.strptime(td[0], "%b %d, %Y").date().isoformat()
                except ValueError:
                    continue
                out["announcements"].append({"date": d, "kind": kind, "title": td[1][:160]})
    fsec = soup.find(id="financials")
    fin = fsec.find_all("table") if fsec else []
    for label, t in zip(["annual", "quarterly"], fin):
        out["financials"][label] = _table(t)
    rt = soup.find(id="ratios")
    if rt and rt.find("table"):
        out["ratios"] = _table(rt.find("table"))
    out["announcements"].sort(key=lambda a: (a["date"], a["kind"], a["title"]), reverse=True)
    return out


# ----------------------------------------------------------------- news (RSS)
def _clean(s: str | None, n: int) -> str:
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()[:n]


def parse_rss(xml_text: str, source: str) -> list[dict]:
    items = []
    try:
        root = ET.fromstring(xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text)
    except ET.ParseError:
        return items
    for it in root.iter("item"):
        title = _clean(it.findtext("title"), 200)
        pub = it.findtext("pubDate")
        try:
            dt = parsedate_to_datetime(pub).astimezone(timezone.utc) if pub else None
        except (TypeError, ValueError):
            dt = None
        if not title or dt is None:
            continue
        items.append({"source": source, "title": title, "url": (it.findtext("link") or "").strip(),
                      "published_utc": dt.strftime("%Y-%m-%dT%H:%MZ"),
                      "summary": _clean(it.findtext("description"), 300)})
    return items


def fetch_news(log=print) -> tuple[list[dict], list[str]]:
    http, items, errors = Http(delay=0.3), [], []
    for feed in settings()["news"]["feeds"]:
        try:
            r = http.get(feed["url"])
            if r.status_code == 200:
                got = parse_rss(r.text, feed["name"])
                items += got
                log(f"  {feed['name']}: {len(got)} items")
            else:
                errors.append(f"{feed['name']}: HTTP {r.status_code}")
        except Exception as e:  # noqa: BLE001 - record and continue
            errors.append(f"{feed['name']}: {type(e).__name__}")
    # de-duplicate by title, stable order
    seen, uniq = set(), []
    for it in sorted(items, key=lambda x: (x["published_utc"], x["title"]), reverse=True):
        k = it["title"].lower()
        if k not in seen:
            seen.add(k)
            uniq.append(it)
    return uniq, errors


# ----------------------------------------------------------------- Google News search (RSS)
GNEWS = "https://news.google.com/rss/search"


def google_news(query: str, http: Http) -> tuple[list[dict], str | None]:
    """Free Google News RSS search. Returns (items, error). Title publisher suffix removed."""
    r = None
    for wait in (0, 15, 40):            # back off politely if rate-limited (HTTP 429)
        if wait:
            time.sleep(wait)
        try:
            r = http.get(GNEWS, params={"q": query, "hl": "en-PK", "gl": "PK", "ceid": "PK:en"})
        except Exception as e:  # noqa: BLE001
            return [], f"google news '{query[:40]}': {type(e).__name__}"
        if r.status_code != 429:
            break
    if r.status_code != 200:
        return [], f"google news '{query[:40]}': HTTP {r.status_code}"
    try:
        root = ET.fromstring(r.content)
    except ET.ParseError:
        return [], f"google news '{query[:40]}': bad XML"
    out = []
    for it in root.iter("item"):
        src_el = it.find("source")
        src = (src_el.text or "").strip() if src_el is not None else "Google News"
        title = _clean(it.findtext("title"), 220)
        if src and title.endswith(f" - {src}"):
            title = title[: -len(src) - 3].strip()
        pub = it.findtext("pubDate")
        try:
            dt = parsedate_to_datetime(pub).astimezone(timezone.utc) if pub else None
        except (TypeError, ValueError):
            dt = None
        if title and dt:
            out.append({"source": src, "title": title[:200], "url": (it.findtext("link") or "").strip(),
                        "published_utc": dt.strftime("%Y-%m-%dT%H:%MZ"), "summary": ""})
    return out, None


# ----------------------------------------------------------------- corporate-action adjustment
def adjust_history(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    """Back-adjust OHLC for dividends, bonus and rights.

    On an ex-date PSX publishes LDCP = previous close already adjusted for the
    entitlement (e.g. MTL 302.90 -> 291.90 on 2026-10-19). So the factor is
    ldcp_t / close_(t-1), read from PSX's own data. Earlier prices are multiplied
    by the product of later factors. Volumes are left as traded.
    Returns (adjusted rows, list of events).
    """
    factors, events = [1.0] * len(rows), []
    for i in range(1, len(rows)):
        prev, cur = rows[i - 1]["close"], rows[i]["ldcp"]
        if prev and cur:
            f = cur / prev
            if abs(f - 1) > 0.002 and 0.2 <= f <= 1.5:
                factors[i] = f
                events.append({"date": rows[i]["date"], "factor": r2(f, 4), "marker": rows[i].get("ex_marker", "")})
    out, cum = [None] * len(rows), 1.0
    for i in range(len(rows) - 1, -1, -1):
        r = dict(rows[i])
        if cum != 1.0:
            for k in ("open", "high", "low", "close", "ldcp"):
                r[k] = r2(r[k] * cum, 4)
        out[i] = r
        cum *= factors[i]
    return out, events


# ----------------------------------------------------------------- manual inputs
def manual_fipi_lipi() -> list[dict] | None:
    """Optional CSV you download yourself from NCCPL (columns: date,category,net_usd_m)."""
    path = INPUTS_DIR / "fipi_lipi.csv"
    if not path.exists():
        return None
    with path.open(encoding="utf-8") as f:
        rows = [{k.strip().lower(): (v or "").strip() for k, v in row.items()} for row in csv.DictReader(f)]
    out = []
    for r in rows:
        try:
            out.append({"date": r["date"], "category": r["category"], "net_usd_m": r2(float(r["net_usd_m"]))})
        except (KeyError, ValueError):
            continue
    return sorted(out, key=lambda x: (x["date"], x["category"]))
