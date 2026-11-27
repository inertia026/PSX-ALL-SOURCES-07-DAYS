# Post-mortem: run as of 2026-11-20 (window 23–27 Nov 2026)

> **Not financial advice.** Research notes on an automated experiment.

**Result:** 14 of 30 calls right (46.7%). Top 5 averaged +0.07%, against +0.16% for the KSE-100 proxy. Score-vs-return rank correlation −0.03.
**Method:** zero tokens. Python compared every stage's output with actual returns, then backtested the Python market score
weekly over the past year (39 weeks × 30 stocks, no agents).

## 1. What each stage contributed (Spearman vs actual 5-day return, n=30; about ±0.36 needed to be meaningful)

| Signal | Correlation | Reading |
|---|---|---|
| Market score (Python) | +0.13 | weak, right sign |
| Fundamental score (Python) | **−0.61** | strongly wrong this week |
| News view (agent) | −0.17 | no help |
| Sentiment mood (agent) | +0.02 | no help |
| Debate net score | −0.01 | no help |
| Research Manager direction | 0.00 | no help |
| Portfolio Manager direction | −0.13 | slightly worse than RM |
| Final ranking score | −0.03 | no help |
| Prior 5-day return | **+0.35** | best single signal this week (momentum) |
| RSI(14) | +0.32 | high RSI went up, but the system penalised it as "overbought" |

Hit rate by stage: Python debate proposal 15/28, Research Manager 16/30, Portfolio Manager 14/30.
Naive baselines did better: always "up" 17/30, always "flat" 20/30.

## 2. The past-year backtest (most important finding)

| Test (39 weekly snapshots) | Result |
|---|---|
| Market score weekly correlation with next 5 days | +0.005 (positive in 46% of weeks), **no edge** |
| Top 5 by market score, next-5-day average | −0.38% (bottom 5: +0.26%; all: +0.06%) |
| Prior 5-day return > +5% | next 5 days +1.45%, up 62% of the time (n=120) |
| RSI > 70 ("overbought") | next 5 days +0.87% (n=36) |
| RSI < 35 ("oversold") | next 5 days −0.81% (n=106) |
| Typical 5-day move size | 3.28% (this week was quiet: 0.99%) |

The core Python score had no predictive power over the past year. Two of its rules point the wrong way on PSX:
"overbought is bearish" and "oversold is a bounce". Short-term strength has tended to continue.

## 3. Root causes
1. **The signals were never validated.** The weights were picked by hand, never fitted or tested on PSX history.
2. **Agents add layers, not information.** The debate, Research Manager and Portfolio Manager only re-weigh the same
   evidence pack. With no edge in the inputs, extra layers just add noise.
3. **The direction call is absolute, not relative.** The market was flat (+0.16%). The system predicts "up" or "down"
   against zero rather than against the market or sector, so in a flat week most calls are a coin flip.
4. **The hit metric is lopsided.** A flat call counts as right inside ±1%, an easy target in a quiet week. "Always flat"
   would have scored 20/30. Rank correlation, top-minus-bottom spread and excess return are the honest measures.
5. **Move sizes are not calibrated.** Predicted moves for non-flat calls averaged 1.79%, but the formula has no link to
   how often moves of that size actually happen.
6. **Event effects.** PPL, OGDC and HUBC went ex-dividend inside the window, and PSEL fell 7.7% on a stock-specific
   move. A sample of 30 is easily swung by one or two names.

## 4. Improvements (in priority order)
1. **Add a `psx7 backtest` command (Python, zero tokens).** Walk-forward over 1–2 years for all KSE-100 stocks. Report
   the weekly correlation and top-minus-bottom spread for every Python signal. A signal enters the score only if it shows
   a stable edge.
2. **Fix the signal rules using the backtest.** Drop or flip "RSI > 70 = bearish" and "RSI < 35 = bounce". Add
   short-term momentum (5- and 20-day relative strength), volume confirmation and sector-relative strength. Re-weight
   fundamentals: they act on months, not 5 days, so make them a tie-breaker.
3. **Predict relative performance.** Rank stocks against the KSE-100 proxy (outperform / inline / underperform) rather
   than absolute up/down. This is what a top-30 ranking really needs.
4. **Calibrate the expected move.** Fit it from history (score bucket → average next-5-day move) instead of
   ATR × conviction.
5. **Give agents a narrow, testable job.** Let the News agent flag events only (results date, payout, regulatory hit)
   that shift a stock up or down by at most a small fixed amount. Debate, Research Manager and Portfolio Manager become
   explanation and veto layers ("avoid" or "watch" moves a stock to the bottom). Each layer's added value is tracked in
   the scorecard; cut any layer that shows none after about 8 weeks. This also saves tokens.
6. **Better scorecard metrics.** Show rank correlation, top-5 minus bottom-5 spread, top-5 excess return, and hit rate
   versus the naive baselines (always up, always flat, momentum only). Also score each stage's direction separately.
7. **Handle events in the window.** Mark expected ex-dates and results dates as "event risk" so their moves aren't
   treated as normal signal.
8. **Judge on 8+ weeks, not one.** Keep weekly runs going; one week can't separate skill from luck.

## 5. Update (2026-11-27): full backtest and fixes
A wider backtest (`python -m psx7 backtest`: 111 weeks, 100 KSE-100 stocks, returns vs market) replaced the quick
30-stock check above, and **corrected part of section 2**. Against the market, "stocks that ran up keep running" did **not**
hold: stretched stocks (far above their 20-day average, RSI > 70, or > 4 pts ahead of the market in 5 days) and very
volatile stocks lagged the next week, and calm stocks did best. Trend signals had no edge.

Changes made (v1.3):
- Market score: points only for those backtested rules; trend items are context only. IC went from −0.011 (t −0.7) to **+0.057 (t +3.3)**, positive in 64% of weeks and in both halves.
- Quant score is now 0.8 × market + 0.2 × fundamentals (fundamentals can't be backtested).
- Expected move is a fixed 0.5% edge × conviction, no longer ATR-scaled; the liquidity penalty is 0.25.

Still open: relative (vs market) calls, a fairer scorecard with baselines, event-risk flags, and the split-adjustment gap
(splits beyond 5:1 are not adjusted).
