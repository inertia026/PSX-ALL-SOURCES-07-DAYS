# BAHL: Bank AL Habib Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: COMMERCIAL BANKS · Close 169.9 · Rank 3/30

## 1. Analysts

### Market (Python, score +45)
- `M-BAHL-1` Close 169.90 is above 20-day average 159.46 (+10)
- `M-BAHL-2` Close is above 50-day average 152.45 (+10)
- `M-BAHL-3` 20-day average is above 50-day average (short-term trend up) (+10)
- `M-BAHL-4` Close is above 200-day average 158.34 (+5)
- `M-BAHL-5` RSI(14) 76.4: overbought, pullback risk (-10)
- `M-BAHL-6` MACD histogram +1.05 (bullish crossover side) (+10)
- `M-BAHL-7` 5-day return +1.5% vs market -0.3% (relative +1.8 pts) (+0)
- `M-BAHL-8` 20-day return +16.7% vs market +8.2% (relative +8.5 pts) (+10)
- `M-BAHL-9` 5-day volume is 0.67x the 20-day average (+0)
- `M-BAHL-10` Price sits at 70% of its 52-week range (131.95 to 186.44) (+0)
- `M-BAHL-11` 20-day support 143.67, resistance 171.97 (+0)
- `M-BAHL-12` Dividend/bonus/rights adjustment on 2026-10-30 (x0.9774): earlier prices adjusted, so the ex-date drop is not counted as a fall (+0)

### Fundamentals (Python, score +0)
- `F-BAHL-1` P/E (TTM) 6.74 vs top-30 median 7.59 (cheaper by 11%) (+0)
- `F-BAHL-2` Latest annual EPS growth -23.1% (-10)
- `F-BAHL-3` Net margin 9.1% vs 8.3% a year earlier (+0)
- `F-BAHL-4` Q3 2026 EPS +39.4% vs same quarter last year (+10)
- `F-BAHL-5` 1-year price change +6.5% (+0)
- `F-BAHL-C1` catalyst: Announcement 2026-11-20: Disclosure of Interest by a Director CEO, or Executive of a listed company and their Spous
- `F-BAHL-C2` catalyst: Announcement 2026-11-13: BAHL - Credit of 3rd Interim Cash Dividend

### News (agent) view: neutral
- `N-BAHL-1` [Bank AL Habib Executive Syed Anser Abbas Zaidi Reports Two Share Sales](https://news.google.com/rss/articles/CBMib0FVX3lxTE96UGVNSm0xNkJpQzRsVlhycktLLU5oOFYwRXZRZ2pqaFVqT2JjZEMycUZsYlppem5GNEo2QVZhMERzaktIT3FnaExDc3dmdC1hT0I5LXVXZkpWMmFYMTVicjJKN25rUUNFM1Z2UGNocw?oc=5): negative, low impact. Executive share sales are a minor negative signal; two sales, size not stated.
- `N-BAHL-2` [Bank AL Habib credits third interim cash dividend of Rs. 3.50 per share](https://news.google.com/rss/articles/CBMiakFVX3lxTE8zSWwwdUFDUHY5Tnc1aW94bm9iVHFNaDRXbW1tdTV3cGhTUXlQWXMxbi00LUxzazNTbXdYSjJZODVmSVJ5V1dJMHRocU5veFdKb1lXWm1nNnE4QWI1Y1RSd2g1NEVzUzBHNnc?oc=5): positive, low impact. Cash dividend Rs 3.50 credited 7 days ago; modest support, largely already in the price.

### Sentiment (agent): neutral (low)
- Five-day return +1.48% beats market -0.28%, but volume is light (0.67). _(no cite)_
- News split: one negative (N-BAHL-1) and one positive (N-BAHL-2), both low impact. `N-BAHL-1` `N-BAHL-2`
- No social posts to confirm the move. _(no cite)_

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **strong** `F-BAHL-4` Q3 2026 EPS +39.4% vs same quarter last year (counts 3.0)
- **moderate** `M-BAHL-8` 20-day return +16.7% vs market +8.2% (relative +8.5 pts) → rebutted: *stale* (counts 1.0)
- **weak** `M-BAHL-6` MACD histogram +1.05 (bullish crossover side) (counts 1.0)
- **Bull total: 5.0**

### Bear: picks (rebuttals by Bull)
- **strong** `M-BAHL-5` RSI(14) 76.4: overbought, pullback risk → rebutted: *outweighed_by* by `F-BAHL-4` (counts 0.0)
- **weak** `N-BAHL-1` News (low impact): Bank AL Habib Executive Syed Anser Abbas Zaidi Reports Two Share Sales → rebutted: *weak_signal* (counts 0.5)
- **Bear total: 0.5**

Net debate score **+4.5** → Python proposal: **up / medium**

## 3. Research Manager → Trader
- Decision **accept**: direction **up**, conviction **medium**. Strong Q3 EPS growth outweighs overbought RSI; medium conviction up is justified.
- Q3 2026 EPS +39.4% vs same quarter last year `F-BAHL-4`
- RSI(14) 76.4: overbought, pullback risk `M-BAHL-5`
- MACD histogram +1.05 (bullish crossover side) `M-BAHL-6`
- Trader setup *momentum*; invalid if: Close below stop 165.53 or failure at 171.97 resistance invalidates the call.
- Levels (Python, from ATR): entry ref 169.9, expected move pct 2.39, target 173.97, stop 165.53

## 4. Risk debate
- **aggressive**: r1 medium (+0) Highest expected move of the batch at 2.39%, with medium conviction. Levels give roughly 1:1 reward to risk, so no raise is justified. Director dealing and dividend credit are minor. → r2 medium (+0) Expected move 2.39% beats ATR 2.14%, but levels are roughly 1:1, so no raise is earned. Director dealing and dividend credit are minor. Hold conviction.
- **neutral**: r1 medium (+0) Momentum up with target 173.97 (about +2.4%) against stop 165.53 (about -2.6%), roughly 1:1. Dividend credit and director disclosure are neutral to slightly supportive. Keep conviction. → r2 medium (+0) Target 173.97 (about +2.4%) against stop 165.53 (about -2.6%) is roughly 1:1 with medium conviction. Director dealing and dividend credit are neutral. Keep conviction.
- **conservative**: r1 medium (+0) Medium conviction with 2.39% expected move against 2.14% ATR. Stop 165.53 is about 2.6% below entry. Director dealing and dividend credit are neutral. Liquidity adequate. → r2 medium (+0) Expected move 2.39% against ATR 2.14%, with stop about 2.6% below entry. Reward-to-risk is roughly 1:1, not favorable enough to raise. Director dealing and dividend credit are neutral. Keep medium.
- Consensus (median): risk **medium**, conviction after risk **medium**

## 5. Portfolio Manager
- Final **up / medium**, flag caution. Strong quarterly EPS growth and bullish MACD, but RSI 76.4 overbought raises pullback risk within five days.
- Expected 5-day move +2.39%, hybrid score +1.794
