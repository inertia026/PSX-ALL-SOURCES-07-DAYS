# How the strategy worked: run as of 2026-11-27

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

## Summary (agent narrative)

## How this run reached its result **Market backdrop (mixed).** The index fell below 178,000 after political tensions and profit-taking, and the KSE-100 dropped nearly 400 points on geopolitical concerns (MAC-5, MAC-8, MAC-9). Weekly SPI inflation dipped 0.11% and the rupee gained slightly to 276.42 per dollar (MAC-7, MAC-11), both mild positives. The IMF's push for over 100 changes to the sovereign wealth fund law is a governance overhang (MAC-4). Breadth weakened: advancers led on 23 and 24 November, but decliners led from 25 to 27 November, with 308 decliners against 171 advancers on the 27th. Social mood was neutral. **Top 5.** OGDC, POL, PPL, MARI and PSO ranked highest. All carry an "up" direction with small expected moves of 0.25% to 0.5%. Drivers were strong earnings growth (Q1 2027 EPS up about 51% to 53% for OGDC and POL, 172% for PSO, 39% for MARI, 26% for PPL), calm daily ranges, which were favoured in the backtest, and minor news. Conviction was medium for OGDC and POL and low for the other three. **Where agents disagreed.** The bull side won the debate on all ten names shown, so the bear side did not prevail on any of them. Caution flags were raised on POL, PPL and MTL. LUCK carried a watch-closely flag. FCCL, EFERT and LUCK were rated high risk, while the top 5 were rated medium. **Missing data.** FIPI/LIPI foreign and local investor flows were not supplied, so the ranking contains no flow evidence.

## Stage 0: Frozen snapshot
- As-of close: **2026-11-27**; forecast window **2026-11-30, 2026-12-01, 2026-12-02, 2026-12-03, 2026-12-04**
- Universe: top 30 KSE-100 by free-float market cap: AKBL, ATRL, BAFL, BAHL, BOP, DGKC, EFERT, ENGROH, FABL, FATIMA, FCCL, FFC, HBL, HMB, HUBC, LUCK, MARI, MCB, MEBL, MLCF, MTL, NBP, OGDC, POL, PPL, PSEL, PSO, SRVI, SYS, UBL
- Fingerprint `5b86ae9c67b7df42e9ef4fcb0cc4ffe8d414caba047a6aaa02654111b771bf30`: every agent answer is cached against its exact input, so re-running replays identical results.
- Missing or blocked sources: FIPI/LIPI numbers (NCCPL blocks scripts; flow headlines used instead); Social posts (collector off or found nothing)
- News: 29/30 companies had news in the last 14 days (RSS feeds + Google News search); 2 foreign-flow headlines.
- Price adjustments (dividend/bonus/rights, from PSX's own adjusted previous close): 76 events across 27 stocks.

## Stage 1: Analysts
- **Market (Python):** scores range -30 to +15; positive for 19 of 30.
- **Fundamentals (Python):** positive for 18 of 30 (P/E vs peers, EPS growth, margins, catalysts).
- **News (agent):** 29 stocks had news in 14 days; views: neutral: 14, positive: 10, mixed: 5, none: 1. Macro view: **mixed**.
  - Macro: Political tensions and profit-taking pushed PSX below 178,000, making sentiment cautious into the next week. (negative)
  - Macro: KSE-100 fell nearly 400 points on geopolitical concerns and volatile trade, adding near-term pressure. (negative)
  - Macro: Weekly SPI inflation dipped 0.11 percent, a mildly supportive signal for rate expectations. (positive)
  - Macro: Rupee gained 0.01 percent to 276.42 per dollar, a small currency stability positive. (positive)
  - Macro: IMF seeking over 100 changes to the sovereign wealth fund law is a governance overhang with uncertain timing. (negative)
- **Sentiment (agent):** moods: neutral: 16, bullish: 9, bearish: 5. Social market mood: neutral.
- **Merge:** all four outputs combined into a compact evidence pack per stock with IDs (M-, F-, N-, MAC-, S-).

## Stage 2: Bull vs Bear (structured)
- 2 rounds, 5 stocks per call. Python split each stock's evidence into a bull menu and a bear menu;
  round 1 the agents picked and weighted items, round 2 they rebutted opponent picks with fixed reasons. Python scored it:
  weights strong 3, moderate 2, weak 1, rebutted points count 0.5, effectively 'outweighed' points count 0.0.
- Python proposals: up: 13, down: 9, flat: 8.

## Stage 3: Research Manager → Trader
- Research Manager decisions: accept: 29, override: 1 (overrides are limited to one step).
- Directions: up: 13, down: 10, flat: 7; convictions: low: 22, medium: 7, high: 1.
- Trader setups: avoid: 20, catalyst: 3, momentum: 3, pullback: 3, mean_reversion: 1. Targets and stops come from volatility (ATR), not from the agent.

## Stage 4: Risk debate
- Aggressive, Neutral and Conservative, 2 rounds. Final risk (median of three): high: 14, medium: 12, low: 4.

## Stage 5: Portfolio Manager and ranking
- Final calls: down: 10, flat: 10, up: 10; flags: caution: 14, watch_closely: 6.
- PM rule clamps applied: 0.
- Ranking is the formula `expected move × (1 − risk penalty) − liquidity penalty`; ties by quant score then ticker. The PM cannot reorder.
- Top 5: OGDC (+0.50%), POL (+0.50%), PPL (+0.25%), MARI (+0.25%), PSO (+0.25%)

## Cost and repeatability
- Agent calls this run: **93**; answers replayed from cache: **0**; neutral fallbacks: **0**.
- Market and Fundamentals analysts, scoring, levels, reports and scorecard use **zero tokens** (Python).

## Last scored run
- Run 2026-11-20: hit rate 46.67%, top 5 0.07% vs KSE-100 proxy 0.16%. See [scorecard](../scorecard.md).

