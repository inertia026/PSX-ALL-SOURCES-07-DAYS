# How the strategy worked: run as of 2026-11-20

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

## Summary (agent narrative)

## How this run reached its result **Market backdrop:** The KSE-100 closed up 610 points at 177,382 (MAC-8), and the rupee was steady at 276.51 per dollar (MAC-4). The macro view is mixed: inflation reached 10.41% (MAC-6) and foreign investors repatriated $1.16 billion in July-October (MAC-11). Social mood is neutral. Over the last five sessions, advancers beat decliners on only two days. On 20 Nov, 227 stocks advanced and 259 declined, on traded value of about PKR 4.73 trillion, far above earlier days. Across the top 30, 16 rose, 10 were flat and 4 fell. **What drove the top 5:** - **PPL** (score 1.903): Q1 2027 EPS up 25.5%, and the close is above its 20-day average. - **EFERT** (1.811): 5-day return of +5.9% and urea price-hike news, but RSI 77.2 flags overbought. - **BAHL** (1.794): Q3 2026 EPS up 39.4%, but RSI 76.4 flags overbought. - **MEBL** (1.761): close above both 20-day and 50-day averages, plus SBP deposit-rule news. - **HBL** (1.702): short-term trend up, plus the same SBP deposit-rule news. **Where agents disagreed:** The file shows no visible split. All top 10 were won by the bull side, all are rated direction up, and risk is medium for every name. Conviction is medium for nine names and low for UBL. Caution flags on EFERT, BAHL, MEBL and MTL mark the main risks. The bear arguments are not in the file, so the size of any disagreement cannot be measured. **Missing data:** FIPI/LIPI foreign and local investor flow data was not supplied.

## Stage 0: Frozen snapshot
- As-of close: **2026-11-20**; forecast window **2026-11-23, 2026-11-24, 2026-11-25, 2026-11-26, 2026-11-27**
- Universe: top 30 KSE-100 by free-float market cap: AKBL, ATRL, BAFL, BAHL, BOP, DGKC, EFERT, ENGROH, FABL, FATIMA, FCCL, FFC, HBL, HMB, HUBC, LUCK, MARI, MCB, MEBL, MLCF, MTL, NBP, OGDC, POL, PPL, PSEL, PSO, SRVI, SYS, UBL
- Fingerprint `e228cc282020ccd46b1d48a597524ddeaa97553217d99926c7e06c0d8899edcd`: every agent answer is cached against its exact input, so re-running replays identical results.
- Missing or blocked sources: FIPI/LIPI numbers (NCCPL blocks scripts; flow headlines used instead); Social posts (collector off or found nothing)
- News: 28/30 companies had news in the last 14 days (RSS feeds + Google News search); 2 foreign-flow headlines.
- Price adjustments (dividend/bonus/rights, from PSX's own adjusted previous close): 80 events across 27 stocks.

## Stage 1: Analysts
- **Market (Python):** scores range -75 to +85; positive for 25 of 30.
- **Fundamentals (Python):** positive for 18 of 30 (P/E vs peers, EPS growth, margins, catalysts).
- **News (agent):** 28 stocks had news in 14 days; views: positive: 13, neutral: 12, mixed: 2, none: 2, negative: 1. Macro view: **mixed**.
  - Macro: KSE-100 closed up 610 points at 177,382, extending recovery; supportive for equity sentiment. (positive)
  - Macro: Rupee gained marginally to 276.51 per dollar in the interbank market, signalling a stable currency. (positive)
  - Macro: Short-term inflation reached 10.41% year-on-year, led by wheat flour prices, adding pressure on policy and households. (negative)
  - Macro: Foreign investors repatriated $1.16 billion from Pakistan in July-October FY27, weighing on external flows. (negative)
  - Macro: SBP's revised financing framework for builders and developers adds new valuation requirements, a mixed credit-sector signal. (neutral)
- **Sentiment (agent):** moods: neutral: 18, bullish: 8, bearish: 4. Social market mood: neutral.
- **Merge:** all four outputs combined into a compact evidence pack per stock with IDs (M-, F-, N-, MAC-, S-).

## Stage 2: Bull vs Bear (structured)
- 2 rounds, 5 stocks per call. Python split each stock's evidence into a bull menu and a bear menu;
  round 1 the agents picked and weighted items, round 2 they rebutted opponent picks with fixed reasons. Python scored it:
  weights strong 3, moderate 2, weak 1, rebutted points count 0.5, effectively 'outweighed' points count 0.0.
- Python proposals: up: 17, flat: 8, down: 5.

## Stage 3: Research Manager → Trader
- Research Manager decisions: accept: 28, override: 2 (overrides are limited to one step).
- Directions: up: 17, flat: 8, down: 5; convictions: low: 19, medium: 11.
- Trader setups: avoid: 15, momentum: 7, catalyst: 3, pullback: 3, breakout: 2. Targets and stops come from volatility (ATR), not from the agent.

## Stage 4: Risk debate
- Aggressive, Neutral and Conservative, 2 rounds. Final risk (median of three): medium: 16, high: 12, low: 2.

## Stage 5: Portfolio Manager and ranking
- Final calls: up: 16, flat: 10, down: 4; flags: caution: 15, watch_closely: 6.
- PM rule clamps applied: 0.
- Ranking is the formula `expected move × (1 − risk penalty) − liquidity penalty`; ties by quant score then ticker. The PM cannot reorder.
- Top 5: PPL (+2.54%), EFERT (+2.41%), BAHL (+2.39%), MEBL (+2.35%), HBL (+2.27%)

## Cost and repeatability
- Agent calls this run: **93**; answers replayed from cache: **0**; neutral fallbacks: **0**.
- Market and Fundamentals analysts, scoring, levels, reports and scorecard use **zero tokens** (Python).

