# POL: Pakistan Oilfields Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: OIL & GAS EXPLORATION COMPANIES · Close 662.07 · Rank 2/30

## 1. Analysts

### Market (Python, score +15)
- `M-POL-1` Close 662.07 is -0.2% from its 20-day average 663.66 (+0)
- `M-POL-2` Close is below 50-day average 670.54 (context only) (+0)
- `M-POL-3` 20-day average is below 50-day average (short-term trend down; context only) (+0)
- `M-POL-4` RSI(14) 46.9 (+0)
- `M-POL-5` MACD histogram -0.04 (context only) (+0)
- `M-POL-6` 5-day return +0.4% vs market +0.2% (relative +0.3 pts) (+0)
- `M-POL-7` 20-day return +0.8% vs market +6.3% (relative -5.4 pts; context only) (+0)
- `M-POL-8` Daily range (ATR) 1.0% of price: calm; low-volatility stocks did best in the backtest (+15)
- `M-POL-9` 5-day volume is 0.40x the 20-day average (+0)
- `M-POL-10` Price sits at 80% of its 52-week range (521.13 to 697.40; context only) (+0)
- `M-POL-11` 20-day support 654.00, resistance 690.00 (+0)

### Fundamentals (Python, score +40)
- `F-POL-1` P/E (TTM) 5.42 vs top-30 median 7.51 (cheaper by 28%) (+15)
- `F-POL-2` Latest annual EPS growth +32.0% (+10)
- `F-POL-3` Net margin 50.6% vs 42.3% a year earlier (+5)
- `F-POL-4` Q1 2027 EPS +50.9% vs same quarter last year (+10)
- `F-POL-5` 1-year price change +7.8% (+0)

### News (agent) view: positive
- `N-POL-1` [Pakistan Oilfields posts strong FY26 earnings growth amid higher energy prices, says research house](https://news.google.com/rss/articles/CBMixAFBVV95cUxPS01BTHNHVHczbTU1U1NrVFNpclBvZUtFU2Vhbm5KMDd2c3hkRWgyY3pSUE9QWDBPclJBN1A3ZjN3dVNxcFdCNXpyYTZzWTFqTmRweWxVS0RheEtxdFFreENHZ0IzMmRWc1JYYUlGZFM3LTJDZ3VzQThPVV9oSjlOZXpjajdwS3RLY1JVUk42SzJOVzdXNXEtTFRwSmd5ZHByUzBZUndyUVE5bk9uOXphbUp5eG1hSjJibmhWYzI3dXIweFlX?oc=5): positive, low impact. FY26 earnings growth reported 11 days ago; largely already priced in, so low impact.

### Sentiment (agent): neutral (low)
- One low-impact positive news item and a small 0.43% gain. `N-POL-1`
- Thin 0.4 volume ratio and weak market sentiment limit conviction. `FL-1` `N-POL-1`

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **strong** `F-POL-4` Q1 2027 EPS +50.9% vs same quarter last year (counts 3.0)
- **moderate** `F-POL-1` P/E (TTM) 5.42 vs top-30 median 7.51 (cheaper by 28%) → rebutted: *not_5day_relevant* (counts 1.0)
- **moderate** `M-POL-8` Daily range (ATR) 1.0% of price: calm; low-volatility stocks did best in the backtest (counts 2.0)
- **Bull total: 6.0**

### Bear: picks (rebuttals by Bull)
- **weak** `MD-1` Macro: Political tensions and profit-taking pushed PSX below 178,000, making sentiment cautious into the next week. (counts 1.0)
- **moderate** `MD-2` Macro: KSE-100 fell nearly 400 points on geopolitical concerns and volatile trade, adding near-term pressure. → rebutted: *outweighed_by* by `F-POL-4` (counts 0.0)
- **weak** `MD-5` Macro: IMF seeking over 100 changes to the sovereign wealth fund law is a governance overhang with uncertain timing. → rebutted: *not_5day_relevant* (counts 0.5)
- **Bear total: 1.5**

Net debate score **+4.5** → Python proposal: **up / medium**

## 3. Research Manager → Trader
- Decision **accept**: direction **up**, conviction **medium**. Strong EPS growth and very calm volatility; macro bear points are weak or rebutted.
- Q1 2027 EPS +50.9% vs same quarter last year `F-POL-4`
- Daily range (ATR) 1.0% of price: calm; low-volatility stocks did best in the backtest `M-POL-8`
- Macro: Political tensions and profit-taking pushed PSX below 178,000, making sentiment cautious into the next week. `MD-1`
- Trader setup *mean_reversion*; invalid if: Close below stop 653.77 or break of support20 at 654.00 on volume.
- Levels (Python, from ATR): entry ref 662.07, expected move pct 0.5, target 665.38, stop 653.77

## 4. Risk debate
- **aggressive**: r1 medium (+0) Traded value 151.5m is adequate and ATR 1.05% gives a tight range. Target 0.5% above entry against a 1.25% stop gives poor reward, so wait for a better setup. Medium risk. → r2 medium (+0) Round 2: Traded value 151.5m is adequate and ATR 1.05% is tight. Target 0.5% against a 1.25% stop gives small payoff, but downside is contained. Hold at medium.
- **neutral**: r1 low (+0) Liquid, low ATR of 1.05 percent, and a tight stop about 1.25 percent below entry. Target is about 0.5 percent above entry, so payoff is small but the downside is contained. → r2 medium (+0) Liquidity 151.5m and ATR 1.05% contain range, and the stop is tight at 1.25%. Target only 0.5% above entry, so payoff is small. Medium risk, conviction held.
- **conservative**: r1 medium (+0) ATR 1.05% is low, but traded value 151.5m is thin versus peers. Stop 653.77 sits only about 1.25% below entry 662.07, so whipsaw is possible. → r2 medium (+0) ATR 1.05% is low, but traded value 151.5m is thin versus peers. Stop 653.77 sits about 1.25% below entry, so whipsaw is possible. Target is only about 0.5% above entry. Medium risk, no adjustment, consistent with round-1 views.
- Consensus (median): risk **medium**, conviction after risk **medium**

## 5. Portfolio Manager
- Final **up / medium**, flag caution. EPS up 50.9%, calm volatility and positive news support the up call. The weak market (political tension, profit-taking) is a headwind for a mean-reversion setup.
- Expected 5-day move +0.50%, hybrid score +0.375
