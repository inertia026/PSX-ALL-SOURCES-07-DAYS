# HMB: Habib Metropolitan Bank Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: COMMERCIAL BANKS · Close 104.0 · Rank 20/30

## 1. Analysts

### Market (Python, score +15)
- `M-HMB-1` Close 104.00 is +2.4% from its 20-day average 101.57 (+0)
- `M-HMB-2` Close is above 50-day average 97.00 (context only) (+0)
- `M-HMB-3` 20-day average is above 50-day average (short-term trend up; context only) (+0)
- `M-HMB-4` RSI(14) 67.7 (+0)
- `M-HMB-5` MACD histogram +0.01 (context only) (+0)
- `M-HMB-6` 5-day return +0.1% vs market +0.2% (relative -0.1 pts) (+0)
- `M-HMB-7` 20-day return +10.9% vs market +6.3% (relative +4.6 pts; context only) (+0)
- `M-HMB-8` Daily range (ATR) 2.0% of price: calm; low-volatility stocks did best in the backtest (+15)
- `M-HMB-9` 5-day volume is 0.64x the 20-day average (+0)
- `M-HMB-10` Price sits at 47% of its 52-week range (91.57 to 117.95; context only) (+0)
- `M-HMB-11` 20-day support 93.50, resistance 106.00 (+0)
- `M-HMB-12` Dividend/bonus/rights adjustment on 2026-11-02 (x0.9741): earlier prices adjusted, so the ex-date drop is not counted as a fall (+0)

### Fundamentals (Python, score +0)
- `F-HMB-1` P/E (TTM) 5.72 vs top-30 median 7.51 (cheaper by 24%) (+15)
- `F-HMB-2` Latest annual EPS growth -8.5% (-10)
- `F-HMB-3` Net margin 14.2% vs 10.5% a year earlier (+5)
- `F-HMB-4` Q3 2026 EPS -20.9% vs same quarter last year (-10)
- `F-HMB-5` 1-year price change +8.1% (+0)

### News (agent) view: none
- No company news in the last 14 days.

### Sentiment (agent): neutral (low)
- No stock news and a lagging five-day return give no positive crowd signal. `FL-1`
- Negative foreign sentiment backdrop offers no offsetting catalyst. `FL-1`

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **moderate** `F-HMB-3` Net margin 14.2% vs 10.5% a year earlier → rebutted: *not_5day_relevant* (counts 1.0)
- **moderate** `F-HMB-1` P/E (TTM) 5.72 vs top-30 median 7.51 (cheaper by 24%) → rebutted: *outweighed_by* by `F-HMB-4` (counts 0.0)
- **weak** `M-HMB-8` Daily range (ATR) 2.0% of price: calm; low-volatility stocks did best in the backtest (counts 1.0)
- **Bull total: 2.0**

### Bear: picks (rebuttals by Bull)
- **moderate** `F-HMB-4` Q3 2026 EPS -20.9% vs same quarter last year (counts 2.0)
- **moderate** `MD-2` Macro: KSE-100 fell nearly 400 points on geopolitical concerns and volatile trade, adding near-term pressure. (counts 2.0)
- **weak** `MD-1` Macro: Political tensions and profit-taking pushed PSX below 178,000, making sentiment cautious into the next week. (counts 1.0)
- **Bear total: 5.0**

Net debate score **-3.0** → Python proposal: **down / low** (lowered one step: quant score disagrees)

## 3. Research Manager → Trader
- Decision **accept**: direction **down**, conviction **low**. Q3 EPS decline and market drop outweigh the cheap P/E. Low conviction fits.
- Q3 2026 EPS -20.9% vs same quarter last year `F-HMB-4`
- Macro: KSE-100 fell nearly 400 points on geopolitical concerns and volatile trade, adding near-term pressure. `MD-2`
- Trader setup *avoid*; invalid if: A close above resistance20 106.0 with rising turnover would contradict the down call.
- Levels (Python, from ATR): entry ref 104.0, expected move pct -0.25, target 103.74, stop 106.44. Short selling is limited on PSX; a 'down' call means avoid/reduce.

## 4. Risk debate
- **aggressive**: r1 medium (-1) Thin liquidity at about 22 PKR m a day, with a 1.95% ATR against a -0.25% expected move, means noise dominates. Down call is weak; avoid it. → r2 high (-1) Conservative and neutral are right that 22.4M PKR daily traded value makes fills and exits slip. Thin liquidity is a real risk, so I raise the rating to high. Keep avoid.
- **neutral**: r1 medium (+0) Avoid plan on a down call with a -0.25% expected move and low conviction. Traded value of only 22.4M PKR makes exits and fills harder. Thin liquidity raises execution risk. Keep avoid. → r2 medium (-1) Down call with thin 22.4M PKR daily traded value raises fill and exit slippage against a -0.25% expected move. Aggressive and conservative both lower conviction, so I agree. Keep avoid.
- **conservative**: r1 high (-1) Down call, low conviction, ATR 1.95%, and average traded value only 22.4M PKR, which is thin liquidity. Exit or entry fills could slip. Avoid stance is correct; lower conviction further. → r2 high (-1) Down call with thin liquidity at 22.4M PKR and ATR 1.95%. Fills and exits could slip. Lower conviction further and keep the avoid stance.
- Consensus (median): risk **high**, conviction after risk **low**

## 5. Portfolio Manager
- Final **down / low**, flag none. EPS fell 20.9% year on year and the market is weak. Risk is high, and conviction is already at the floor.
- Expected 5-day move -0.25%, hybrid score -0.125
