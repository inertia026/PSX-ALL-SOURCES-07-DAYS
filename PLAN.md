# PSX 7-Day Growth Potential: Strategy Plan (v0.4)

> **Status: BUILT (v1). No run has been performed.** Runs are done separately,
> when you choose (see README / the `psx-run` skill).
>
> This is a research and decision-support tool. It is not financial advice.

---

## 1. Goal

Each run ranks the **top 30 KSE-100 companies by free-float market cap** by their
**potential price growth over the next 5 trading days (about 7 calendar days)**,
highlights the **top 5**, and explains in plain language how the strategy reached
that result.

## 2. Source of truth: the agent flow (from the reference image)

```
 STAGE 1: ANALYSTS          STAGE 2: RESEARCH DEBATE      STAGE 3      STAGE 4: RISK DEBATE         STAGE 5
 ─────────────────          ────────────────────────      ───────      ────────────────────         ───────
 Market        ─┐                ┌─ Bull ─┐                               ┌─ Aggressive ──┐
 Fundamentals  ─┤                │   ⇅    │                               │               │
 News          ─┼─► (merge) ─────┤        ├─► Research ─► Trader ─────────┼─ Neutral ─────┼─► Portfolio
 Sentiment     ─┘                │   ⇅    │   Manager                     │               │   Manager
                                 └─ Bear ─┘                               └─ Conservative ┘
```

The pipeline keeps this exact order and these exact roles. Nothing is added
between stages; extra logic (scoring, ranking) lives inside the existing roles.

## 2a. Design principles: deterministic and token-light

Two rules govern every design choice: **(1) as deterministic as possible** and
**(2) as few tokens as possible.** Both follow from one idea: **code decides,
Claude explains.** Anything that can be calculated is Python (repeatable, zero
tokens). Claude is used only where reading or arguing over text adds value.

**Determinism**

1. **Frozen snapshot.** Python fetches all data first and saves it as one dated
   snapshot with a SHA-256 fingerprint. Agents read only the snapshot. No live
   web access during the agent stages.
2. **All numbers from Python.** Indicators, valuation, liquidity, flows,
   breadth, and the **expected 5-day move** (volatility × direction × conviction).
3. **Fixed answer forms.** Agents return JSON with enumerated fields
   (direction: up/flat/down; conviction: low/medium/high; risk: low/medium/high),
   and every argument cites an evidence ID. Python validates and rejects anything else.
4. **Replay cache.** Each agent answer is saved under
   `hash(prompt version + agent definition + exact job input)`. The job input is
   built only from the fingerprinted snapshot, so re-running the same snapshot
   replays the saved answers: identical output, zero tokens. Editing an agent's
   instructions invalidates only that agent's cache.
7. **Fixed aggregation.** The three risk views are combined by median; the
   Portfolio Manager cannot flip up/down (only to flat) and can move conviction by
   at most one level. Python enforces both rules.
5. **Formula ranking.** The hybrid score and tie-breaks (alphabetical) are code.
   The Portfolio Manager can **flag** a stock with a reason, but cannot reorder.
6. **Fixed order.** Versioned prompts, alphabetical stock order, fixed batches.

**Token efficiency**

1. **Market and Fundamentals analysts are pure Python** rule-based reports.
   They keep their place in the flow, cost zero tokens and are fully repeatable.
2. **Compact evidence packs** (about 300 tokens per stock), never raw price tables.
3. **Structured Bull vs Bear debate:** agents pick evidence IDs, weights and
   rebuttal reasons from fixed lists (about 15–30 output tokens per stock); Python
   scores the debate (section 4, Stage 2). Other agents keep strict word caps.
4. **Lean subagents:** Read/Write tools only, larger batches, outputs written to
   files, one-line "done" replies so the main session stays small.
5. **Reuse:** macro news summarised once per run; stocks with no news in 7 days
   skip the News agent call.
6. **Python writes the reports** (ranking, HTML, scorecard, most of "how it
   worked"); one short Claude call adds the narrative summary.
7. **Model tiers:** Haiku for News, Sentiment and debaters; Sonnet for the
   Research Manager and Portfolio Manager. Opus stays an option in config.

## 3. Decisions made

| Topic | Decision |
|---|---|
| LLM | **Claude, mixed tiers.** News, Sentiment, Bull/Bear and risk debaters on Haiku; Research Manager and Portfolio Manager on Sonnet. Set in config. |
| Billing | **Your Claude subscription's usage**, not a separately bought API key. No Anthropic API key is needed. |
| Run engine | **Inside Claude Code.** You start a run in Claude Code. Python scripts fetch and calculate data; each of the 12 roles runs as a Claude Code subagent. |
| Usage control | **Batch stocks per call** where the role allows it (section 9). About 220 calls per run instead of about 510. Progress is saved after each stage so a run can resume after a usage-limit reset. |
| Codebase | **Our own pipeline**, following the image's flow. Not a fork of TradingAgents. |
| Universe | **Top 30 KSE-100 members by free-float market cap**, refreshed each run. |
| Horizon | **5 PSX trading days.** Run on the **weekend** using Friday close; the window is Monday to Friday. |
| Debate depth | **2 rounds** of Bull vs Bear, and **2 rounds** of the risk debate. |
| Data | **Free public sources only** (details in section 5). |
| Sentiment inputs | News tone + market breadth, live web search for social posts, and FIPI/LIPI flows. |
| Final ranking | **Hybrid score** by formula. The Portfolio Manager may flag stocks with reasons but does not reorder them (section 2a). |
| News window | **Last 14 days** of company and macro news (agents weight the last 7 days more). Collected at snapshot time: RSS feeds + Google News RSS search per company. No daily job needed. |
| Liquidity penalty | Applies below **PKR 20 million/day** average traded value (20-day average). |
| Output | **All 30 ranked + top 5 explained in depth.** |
| Report format | **Markdown + an HTML page** per run. |
| Scorecard | **In version 1.** Each run first scores the previous run against actual prices. |
| Repo | New, separate, **public** GitHub repo named **`PSX-ALL-SOURCES-07-DAYS`**. Code **and** all run reports are published. |

## 4. The roles in detail

### Stage 1: Analysts (run in parallel, per stock)

| Role | Inputs | Output |
|---|---|---|
| **Market** (Python) | Daily OHLCV for about 1 year, KSE-100 proxy | Trend (20/50/200-day averages), momentum (RSI, MACD), volatility (ATR), 20-day support/resistance, volume spikes, relative strength vs the KSE-100 proxy, 52-week position, ex-dividend flags. Rule-based signals with points; score −100 to +100. |
| **Fundamentals** (Python) | PSX company page: P/E (TTM), ratios, annual and quarterly EPS, announcements | P/E vs top-30 median, EPS growth, margin trend, latest quarter vs a year earlier, and **catalysts**: board-meeting notices (last 14 days), results and other announcements (last 7 days). Score −100 to +100. |
| **News** | Company headlines (last 14 days, matched by title), macro headlines | Company-specific and macro drivers: SBP policy rate, PKR/USD, IMF reviews, oil prices, budget, circulars. Each item tagged positive / negative / neutral with an expected impact. |
| **Sentiment** | Headline tone, market breadth (advancers/decliners, volume), social posts, foreign-flow headlines (+ NCCPL numbers if supplied) | Mood score for the stock and the market, and whether foreign and local investors are buying or selling. |

**Merge:** the four reports become one **evidence pack** per stock. Every fact keeps
its source and date, so later stages can cite it.

### Stage 2: Research debate

**Structured debate (v1.1): agents choose, Python counts.** No free-text arguments.

- **Menus (Python):** each stock's evidence is split into a **bull menu**
  (positive signals, positive news/macro/social, bullish mood) and a **bear menu**
  (the negatives). Catalysts appear in both.
- **Round 1:** Bull and Bear each pick 1–4 items from their own menu and weight
  each strong / moderate / weak.
- **Round 2:** each side rebuts up to 3 opponent picks with one fixed reason:
  `stale`, `outweighed_by` (+ an item from its own menu), `not_5day_relevant`,
  `mechanical`, `weak_signal`.
- **Scoring (Python):** strong 3, moderate 2, weak 1. A rebutted pick counts half;
  a pick `outweighed_by` an equal-or-stronger item counts zero.
  Net = Bull total − Bear total. Net ≥ +2 → up, ≤ −2 → down, else flat.
  Conviction: |net| ≥ 6 high, ≥ 3.5 medium, else low; one step lower if the
  quant score points the other way.
- Batched: 5 stocks per call, grouped by sector. All thresholds are in `config/settings.yaml`.

### Stage 3: Research Manager → Trader

- **Research Manager** (stronger model) reviews Python's debate score and
  proposal. It **accepts**, or **overrides by at most one step** in direction
  and/or conviction with a short reason (Python enforces the limit), and names up
  to 3 deciding evidence IDs. 5 stocks per call.
- **Trader** keeps direction and conviction, picks the setup (breakout,
  pullback, momentum, catalyst, mean reversion, or avoid) and states what would
  invalidate the call. Expected move, target and stop are computed by Python from ATR.

### Stage 4: Risk debate

- **Aggressive**: pushes for more upside; argues the risk is worth it.
- **Neutral**: weighs both sides.
- **Conservative**: focuses on downside, liquidity, event risk (results day,
  policy announcements) and concentration.
- **2 rounds.** Each role gives a risk rating (low / medium / high) and a
  conviction adjustment (−1 / 0 / +1). Python takes the **median** of the three.

### Stage 5: Portfolio Manager (stronger model)

1. Gives the final direction and conviction per stock (cannot flip up/down;
   conviction moves at most one level).
2. May **flag** a stock (caution / watch closely) with a reason.
3. Python computes the hybrid score, ranks all 30 and picks the top 5. The PM
   does not reorder.

## 5. Data sources (free; checked during the build on 2026-11-20)

| Need | Source | Status |
|---|---|---|
| Daily OHLCV + sector code, every stock | PSX daily market summary files (`/download/mkt_summary/<date>.Z`), cached forever | works |
| KSE-100 members + free-float shares | PSX index page `/indices/KSE100` | works |
| Financials, ratios, P/E, announcements | PSX company pages `/company/<SYMBOL>` | works |
| News (company + macro) | Business Recorder + Dawn RSS (1–3 days deep) **and Google News RSS search** per company and for 5 macro topics (14 days deep; polite delay + back-off) | works: 28/30 companies had news in a live check |
| Foreign-flow signal | Headlines about foreign/local investor flows (Pakistan-context only) | works |
| Social sentiment | One web-search "social collector" agent per run, frozen into the snapshot | works (costs 1 call) |
| FIPI/LIPI flows | NCCPL site blocks scripts (bot protection; we do not bypass) | manual CSV in `inputs/` |
| KSE-100 index history | Not available to scripts | rebuilt as free-float-weighted proxy |
| Dividend / bonus / rights adjustment | PSX publishes LDCP = previous close **adjusted** for the entitlement on the ex-date | prices back-adjusted with factor LDCP ÷ previous close |
| Yahoo Finance `.KA` | Data stopped in 2024 | not used |
| Profit, Mettis feeds; Reddit | Feeds removed / blocked | not used |

Every data point records its source. If a source fails, the report lists it
under "Missing or blocked sources" instead of filling in guesses.

Every data point records its source and fetch time. If a source fails, the
report says so instead of filling in guesses.

## 6. Hybrid scoring (first draft, tune later)

```
direction_sign   = { up: +1, flat: 0, down: −1 }
conviction_mult  = { low: 0.5, medium: 1.0, high: 1.5 }
expected_5d_move = direction_sign × conviction_mult × min(ATR%(14), 1.5 × top-30 median) × √5 × 0.5
hybrid_score     = expected_5d_move × conviction_weight
                   − risk_penalty × |expected_5d_move|
                   − liquidity_penalty (if 20-day avg traded value < PKR 20m)
tie-break        = higher quant score, then ticker A→Z
```

The Portfolio Manager does not reorder; it may flag stocks with a reason.
All weights live in `config/settings.yaml`.

## 7. Output of every run

Saved under `runs/YYYY-MM-DD/` in the repo:

1. **`ranking.md` / `ranking.html`**: all 30 stocks with the final call, expected
   5-day move, conviction, risk rating and hybrid score. Top 5 highlighted.
2. **`stocks/<TICKER>.md`**: full trail for each stock: the four analyst reports,
   the Bull/Bear debate, the RM view, the trader plan, the risk debate and the PM decision.
3. **`how_it_worked.md`**: a plain-language walk-through of this run: what each
   stage found, what drove the top 5, which data was missing, and where agents disagreed.
4. **`run_meta.json`**: date, models used, data sources reached, and number of agent calls.

Because the repo is public, every run's ranking and reports are published, each
with a "not financial advice" note at the top.

## 8. Evaluation (scorecard, in version 1)

- Each new run starts by scoring the previous run. This uses price data only,
  with no Claude calls. Returns chain close ÷ PSX's adjusted previous close each
  day, so dividends inside the window aren't counted as losses. The KSE-100 proxy
  weights are saved in the published `ranking.json`, so scoring works on any machine.
- **Past dates (`--date`)** are approximate: PSX only publishes today's index members
  and free float. The report shows a warning; news after the as-of date is excluded.
- After each 5-day window closes, score the earlier run: direction hit rate,
  rank correlation between predicted and actual returns, and top 5 average
  return vs KSE-100.
- The scores add up in `runs/scorecard.md` so we can see if the strategy works
  over time.
- Backtesting on past weeks is possible later, but LLMs may "know" past prices,
  so results need care.

## 9. Usage per run and batching

Runs use your Claude subscription, so the limit is **usage**, not money.
Unbatched, a run would be about 17 calls per stock, or **about 510 calls**.
Batching cuts that while keeping every role from the image:

| Stage | How it runs | Calls (approx.) |
|---|---|---|
| Data fetch, indicators, Market + Fundamentals analysts | Python only | 0 |
| Social collector | One web-search agent | 1 |
| News | 1 macro job + batches of 5 (only stocks that have news) | 3 to 7 |
| Sentiment | Batches of 5, grouped by sector | 6 |
| Bull vs Bear, 2 rounds | Structured picks, batches of 5 | 2 sides × 2 rounds × 6 = 24 |
| Research Manager | Reviews Python's proposal, batches of 5, Sonnet | 6 |
| Trader | Batches of 5 | 6 |
| Risk debate, 3 roles × 2 rounds | Batches of 5 | 6 × 6 = 36 |
| Portfolio Manager | Batches of 5, Sonnet; ranking is Python | 6 |
| Run narrator | One short summary | 1 |
| **Total** | | **about 90** |

The synthetic test run made 89 calls (it was 209 before the structured debate).
The risk debate (36 calls) is now the largest stage; it stays free-form by choice.

- Progress is saved to disk after each stage and each batch. If you hit a usage
  limit, the run resumes from where it stopped.
- Each run's real usage is recorded in `run_meta.json`.

## 10. Repo layout (planned)

```
PSX-ALL-SOURCES-07-DAYS/
├── .claude/
│   ├── agents/          10 agent roles + social collector + run narrator
│   └── skills/psx-run/  the run procedure (stage order, batching, resume)
├── config/              settings.yaml, holidays.yaml, aliases.yaml
├── psx7/
│   ├── sources.py       free data fetchers and parsers
│   ├── snapshot.py      Stage 0: frozen, fingerprinted snapshot
│   ├── indicators.py    RSI, MACD, ATR, averages (plain Python)
│   ├── analysts.py      Market + Fundamentals analysts, evidence packs
│   ├── stages.py        agent stages, validation, replay cache, fallbacks
│   ├── scoring.py       expected move, levels, hybrid score, ranking
│   ├── scorecard.py     scoring of past runs
│   ├── report.py        Markdown + HTML reports
│   └── cli.py           snapshot / step / finish / status / sync-agents
├── tests/               offline tests (saved PSX pages, synthetic pipeline)
├── runs/                one folder per run date (reports published)
└── PLAN.md              this document
```

Python 3.12 for data and scoring. Claude Code subagents for the 12 roles. No API key.

## 11. Still open

Nothing major. Small details (exact prompts, score weights, which free sources
actually respond) get settled during the build and the first separate run.
