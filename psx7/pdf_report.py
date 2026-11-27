"""Large-font PDF of a finished run (zero tokens). Built only from files already in runs/<as-of>/.

Pages: cover with key numbers, top 5 explained, all 30 ranked, how the strategy worked, glossary.
"""
from __future__ import annotations

import html
import re
from collections import Counter
from pathlib import Path

from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

from .util import read_json

rl_config.invariant = 1            # same run files -> byte-identical PDF (no timestamps)

INK, MUTED, LINE = colors.HexColor("#1b1f24"), colors.HexColor("#555b63"), colors.HexColor("#c9ced4")
ACCENT, SOFT = colors.HexColor("#0b4f8a"), colors.HexColor("#eef3f8")
CALL_BG = {"up": colors.HexColor("#d9f2df"), "down": colors.HexColor("#f8d9d9"), "flat": colors.HexColor("#ececec")}
CALL_FG = {"up": colors.HexColor("#11652b"), "down": colors.HexColor("#9b1c1c"), "flat": colors.HexColor("#444444")}

_FONT_CANDIDATES = [  # (regular, bold)
    ("C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/arialbd.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("/Library/Fonts/Arial.ttf", "/Library/Fonts/Arial Bold.ttf"),
]
_ASCII = {"−": "-", "→": "->", "⇅": "<->", "≥": ">=", "≤": "<=", "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-"}


def _fonts() -> tuple[str, str, bool]:
    for reg, bold in _FONT_CANDIDATES:
        if Path(reg).exists() and Path(bold).exists():
            if "Body" not in pdfmetrics.getRegisteredFontNames():
                pdfmetrics.registerFont(TTFont("Body", reg))
                pdfmetrics.registerFont(TTFont("Body-Bold", bold))
                pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body", boldItalic="Body-Bold")
            return "Body", "Body-Bold", True
    return "Helvetica", "Helvetica-Bold", False


FONT, BOLD, UNICODE = _fonts()


def _t(s) -> str:
    s = "" if s is None else str(s)
    if not UNICODE:
        for k, v in _ASCII.items():
            s = s.replace(k, v)
    return s


def _md(s: str) -> str:
    """Escape, then **bold** and `code` -> reportlab markup."""
    s = html.escape(_t(s), quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`([^`]+)`", r"<b>\1</b>", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", s)
    return re.sub(r"(?<![\w*])\*([^*]+)\*(?!\w)", r"\1", s)


def _styles() -> dict:
    base = dict(fontName=FONT, textColor=INK)
    return {
        "title": ParagraphStyle("title", fontName=BOLD, fontSize=34, leading=42, textColor=ACCENT, alignment=TA_CENTER),
        "sub": ParagraphStyle("sub", fontName=FONT, fontSize=18, leading=26, textColor=MUTED, alignment=TA_CENTER),
        "h1": ParagraphStyle("h1", fontName=BOLD, fontSize=24, leading=30, textColor=ACCENT, spaceBefore=4, spaceAfter=10),
        "h2": ParagraphStyle("h2", fontName=BOLD, fontSize=18, leading=24, textColor=INK, spaceBefore=10, spaceAfter=4),
        "body": ParagraphStyle("body", fontSize=14, leading=20, spaceAfter=6, **base),
        "bullet": ParagraphStyle("bullet", fontSize=14, leading=20, leftIndent=18, bulletIndent=4, spaceAfter=4, **base),
        "cell": ParagraphStyle("cell", fontSize=13, leading=16, **base),
        "cellb": ParagraphStyle("cellb", fontName=BOLD, fontSize=13, leading=16, textColor=INK),
        "head": ParagraphStyle("head", fontName=BOLD, fontSize=13, leading=16, textColor=colors.white),
        "big": ParagraphStyle("big", fontName=BOLD, fontSize=30, leading=34, textColor=ACCENT, alignment=TA_CENTER),
        "label": ParagraphStyle("label", fontName=FONT, fontSize=13, leading=16, textColor=MUTED, alignment=TA_CENTER),
        "warn": ParagraphStyle("warn", fontName=BOLD, fontSize=14, leading=20, textColor=colors.HexColor("#7a4b00")),
    }


def _pct(x) -> str:
    return "n/a" if x is None else f"{x:+.2f}%"


def _flag(r) -> str:
    out = [r["flag"].replace("_", " ")] if r.get("flag") not in (None, "none") else []
    return " ".join(out + (["illiquid"] if r.get("illiquid") else []))


def _grid(data, widths, call_col=None, rows=None, zebra=True) -> Table:
    t = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    st = [("BACKGROUND", (0, 0), (-1, 0), ACCENT), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
          ("LINEBELOW", (0, 0), (-1, -1), 0.5, LINE), ("TOPPADDING", (0, 0), (-1, -1), 5),
          ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("LEFTPADDING", (0, 0), (-1, -1), 6)]
    for i in range(1, len(data)):
        if zebra and i % 2 == 0:
            st.append(("BACKGROUND", (0, i), (-1, i), SOFT))
        if call_col is not None and rows:
            d = rows[i - 1]["final_direction"]
            st.append(("BACKGROUND", (call_col, i), (call_col, i), CALL_BG.get(d, colors.white)))
    t.setStyle(TableStyle(st))
    return t


def _call(r, S) -> Paragraph:
    d = r["final_direction"]
    return Paragraph(f'<font color="#{CALL_FG.get(d, INK).hexval()[2:]}"><b>{d.upper()}</b></font>', S["cell"])


def _how_sections(text: str) -> list[tuple[str, list[str]]]:
    """Stage sections of how_it_worked.md (the agent narrative is skipped: the PDF covers it from data)."""
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("## "):
            title = line[3:].strip()
            cur = None if title.lower().startswith("summary") else (title, [])
            if cur:
                out.append(cur)
        elif cur is not None and line.strip() and not line.startswith(("#", ">")):
            cur[1].append(line.rstrip())
    return out


GLOSSARY = [
    ("Call", "Expected direction over the 5 trading days: UP, FLAT or DOWN. Decided by the Portfolio Manager within Python's rules."),
    ("Conviction", "How strongly the evidence points one way: low, medium or high. It scales the expected move."),
    ("Risk", "Median of the Aggressive, Neutral and Conservative risk analysts: low, medium or high. Higher risk lowers the score."),
    ("Expected 5-day move", "Python formula: direction x conviction x the stock's normal daily range (ATR, capped) over 5 days. Not a promise."),
    ("Score", "Ranking number: expected move x (1 - risk penalty) - liquidity penalty. Higher is better. Agents cannot change the order."),
    ("Quant", "Market score plus fundamentals score from pure Python indicators (trend, RSI, MACD, P/E, EPS growth, margins)."),
    ("Target / Stop", "Price levels from volatility (ATR): where the expected move would land, and where the idea is wrong."),
    ("Caution", "The Portfolio Manager sees a specific risk (for example overbought RSI, weak quant score)."),
    ("Watch closely", "Mixed evidence; the call is flat but worth watching."),
    ("Illiquid", "Average traded value below PKR 20 million a day; the score gets a penalty."),
    ("RSI", "Relative Strength Index. Above 70 is usually called overbought, below 30 oversold."),
]


def build_pdf(run: Path) -> Path:
    run = Path(run)
    rk, meta = read_json(run / "ranking.json"), read_json(run / "run_meta.json")
    how_path = run / "how_it_worked.md"
    how = how_path.read_text(encoding="utf-8") if how_path.exists() else ""
    rows, S = rk["rows"], _styles()
    top = [r for r in rows if r.get("top")] or rows[:5]
    win = rk["window"]
    out = run / f"PSX_report_{rk['as_of']}.pdf"

    def deco(c, doc):
        c.saveState()
        c.setFont(FONT, 10)
        c.setFillColor(MUTED)
        w, _ = doc.pagesize
        c.drawString(15 * mm, 8 * mm, _t(f"PSX top-30 five-day ranking, as of {rk['as_of']}. Not financial advice."))
        c.drawRightString(w - 15 * mm, 8 * mm, f"Page {doc.page}")
        c.restoreState()

    doc = SimpleDocTemplate(str(out), pagesize=landscape(A4), leftMargin=15 * mm, rightMargin=15 * mm,
                            topMargin=14 * mm, bottomMargin=16 * mm, title=f"PSX ranking {rk['as_of']}",
                            author="PSX-ALL-SOURCES-07-DAYS", subject="Five-day ranking of top 30 KSE-100 stocks")
    W = doc.width
    st: list = []

    # ------------------------------------------------------------ cover
    calls = Counter(r["final_direction"] for r in rows)
    st += [Spacer(1, 18 * mm), Paragraph("PSX Top-30 Five-Day Ranking", S["title"]), Spacer(1, 4 * mm),
           Paragraph(_t(f"Prices as of {rk['as_of']} close  ·  Forecast window {win[0]} to {win[-1]} (5 trading days)"), S["sub"]),
           Spacer(1, 12 * mm)]
    tiles = [(str(calls.get("up", 0)), "UP calls"), (str(calls.get("flat", 0)), "FLAT calls"),
             (str(calls.get("down", 0)), "DOWN calls"), (top[0]["symbol"] if top else "-", "Rank 1"),
             (str(meta.get("agent_calls", "-")), "Agent calls"), (str(meta.get("fallbacks", "-")), "Fallbacks")]
    tt = Table([[Paragraph(v, S["big"]) for v, _ in tiles], [Paragraph(k, S["label"]) for _, k in tiles]],
               colWidths=[W / len(tiles)] * len(tiles))
    tt.setStyle(TableStyle([("BOX", (0, 0), (-1, -1), 0.8, LINE), ("INNERGRID", (0, 0), (-1, -1), 0.5, LINE),
                            ("BACKGROUND", (0, 0), (-1, -1), SOFT), ("TOPPADDING", (0, 0), (-1, -1), 10),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
    st += [tt, Spacer(1, 12 * mm)]
    disc = Table([[Paragraph("Not financial advice. This is an automated research experiment on free public data. "
                             "It can be wrong, data may be incomplete, and it says nothing about your own situation.", S["warn"])]],
                 colWidths=[W])
    disc.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#fff4dc")),
                              ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#e0b35a")),
                              ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                              ("LEFTPADDING", (0, 0), (-1, -1), 12)]))
    st += [disc, Spacer(1, 8 * mm),
           Paragraph(_t(f"Snapshot fingerprint {rk['fingerprint'][:12]}  ·  prompt version {meta.get('prompt_version', '-')}"), S["label"])]
    if meta.get("missing_sources"):
        st += [Spacer(1, 3 * mm), Paragraph(_t("Missing data: " + "; ".join(meta["missing_sources"])), S["label"])]
    st.append(PageBreak())

    # ------------------------------------------------------------ top 5
    st.append(Paragraph(f"Top {len(top)} at a glance", S["h1"]))
    head = ["#", "Stock", "Call", "Conviction", "Risk", "Exp. 5-day move", "Entry", "Target", "Stop", "Flag"]
    data = [[Paragraph(h, S["head"]) for h in head]]
    for r in top:
        lv = r["levels"]
        data.append([Paragraph(str(r["rank"]), S["cellb"]), Paragraph(f"<b>{r['symbol']}</b>", S["cell"]), _call(r, S),
                     Paragraph(r["final_conviction"], S["cell"]), Paragraph(r["risk_rating"], S["cell"]),
                     Paragraph(f"<b>{_pct(r['expected_move_pct'])}</b>", S["cell"]),
                     *[Paragraph(str(lv.get(k, "-")), S["cell"]) for k in ("entry_ref", "target", "stop")],
                     Paragraph(_flag(r) or "-", S["cell"])])
    st.append(_grid(data, [x * W for x in (.05, .1, .09, .12, .09, .14, .1, .1, .09, .12)], call_col=2, rows=top))
    st.append(PageBreak())

    st.append(Paragraph(f"Why the top {len(top)}", S["h1"]))
    for r in top:
        block = [Paragraph(_t(f"{r['rank']}. {r['symbol']}: {r['name']}"), S["h2"]),
                 Paragraph(_t(f"<b>Call {r['final_direction'].upper()}</b>, conviction {r['final_conviction']}, "
                              f"risk {r['risk_rating']}, setup {r['setup']}. Expected move <b>{_pct(r['expected_move_pct'])}</b> "
                              f"(score {r['hybrid_score']:+.3f}, quant {r['quant_score']:+.0f})."), S["body"]),
                 Paragraph("<b>Deciding points:</b>", S["body"])]
        block += [Paragraph(_md(p), S["bullet"], bulletText="•") for p in r.get("deciding_points") or ["none"]]
        block.append(Paragraph(f"<b>Portfolio Manager:</b> {_md(r.get('pm_reason') or '-')}", S["body"]))
        if _flag(r):
            block.append(Paragraph(_t(f"Flag: {_flag(r)}"), S["warn"]))
        st += [KeepTogether(block), Spacer(1, 3 * mm)]
    st.append(PageBreak())

    # ------------------------------------------------------------ all 30
    st.append(Paragraph(f"All {len(rows)} stocks ranked", S["h1"]))
    head = ["#", "Stock", "Sector", "Call", "Conviction", "Risk", "Exp. move", "Score", "Quant", "Flag"]
    data = [[Paragraph(h, S["head"]) for h in head]]
    for r in rows:
        sym = f"<b>{r['symbol']}</b>" if r.get("top") else r["symbol"]
        data.append([Paragraph(str(r["rank"]), S["cell"]), Paragraph(sym, S["cell"]),
                     Paragraph(_md(r.get("sector", "").title()), S["cell"]), _call(r, S),
                     Paragraph(r["final_conviction"], S["cell"]), Paragraph(r["risk_rating"], S["cell"]),
                     Paragraph(_pct(r["expected_move_pct"]), S["cell"]), Paragraph(f"{r['hybrid_score']:+.3f}", S["cell"]),
                     Paragraph(f"{r['quant_score']:+.0f}", S["cell"]), Paragraph(_flag(r) or "-", S["cell"])])
    st.append(_grid(data, [x * W for x in (.04, .08, .21, .09, .12, .08, .1, .08, .07, .13)], call_col=3, rows=rows))
    st.append(PageBreak())

    # ------------------------------------------------------------ how it worked
    st.append(Paragraph("How the strategy worked this run", S["h1"]))
    for title, lines in _how_sections(how):
        st.append(Paragraph(_md(title), S["h2"]))
        for ln in lines:
            s = ln.strip()
            if s.startswith("- "):
                indent = len(ln) - len(ln.lstrip())
                sty = ParagraphStyle("b2", parent=S["bullet"], leftIndent=18 + indent * 6, bulletIndent=4 + indent * 6)
                st.append(Paragraph(_md(s[2:]), sty, bulletText="•"))
            else:
                st.append(Paragraph(_md(s), S["body"]))
    st.append(PageBreak())

    # ------------------------------------------------------------ glossary
    st.append(Paragraph("How to read this report", S["h1"]))
    data = [[Paragraph("Term", S["head"]), Paragraph("Meaning", S["head"])]]
    data += [[Paragraph(f"<b>{k}</b>", S["cell"]), Paragraph(_t(v), S["cell"])] for k, v in GLOSSARY]
    st.append(_grid(data, [W * .2, W * .8]))

    doc.build(st, onFirstPage=deco, onLaterPages=deco)
    return out
