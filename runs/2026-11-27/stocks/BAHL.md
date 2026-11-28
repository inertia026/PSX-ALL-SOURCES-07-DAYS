# BAHL: Bank AL Habib Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: COMMERCIAL BANKS · Close 169.89 · Rank 15/30

## 1. Analysts

### Market (Python, score +5)
- `M-BAHL-1` Close 169.89 is +3.0% from its 20-day average 164.87 (+0)
- `M-BAHL-2` Close is above 50-day average 154.50 (context only) (+0)
- `M-BAHL-3` 20-day average is above 50-day average (short-term trend up; context only) (+0)
- `M-BAHL-4` RSI(14) 72.9: stretched, such stocks lagged the next week in the backtest (-10)
- `M-BAHL-5` MACD histogram -0.15 (context only) (+0)
- `M-BAHL-6` 5-day return -0.0% vs market +0.2% (relative -0.2 pts) (+0)
- `M-BAHL-7` 20-day return +12.4% vs market +6.3% (relative +6.1 pts; context only) (+0)
- `M-BAHL-8` Daily range (ATR) 2.0% of price: calm; low-volatility stocks did best in the backtest (+15)
- `M-BAHL-9` 5-day volume is 0.68x the 20-day average (+0)
- `M-BAHL-10` Price sits at 70% of its 52-week range (131.95 to 186.44; context only) (+0)
- `M-BAHL-11` 20-day support 146.02, resistance 171.97 (+0)
- `M-BAHL-12` Dividend/bonus/rights adjustment on 2026-10-30 (x0.9774): earlier prices adjusted, so the ex-date drop is not counted as a fall (+0)

### Fundamentals (Python, score +0)
- `F-BAHL-1` P/E (TTM) 6.74 vs top-30 median 7.51 (cheaper by 10%) (+0)
- `F-BAHL-2` Latest annual EPS growth -23.1% (-10)
- `F-BAHL-3` Net margin 9.1% vs 8.3% a year earlier (+0)
- `F-BAHL-4` Q3 2026 EPS +39.4% vs same quarter last year (+10)
- `F-BAHL-5` 1-year price change +7.4% (+0)
- `F-BAHL-C1` catalyst: Announcement 2026-11-20: Disclosure of Interest by a Director CEO, or Executive of a listed company and their Spous

### News (agent) view: neutral
- `N-BAHL-1` [Bank AL Habib Executive Syed Anser Abbas Zaidi Reports Two Share Sales](https://news.google.com/rss/articles/CBMib0FVX3lxTE96UGVNSm0xNkJpQzRsVlhycktLLU5oOFYwRXZRZ2pqaFVqT2JjZEMycUZsYlppem5GNEo2QVZhMERzaktIT3FnaExDc3dmdC1hT0I5LXVXZkpWMmFYMTVicjJKN25rUUNFM1Z2UGNocw?oc=5): negative, low impact. Executive share sales are a mild signal; routine, older than 7 days and largely priced.

### Sentiment (agent): neutral (low)
- Single low-impact negative news item (N-BAHL-1); no social mentions. `N-BAHL-1`
- Flat five-day move (-0.01%) with weak volume (0.68) shows no clear crowd conviction. `FL-2`

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **strong** `F-BAHL-4` Q3 2026 EPS +39.4% vs same quarter last year → rebutted: *outweighed_by* by `M-BAHL-4` (counts 0.0)
- **weak** `M-BAHL-8` Daily range (ATR) 2.0% of price: calm; low-volatility stocks did best in the backtest (counts 1.0)
- **Bull total: 1.0**

### Bear: picks (rebuttals by Bull)
- **strong** `M-BAHL-4` RSI(14) 72.9: stretched, such stocks lagged the next week in the backtest → rebutted: *outweighed_by* by `F-BAHL-4` (counts 0.0)
- **moderate** `N-BAHL-1` News (low impact): Bank AL Habib Executive Syed Anser Abbas Zaidi Reports Two Share Sales (counts 2.0)
- **weak** `F-BAHL-2` Latest annual EPS growth -23.1% → rebutted: *not_5day_relevant* (counts 0.5)
- **Bear total: 2.5**

Net debate score **-1.5** → Python proposal: **flat / low**

## 3. Research Manager → Trader
- Decision **accept**: direction **flat**, conviction **low**. Strong RSI and EPS points cancel; small bear lean from insider sales does not justify a call.
- Q3 2026 EPS +39.4% vs same quarter last year `F-BAHL-4`
- RSI(14) 72.9: stretched, such stocks lagged the next week in the backtest `M-BAHL-4`
- News (low impact): Bank AL Habib Executive Syed Anser Abbas Zaidi Reports Two Share Sales `N-BAHL-1`
- Trader setup *avoid*; invalid if: Break above resistance 171.97 or drop below support 146.02 would end the flat call.
- Levels (Python, from ATR): entry ref 169.89, expected move pct 0.0, target 169.89

## 4. Risk debate
- **aggressive**: r1 low (+0) Flat call with zero expected move, so there is no growth for the plan to capture. Director disclosure is a minor catalyst. Liquidity of 78m is adequate. Risk low. Keep conviction. → r2 low (+0) Flat call with zero expected move, so there is no growth to capture. Director disclosure is minor and liquidity of 78.3M is adequate. Risk low, but nothing to buy. Keep conviction.
- **neutral**: r1 medium (+0) Flat call with low conviction and avoid setup. No expected move, so no edge either way. Director disclosure is minor. Liquidity 78.3M is adequate. Medium risk, keep conviction. → r2 medium (+0) Medium risk. Flat call with zero expected move gives no edge either way. Director dealing disclosure is minor and liquidity of 78.3M is adequate. Keep conviction, avoid.
- **conservative**: r1 medium (+0) Flat call on low conviction with ATR 1.97% and only a director dealing disclosure. No edge in the window. Liquidity is adequate. Stay out. → r2 medium (+0) Flat call, zero expected move, so no edge in the window. ATR 1.97%, traded value 78.3M is adequate, director dealing disclosure is minor. Medium risk, stay out. Cites F-BAHL-C1.
- Consensus (median): risk **medium**, conviction after risk **low**

## 5. Portfolio Manager
- Final **flat / low**, flag none. Strong EPS growth offset by stretched RSI 72.9 that lagged in backtest; no clear edge, stay flat.
- Expected 5-day move +0.00%, hybrid score +0.000
