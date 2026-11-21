# DGKC: D.G. Khan Cement Company Limited

> **Not financial advice.** This is an automated research experiment. It can be wrong, uses free data that may be incomplete, and says nothing about your own situation.

Sector: CEMENT · Close 204.0 · Rank 14/30

## 1. Analysts

### Market (Python, score +65)
- `M-DGKC-1` Close 204.00 is above 20-day average 194.75 (+10)
- `M-DGKC-2` Close is above 50-day average 190.32 (+10)
- `M-DGKC-3` 20-day average is above 50-day average (short-term trend up) (+10)
- `M-DGKC-4` Close is above 200-day average 195.63 (+5)
- `M-DGKC-5` RSI(14) 60.5: positive momentum (+10)
- `M-DGKC-6` MACD histogram +0.67 (bullish crossover side) (+10)
- `M-DGKC-7` 5-day return -0.0% vs market -0.3% (relative +0.2 pts) (+0)
- `M-DGKC-8` 20-day return +14.5% vs market +8.2% (relative +6.3 pts) (+10)
- `M-DGKC-9` 5-day volume is 0.73x the 20-day average (+0)
- `M-DGKC-10` Price sits at 54% of its 52-week range (144.30 to 254.59) (+0)
- `M-DGKC-11` 20-day support 173.15, resistance 215.31 (+0)

### Fundamentals (Python, score +15)
- `F-DGKC-1` P/E (TTM) 7.71 vs top-30 median 7.59 (dearer by 2%) (+0)
- `F-DGKC-2` Latest annual EPS growth +31.7% (+10)
- `F-DGKC-3` Net margin 14.4% vs 12.1% a year earlier (+5)
- `F-DGKC-4` Q1 2027 EPS +7.5% vs same quarter last year (+0)
- `F-DGKC-5` 1-year price change +8.3% (+0)
- `F-DGKC-C1` catalyst: Announcement 2026-11-16: CHANGE OFOF EXTERNAL AUDITORSNAME

### News (agent) view: neutral
- `N-DGKC-1` [D.G. Khan Cement changes the name of its external audit firm](https://news.google.com/rss/articles/CBMib0FVX3lxTE9rdU1WVkd1cFNXdEJEWVdYNDA2OXNwYzViSEplbXo2RGxhMlg2RzN4ZXUwYUdYR3ljR1p1Z2x1WV9HaU4wRlNpckxuWnNzUGx4NWxHZXN0U0QzT3I5aDJkQWJtNGpaQTFGanA5WGlmOA?oc=5): neutral, low impact. Routine change of external audit firm name; no effect on fundamentals.
- `N-DGKC-2` [D.G. Khan Cement director reports purchase of 25,000 shares](https://news.google.com/rss/articles/CBMiakFVX3lxTE1JQzJueGdqZmtNYVB2b0RBbHZ6cjNyU3FYS25lc0VjQWl1TWprc0FvREgxZGpTbDEwWUFDMUk0UkVNMGxSMHFVdXQzZXFIeF8yN0RiLVhkQjBYc3Q5RnRLeTdram1NOFA4MFE?oc=5): positive, low impact. Director bought 25,000 shares, a mild confidence signal, but 10 days old.

### Sentiment (agent): neutral (low)
- Mixed news: one neutral and one positive item, both low impact. `N-DGKC-1` `N-DGKC-2`
- Price flat over 5 days, in line with a soft market. _(no cite)_
- Weak flow headlines and no social chatter leave no clear direction. `FL-1`

## 2. Bull vs Bear (structured: agents pick evidence, Python scores)

### Bull: picks (rebuttals by Bear)
- **strong** `M-DGKC-8` 20-day return +14.5% vs market +8.2% (relative +6.3 pts) → rebutted: *stale* (counts 1.5)
- **moderate** `N-DGKC-2` News (low impact): D.G. Khan Cement director reports purchase of 25,000 shares → rebutted: *weak_signal* (counts 1.0)
- **moderate** `M-DGKC-1` Close 204.00 is above 20-day average 194.75 (counts 2.0)
- **Bull total: 4.5**

### Bear: picks (rebuttals by Bull)
- **moderate** `F-DGKC-C1` Announcement 2026-11-16: CHANGE OFOF EXTERNAL AUDITORSNAME → rebutted: *not_5day_relevant* (counts 1.0)
- **weak** `MD-4` Macro: Foreign investors repatriated $1.16 billion from Pakistan in July-October FY27, weighing on external flows. → rebutted: *stale* (counts 0.5)
- **Bear total: 1.5**

Net debate score **+3.0** → Python proposal: **up / low**

## 3. Research Manager → Trader
- Decision **accept**: direction **up**, conviction **low**. Close above 20-day average supports up; other bull evidence is stale or weak, so low conviction fits.
- Announcement 2026-11-16: CHANGE OFOF EXTERNAL AUDITORSNAME `F-DGKC-C1`
- Close 204.00 is above 20-day average 194.75 `M-DGKC-1`
- 20-day return +14.5% vs market +8.2% (relative +6.3 pts) `M-DGKC-8`
- Trader setup *momentum*; invalid if: Close below 20-day average 194.75 or stop 197.14 breaks the momentum call.
- Levels (Python, from ATR): entry ref 204.0, expected move pct 1.57, target 207.19, stop 197.14

## 4. Risk debate
- **aggressive**: r1 high (-1) Momentum call has a 3.4% stop against a 1.6% target, which is a poor payoff. Auditor change is a governance flag. Liquidity is strong, but the upside does not justify the volatility. → r2 high (-1) Agree with round 1. A 3.4% stop against a 1.6% target is a poor payoff, and the auditor change is a governance flag. Liquidity is strong, but the upside does not justify the volatility. Rate high.
- **neutral**: r1 high (-1) Momentum target +1.57% against a 3.4% stop gives about 0.47 reward-to-risk. Auditor change adds governance uncertainty. Low conviction and ATR 2.8% argue against sizing up. → r2 high (-1) Peers agree on high risk. Stop about 3.4% away against a 1.6% target, roughly 0.47 reward-to-risk. Auditor change is a governance flag. Lower conviction.
- **conservative**: r1 high (-1) Low-conviction momentum call with poor reward-to-risk: stop about 3.3% below entry, target only about 1.6% above. Auditor change announcement is a governance flag. Lower conviction. → r2 high (-1) Agree with all views: stop about 3.3% versus target 1.6%, poor payoff. Auditor change is a governance flag on a low-conviction momentum call. Keep high risk and lower conviction.
- Consensus (median): risk **high**, conviction after risk **low**

## 5. Portfolio Manager
- Final **up / low**, flag caution. Momentum and relative strength are positive, but high risk rating and an auditor change announcement keep conviction low.
- Expected 5-day move +1.57%, hybrid score +0.783
