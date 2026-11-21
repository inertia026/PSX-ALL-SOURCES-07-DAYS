# AKBL: Askari Bank Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: COMMERCIAL BANKS · Close 115.81 · Rank 24/30

## 1. Analysts

### Market (Python, score +35)
- `M-AKBL-1` Close 115.81 is above 20-day average 112.85 (+10)
- `M-AKBL-2` Close is above 50-day average 107.51 (+10)
- `M-AKBL-3` 20-day average is above 50-day average (short-term trend up) (+10)
- `M-AKBL-4` Close is above 200-day average 97.57 (+5)
- `M-AKBL-5` RSI(14) 57.9: positive momentum (+10)
- `M-AKBL-6` MACD histogram -0.22 (bearish crossover side) (-10)
- `M-AKBL-7` 5-day return -0.5% vs market -0.3% (relative -0.2 pts) (+0)
- `M-AKBL-8` 20-day return +12.5% vs market +8.2% (relative +4.3 pts) (+0)
- `M-AKBL-9` 5-day volume is 0.48x the 20-day average (+0)
- `M-AKBL-10` Price sits at 82% of its 52-week range (69.12 to 126.00) (+0)
- `M-AKBL-11` 20-day support 101.39, resistance 126.00 (+0)
- `M-AKBL-12` Dividend/bonus/rights adjustment on 2026-11-03 (x0.9815): earlier prices adjusted, so the ex-date drop is not counted as a fall (+0)

### Fundamentals (Python, score +5)
- `F-AKBL-1` P/E (TTM) 6.65 vs top-30 median 7.59 (cheaper by 12%) (+0)
- `F-AKBL-2` Latest annual EPS growth +8.4% (+0)
- `F-AKBL-3` Net margin 7.6% vs 5.2% a year earlier (+5)
- `F-AKBL-4` Q3 2026 EPS -3.5% vs same quarter last year (+0)
- `F-AKBL-5` 1-year price change +21.6% (+0)
- `F-AKBL-C1` catalyst: Board meeting notice (2026-11-18): results or payout may land in the window

### News (agent) view: none
- No company news in the last 14 days.

### Sentiment (agent): neutral (low)
- Market breadth negative over five days; foreign repatriation headline (FL-1). `FL-1`
- No news or social items; inputs are thin for this stock. _(no cite)_
- Five-day return -0.50% trails market -0.28% on low volume (0.48). _(no cite)_

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **moderate** `F-AKBL-3` Net margin 7.6% vs 5.2% a year earlier → rebutted: *not_5day_relevant* (counts 1.0)
- **moderate** `M-AKBL-3` 20-day average is above 50-day average (short-term trend up) (counts 2.0)
- **weak** `MD-1` Macro: KSE-100 closed up 610 points at 177,382, extending recovery; supportive for equity sentiment. (counts 1.0)
- **Bull total: 4.0**

### Bear: picks (rebuttals by Bull)
- **moderate** `M-AKBL-6` MACD histogram -0.22 (bearish crossover side) (counts 2.0)
- **weak** `F-AKBL-C1` Board meeting notice (2026-11-18): results or payout may land in the window → rebutted: *not_5day_relevant* (counts 0.5)
- **Bear total: 2.5**

Net debate score **+1.5** → Python proposal: **flat / low**

## 3. Research Manager → Trader
- Decision **accept**: direction **flat**, conviction **low**. Trend support and MACD weakness roughly offset; low-conviction flat is fair.
- 20-day average is above 50-day average (short-term trend up) `M-AKBL-3`
- MACD histogram -0.22 (bearish crossover side) `M-AKBL-6`
- Trader setup *avoid*; invalid if: Close above resistance 126.0 or below support 101.39 would invalidate the flat view.
- Levels (Python, from ATR): entry ref 115.81, expected move pct 0.0, target 115.81

## 4. Risk debate
- **aggressive**: r1 high (+0) Flat setup with zero expected move gives no upside to justify the risk. A board meeting may bring results or payout, a real but unpriced swing. Stay out. → r2 high (+0) Zero expected move gives no upside to justify risk. Board meeting may bring results or payout, a real unpriced swing. Stay out. Rating high.
- **neutral**: r1 medium (+0) Avoid setup with zero expected move. Board meeting may bring results or payout in the window, adding event uncertainty without a directional edge. Keep avoid. → r2 high (+0) Flat setup with zero expected move gives no edge. ATR 2.91% and a board meeting add event risk. Both other analysts also rate high. Keep avoid.
- **conservative**: r1 high (-1) Flat view with zero expected move and the highest ATR in the batch (2.91%). Board meeting may land in the window, adding results or payout risk. Avoid. → r2 high (-1) Flat view with zero expected move and the highest ATR in the batch (2.91%). Board meeting may bring results or payout in the window. Neutral's medium rating understates event risk. Keep high.
- Consensus (median): risk **high**, conviction after risk **low**

## 5. Portfolio Manager
- Final **flat / low**, flag none. Research flat, avoid setup, high risk, MACD bearish side. No edge.
- Expected 5-day move +0.00%, hybrid score +0.000
