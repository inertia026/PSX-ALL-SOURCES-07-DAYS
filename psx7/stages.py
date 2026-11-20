"""Agent stages, in the exact order of the reference flow.

    Analysts (Market*, Fundamentals*, News, Sentiment)  -> merge (evidence packs)
    -> Bull vs Bear (round 1, round 2) -> Research Manager -> Trader
    -> Aggressive / Neutral / Conservative (round 1, round 2) -> Portfolio Manager
    (* = pure Python, see analysts.py)

Each stage turns into small job files. A Claude Code subagent reads one job file
and writes one output file. Python validates outputs, replays cached answers,
and writes a neutral fallback if an agent fails twice.
"""
from __future__ import annotations

from pathlib import Path
from statistics import median

from . import debate as dbt
from . import scoring
from .analysts import compact_pack
from .util import CACHE_DIR, ROOT, read_json, settings, sha256, write_json

AGENT_DIR = ROOT / ".claude" / "agents"
LEVELS = ["low", "medium", "high"]
DIRS = ["up", "flat", "down"]
TONES = ["positive", "negative", "neutral"]
VIEWS = ["positive", "negative", "neutral", "mixed"]
RISK_ROLES = ["aggressive", "neutral", "conservative"]
SETUPS = ["breakout", "pullback", "momentum", "catalyst", "mean_reversion", "avoid"]
FLAGS = ["none", "caution", "watch_closely"]

STAGE_ORDER = ["social", "news", "sentiment", "debate_r1", "debate_r2", "research_manager",
               "trader", "risk_r1", "risk_r2", "portfolio_manager", "narrative"]


# ======================================================================== helpers
def words(text, n: int) -> str:
    w = str(text or "").split()
    return " ".join(w[:n]) + (" ..." if len(w) > n else "")


def enum(v, allowed: list[str], field: str, errs: list[str]):
    v = str(v or "").strip().lower()
    if v not in allowed:
        errs.append(f"{field}={v!r} not in {allowed}")
        return None
    return v


def cites(v, allowed: set[str]) -> list[str]:
    if not isinstance(v, list):
        v = [v] if v else []
    return sorted({str(x).strip() for x in v if str(x).strip() in allowed})


def chunks(items: list, n: int) -> list[list]:
    return [items[i:i + n] for i in range(0, len(items), max(1, n))]


def sector_order(ctx) -> list[str]:
    """Stocks grouped by sector, then A->Z: fixed, repeatable batches."""
    return sorted(ctx.snap["universe"], key=lambda s: (str(ctx.packs[s]["sector"]), s))


def results_by_symbol(out: dict, expected: list[str], errs: list[str]) -> dict:
    res = out.get("results") if isinstance(out, dict) else None
    if not isinstance(res, list):
        errs.append("missing 'results' list")
        return {}
    got = {str(r.get("symbol", "")).upper(): r for r in res if isinstance(r, dict)}
    missing = [s for s in expected if s not in got]
    if missing:
        errs.append(f"missing symbols {missing}")
    return {s: got[s] for s in expected if s in got}


class Ctx:
    """Everything a stage needs: snapshot, packs, and earlier stage results."""

    def __init__(self, run: Path):
        self.run = run
        self.snap = read_json(run / "snapshot" / "snapshot.json")
        self.packs = read_json(run / "analysts.json")
        self.cfg = settings()

    def stage(self, name: str) -> dict:
        p = self.run / "stages" / f"{name}.json"
        return read_json(p) if p.exists() else {}

    def allowed_ids(self, sym: str) -> set[str]:
        p = self.packs[sym]
        ids = {x["id"] for x in p["market"]["signals"] + p["fundamentals"]["signals"] + p["fundamentals"]["catalysts"]}
        ids |= {n["id"] for n in p["news"]}
        ids |= {n["id"] for n in self.snap.get("macro_news", [])}
        ids |= {i["id"] for i in (self.snap.get("social") or {}).get("items", [])}
        ids |= {d["id"] for d in self.stage("news").get("macro", {}).get("drivers", []) if d.get("id")}
        ids.add(f"SENT-{sym}")
        return ids

    def pack_for_agents(self, sym: str) -> dict:
        """Compact pack + results of News and Sentiment (the merge step)."""
        news = self.stage("news").get("stocks", {}).get(sym, {})
        titles = {n["id"]: n["title"] for n in self.packs[sym]["news"]}
        extra = {
            "news_view": news.get("news_view", "none"),
            "news": [{"id": i["id"], "headline": titles.get(i["id"], ""), "tone": i["tone"], "impact": i["impact"]}
                     for i in news.get("items", [])],
            "sentiment": self.stage("sentiment").get(sym),
            "macro": self.stage("news").get("macro"),
        }
        return compact_pack(self.packs[sym], extra)


# ======================================================================== stages
class Stage:
    name = ""
    agent = ""
    rules: list[str] = []
    output_format: dict = {}

    def jobs(self, ctx: Ctx) -> list[dict]:          # [{job_id, agent, symbols, data}]
        raise NotImplementedError

    def validate(self, job: dict, out: dict, ctx: Ctx) -> tuple[dict | None, list[str]]:
        raise NotImplementedError

    def fallback(self, job: dict, ctx: Ctx) -> dict:
        raise NotImplementedError

    def merge(self, outputs: list[tuple[dict, dict]], ctx: Ctx) -> dict:
        merged = {}
        for _job, out in outputs:
            merged.update(out["by_symbol"])
        return merged

    def enabled(self, ctx: Ctx) -> bool:
        return True


# ---------------------------------------------------------------- social collector
class Social(Stage):
    name, agent = "social", "social-collector"
    rules = ["Use WebSearch at most 3 times. Only use posts/articles dated in the 7 days up to as_of.",
             "Report what people say; do not add your own opinion.", "At most 10 items."]
    output_format = {"result": {"market_mood": "bullish|neutral|bearish",
                                "items": [{"symbol": "TICKER or null", "text": "<=25 words", "tone": "positive|negative|neutral", "source": "url"}]}}

    def enabled(self, ctx):
        return bool(ctx.cfg["sentiment"]["social_collector"]) and ctx.snap.get("social") is None

    def jobs(self, ctx):
        return [{"job_id": "social", "agent": self.agent, "symbols": [],
                 "data": {"as_of": ctx.snap["as_of"],
                          "stocks": [{"symbol": s, "name": ctx.packs[s]["name"]} for s in ctx.snap["universe"]]}}]

    def validate(self, job, out, ctx):
        errs, r = [], (out or {}).get("result")
        if not isinstance(r, dict):
            return None, ["missing 'result' object"]
        mood = enum(r.get("market_mood"), ["bullish", "neutral", "bearish"], "market_mood", errs)
        items = []
        uni = set(ctx.snap["universe"])
        for it in (r.get("items") or [])[:10]:
            if not isinstance(it, dict):
                continue
            tone = str(it.get("tone", "")).lower()
            sym = str(it.get("symbol") or "").upper() or None
            items.append({"id": f"S-{len(items) + 1}", "symbol": sym if sym in uni else None,
                          "text": words(it.get("text"), 25), "tone": tone if tone in TONES else "neutral",
                          "source": str(it.get("source", ""))[:200]})
        return (None, errs) if errs else ({"market_mood": mood, "items": items}, [])

    def fallback(self, job, ctx):
        return {"market_mood": "neutral", "items": [], "fallback": True}

    def merge(self, outputs, ctx):
        return outputs[0][1]


# ---------------------------------------------------------------- news analyst
class News(Stage):
    name, agent = "news", "news-analyst"
    rules = ["Judge each headline only for its likely effect on the stock in the next 5 trading days.",
             "Use only the given headlines. 'why' <= 20 words."]
    output_format = {"results": [{"symbol": "TICKER", "news_view": "positive|negative|neutral|mixed",
                                  "items": [{"id": "N-TICKER-1", "tone": "positive|negative|neutral",
                                             "impact": "low|medium|high", "why": "<=20 words"}]}],
                     "macro (macro job only)": {"macro_view": "positive|negative|neutral|mixed",
                                                "drivers": [{"text": "<=25 words", "tone": "positive|negative|neutral",
                                                             "cites": ["MAC-1"]}]}}

    def jobs(self, ctx):
        jobs = []
        macro = ctx.snap.get("macro_news", [])
        if macro:
            jobs.append({"job_id": "macro", "agent": self.agent, "symbols": [],
                         "data": {"task": "macro", "headlines": [{"id": n["id"], "title": n["title"], "summary": n["summary"][:200],
                                                                   "date": n["published_utc"][:10]} for n in macro]}})
        with_news = [s for s in sector_order(ctx) if ctx.packs[s]["news"]]
        for i, batch in enumerate(chunks(with_news, ctx.cfg["batching"]["news"]), 1):
            jobs.append({"job_id": f"batch{i:02d}", "agent": self.agent, "symbols": batch,
                         "data": {"task": "stocks", "stocks": [
                             {"symbol": s, "name": ctx.packs[s]["name"],
                              "headlines": [{"id": n["id"], "title": n["title"], "summary": n["summary"][:200],
                                             "date": n["published_utc"][:10]} for n in ctx.packs[s]["news"]]}
                             for s in batch]}})
        return jobs

    def validate(self, job, out, ctx):
        errs = []
        if job["job_id"] == "macro":
            m = (out or {}).get("macro")
            if not isinstance(m, dict):
                return None, ["missing 'macro' object"]
            view = enum(m.get("macro_view"), VIEWS, "macro_view", errs)
            allowed = {n["id"] for n in ctx.snap["macro_news"]}
            drivers = [{"text": words(d.get("text"), 25), "tone": d.get("tone") if d.get("tone") in TONES else "neutral",
                        "cites": cites(d.get("cites"), allowed)} for d in (m.get("drivers") or [])[:5] if isinstance(d, dict)]
            drivers = [dict(d, id=f"MD-{i}") for i, d in enumerate(drivers, 1)]
            return (None, errs) if errs else ({"macro": {"macro_view": view, "drivers": drivers}}, [])
        rows, by = results_by_symbol(out, job["symbols"], errs), {}
        for s, r in rows.items():
            ids = {n["id"] for n in ctx.packs[s]["news"]}
            items = []
            for it in r.get("items") or []:
                if isinstance(it, dict) and it.get("id") in ids:
                    items.append({"id": it["id"], "tone": it.get("tone") if it.get("tone") in TONES else "neutral",
                                  "impact": it.get("impact") if it.get("impact") in LEVELS else "low",
                                  "why": words(it.get("why"), 20)})
            by[s] = {"news_view": enum(r.get("news_view"), VIEWS, f"{s}.news_view", errs), "items": items}
        return (None, errs) if errs else ({"by_symbol": by}, [])

    def fallback(self, job, ctx):
        if job["job_id"] == "macro":
            return {"macro": {"macro_view": "neutral", "drivers": []}, "fallback": True}
        return {"by_symbol": {s: {"news_view": "neutral", "items": [], "fallback": True} for s in job["symbols"]}}

    def merge(self, outputs, ctx):
        merged = {"macro": {"macro_view": "none", "drivers": []},
                  "stocks": {s: {"news_view": "none", "items": []} for s in ctx.snap["universe"]}}
        for job, out in outputs:
            if job["job_id"] == "macro":
                merged["macro"] = out["macro"]
            else:
                merged["stocks"].update(out["by_symbol"])
        return merged


# ---------------------------------------------------------------- sentiment analyst
class Sentiment(Stage):
    name, agent = "sentiment", "sentiment-analyst"
    rules = ["Judge market mood toward each stock for the next 5 trading days.",
             "Use breadth, flows, social items, news tones and the price/volume facts given. Up to 3 reasons, each <= 20 words, citing ids where possible."]
    output_format = {"results": [{"symbol": "TICKER", "mood": "bullish|neutral|bearish", "strength": "low|medium|high",
                                  "reasons": [{"text": "<=20 words", "cites": ["S-1", "N-TICKER-2"]}]}]}

    def jobs(self, ctx):
        news, social = ctx.stage("news"), ctx.stage("social") or ctx.snap.get("social") or {}
        shared = {"breadth_last_5_days": ctx.snap["breadth_5d"],
                  "foreign_local_flows": ctx.snap.get("fipi_lipi") or "not available (NCCPL blocks scripts; no manual file)",
                  "macro_view": news.get("macro", {}).get("macro_view", "none"),
                  "social_market_mood": social.get("market_mood", "not collected")}
        jobs = []
        for i, batch in enumerate(chunks(sector_order(ctx), ctx.cfg["batching"]["sentiment"]), 1):
            stocks = []
            for s in batch:
                f = ctx.packs[s]["market"]["facts"]
                stocks.append({"symbol": s, "ret5_pct": f["ret5_pct"], "mkt_ret5_pct": f["mkt_ret5_pct"],
                               "vol_ratio_5_20": f["vol_ratio_5_20"],
                               "news_view": news.get("stocks", {}).get(s, {}).get("news_view", "none"),
                               "news_tones": [{"id": x["id"], "tone": x["tone"], "impact": x["impact"]}
                                              for x in news.get("stocks", {}).get(s, {}).get("items", [])],
                               "social": [x for x in social.get("items", []) if x.get("symbol") == s]})
            jobs.append({"job_id": f"batch{i:02d}", "agent": self.agent, "symbols": batch,
                         "data": {"shared": shared, "stocks": stocks}})
        return jobs

    def validate(self, job, out, ctx):
        errs, by = [], {}
        for s, r in results_by_symbol(out, job["symbols"], errs).items():
            allowed = ctx.allowed_ids(s)
            by[s] = {"mood": enum(r.get("mood"), ["bullish", "neutral", "bearish"], f"{s}.mood", errs),
                     "strength": enum(r.get("strength"), LEVELS, f"{s}.strength", errs),
                     "reasons": [{"text": words(x.get("text"), 20), "cites": cites(x.get("cites"), allowed)}
                                 for x in (r.get("reasons") or [])[:3] if isinstance(x, dict)]}
        return (None, errs) if errs else ({"by_symbol": by}, [])

    def fallback(self, job, ctx):
        return {"by_symbol": {s: {"mood": "neutral", "strength": "low", "reasons": [], "fallback": True}
                              for s in job["symbols"]}}


# ---------------------------------------------------------------- Bull vs Bear (structured)
class Debate(Stage):
    """Agents pick evidence IDs (round 1) and rebuttal reasons (round 2). No free text."""

    def __init__(self, rnd: int):
        self.rnd = rnd
        self.name = f"debate_r{rnd}"
        cfg = settings()["debate"]
        if rnd == 1:
            self.rules = [f"For each stock, pick 1-{cfg['max_picks']} items from YOUR menu that best support your side for the NEXT 5 TRADING DAYS.",
                          "Weight each pick strong|moderate|weak. Prefer recent, specific, 5-day-relevant items. Use only ids from your menu.",
                          "If your menu is empty, return an empty picks list."]
            self.output_format = {"results": [{"symbol": "TICKER", "picks": [{"id": "M-TICKER-2", "weight": "strong|moderate|weak"}]}]}
        else:
            self.rules = [f"For each stock, rebut 0-{cfg['max_rebuttals']} of the opponent's picks (target = their id).",
                          "reason: " + "|".join(dbt.REBUTTAL_REASONS) + ". For outweighed_by, set 'by' to an id from YOUR menu; otherwise by = null.",
                          "Only rebut where the reason genuinely applies; zero rebuttals is fine."]
            self.output_format = {"results": [{"symbol": "TICKER", "rebuttals": [{"target": "F-TICKER-1", "reason": "stale", "by": None}]}]}

    def enabled(self, ctx):
        return self.rnd <= ctx.cfg["debate"]["research_rounds"]

    def jobs(self, ctx):
        jobs, r1 = [], ctx.stage("debate_r1")
        for i, batch in enumerate(chunks(sector_order(ctx), ctx.cfg["batching"]["debate"]), 1):
            for side in ("bull", "bear"):
                opp, stocks = ("bear" if side == "bull" else "bull"), []
                for s in batch:
                    m = dbt.menus(ctx, s)
                    d = {"symbol": s, "name": ctx.packs[s]["name"], "your_menu": m[side]}
                    if self.rnd == 2:
                        text = dbt.evidence_text(ctx, s)
                        d["opponent_picks"] = [{"id": p["id"], "weight": p["weight"], "text": text.get(p["id"], "")}
                                               for p in r1.get(s, {}).get(opp, {}).get("picks", [])]
                        d["your_picks"] = r1.get(s, {}).get(side, {}).get("picks", [])
                    stocks.append(d)
                jobs.append({"job_id": f"batch{i:02d}-{side}", "agent": f"{side}-researcher", "symbols": batch,
                             "side": side, "data": {"side": side, "round": self.rnd, "stocks": stocks}})
        return jobs

    def validate(self, job, out, ctx):
        errs, by, cfg = [], {}, ctx.cfg["debate"]
        side = job["side"]
        opp = "bear" if side == "bull" else "bull"
        r1 = ctx.stage("debate_r1")
        for s, r in results_by_symbol(out, job["symbols"], errs).items():
            menu = {x["id"] for x in dbt.menus(ctx, s)[side]}
            if self.rnd == 1:
                picks, seen = [], set()
                for p in (r.get("picks") or []):
                    if isinstance(p, dict) and p.get("id") in menu and p["id"] not in seen \
                            and p.get("weight") in dbt.WEIGHTS and len(picks) < cfg["max_picks"]:
                        seen.add(p["id"])
                        picks.append({"id": p["id"], "weight": p["weight"]})
                if menu and not picks:
                    errs.append(f"{s}: no valid picks from menu")
                by[s] = {side: {"picks": picks}}
            else:
                opp_picks = {p["id"]: p["weight"] for p in r1.get(s, {}).get(opp, {}).get("picks", [])}
                own_w = {p["id"]: p["weight"] for p in r1.get(s, {}).get(side, {}).get("picks", [])}
                rebs, seen = [], set()
                for rb in (r.get("rebuttals") or []):
                    if not isinstance(rb, dict) or rb.get("target") not in opp_picks or rb["target"] in seen:
                        continue
                    reason = rb.get("reason")
                    if reason not in dbt.REBUTTAL_REASONS or len(rebs) >= cfg["max_rebuttals"]:
                        continue
                    by_id = rb.get("by") if reason == "outweighed_by" and rb.get("by") in menu else None
                    eff = bool(by_id) and dbt.WEIGHTS.index(own_w.get(by_id, "moderate")) >= dbt.WEIGHTS.index(opp_picks[rb["target"]])
                    seen.add(rb["target"])
                    rebs.append({"target": rb["target"], "reason": reason, "by": by_id, "effective": eff})
                by[s] = {side: {"rebuttals": rebs}}
        return (None, errs) if errs else ({"by_symbol": by}, [])

    def fallback(self, job, ctx):
        key = "picks" if self.rnd == 1 else "rebuttals"
        return {"by_symbol": {s: {job["side"]: {key: [], "fallback": True}} for s in job["symbols"]}}

    def merge(self, outputs, ctx):
        merged: dict = {}
        for _job, out in outputs:
            for s, v in out["by_symbol"].items():
                merged.setdefault(s, {}).update(v)
        return merged


# ---------------------------------------------------------------- Research Manager
class ResearchManager(Stage):
    name, agent = "research_manager", "research-manager"
    rules = ["Python scored the Bull vs Bear debate and proposes direction + conviction. Review it.",
             "decision 'accept' keeps the proposal. 'override' may move direction and/or conviction by ONE step only, and needs a reason.",
             "Override only for something the score misses (e.g. one point clearly dominates, or evidence is stale). reason <= 25 words.",
             "deciding_ids: up to 3 evidence ids that decide the call."]
    output_format = {"results": [{"symbol": "TICKER", "decision": "accept|override", "direction": "up|flat|down",
                                  "conviction": "low|medium|high", "reason": "<=25 words", "deciding_ids": ["M-TICKER-3"]}]}

    def jobs(self, ctx):
        jobs = []
        for i, batch in enumerate(chunks(sector_order(ctx), ctx.cfg["batching"]["research_manager"]), 1):
            stocks = []
            for s in batch:
                t = dbt.tally(ctx, s)
                stocks.append({"symbol": s, "name": ctx.packs[s]["name"],
                               "bull": t["bull"], "bear": t["bear"], "net_score": t["net"],
                               "quant_score": t["quant_score"], "proposal": t["proposal"]})
            jobs.append({"job_id": f"batch{i:02d}", "agent": self.agent, "symbols": batch, "data": {"stocks": stocks}})
        return jobs

    def _result(self, ctx, s, decision, direction, conviction, reason, ids, notes):
        t = dbt.tally(ctx, s)
        text = dbt.evidence_text(ctx, s)
        winner = {"up": "bull", "down": "bear"}.get(direction, "draw")
        return {"winner": winner, "direction": direction, "conviction": conviction, "decision": decision,
                "reason": reason, "proposal": t["proposal"], "net_score": t["net"], "clamp_notes": notes,
                "deciding_points": [{"text": text.get(i, ""), "cites": [i]} for i in ids]}

    def validate(self, job, out, ctx):
        errs, by = [], {}
        for s, r in results_by_symbol(out, job["symbols"], errs).items():
            prop = dbt.tally(ctx, s)["proposal"]
            decision = enum(r.get("decision"), ["accept", "override"], f"{s}.decision", errs)
            if decision is None:
                continue
            ids = cites(r.get("deciding_ids"), set(dbt.evidence_text(ctx, s)))[:3]
            reason = words(r.get("reason"), 25)
            if decision == "accept":
                by[s] = self._result(ctx, s, "accept", prop["direction"], prop["conviction"], reason, ids, [])
                continue
            d = enum(r.get("direction"), DIRS, f"{s}.direction", errs)
            c = enum(r.get("conviction"), LEVELS, f"{s}.conviction", errs)
            if d and c:
                d, c, notes = dbt.clamp_override(prop, d, c)
                by[s] = self._result(ctx, s, "override", d, c, reason, ids, notes)
        return (None, errs) if errs else ({"by_symbol": by}, [])

    def fallback(self, job, ctx):
        by = {}
        for s in job["symbols"]:
            p = dbt.tally(ctx, s)["proposal"]
            by[s] = dict(self._result(ctx, s, "accept", p["direction"], p["conviction"],
                                      "(agent failed twice; Python proposal kept)", [], []), fallback=True)
        return {"by_symbol": by}


# ---------------------------------------------------------------- Trader
class Trader(Stage):
    name, agent = "trader", "trader"
    rules = ["Do not change the direction or conviction. Pick the setup that best fits, and say what would prove the call wrong.",
             "Use 'avoid' if the plan is not tradeable (e.g. thin volume, event risk). invalidation <= 20 words."]
    output_format = {"results": [{"symbol": "TICKER", "setup": "|".join(SETUPS), "invalidation": "<=20 words"}]}

    def jobs(self, ctx):
        rm, jobs = ctx.stage("research_manager"), []
        for i, batch in enumerate(chunks(sector_order(ctx), ctx.cfg["batching"]["trader"]), 1):
            stocks = []
            for s in batch:
                f = ctx.packs[s]["market"]["facts"]
                v = rm.get(s, {})
                plan = scoring.levels(f, v.get("direction", "flat"), v.get("conviction", "low"))
                stocks.append({"symbol": s, "direction": v.get("direction"), "conviction": v.get("conviction"),
                               "deciding_points": [p["text"] for p in v.get("deciding_points", [])],
                               "close": f["close"], "atr_pct": f["atr_pct"], "sma20": f["sma20"],
                               "support20": f["support20"], "resistance20": f["resistance20"],
                               "avg_traded_value_pkr_m": f["avg_traded_value_pkr_m"],
                               "catalysts": [c["text"] for c in ctx.packs[s]["fundamentals"]["catalysts"]],
                               "python_levels": plan})
            jobs.append({"job_id": f"batch{i:02d}", "agent": self.agent, "symbols": batch, "data": {"stocks": stocks}})
        return jobs

    def validate(self, job, out, ctx):
        errs, by = [], {}
        for s, r in results_by_symbol(out, job["symbols"], errs).items():
            by[s] = {"setup": enum(r.get("setup"), SETUPS, f"{s}.setup", errs),
                     "invalidation": words(r.get("invalidation"), 20)}
        return (None, errs) if errs else ({"by_symbol": by}, [])

    def fallback(self, job, ctx):
        return {"by_symbol": {s: {"setup": "avoid", "invalidation": "(agent failed twice)", "fallback": True}
                              for s in job["symbols"]}}


# ---------------------------------------------------------------- Risk debate
class Risk(Stage):
    def __init__(self, rnd: int):
        self.rnd = rnd
        self.name = f"risk_r{rnd}"
        if rnd == 1:
            self.rules = ["Rate the risk of the trader's 5-day plan from YOUR risk appetite.",
                          "conviction_adjust: -1 lower, 0 keep, +1 raise. argument <= 40 words, cite ids where possible."]
            self.output_format = {"results": [{"symbol": "TICKER", "risk_rating": "low|medium|high",
                                               "conviction_adjust": 0, "argument": "<=40 words", "cites": ["M-TICKER-5"]}]}
        else:
            self.rules = ["Read the other two risk analysts' round-1 views and reply. You may change your rating.",
                          "conviction_adjust: -1, 0 or +1. response <= 40 words."]
            self.output_format = {"results": [{"symbol": "TICKER", "risk_rating": "low|medium|high",
                                               "conviction_adjust": 0, "response": "<=40 words"}]}

    def enabled(self, ctx):
        return self.rnd <= ctx.cfg["debate"]["risk_rounds"]

    def jobs(self, ctx):
        rm, tr, r1 = ctx.stage("research_manager"), ctx.stage("trader"), ctx.stage("risk_r1")
        liq_min = ctx.cfg["liquidity"]["min_avg_traded_value_pkr"] / 1e6
        jobs = []
        for i, batch in enumerate(chunks(sector_order(ctx), ctx.cfg["batching"]["risk"]), 1):
            for role in RISK_ROLES:
                stocks = []
                for s in batch:
                    f, v, t = ctx.packs[s]["market"]["facts"], rm.get(s, {}), tr.get(s, {})
                    d = {"symbol": s, "direction": v.get("direction"), "conviction": v.get("conviction"),
                         "setup": t.get("setup"), "invalidation": t.get("invalidation"),
                         "python_levels": scoring.levels(f, v.get("direction", "flat"), v.get("conviction", "low")),
                         "atr_pct": f["atr_pct"], "avg_traded_value_pkr_m": f["avg_traded_value_pkr_m"],
                         "below_liquidity_threshold": (f["avg_traded_value_pkr_m"] or 0) < liq_min,
                         "catalysts": [{"id": c["id"], "text": c["text"]} for c in ctx.packs[s]["fundamentals"]["catalysts"]],
                         "ex_dividend_recent": f["ex_marker_recent"]}
                    if self.rnd == 2:
                        d["round1_views"] = r1.get(s, {})
                    stocks.append(d)
                jobs.append({"job_id": f"batch{i:02d}-{role}", "agent": f"risk-{role}", "symbols": batch,
                             "role": role, "data": {"your_role": role, "stocks": stocks}})
        return jobs

    def validate(self, job, out, ctx):
        errs, by = [], {}
        for s, r in results_by_symbol(out, job["symbols"], errs).items():
            try:
                adj = max(-1, min(1, int(r.get("conviction_adjust", 0))))
            except (TypeError, ValueError):
                adj = 0
            v = {"risk_rating": enum(r.get("risk_rating"), LEVELS, f"{s}.risk_rating", errs), "conviction_adjust": adj}
            if self.rnd == 1:
                v.update(argument=words(r.get("argument"), 40), cites=cites(r.get("cites"), ctx.allowed_ids(s)))
            else:
                v["response"] = words(r.get("response"), 40)
            by[s] = {job["role"]: v}
        return (None, errs) if errs else ({"by_symbol": by}, [])

    def fallback(self, job, ctx):
        return {"by_symbol": {s: {job["role"]: {"risk_rating": "medium", "conviction_adjust": 0, "fallback": True}}
                              for s in job["symbols"]}}

    def merge(self, outputs, ctx):
        merged: dict = {}
        for _job, out in outputs:
            for s, v in out["by_symbol"].items():
                merged.setdefault(s, {}).update(v)
        return merged


def risk_consensus(ctx: Ctx, sym: str) -> dict:
    """Median of the three final risk views (deterministic aggregation)."""
    last = ctx.stage("risk_r2") or ctx.stage("risk_r1")
    views = last.get(sym, {})
    ratings = sorted(LEVELS.index(v["risk_rating"]) for v in views.values() if v.get("risk_rating") in LEVELS)
    adjs = sorted(v.get("conviction_adjust", 0) for v in views.values())
    rating = LEVELS[int(median(ratings))] if ratings else "medium"
    adj = int(median(adjs)) if adjs else 0
    base = ctx.stage("research_manager").get(sym, {}).get("conviction", "low")
    conv = LEVELS[max(0, min(2, LEVELS.index(base) + adj))]
    return {"risk_rating": rating, "conviction_adjust": adj, "conviction_after_risk": conv}


# ---------------------------------------------------------------- Portfolio Manager
class PortfolioManager(Stage):
    name, agent = "portfolio_manager", "portfolio-manager"
    rules = ["Give the final call per stock. final_direction must be the research direction or 'flat' (never flip up/down).",
             "final_conviction may move at most one level from conviction_after_risk.",
             "You do NOT rank stocks; the formula does. Use 'flag' to warn about anything the numbers miss. reason <= 30 words."]
    output_format = {"results": [{"symbol": "TICKER", "final_direction": "up|flat|down", "final_conviction": "low|medium|high",
                                  "flag": "|".join(FLAGS), "reason": "<=30 words"}]}

    def jobs(self, ctx):
        rm, tr, sen, news = ctx.stage("research_manager"), ctx.stage("trader"), ctx.stage("sentiment"), ctx.stage("news")
        jobs = []
        for i, batch in enumerate(chunks(sector_order(ctx), ctx.cfg["batching"]["portfolio_manager"]), 1):
            stocks = []
            for s in batch:
                v = rm.get(s, {})
                stocks.append({"symbol": s, "research_direction": v.get("direction"), "research_conviction": v.get("conviction"),
                               "deciding_points": [p["text"] for p in v.get("deciding_points", [])],
                               **risk_consensus(ctx, s), "setup": tr.get(s, {}).get("setup"),
                               "quant_score": ctx.packs[s]["quant_score"],
                               "sentiment": sen.get(s, {}).get("mood"),
                               "news_view": news.get("stocks", {}).get(s, {}).get("news_view")})
            jobs.append({"job_id": f"batch{i:02d}", "agent": self.agent, "symbols": batch,
                         "data": {"macro_view": news.get("macro", {}).get("macro_view"), "stocks": stocks}})
        return jobs

    def validate(self, job, out, ctx):
        errs, by = [], {}
        rm = ctx.stage("research_manager")
        for s, r in results_by_symbol(out, job["symbols"], errs).items():
            d = enum(r.get("final_direction"), DIRS, f"{s}.final_direction", errs)
            c = enum(r.get("final_conviction"), LEVELS, f"{s}.final_conviction", errs)
            flag = enum(r.get("flag"), FLAGS, f"{s}.flag", errs)
            if None in (d, c, flag):
                continue
            notes = []
            rd = rm.get(s, {}).get("direction", "flat")
            if d not in (rd, "flat"):
                notes.append(f"direction {d} not allowed (research said {rd}); set to flat")
                d = "flat"
            after = risk_consensus(ctx, s)["conviction_after_risk"]
            lo, hi = max(0, LEVELS.index(after) - 1), min(2, LEVELS.index(after) + 1)
            ci = min(max(LEVELS.index(c), lo), hi)
            if LEVELS[ci] != c:
                notes.append(f"conviction {c} clamped to {LEVELS[ci]}")
            by[s] = {"final_direction": d, "final_conviction": LEVELS[ci], "flag": flag,
                     "reason": words(r.get("reason"), 30), "clamp_notes": notes}
        return (None, errs) if errs else ({"by_symbol": by}, [])

    def fallback(self, job, ctx):
        by = {}
        for s in job["symbols"]:
            rc = risk_consensus(ctx, s)
            by[s] = {"final_direction": ctx.stage("research_manager").get(s, {}).get("direction", "flat"),
                     "final_conviction": rc["conviction_after_risk"], "flag": "caution",
                     "reason": "(PM agent failed twice; research call kept)", "clamp_notes": [], "fallback": True}
        return {"by_symbol": by}


# ---------------------------------------------------------------- narrative
class Narrative(Stage):
    name, agent = "narrative", "run-narrator"
    rules = ["Write a plain-language summary (<= 250 words, Markdown) of how this run reached its result:",
             "what the market backdrop was, what drove the top 5, where agents disagreed, and what data was missing.",
             "Only use the data given. No investment advice wording ('you should buy')."]
    output_format = {"result": {"summary_md": "<= 250 words"}}

    def jobs(self, ctx):
        table = scoring.rank(ctx)
        news, social = ctx.stage("news"), ctx.stage("social")
        return [{"job_id": "narrative", "agent": self.agent, "symbols": [],
                 "data": {"as_of": ctx.snap["as_of"], "window": ctx.snap["window"],
                          "macro": news.get("macro"), "social_market_mood": (social or {}).get("market_mood"),
                          "breadth_last_5_days": ctx.snap["breadth_5d"],
                          "missing_sources": ctx.snap["source_errors"]
                          + ([] if ctx.snap.get("fipi_lipi") else ["FIPI/LIPI flows (not supplied)"]),
                          "top10": [{k: r[k] for k in ("rank", "symbol", "final_direction", "final_conviction",
                                                       "risk_rating", "expected_move_pct", "hybrid_score", "flag",
                                                       "winner", "deciding_points")} for r in table[:10]],
                          "counts": {d: sum(1 for r in table if r["final_direction"] == d) for d in DIRS}}}]

    def validate(self, job, out, ctx):
        r = (out or {}).get("result")
        if not isinstance(r, dict) or not r.get("summary_md"):
            return None, ["missing result.summary_md"]
        return {"summary_md": words(r["summary_md"], 260)}, []

    def fallback(self, job, ctx):
        return {"summary_md": "_Narrative agent failed twice; see the stage-by-stage sections below._", "fallback": True}

    def merge(self, outputs, ctx):
        return outputs[0][1]


def all_stages() -> list[Stage]:
    return [Social(), News(), Sentiment(), Debate(1), Debate(2), ResearchManager(), Trader(),
            Risk(1), Risk(2), PortfolioManager(), Narrative()]


# ======================================================================== job engine
def agent_hash(agent: str) -> str:
    p = AGENT_DIR / f"{agent}.md"
    # normalise line endings so a Windows checkout gives the same key
    return sha256(p.read_text(encoding="utf-8").replace("\r\n", "\n")) if p.exists() else "missing"


def cache_key(stage: Stage, job: dict) -> str:
    return sha256({"v": settings()["prompt_version"], "stage": stage.name, "agent": job["agent"],
                   "agent_def": agent_hash(job["agent"]), "data": job["data"]})


def job_paths(run: Path, stage: Stage, job: dict) -> tuple[Path, Path]:
    d = run / "jobs" / stage.name
    return d / f"{job['job_id']}.input.json", d / f"{job['job_id']}.output.json"


def prepare(run: Path, stage: Stage, ctx: Ctx, state: dict) -> list[dict]:
    """Write job inputs; replay cached answers. Returns jobs still needing an agent."""
    pending = []
    for job in stage.jobs(ctx):
        inp, outp = job_paths(run, stage, job)
        key = cache_key(stage, job)
        job["cache_key"] = key
        cached = CACHE_DIR / "agents" / f"{key}.json"
        done = run / "jobs" / stage.name / f"{job['job_id']}.final.json"
        if done.exists() and read_json(done).get("cache_key") == key:
            continue
        if cached.exists():
            write_json(done, {"cache_key": key, "source": "replay", "clean": read_json(cached)})
            state["replayed"] = state.get("replayed", 0) + 1
            continue
        write_json(inp, {"job_id": job["job_id"], "stage": stage.name, "agent": job["agent"],
                         "output_path": str(outp.relative_to(ROOT)).replace("\\", "/"),
                         "rules": stage.rules, "output_format": stage.output_format,
                         "symbols": job["symbols"], "data": job["data"],
                         "_meta": {k: job[k] for k in ("side", "role") if k in job}})
        pending.append(job)
    return pending


def collect(run: Path, stage: Stage, ctx: Ctx, state: dict) -> tuple[list[dict], list[str]]:
    """Validate agent outputs. Returns (jobs still pending, messages)."""
    msgs, pending = [], []
    attempts = state.setdefault("attempts", {})
    for job in stage.jobs(ctx):
        inp, outp = job_paths(run, stage, job)
        key = cache_key(stage, job)
        done = run / "jobs" / stage.name / f"{job['job_id']}.final.json"
        if done.exists() and read_json(done).get("cache_key") == key:
            continue
        akey = f"{stage.name}/{job['job_id']}"
        if outp.exists():
            try:
                raw = read_json(outp)
                clean, errs = stage.validate(job, raw, ctx)
            except Exception as e:  # noqa: BLE001 - malformed JSON counts as a failed attempt
                clean, errs = None, [f"unreadable output: {type(e).__name__}: {e}"]
            if clean is not None:
                write_json(CACHE_DIR / "agents" / f"{key}.json", clean)
                write_json(done, {"cache_key": key, "source": "agent", "clean": clean})
                state["agent_calls"] = state.get("agent_calls", 0) + 1
                continue
            attempts[akey] = attempts.get(akey, 0) + 1
            outp.rename(outp.with_suffix(f".rejected{attempts[akey]}.json"))
            msgs.append(f"{akey}: rejected ({'; '.join(errs)[:200]})")
            if attempts[akey] >= 2:
                write_json(done, {"cache_key": key, "source": "fallback", "clean": stage.fallback(job, ctx)})
                state["fallbacks"] = state.get("fallbacks", 0) + 1
                msgs.append(f"{akey}: failed twice, neutral fallback used")
                continue
        pending.append(job)
    return pending, msgs


def finalize(run: Path, stage: Stage, ctx: Ctx) -> dict:
    outs = []
    for job in stage.jobs(ctx):
        done = read_json(run / "jobs" / stage.name / f"{job['job_id']}.final.json")
        outs.append((job, done["clean"]))
    merged = stage.merge(outs, ctx)
    write_json(run / "stages" / f"{stage.name}.json", merged)
    return merged
