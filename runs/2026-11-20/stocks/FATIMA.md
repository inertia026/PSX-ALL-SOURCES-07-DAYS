# FATIMA: Fatima Fertilizer Company Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: FERTILIZER · Close 145.25 · Rank 29/30

## 1. Analysts

### Market (Python, score +25)
- `M-FATIMA-1` Close 145.25 is above 20-day average 142.58 (+10)
- `M-FATIMA-2` Close is above 50-day average 142.45 (+10)
- `M-FATIMA-3` 20-day average is above 50-day average (short-term trend up) (+10)
- `M-FATIMA-4` Close is below 200-day average 147.44 (-5)
- `M-FATIMA-5` RSI(14) 52.1: neutral momentum (+0)
- `M-FATIMA-6` MACD histogram +0.37 (bullish crossover side) (+10)
- `M-FATIMA-7` 5-day return -5.0% vs market -0.3% (relative -4.7 pts) (-10)
- `M-FATIMA-8` 20-day return +8.4% vs market +8.2% (relative +0.2 pts) (+0)
- `M-FATIMA-9` 5-day volume is 1.35x the 20-day average (+0)
- `M-FATIMA-10` Price sits at 38% of its 52-week range (118.84 to 189.20) (+0)
- `M-FATIMA-11` 20-day support 131.00, resistance 157.00 (+0)

### Fundamentals (Python, score -25)
- `F-FATIMA-1` P/E (TTM) 12.62 vs top-30 median 7.59 (dearer by 66%) (-10)
- `F-FATIMA-2` Latest annual EPS growth -12.9% (-10)
- `F-FATIMA-3` Net margin 17.9% vs 14.7% a year earlier (+5)
- `F-FATIMA-4` Q3 2026 EPS -25.6% vs same quarter last year (-10)
- `F-FATIMA-5` 1-year price change +7.5% (+0)
- `F-FATIMA-C1` catalyst: Announcement 2026-11-16: Material Information

### News (agent) view: neutral
- `N-FATIMA-1` [Fatima Fertilizer : Material Information](https://news.google.com/rss/articles/CBMilgFBVV95cUxOVElBUHZLNWxJT0ZyeU5KVDc1UmVWSFA3aGNUOTNEVkVjUmRfQWpfNlA2ZExKWjdoVm5iaV9JeVFJTTNGcGN0eXdiSV81VVpvVUNfbThXT1lwaHVfNWliTDZlZGltOFVXSTFHanV5VV9OU1B3Qzk3TFdVc2Nvd2Z0UE9NMjBYSXRTWGlxU3lFQlJoS29haFE?oc=5): neutral, low impact. Generic material-information notice with no stated financial content; routine.
- `N-FATIMA-2` [Fatima Fertilizer reports copper and gold mineralisation at National Resources’ Chagai project](https://news.google.com/rss/articles/CBMibEFVX3lxTE5UY1h6MkwtU0lRanh3YTlLbVhYNTJOQ1ZhMTl5VVlWNldoWUVrdF9nazZiWFdYZW5wUjdfUEFmWm85MnRhcGNoSzkwR2FOZXF5dFZlYXZZVmZPUWxWNUJld2tUYXQtNzQtZHREdA?oc=5): positive, low impact. Mineral find at Chagai project; Fatima's stake and scale unclear, so limited near-term impact.

### Sentiment (agent): bearish (low)
- News is low-impact and mixed, offering no clear positive catalyst. `N-FATIMA-1` `N-FATIMA-2`
- Shares fell about 5% on 1.35x average volume, indicating active selling pressure. _(no cite)_
- No social posts; weak market breadth adds to the cautious tone. _(no cite)_

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **moderate** `M-FATIMA-1` Close 145.25 is above 20-day average 142.58 (counts 2.0)
- **weak** `M-FATIMA-6` MACD histogram +0.37 (bullish crossover side) → rebutted: *weak_signal* (counts 0.5)
- **Bull total: 2.5**

### Bear: picks (rebuttals by Bull)
- **strong** `M-FATIMA-7` 5-day return -5.0% vs market -0.3% (relative -4.7 pts) (counts 3.0)
- **moderate** `F-FATIMA-4` Q3 2026 EPS -25.6% vs same quarter last year → rebutted: *stale* (counts 1.0)
- **weak** `M-FATIMA-4` Close is below 200-day average 147.44 → rebutted: *weak_signal* (counts 0.5)
- **Bear total: 4.5**

Net debate score **-2.0** → Python proposal: **down / low** (lowered one step: quant score disagrees)

## 3. Research Manager → Trader
- Decision **accept**: direction **down**, conviction **low**. Sharp relative 5-day underperformance leads; close above 20-day average limits the margin, so low conviction fits.
- Close 145.25 is above 20-day average 142.58 `M-FATIMA-1`
- 5-day return -5.0% vs market -0.3% (relative -4.7 pts) `M-FATIMA-7`
- Trader setup *avoid*; invalid if: Stock is down with material announcement; a close above 157 resistance would prove the downside call wrong.
- Levels (Python, from ATR): entry ref 145.25, expected move pct -1.95, target 142.42, stop 151.6. Short selling is limited on PSX; a 'down' call means avoid/reduce.

## 4. Risk debate
- **aggressive**: r1 high (-1) Avoid call with low conviction, ATR 3.64%, and thin liquidity at 153.4m. Material announcement 2026-11-16 is unexplained in the data. Downside risk is high for any holder. → r2 high (-1) Agree with avoid. Material announcement 2026-11-16 (F-FATIMA-C1), ATR 3.64 and thinnest liquidity at 153M PKR make event risk high. Short selling is limited, so there is no clean upside here for holders.
- **neutral**: r1 high (-1) Avoid setup with material announcement and ATR 3.6%, the highest volatility here. Liquidity thinnest at 153M PKR. Downside call with low conviction; high risk for any long exposure. Lower conviction. → r2 high (-1) Material announcement 2026-11-16 (F-FATIMA-C1) with ATR 3.64 and thinnest liquidity at 153M supports high risk. Low conviction downside call; avoid stance. Lower conviction, consistent with the other two.
- **conservative**: r1 high (-1) Highest ATR at 3.64 with thinner liquidity of 153.4M. Material announcement on 2026-11-16 adds event risk. Low conviction and PSX short limits make avoid the safer stance. → r2 high (-1) Agree with high risk. Material announcement 2026-11-16 adds event risk, ATR is highest at 3.64, and liquidity is thinnest at 153M PKR. Low conviction on an avoid call supports the downgrade.
- Consensus (median): risk **high**, conviction after risk **low**

## 5. Portfolio Manager
- Final **down / low**, flag caution. Weak relative return and bearish sentiment favor downside, but price still above 20-day average and risk is high.
- Expected 5-day move -1.95%, hybrid score -0.975
