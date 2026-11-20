"""Parsers against saved PSX pages (offline)."""
from pathlib import Path

from psx7 import sources
from psx7.snapshot import match_patterns

FX = Path(__file__).parent / "fixtures"


def test_eod_parser_skips_futures_and_strips_ex_marker():
    rows = sources.parse_eod_text((FX / "eod_sample.lis").read_text(encoding="latin-1"))
    syms = {r["symbol"] for r in rows}
    assert "OGDC" in syms and not any("-" in s for s in syms)
    ogdc = next(r for r in rows if r["symbol"] == "OGDC")
    assert ogdc["ex_marker"] == "XD" and not ogdc["name"].endswith("XD")
    assert ogdc["date"] == "2026-11-19" and ogdc["close"] > 0


def test_kse100_has_100_members_with_free_float():
    m = sources.parse_kse100((FX / "kse100.html").read_text(encoding="utf-8"))
    assert len(m) == 100
    assert all(x["free_float_shares"] for x in m)
    assert all(not x["symbol"].endswith("XD") for x in m)


def test_company_page_parts():
    c = sources.parse_company((FX / "company_OGDC.html").read_text(encoding="utf-8"))
    assert c["sector"]
    assert c["stats"]["pe_ratio"] > 0
    assert c["financials"]["annual"]["periods"][0].isdigit()
    assert c["financials"]["quarterly"]["periods"][0].startswith("Q")
    assert {a["kind"] for a in c["announcements"]} <= {"financial_results", "board_meetings", "others"}


def test_rss_and_alias_matching():
    items = sources.parse_rss((FX / "rss_sample.xml").read_text(encoding="utf-8"), "test")
    assert len(items) == 3  # item without a date is dropped
    ogdc = match_patterns("OGDC", "Oil & Gas Development Company Limited")
    luck = match_patterns("LUCK", "Lucky Cement Limited")
    assert any(p.search(items[0]["title"]) for p in ogdc)
    assert not any(p.search("Lucky day for cricket fans") for p in luck)


def test_trading_days_skip_weekends_and_holidays():
    from datetime import date
    days = sources.next_trading_days(date(2026, 12, 18), 5)   # Fri; 25 Dec is a holiday
    assert days == ["2026-12-21", "2026-12-22", "2026-12-23", "2026-12-24", "2026-12-28"]
