# HBL: Habib Bank Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: COMMERCIAL BANKS · Close 304.12 · Rank 27/30

## 1. Analysts

### Market (Python, score +15)
- `M-HBL-1` Close 304.12 is +0.6% from its 20-day average 302.36 (+0)
- `M-HBL-2` Close is above 50-day average 294.70 (context only) (+0)
- `M-HBL-3` 20-day average is above 50-day average (short-term trend up; context only) (+0)
- `M-HBL-4` RSI(14) 56.8 (+0)
- `M-HBL-5` MACD histogram -0.40 (context only) (+0)
- `M-HBL-6` 5-day return +0.2% vs market +0.2% (relative +0.1 pts) (+0)
- `M-HBL-7` 20-day return +5.3% vs market +6.3% (relative -1.0 pts; context only) (+0)
- `M-HBL-8` Daily range (ATR) 1.7% of price: calm; low-volatility stocks did best in the backtest (+15)
- `M-HBL-9` 5-day volume is 0.36x the 20-day average (+0)
- `M-HBL-10` Price sits at 69% of its 52-week range (222.11 to 340.93; context only) (+0)
- `M-HBL-11` 20-day support 282.10, resistance 318.99 (+0)
- `M-HBL-12` Dividend/bonus/rights adjustment on 2026-11-02 (x0.9794): earlier prices adjusted, so the ex-date drop is not counted as a fall (+0)

### Fundamentals (Python, score +5)
- `F-HBL-1` P/E (TTM) 6.68 vs top-30 median 7.51 (cheaper by 11%) (+0)
- `F-HBL-2` Latest annual EPS growth +10.1% (+0)
- `F-HBL-3` Net margin 9.8% vs 7.4% a year earlier (+5)
- `F-HBL-4` Q3 2026 EPS +13.5% vs same quarter last year (+0)
- `F-HBL-5` 1-year price change +0.6% (+0)

### News (agent) view: positive
- `N-HBL-1` [Govt to support HBL in expanding trade links with four countries](https://news.google.com/rss/articles/CBMiUEFVX3lxTE55OGJpTTJUVWRvMnNfUzNtV1BVcWs2N2E2ODhtVjB0dC1jYUM2TVZJVVVrUkZaWXFZenhfSlZSenpIc0FuNnRCNGEyaFFiNzJs0gFWQVVfeXFMTTB1cFZXTXlfUWFVRHVKOEE2RHlkaXdQYzlDTjE2S2tTZDh1ejFyQ3REbEd4QXNoay0tcjFOMkhwYWpjTmZMUWZtZG1pV3JqQkpJb2ViQWc?oc=5): positive, low impact. Government support for expanding trade links with four countries is a modest, indirect positive for HBL.
- `N-HBL-2` [HBL, UBL, Meezan Bank Among Biggest Winners From SBP’s New Deposit Rule](https://news.google.com/rss/articles/CBMimgFBVV95cUxNTlJwMExxMlVpWEFoMXZseGtwY3Z2UzNlWDBrN1o0QlpzVTEyNlpvTUZoUlBPOV9RdGpMOXZXOVhneVI4Ny1OSVk5RE9ma2s5OXFoaG9qMG1EejNWNk1pVnhZS29aZWZMSkcxa091TXpsbUQ3MU1aRkU5RllrZWFCeTJMRS1yQ2JDQ1dadTNpX1JkLUhOTy1ZdUR3?oc=5): positive, low impact. Named a winner from the SBP deposit rule, but dated 11-16 and likely already priced in.

### Sentiment (agent): bullish (low)
- Two low-impact positive news tones support a constructive crowd view. `N-HBL-1` `N-HBL-2`
- Foreign confidence turned negative, tempering the positive tone; volume is light. `FL-1`

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **moderate** `F-HBL-3` Net margin 9.8% vs 7.4% a year earlier → rebutted: *not_5day_relevant* (counts 1.0)
- **weak** `N-HBL-2` News (low impact): HBL, UBL, Meezan Bank Among Biggest Winners From SBP’s New Deposit Rule → rebutted: *weak_signal* (counts 0.5)
- **weak** `M-HBL-8` Daily range (ATR) 1.7% of price: calm; low-volatility stocks did best in the backtest (counts 1.0)
- **Bull total: 2.5**

### Bear: picks (rebuttals by Bull)
- **moderate** `MD-2` Macro: KSE-100 fell nearly 400 points on geopolitical concerns and volatile trade, adding near-term pressure. (counts 2.0)
- **moderate** `MD-1` Macro: Political tensions and profit-taking pushed PSX below 178,000, making sentiment cautious into the next week. (counts 2.0)
- **weak** `MD-5` Macro: IMF seeking over 100 changes to the sovereign wealth fund law is a governance overhang with uncertain timing. → rebutted: *not_5day_relevant* (counts 0.5)
- **Bear total: 4.5**

Net debate score **-2.0** → Python proposal: **down / low** (lowered one step: quant score disagrees)

## 3. Research Manager → Trader
- Decision **accept**: direction **down**, conviction **low**. Bear leads on market weakness; bull points are weak or not 5-day relevant. Low conviction fits.
- Macro: Political tensions and profit-taking pushed PSX below 178,000, making sentiment cautious into the next week. `MD-1`
- Macro: KSE-100 fell nearly 400 points on geopolitical concerns and volatile trade, adding near-term pressure. `MD-2`
- Trader setup *avoid*; invalid if: Recovery above resistance20 318.99 on rising volume would invalidate the down call.
- Levels (Python, from ATR): entry ref 304.12, expected move pct -0.25, target 303.36, stop 310.48. Short selling is limited on PSX; a 'down' call means avoid/reduce.

## 4. Risk debate
- **aggressive**: r1 low (-1) Down call gives no long edge and PSX short selling is limited, so the plan is simply to stay out. The -0.25% expected move is too small to act on. → r2 low (-1) Down call has no long edge and a -0.25% expected move is too small to act on. Keep avoid. Risk stays low because there is no position to lose.
- **neutral**: r1 low (+0) Avoid plan with low conviction and a tiny expected move of -0.25%. Short selling is limited on PSX, so the down call adds little. Liquid with ATR 1.74%, so risk is contained. Keep avoid. → r2 low (+0) Down call with a -0.25% expected move and low conviction gives no long edge, and short selling is limited on PSX. Avoid is right; ATR 1.74% is contained in a liquid name. Keep avoid.
- **conservative**: r1 low (+0) Down call with low conviction and ATR 1.74%. Plan is avoid, so exposure is minimal. Recovery above 318.99 on volume invalidates. Recent ex-dividend 2026-11-02 adds noise. → r2 low (+0) Down call, low conviction, ATR 1.74%, liquid. Avoid plan keeps exposure minimal. Expected move -0.25% is too small to trade. Recovery above 318.99 invalidates.
- Consensus (median): risk **low**, conviction after risk **low**

## 5. Portfolio Manager
- Final **down / low**, flag caution. Research says down, but news is positive and sentiment bullish; weak market pressure supports a low-conviction downside only.
- Expected 5-day move -0.25%, hybrid score -0.250
