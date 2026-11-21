# HMB: Habib Metropolitan Bank Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: COMMERCIAL BANKS · Close 103.94 · Rank 16/30

## 1. Analysts

### Market (Python, score +45)
- `M-HMB-1` Close 103.94 is above 20-day average 98.84 (+10)
- `M-HMB-2` Close is above 50-day average 96.10 (+10)
- `M-HMB-3` 20-day average is above 50-day average (short-term trend up) (+10)
- `M-HMB-4` Close is below 200-day average 104.52 (-5)
- `M-HMB-5` RSI(14) 72.3: positive momentum (+10)
- `M-HMB-6` MACD histogram +0.56 (bullish crossover side) (+10)
- `M-HMB-7` 5-day return +1.5% vs market -0.3% (relative +1.7 pts) (+0)
- `M-HMB-8` 20-day return +12.3% vs market +8.2% (relative +4.1 pts) (+0)
- `M-HMB-9` 5-day volume is 0.59x the 20-day average (+0)
- `M-HMB-10` Price sits at 47% of its 52-week range (91.57 to 117.95) (+0)
- `M-HMB-11` 20-day support 91.57, resistance 104.99 (+0)
- `M-HMB-12` Dividend/bonus/rights adjustment on 2026-11-02 (x0.9741): earlier prices adjusted, so the ex-date drop is not counted as a fall (+0)

### Fundamentals (Python, score +0)
- `F-HMB-1` P/E (TTM) 5.72 vs top-30 median 7.59 (cheaper by 25%) (+15)
- `F-HMB-2` Latest annual EPS growth -8.5% (-10)
- `F-HMB-3` Net margin 14.2% vs 10.5% a year earlier (+5)
- `F-HMB-4` Q3 2026 EPS -20.9% vs same quarter last year (-10)
- `F-HMB-5` 1-year price change +7.8% (+0)

### News (agent) view: positive
- `N-HMB-1` [Habib Metropolitan Bank credits third interim cash dividend of Rs. 2.50 per share](https://news.google.com/rss/articles/CBMiaEFVX3lxTE9DbWdieV9xVXhTTkQyd3hWTW1YQ2pMSTlscUZaZ3U0MHhlWURoeHQzS3I0NHdIczZ0S0lfY2VmZGtlOWZaVTc1QUFBSFViRmROSWp1SnhJcnlfem9WQnpObWZLUnNnVEZD?oc=5): positive, low impact. Dividend headline 10 days old; cash credit likely already priced in.

### Sentiment (agent): bullish (low)
- Single low-impact positive news item; limited evidence behind the bullish tilt. `N-HMB-1`
- Five-day return of +1.45% beats the market's -0.28% move. _(no cite)_
- Foreign investors see IMF programme as key to stability, a mildly supportive backdrop. `FL-2`

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **strong** `M-HMB-1` Close 103.94 is above 20-day average 98.84 (counts 3.0)
- **moderate** `M-HMB-3` 20-day average is above 50-day average (short-term trend up) (counts 2.0)
- **moderate** `F-HMB-3` Net margin 14.2% vs 10.5% a year earlier → rebutted: *not_5day_relevant* (counts 1.0)
- **weak** `MD-1` Macro: KSE-100 closed up 610 points at 177,382, extending recovery; supportive for equity sentiment. → rebutted: *weak_signal* (counts 0.5)
- **Bull total: 6.5**

### Bear: picks (rebuttals by Bull)
- **strong** `F-HMB-4` Q3 2026 EPS -20.9% vs same quarter last year → rebutted: *stale* (counts 1.5)
- **moderate** `M-HMB-4` Close is below 200-day average 104.52 (counts 2.0)
- **weak** `MD-4` Macro: Foreign investors repatriated $1.16 billion from Pakistan in July-October FY27, weighing on external flows. (counts 1.0)
- **Bear total: 4.5**

Net debate score **+2.0** → Python proposal: **up / low**

## 3. Research Manager → Trader
- Decision **accept**: direction **up**, conviction **low**. Short-term trend up, but below 200-day average limits conviction; low-conviction up is fair.
- Close 103.94 is above 20-day average 98.84 `M-HMB-1`
- 20-day average is above 50-day average (short-term trend up) `M-HMB-3`
- Close is below 200-day average 104.52 `M-HMB-4`
- Trader setup *avoid*; invalid if: Thin volume persists and close falls below stop 101.28.
- Levels (Python, from ATR): entry ref 103.94, expected move pct 1.2, target 105.18, stop 101.28

## 4. Risk debate
- **aggressive**: r1 high (-1) Avoid setup with 1.2% expected move against 2.56% stop distance and only 21.9m traded value. Thin liquidity is a real hazard, not a detail. High risk, lower conviction. → r2 high (-1) High risk, agree with the others. Only 21.9m PKR traded value and a 1.2% expected move against a 2.56% stop distance. Exits could be hard. Avoid the plan.
- **neutral**: r1 high (-1) Avoid setup with low conviction and thin liquidity (21.9m PKR average traded value). Target 1.24 above entry against 2.66 stop distance, about 0.47 reward-to-risk. Plan should not be taken. → r2 high (-1) Agree with both peers. Thin liquidity (21.9m), low conviction and roughly 0.47 reward-to-risk make the plan unattractive. High risk, reduce conviction.
- **conservative**: r1 high (-1) Avoid setup with low conviction and 21.9M PKR average traded value, thin liquidity. Expected move only 1.2% against ATR 2.14, so exits may be hard. Ex-dividend 2026-11-02 passed. Reduce conviction. → r2 high (-1) High risk held. Expected move 1.2% against a 2.56% stop distance, with thin 21.9m traded value. Both other analysts also reject the plan. Lower conviction and avoid.
- Consensus (median): risk **high**, conviction after risk **low**

## 5. Portfolio Manager
- Final **up / low**, flag caution. High risk, setup rated avoid, and price still below 200-day average; short-term trend up but low conviction only.
- Expected 5-day move +1.20%, hybrid score +0.598
