# PSX-ALL-SOURCES-07-DAYS

Ranks the **top 30 KSE-100 companies by free-float market cap** by their potential
price move over the **next 5 trading days**, using a 12-role agent flow:

```
Market*        ─┐            ┌─ Bull ─┐                                   ┌─ Aggressive ───┐
Fundamentals*  ─┤            │   ⇅    │                                   │                │
News           ─┼─► merge ───┤        ├─► Research Manager ─► Trader ─────┼─ Neutral ──────┼─► Portfolio Manager
Sentiment      ─┘            └─ Bear ─┘                                   └─ Conservative ─┘
                                                        (* = pure Python, zero tokens)
```

> **Not financial advice.** This is an automated research experiment on free data.
> It can be wrong and says nothing about anyone's personal situation.

## Design principles

1. **Deterministic.** Data is frozen into a fingerprinted snapshot first. Python computes
   every number (indicators, valuation, expected move, levels, score, ranking). Agents
   only fill fixed JSON forms with enumerated answers and cited evidence IDs. Every agent
   answer is cached by its exact input, so re-running a snapshot replays identical results.
2. **Token-light.** Two analysts are pure Python, agents see ~300-token evidence packs,
   strict word caps, batching by sector, Haiku/Sonnet tiers, Python-written reports.
   About 90 agent calls per run.
3. **Structured Bull vs Bear debate.** Agents pick evidence IDs and weights from
   Python-built bull/bear menus, then rebut with fixed reasons. Python scores the debate
   and proposes the call; the Research Manager accepts or adjusts it by one step.

Full strategy: [PLAN.md](PLAN.md).

## Requirements

- Python 3.12, `pip install -r requirements.txt`
- [Claude Code](https://claude.com/claude-code) logged in with your Claude subscription (no API key)

## Running (inside Claude Code)

Ask Claude Code to "do this week's run" (uses the `psx-run` skill), or by hand:

```bash
python -m psx7 snapshot            # Stage 0: fetch + freeze data, Python analysts, score past runs
python -m psx7 step                # prints agent jobs; Claude launches them; repeat until DONE
python -m psx7 finish              # ranking + reports (+ PDF)
```

Check the Python signals against history (zero tokens, about 3 years of PSX files):

```bash
python -m psx7 backtest            # writes runs/backtest/backtest.md
```

Outputs land in `runs/<as-of date>/`:

| File | What |
|---|---|
| `ranking.md` / `ranking.html` | All 30 ranked, top 5 explained |
| `PSX_report_<date>.pdf` | Large-font PDF: key numbers, top 5, all 30, how it worked, glossary (`python -m psx7 pdf`) |
| `how_it_worked.md` | Stage-by-stage explanation of this run |
| `stocks/<TICKER>.md` | Full trail per stock: analysts, debate, trader, risk, PM |
| `stages/*.json` | Validated agent results per stage |
| `run_meta.json` | Models, agent calls, cache replays, missing sources |
| `runs/scorecard.md` | Past runs scored against actual prices |
| `runs/backtest/backtest.md` | Walk-forward test of every Python market signal (`python -m psx7 backtest`) |

## Data sources (free)

| Data | Source | Status |
|---|---|---|
| Daily OHLCV, all stocks | PSX daily market summary files | ✅ |
| KSE-100 members, free float | PSX data portal index page | ✅ |
| Financials, ratios, announcements | PSX company pages | ✅ |
| News (14 days) | Business Recorder and Dawn RSS + Google News RSS search per company | ✅ |
| Foreign-flow headlines | From the same news (Pakistan context only) | ✅ |
| Social chatter | One small web-search agent per run (optional) | ✅ |
| FIPI/LIPI numbers | NCCPL blocks scripts. Optional CSV in `inputs/fipi_lipi.csv` (`date,category,net_usd_m`) | optional |
| KSE-100 index history | Not free for scripts. Rebuilt as a free-float-weighted proxy | proxy |

Prices are **back-adjusted** for dividends, bonus and rights using PSX's own adjusted previous close (LDCP) on
ex-dates. The scorecard chains close ÷ LDCP day by day, so payouts inside a window aren't counted as losses.
The expected move is a fixed, backtest-sized edge (0.5% for a medium-conviction call), not a volatility multiple:
in the backtest, volatile stocks lagged the market over 5 days.

## Settings

`config/settings.yaml`: universe size, news window, liquidity threshold, model per role,
batch sizes, debate rounds, score weights. After changing `models:`, run
`python -m psx7 sync-agents`. `config/holidays.yaml`: PSX holidays (update Eid dates
when announced). `config/aliases.yaml`: names used to match news to tickers.

## Tests

```bash
python -m pytest -q
```
Offline: parsers on saved PSX pages, plus a full pipeline on synthetic data with fake
agents (checks validation, retry, fallback, PM rules and byte-identical replay).
