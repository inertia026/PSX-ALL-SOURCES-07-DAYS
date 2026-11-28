# MARI: Mari Energies Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: OIL & GAS EXPLORATION COMPANIES · Close 717.89 · Rank 4/30

## 1. Analysts

### Market (Python, score +15)
- `M-MARI-1` Close 717.89 is +3.5% from its 20-day average 693.37 (+0)
- `M-MARI-2` Close is above 50-day average 658.46 (context only) (+0)
- `M-MARI-3` 20-day average is above 50-day average (short-term trend up; context only) (+0)
- `M-MARI-4` RSI(14) 66.2 (+0)
- `M-MARI-5` MACD histogram +0.87 (context only) (+0)
- `M-MARI-6` 5-day return -0.1% vs market +0.2% (relative -0.2 pts) (+0)
- `M-MARI-7` 20-day return +12.8% vs market +6.3% (relative +6.6 pts; context only) (+0)
- `M-MARI-8` Daily range (ATR) 2.2% of price: calm; low-volatility stocks did best in the backtest (+15)
- `M-MARI-9` 5-day volume is 0.33x the 20-day average (+0)
- `M-MARI-10` Price sits at 81% of its 52-week range (528.91 to 761.90; context only) (+0)
- `M-MARI-11` 20-day support 629.01, resistance 761.90 (+0)

### Fundamentals (Python, score +15)
- `F-MARI-1` P/E (TTM) 9.25 vs top-30 median 7.51 (dearer by 23%) (-10)
- `F-MARI-2` Latest annual EPS growth +33.7% (+10)
- `F-MARI-3` Net margin 45.4% vs 36.8% a year earlier (+5)
- `F-MARI-4` Q1 2027 EPS +39.1% vs same quarter last year (+10)
- `F-MARI-5` 1-year price change +1.6% (+0)

### News (agent) view: positive
- `N-MARI-1` [Mari Energies Announces Major Copper-Gold Discovery in Balochistan](https://news.google.com/rss/articles/CBMilwFBVV95cUxNTTNBdWg2c253Y0Y4dVdfSHdtRmdzYXJiaE1MQnJaMmlReGpPZWFROVlyVGNkeGxpa0ItdWgxdGNmT3lDUjVRVWVneTBabVhreXdMeTV1ZXRDUzBhdk9YbWJZOUlPeWxhTS1sMGNvRl9IUE85My1hSTdvNnU1N3RmTUxQazlzYnFkOFJ5ZW00UjlmcFBDN0lv?oc=5): positive, low impact. Positive discovery claim, but 8 days old and likely partly priced in.

### Sentiment (agent): neutral (low)
- One low-impact positive news item, while the price is flat over five days. `N-MARI-1`
- Volume ratio of 0.33 shows thin crowd participation. `N-MARI-1`

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **strong** `F-MARI-4` Q1 2027 EPS +39.1% vs same quarter last year (counts 3.0)
- **moderate** `M-MARI-8` Daily range (ATR) 2.2% of price: calm; low-volatility stocks did best in the backtest (counts 2.0)
- **weak** `N-MARI-1` News (low impact): Mari Energies Announces Major Copper-Gold Discovery in Balochistan → rebutted: *weak_signal* (counts 0.5)
- **Bull total: 5.5**

### Bear: picks (rebuttals by Bull)
- **moderate** `F-MARI-1` P/E (TTM) 9.25 vs top-30 median 7.51 (dearer by 23%) → rebutted: *outweighed_by* by `F-MARI-4` (counts 0.0)
- **moderate** `MD-2` Macro: KSE-100 fell nearly 400 points on geopolitical concerns and volatile trade, adding near-term pressure. → rebutted: *outweighed_by* by `F-MARI-4` (counts 0.0)
- **Bear total: 0.0**

Net debate score **+5.5** → Python proposal: **up / medium**

## 3. Research Manager → Trader
- Decision **accept**: direction **up**, conviction **medium**. Strong EPS growth and calm volatility; bear points fully rebutted.
- Q1 2027 EPS +39.1% vs same quarter last year `F-MARI-4`
- Daily range (ATR) 2.2% of price: calm; low-volatility stocks did best in the backtest `M-MARI-8`
- Trader setup *momentum*; invalid if: Close below stop 698.71 or loss of sma20 near 693.37 on volume.
- Levels (Python, from ATR): entry ref 717.89, expected move pct 0.25, target 719.68, stop 698.71

## 4. Risk debate
- **aggressive**: r1 medium (+0) Liquid at 1447.9m with a momentum setup, but target 721.48 is only 0.5% above entry while stop is about 2.7% below. Reward-to-risk is poor, so hold risk at medium. → r2 medium (-1) Round 2: Liquid at 1447.9m, but the plan is lopsided. Target is 0.5% above entry against a 2.7% stop, so reward-to-risk is about 0.2. Momentum needs a break above target.
- **neutral**: r1 medium (-1) Liquid, but the plan is lopsided. Target 721.48 is only about 0.5 percent above entry while stop 698.71 is about 2.7 percent below. Momentum setup needs a break above target to pay. → r2 medium (-1) Liquid at 1447.9m, but target 0.5% above entry against a 2.7% stop is lopsided. Momentum needs a break above target. Medium risk, reduced conviction.
- **conservative**: r1 medium (+0) Liquidity is adequate at 1447.9m and ATR is 2.23%. Stop 698.71 sits about 2.7% below entry 717.89, so normal swings could trigger a stop-out. → r2 medium (-1) Liquidity is adequate at 1447.9m and ATR is 2.23%. Reward is lopsided: target 721.48 is about 0.5% above entry while stop 698.71 is about 2.7% below. Normal swings could stop it out. Downgrade conviction from the neutral view.
- Consensus (median): risk **medium**, conviction after risk **low**

## 5. Portfolio Manager
- Final **up / low**, flag none. EPS growth of 39% and positive news with a calm daily range support the up call. Risk is medium and sentiment neutral, so conviction stays low.
- Expected 5-day move +0.25%, hybrid score +0.188
