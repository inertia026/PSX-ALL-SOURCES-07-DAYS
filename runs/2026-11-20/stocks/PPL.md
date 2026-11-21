# PPL: Pakistan Petroleum Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: OIL & GAS EXPLORATION COMPANIES · Close 223.35 · Rank 1/30

## 1. Analysts

### Market (Python, score +55)
- `M-PPL-1` Close 223.35 is above 20-day average 218.10 (+10)
- `M-PPL-2` Close is above 50-day average 216.06 (+10)
- `M-PPL-3` 20-day average is above 50-day average (short-term trend up) (+10)
- `M-PPL-4` Close is above 200-day average 218.03 (+5)
- `M-PPL-5` RSI(14) 57.7: positive momentum (+10)
- `M-PPL-6` MACD histogram +0.56 (bullish crossover side) (+10)
- `M-PPL-7` 5-day return -1.2% vs market -0.3% (relative -0.9 pts) (+0)
- `M-PPL-8` 20-day return +5.2% vs market +8.2% (relative -3.0 pts) (+0)
- `M-PPL-9` 5-day volume is 0.91x the 20-day average (+0)
- `M-PPL-10` Price sits at 49% of its 52-week range (178.61 to 269.43) (+0)
- `M-PPL-11` 20-day support 205.73, resistance 232.10 (+0)
- `M-PPL-12` Dividend/bonus/rights adjustment on 2026-11-11 (x0.9912): earlier prices adjusted, so the ex-date drop is not counted as a fall (+0)

### Fundamentals (Python, score +25)
- `F-PPL-1` P/E (TTM) 5.86 vs top-30 median 7.59 (cheaper by 23%) (+15)
- `F-PPL-2` Latest annual EPS growth +7.1% (+0)
- `F-PPL-3` Net margin 37.3% vs 38.0% a year earlier (+0)
- `F-PPL-4` Q1 2027 EPS +25.5% vs same quarter last year (+10)
- `F-PPL-5` 1-year price change +9.2% (+0)
- `F-PPL-C1` catalyst: Announcement 2026-11-13: Corporate Briefing Session 2026

### News (agent) view: neutral
- `N-PPL-1` [Pakistan Petroleum Limited credits 60% final cash dividend for FY2025-26](https://news.google.com/rss/articles/CBMiaEFVX3lxTE9ORUNaTUd0VW51VkdITjFHR2pqSmhJV2NlM0VpTzBhMENwZlZGOWRrTWNIczFkREc5TWZLVFcySUNxSEZVRzEwYnhQaGpRbnd1NzhySG1FU1dsaUlEbjdwcTNKcW9uUUhz?oc=5): positive, low impact. 60% final dividend credited; positive but routine and already reflected in the price.

### Sentiment (agent): neutral (low)
- One low-impact positive news item; no social posts. `N-PPL-1`
- Five-day return of -1.2% lags market -0.28%; volume quiet at 0.91x. _(no cite)_
- Foreign outflows reported for FY27 so far keep flows cautious. `FL-1`

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **strong** `F-PPL-4` Q1 2027 EPS +25.5% vs same quarter last year (counts 3.0)
- **moderate** `M-PPL-1` Close 223.35 is above 20-day average 218.10 (counts 2.0)
- **moderate** `M-PPL-3` 20-day average is above 50-day average (short-term trend up) → rebutted: *not_5day_relevant* (counts 1.0)
- **Bull total: 6.0**

### Bear: picks (rebuttals by Bull)
- **moderate** `MD-4` Macro: Foreign investors repatriated $1.16 billion from Pakistan in July-October FY27, weighing on external flows. (counts 2.0)
- **weak** `MD-3` Macro: Short-term inflation reached 10.41% year-on-year, led by wheat flour prices, adding pressure on policy and households. → rebutted: *not_5day_relevant* (counts 0.5)
- **Bear total: 2.5**

Net debate score **+3.5** → Python proposal: **up / medium**

## 3. Research Manager → Trader
- Decision **accept**: direction **up**, conviction **medium**. Strong unrebutted EPS growth and price above 20-day average outweigh the moderate macro outflow concern.
- Q1 2027 EPS +25.5% vs same quarter last year `F-PPL-4`
- Close 223.35 is above 20-day average 218.10 `M-PPL-1`
- Trader setup *momentum*; invalid if: Daily close below stop 217.27 or below 20-day average 218.10 would prove the call wrong.
- Levels (Python, from ATR): entry ref 223.35, expected move pct 2.54, target 229.02, stop 217.27

## 4. Risk debate
- **aggressive**: r1 medium (+0) Momentum setup with roughly 1:1 reward to risk: stop 217.27 is about 2.7% below entry, target 229.02 about 2.5% above. Expected move 2.54% is near the 2.27% ATR. Catalyst is only a briefing session. → r2 medium (+0) Keep medium. Stop 217.27 gives about 1:1 reward to risk, which is thin but defined. Conservative's recent ex-dividend and briefing-session event risk are real, so I accept medium rather than high.
- **neutral**: r1 medium (+0) Stop 217.27 sits about 2.7% below entry 223.35 against a 2.5% target, roughly 1:1 with ATR 2.27%. Medium conviction and a briefing-session catalyst add little edge. Keep conviction. → r2 medium (+0) Stop 217.27 sits about 2.7% below entry against a 2.5% target, near 1:1 with ATR 2.27%. The briefing session adds little edge. Both peers rate medium, so keep rating and conviction.
- **conservative**: r1 medium (+0) ATR 2.27% and liquidity 629m are acceptable. Ex-dividend 2026-11-11 is recent, and the briefing session adds some event risk. Stop 217.27 is defined. → r2 medium (-1) Stop 217.27 is 2.7% below entry and target 2.5% above, so reward-to-risk is under 1:1 with ATR 2.27% and a recent ex-dividend. Briefing session adds event risk. Cut conviction.
- Consensus (median): risk **medium**, conviction after risk **medium**

## 5. Portfolio Manager
- Final **up / medium**, flag none. EPS growth and price above 20-day average support momentum; risk medium, news neutral. Keep medium upside call.
- Expected 5-day move +2.54%, hybrid score +1.903
