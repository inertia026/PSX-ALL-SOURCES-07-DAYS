# Backtest of the Python market signals

Weekly walk-forward from **2024-09-06** to **2026-11-27**: 111 weeks, 100 KSE-100 members (liquid ones only), 7837 stock-weeks.
Target: next-5-day return **relative to the KSE-100 proxy**. Zero tokens. Averages clip returns at ±20% so a few data errors cannot dominate.

IC = rank correlation between the signal and next week's relative return, averaged over weeks. |t| ≥ 2 is a reasonably steady effect; positive IC means 'higher value, better next week'.

| Signal | Mean IC | t-stat | Weeks IC > 0 | Top 20% − bottom 20% | IC 1st half | IC 2nd half |
|---|---|---|---|---|---|---|
| **market_score** | +0.057 | +3.28 | 64.0% | +0.21% | +0.045 | +0.069 |
| pos_52w | +0.022 | +1.29 | 54.1% | +0.06% | +0.019 | +0.024 |
| rel_ret_1d | +0.012 | +0.76 | 53.2% | +0.40% | +0.003 | +0.022 |
| volume_x_direction | +0.000 | +0.03 | 50.5% | +0.02% | -0.013 | +0.014 |
| trend_sma20_vs_50_pct | -0.003 | -0.16 | 55.0% | -0.02% | -0.006 | +0.001 |
| dist_sma200_pct | -0.008 | -0.49 | 48.6% | -0.23% | -0.024 | +0.008 |
| rel_ret_20d | -0.010 | -0.57 | 52.3% | +0.03% | -0.008 | -0.012 |
| rel_ret_60d | -0.012 | -0.66 | 51.4% | -0.26% | -0.018 | -0.005 |
| rsi14 | -0.018 | -1.05 | 45.9% | -0.26% | -0.009 | -0.027 |
| dist_sma50_pct | -0.021 | -1.16 | 48.6% | -0.17% | -0.020 | -0.021 |
| macd_hist_pct | -0.023 | -1.31 | 43.2% | -0.03% | -0.020 | -0.026 |
| dist_sma20_pct | -0.024 | -1.31 | 44.1% | +0.04% | -0.019 | -0.028 |
| volume_ratio_5_20 | -0.024 | -1.78 | 45.9% | -0.23% | -0.020 | -0.028 |
| rel_ret_5d | -0.039 | -2.23 | 39.6% | -0.39% | -0.019 | -0.058 |
| volatility_20d | -0.045 | -2.15 | 40.5% | -0.14% | -0.058 | -0.032 |
| atr_pct | -0.052 | -2.51 | 39.6% | -0.30% | -0.053 | -0.051 |

## Market score buckets (pooled)

| Bucket | Score range | Stock-weeks | Avg next-5d vs market | Median vs market | Beat market | Avg size of move |
|---|---|---|---|---|---|---|
| 1 | -50 to -10 | 1567 | +0.03% | -0.91% | 42.8% | 5.37% |
| 2 | -10 to -5 | 1567 | +0.05% | -0.44% | 45.2% | 4.75% |
| 3 | -5 to +0 | 1567 | +0.71% | -0.05% | 49.6% | 4.21% |
| 4 | +0 to +0 | 1567 | +0.02% | -0.40% | 44.4% | 3.55% |
| 5 | +0 to +15 | 1569 | +0.06% | -0.39% | 44.2% | 2.67% |

_Limits: today's KSE-100 list is used for the whole period (survivorship bias). Fundamentals, news and agents are not backtested._
