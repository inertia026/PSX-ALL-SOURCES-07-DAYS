# PSEL: Pakistan Services Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: MISCELLANEOUS · Close 1153.46 · Rank 29/30

## 1. Analysts

### Market (Python, score -10)
- `M-PSEL-1` Close 1153.46 is -6.9% from its 20-day average 1239.44 (+0)
- `M-PSEL-2` Close is above 50-day average 1121.98 (context only) (+0)
- `M-PSEL-3` 20-day average is above 50-day average (short-term trend up; context only) (+0)
- `M-PSEL-4` RSI(14) 45.9 (+0)
- `M-PSEL-5` MACD histogram -24.55 (context only) (+0)
- `M-PSEL-6` 5-day return -7.7% vs market +0.2% (relative -7.9 pts) (+0)
- `M-PSEL-7` 20-day return +15.9% vs market +6.3% (relative +9.7 pts; context only) (+0)
- `M-PSEL-8` Daily range (ATR) 8.0% of price: very volatile; such stocks lagged in the backtest (-10)
- `M-PSEL-9` 5-day volume is 0.90x the 20-day average (+0)
- `M-PSEL-10` Price sits at 53% of its 52-week range (799.00 to 1470.00; context only) (+0)
- `M-PSEL-11` 20-day support 974.00, resistance 1470.00 (+0)

### Fundamentals (Python, score +15)
- `F-PSEL-1` P/E (TTM) 54.80 vs top-30 median 7.51 (dearer by 630%) (-10)
- `F-PSEL-2` Latest annual EPS growth +294.9% (+10)
- `F-PSEL-3` Net margin 2.8% vs -1.6% a year earlier (+5)
- `F-PSEL-4` Q3 2025 EPS +328.9% vs same quarter last year (+10)
- `F-PSEL-5` 1-year price change +13.5% (+0)
- `F-PSEL-C1` catalyst: Announcement 2026-11-20: Change in name of External Auditors

### News (agent) view: neutral
- `N-PSEL-1` [How the Hashwanis lost control of Pearl Continental](https://news.google.com/rss/articles/CBMinwFBVV95cUxQVVhIUEVmVG56czBsUGFzWG1LLUlYV2ZfcnNPYmJNeVhVZC1SdUhXWml6RUVqNzRiMklVMEdPMlNnVGtid2RpelJVMHFhNTU4VWMyU3dfcW5GelBiZ3ZJM0tTSWN3SDNzcm1jRUZmbURMQU15ZDBBMGQxX3gwdWQzWmJPSHowX0psZENQOGZxWXBubGJWYVFzVjZQbXh5Qm8?oc=5): neutral, low impact. Headline is about Pearl Continental ownership; not clearly about PSEL, so treated as name clash.
- `N-PSEL-2` [Pakistan Services Limited reports a change in its external auditors’ firm name](https://news.google.com/rss/articles/CBMib0FVX3lxTFBIcE1IZ29EOTA3N2lxVkVVa1hjZm15WmVTb2c3VzN6OTlJeC1jVEJMR1VpcThyU0F6Rl9NTzY5NmRkUFdXSE44cGVDWUlVZEg0R2laUWFGSGdYUXZGTm9WcmJBQjhpcjFPNmt2MzBmcw?oc=5): neutral, low impact. Routine change of external auditor firm name; administrative, no expected price effect.

### Sentiment (agent): bearish (low)
- Shares fell 7.71% over five days with no supportive news. `N-PSEL-1` `N-PSEL-2`
- Neutral low-impact news offers no offset to selling pressure. `N-PSEL-2`

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **moderate** `F-PSEL-3` Net margin 2.8% vs -1.6% a year earlier (counts 2.0)
- **weak** `F-PSEL-2` Latest annual EPS growth +294.9% → rebutted: *not_5day_relevant* (counts 0.5)
- **Bull total: 2.5**

### Bear: picks (rebuttals by Bull)
- **strong** `M-PSEL-8` Daily range (ATR) 8.0% of price: very volatile; such stocks lagged in the backtest (counts 3.0)
- **strong** `F-PSEL-1` P/E (TTM) 54.80 vs top-30 median 7.51 (dearer by 630%) → rebutted: *outweighed_by* by `F-PSEL-2` (counts 1.5)
- **moderate** `SENT-PSEL` Crowd mood bearish (low) (counts 2.0)
- **moderate** `MD-2` Macro: KSE-100 fell nearly 400 points on geopolitical concerns and volatile trade, adding near-term pressure. → rebutted: *outweighed_by* by `F-PSEL-2` (counts 1.0)
- **Bear total: 7.5**

Net debate score **-5.0** → Python proposal: **down / medium**

## 3. Research Manager → Trader
- Decision **accept**: direction **down**, conviction **medium**. Very high volatility and bearish crowd mood outweigh margin improvement.
- Net margin 2.8% vs -1.6% a year earlier `F-PSEL-3`
- Daily range (ATR) 8.0% of price: very volatile; such stocks lagged in the backtest `M-PSEL-8`
- Crowd mood bearish (low) `SENT-PSEL`
- Trader setup *avoid*; invalid if: Any upward close above sma20 would contradict the reduce call; a rebound above 1264.03 confirms it wrong.
- Levels (Python, from ATR): entry ref 1153.46, expected move pct -0.25, target 1150.58, stop 1264.03. Short selling is limited on PSX; a 'down' call means avoid/reduce.

## 4. Risk debate
- **aggressive**: r1 high (-1) Setup is avoid on a down call, with ATR 7.99% and traded value 8.6m below threshold. Short selling is limited on PSX, so the only useful action is avoid or reduce. → r2 high (-1) Round 2: Down call with ATR 7.99% and 8.6m traded value. Short selling is limited on PSX, so the only action is avoid or reduce.
- **neutral**: r1 high (-1) Avoid or reduce. Short selling is limited on PSX, ATR is about 8 percent, and traded value is thin. The down call carries high volatility with little tradable exit. → r2 high (-1) Agree. Down call means avoid or reduce since short selling is limited on PSX. ATR 7.99% is highest in batch and traded value 8.6m is below threshold.
- **conservative**: r1 high (-1) Traded value 8.6m is below threshold and ATR 7.99% is the highest in the batch. Down call means avoid or reduce, since short selling is limited on PSX. → r2 high (-1) Avoid or reduce. ATR 7.99% is the highest in the batch and traded value 8.6m is below threshold. Short selling is limited on PSX, so a down call leaves little tradable exit. Auditor announcement F-PSEL-C1 adds noise. Agree with all ...
- Consensus (median): risk **high**, conviction after risk **low**

## 5. Portfolio Manager
- Final **down / low**, flag caution. Bearish crowd mood and a very volatile stock (8% daily range) back the down call. Setup is avoid and risk is high, so conviction stays low.
- Expected 5-day move -0.25%, hybrid score -0.375
