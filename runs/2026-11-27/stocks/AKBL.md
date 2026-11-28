# AKBL: Askari Bank Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: COMMERCIAL BANKS · Close 116.82 · Rank 23/30

## 1. Analysts

### Market (Python, score +0)
- `M-AKBL-1` Close 116.82 is +0.9% from its 20-day average 115.80 (+0)
- `M-AKBL-2` Close is above 50-day average 108.87 (context only) (+0)
- `M-AKBL-3` 20-day average is above 50-day average (short-term trend up; context only) (+0)
- `M-AKBL-4` RSI(14) 57.6 (+0)
- `M-AKBL-5` MACD histogram -0.32 (context only) (+0)
- `M-AKBL-6` 5-day return +0.9% vs market +0.2% (relative +0.7 pts) (+0)
- `M-AKBL-7` 20-day return +8.9% vs market +6.3% (relative +2.7 pts; context only) (+0)
- `M-AKBL-8` Daily range (ATR) 2.5% of price: normal volatility (+0)
- `M-AKBL-9` 5-day volume is 0.34x the 20-day average (+0)
- `M-AKBL-10` Price sits at 84% of its 52-week range (69.12 to 126.00; context only) (+0)
- `M-AKBL-11` 20-day support 103.31, resistance 126.00 (+0)
- `M-AKBL-12` Dividend/bonus/rights adjustment on 2026-11-03 (x0.9815): earlier prices adjusted, so the ex-date drop is not counted as a fall (+0)

### Fundamentals (Python, score +5)
- `F-AKBL-1` P/E (TTM) 6.71 vs top-30 median 7.51 (cheaper by 11%) (+0)
- `F-AKBL-2` Latest annual EPS growth +8.4% (+0)
- `F-AKBL-3` Net margin 7.6% vs 5.2% a year earlier (+5)
- `F-AKBL-4` Q3 2026 EPS -3.5% vs same quarter last year (+0)
- `F-AKBL-5` 1-year price change +21.0% (+0)
- `F-AKBL-C1` catalyst: Announcement 2026-11-26: Disclosure of Material Information
- `F-AKBL-C2` catalyst: Board meeting notice (2026-11-18): results or payout may land in the window

### News (agent) view: neutral
- `N-AKBL-1` [Askari Bank Invests Rs. 1 Billion in Brokerage Business](https://news.google.com/rss/articles/CBMilAFBVV95cUxNVlVlU0V4MEF3U19Fa2lmZi01dUhjdF9tS0swcWdQMUxwUEo4VmkwN255TzJULXd5Umd0Q2ZiYVhtZFgtNkh4YnVSMVAwbkxjOTQ3WmNBOThESm1zYXlhb1pRUndqclVpNjF0YWtqT05nWHFnX0NjOUdGT01WOFZYS0FBYjRZVXhyQVo1Qk0xbXM4QWF00gGaAUFVX3lxTFBjbEEwZUdGMXQtRk5sMEhteDRrbVlQM2xnR3BLZ3BSWlZ1WEluMHVXWVNEY1BFNnR2N3dwQ3d0MFFEWC0takR3QS1TNTdPMlZjLVZxcTNIeDNMdHVSbFU1SThkQ1RUZDI0Zk0wZ1BqMUZud095THJLeTI1M1NJTml4dnlFZHVTaVlSYXVvR3A2aGVDME1HU21Hbmc?oc=5): neutral, low impact. Rs1bn brokerage investment is small relative to bank size; limited near-term earnings effect.
- `N-AKBL-2` [Askari Bank approves Rs1bn investment in Foundation Securities](https://news.google.com/rss/articles/CBMiqAFBVV95cUxNTThOVjJiR0tQT3p6YlhDTy05NkNlTl84RC1OWExBRlhiREpjcndRcWpzRzUxSGZRYmZ3VnNUOHdpamNxLUNoY2VkeEZmcGNlbTE5WDlaRDJoR1l5cWFMWVRrV0s4LW5zTUJyYUlPOGI1R1pHWE4zNmJWWDJBeE0zYkU1WlpmdkdlLXY2Q2kyd1BBS2hvbDdzSUNCTGdSNzVmMzZydzlBUlQ?oc=5): neutral, low impact. Same Rs1bn Foundation Securities investment restated; no new information for the next 5 days.

### Sentiment (agent): neutral (low)
- Both news items are low-impact and neutral; no social chatter to tilt sentiment. `N-AKBL-1` `N-AKBL-2`
- Five-day gain of 0.87% beats the market's 0.16%, but volume is thin (0.34 ratio). `N-AKBL-1`

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **moderate** `F-AKBL-3` Net margin 7.6% vs 5.2% a year earlier → rebutted: *not_5day_relevant* (counts 1.0)
- **weak** `F-AKBL-C2` Board meeting notice (2026-11-18): results or payout may land in the window (counts 1.0)
- **Bull total: 2.0**

### Bear: picks (rebuttals by Bull)
- **moderate** `F-AKBL-C1` Announcement 2026-11-26: Disclosure of Material Information (counts 2.0)
- **moderate** `MD-2` Macro: KSE-100 fell nearly 400 points on geopolitical concerns and volatile trade, adding near-term pressure. → rebutted: *stale* (counts 1.0)
- **weak** `MD-1` Macro: Political tensions and profit-taking pushed PSX below 178,000, making sentiment cautious into the next week. (counts 1.0)
- **Bear total: 4.0**

Net debate score **-2.0** → Python proposal: **down / low** (lowered one step: quant score disagrees)

## 3. Research Manager → Trader
- Decision **accept**: direction **down**, conviction **low**. Bear leads on material disclosure and cautious market; score is modest, low conviction fits.
- Announcement 2026-11-26: Disclosure of Material Information `F-AKBL-C1`
- Macro: Political tensions and profit-taking pushed PSX below 178,000, making sentiment cautious into the next week. `MD-1`
- Trader setup *avoid*; invalid if: Close above resistance 126.0 on rising volume would prove the downside call wrong.
- Levels (Python, from ATR): entry ref 116.82, expected move pct -0.25, target 116.53, stop 120.34. Short selling is limited on PSX; a 'down' call means avoid/reduce.

## 4. Risk debate
- **aggressive**: r1 high (+0) Down call with target 116.53 and no long case to chase. Board meeting notice may bring results or payout inside the window, a binary event. Risk high. Keep conviction. → r2 high (+0) Down call with no long case to chase. Board meeting in the window is a binary event on ATR 2.5 percent, so risk is high. Keep the avoid stance; do not short.
- **neutral**: r1 medium (+0) Avoid setup with low conviction and ATR 2.5%. Board-meeting and disclosure catalysts could move price either way, so risk is medium. Keep conviction. → r2 high (+0) High risk. Two of three analysts rate high. Low-conviction down call with a board meeting that may bring results or payout inside the window, a binary event at 2.5% ATR. Avoid.
- **conservative**: r1 high (-1) ATR 2.5% with a board meeting in the window and a down call on low conviction. Results or payout could gap the price. Avoid. → r2 high (-1) Down call on low conviction with ATR 2.5% and a board meeting that may bring results or payout inside the window. Binary gap risk. Avoid, reduce conviction. Cites F-AKBL-C1 and F-AKBL-C2.
- Consensus (median): risk **high**, conviction after risk **low**

## 5. Portfolio Manager
- Final **down / low**, flag caution. Weak quant score 1.0, high risk and cautious market; bearish call is low conviction with no company-specific catalyst.
- Expected 5-day move -0.25%, hybrid score -0.125
