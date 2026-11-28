# FFC: Fauji Fertilizer Company Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: FERTILIZER · Close 573.72 · Rank 7/30

## 1. Analysts

### Market (Python, score +5)
- `M-FFC-1` Close 573.72 is +1.3% from its 20-day average 566.62 (+0)
- `M-FFC-2` Close is above 50-day average 539.59 (context only) (+0)
- `M-FFC-3` 20-day average is above 50-day average (short-term trend up; context only) (+0)
- `M-FFC-4` RSI(14) 70.8: stretched, such stocks lagged the next week in the backtest (-10)
- `M-FFC-5` MACD histogram -0.81 (context only) (+0)
- `M-FFC-6` 5-day return +0.4% vs market +0.2% (relative +0.3 pts) (+0)
- `M-FFC-7` 20-day return +5.6% vs market +6.3% (relative -0.7 pts; context only) (+0)
- `M-FFC-8` Daily range (ATR) 1.3% of price: calm; low-volatility stocks did best in the backtest (+15)
- `M-FFC-9` 5-day volume is 0.63x the 20-day average (+0)
- `M-FFC-10` Price sits at 72% of its 52-week range (436.78 to 626.50; context only) (+0)
- `M-FFC-11` 20-day support 541.07, resistance 580.00 (+0)
- `M-FFC-12` Dividend/bonus/rights adjustment on 2026-11-06 (x0.9683): earlier prices adjusted, so the ex-date drop is not counted as a fall (+0)

### Fundamentals (Python, score +0)
- `F-FFC-1` P/E (TTM) 10.29 vs top-30 median 7.51 (dearer by 37%) (-10)
- `F-FFC-2` Latest annual EPS growth +13.6% (+0)
- `F-FFC-3` Net margin 17.0% vs 17.3% a year earlier (+0)
- `F-FFC-4` Q3 2026 EPS +15.1% vs same quarter last year (+10)
- `F-FFC-5` 1-year price change +3.3% (+0)

### News (agent) view: positive
- `N-FFC-1` [FFC Company Announcements - Fauji Fertilizer Company Ltd](https://news.google.com/rss/articles/CBMiX0FVX3lxTE1sa0J5ZGZ2Yy03bUtEYTJKa1h1NF9YeFZMNDRxQUhud3R3QV9oVUY1N2lDak42WEJTXzFiQ2RYd2tzU1ROV003RS1RRjlNM2VfQ282UVNYRHV3MWl6M21R?oc=5): neutral, low impact. Generic company announcement title with no content to assess.
- `N-FFC-2` [Fauji Fertilizer Posts Strong Growth in Q1 2026](https://news.google.com/rss/articles/CBMifkFVX3lxTE5BMHhyeFBmakxXQmlmOU92RXMyQ2xUSGV5SDJtdlpjZVBEYmpmTFpOT2tMMWdFd3hUZTFtMV9uaXY3NmFCVHZVZWdSVy1OYVlhYjZ4aDdPNjhmOXg0aTZwdS1FZjJ2Z0hsc0lZQlJ0R3A3aXYzVFk0a2NEbE9iUQ?oc=5): positive, low impact. Q1 2026 growth is positive but eight days old and largely priced in.
- `N-FFC-3` [Fauji Fertilizer And 10 Other PSX Companies Get Huge Tax Relief](https://news.google.com/rss/articles/CBMioAFBVV95cUxOcGUwQ1poaVR5VXZ2OFBrWW9INHBIOFFybi0yT1JPS0NkQ2FZLXM1VDhzS2lTTjZHMzBMREIybGxyV0JWZzdMVENZS1ZzdGl5VWZtWDg1UU10MmYzRDRXM0ZZZjFzVFpoWkVLTlJNRnl6Wk5UQzdwaXVpb2M1LU9ZOXhSUTR4eEFnaE9qYXhVY2tCbmVVbl9GNFduSjlKOF81?oc=5): positive, low impact. Tax relief for FFC and ten peers is positive but eight days old; likely priced.

### Sentiment (agent): bullish (low)
- Two positive low-impact news items; no negative tone recorded. `N-FFC-2` `N-FFC-3`
- Modest outperformance (+0.42 vs +0.16) on below-average volume (0.63). `MAC-4`
- Foreign confidence headline is negative, so conviction stays low. `FL-1`

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **moderate** `N-FFC-3` News (low impact): Fauji Fertilizer And 10 Other PSX Companies Get Huge Tax Relief (counts 2.0)
- **moderate** `F-FFC-4` Q3 2026 EPS +15.1% vs same quarter last year (counts 2.0)
- **weak** `M-FFC-8` Daily range (ATR) 1.3% of price: calm; low-volatility stocks did best in the backtest (counts 1.0)
- **Bull total: 5.0**

### Bear: picks (rebuttals by Bull)
- **moderate** `M-FFC-4` RSI(14) 70.8: stretched, such stocks lagged the next week in the backtest (counts 2.0)
- **weak** `F-FFC-1` P/E (TTM) 10.29 vs top-30 median 7.51 (dearer by 37%) → rebutted: *not_5day_relevant* (counts 0.5)
- **weak** `MD-2` Macro: KSE-100 fell nearly 400 points on geopolitical concerns and volatile trade, adding near-term pressure. → rebutted: *stale* (counts 0.5)
- **Bear total: 3.0**

Net debate score **+2.0** → Python proposal: **up / low**

## 3. Research Manager → Trader
- Decision **accept**: direction **up**, conviction **low**. Tax relief and EPS growth lead, but stretched RSI limits conviction.
- Q3 2026 EPS +15.1% vs same quarter last year `F-FFC-4`
- RSI(14) 70.8: stretched, such stocks lagged the next week in the backtest `M-FFC-4`
- News (low impact): Fauji Fertilizer And 10 Other PSX Companies Get Huge Tax Relief `N-FFC-3`
- Trader setup *momentum*; invalid if: Close below stop 565.00 or failure to clear resistance20 580.00 within the window.
- Levels (Python, from ATR): entry ref 573.72, expected move pct 0.25, target 575.15, stop 565.0

## 4. Risk debate
- **aggressive**: r1 medium (+0) Liquidity is strong at 669.1m and ATR is low at 1.27%. Target 575.15 is just 0.25% above entry while the stop is about 1.5% below. Upside depends on clearing resistance20 580.00. → r2 medium (-1) Conservative and neutral both flag stop 1.5% below entry against a 0.25% target. I concede: reward is too small for the entry. Rating medium, conviction -1.
- **neutral**: r1 medium (-1) Stop 565.00 is about 1.5% below entry 573.72, while target 575.15 is only about 0.25% above. Reward-to-risk is poor for a low-conviction call, and the plan does not reach resistance20 580.00. → r2 medium (-1) Target 575.15 is only 0.25% above entry, while the stop sits about 1.5% below. Resistance20 580.00 is outside the plan. Medium risk holds; reduce conviction.
- **conservative**: r1 medium (-1) Stop about 1.5% below entry against a target only 0.25% above, so reward is far smaller than risk. Low conviction and an expected move too small to justify entry. → r2 medium (-1) Reward is about 0.25% against a stop about 1.5% below, so reward-to-risk is poor for a low-conviction call. Liquidity is strong at 669.1M. Rating medium; avoid entry.
- Consensus (median): risk **medium**, conviction after risk **low**

## 5. Portfolio Manager
- Final **up / low**, flag caution. EPS growth and tax relief news help, but RSI 70.8 is stretched and lagged next week in the backtest.
- Expected 5-day move +0.25%, hybrid score +0.188
