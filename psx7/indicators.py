"""Technical indicators in plain Python (no randomness, no library-version drift)."""
from __future__ import annotations

import math


def sma(xs: list[float], n: int) -> float | None:
    return sum(xs[-n:]) / n if len(xs) >= n else None


def ema_series(xs: list[float], n: int) -> list[float]:
    if not xs:
        return []
    k, out = 2 / (n + 1), [xs[0]]
    for x in xs[1:]:
        out.append(x * k + out[-1] * (1 - k))
    return out


def rsi(closes: list[float], n: int = 14) -> float | None:
    """Wilder's RSI."""
    if len(closes) <= n:
        return None
    gains = [max(closes[i] - closes[i - 1], 0) for i in range(1, len(closes))]
    losses = [max(closes[i - 1] - closes[i], 0) for i in range(1, len(closes))]
    ag, al = sum(gains[:n]) / n, sum(losses[:n]) / n
    for g, l in zip(gains[n:], losses[n:]):
        ag, al = (ag * (n - 1) + g) / n, (al * (n - 1) + l) / n
    if al == 0:
        return 100.0
    return 100 - 100 / (1 + ag / al)


def macd(closes: list[float]) -> tuple[float, float, float] | None:
    if len(closes) < 35:
        return None
    e12, e26 = ema_series(closes, 12), ema_series(closes, 26)
    line = [a - b for a, b in zip(e12, e26)]
    signal = ema_series(line, 9)
    return line[-1], signal[-1], line[-1] - signal[-1]


def atr(highs: list[float], lows: list[float], closes: list[float], n: int = 14) -> float | None:
    """Wilder's ATR."""
    if len(closes) <= n:
        return None
    trs = [max(highs[i] - lows[i], abs(highs[i] - closes[i - 1]), abs(lows[i] - closes[i - 1]))
           for i in range(1, len(closes))]
    a = sum(trs[:n]) / n
    for t in trs[n:]:
        a = (a * (n - 1) + t) / n
    return a


def pct_change(xs: list[float], n: int) -> float | None:
    if len(xs) <= n or xs[-1 - n] == 0:
        return None
    return (xs[-1] / xs[-1 - n] - 1) * 100


def stdev_returns(closes: list[float], n: int = 20) -> float | None:
    if len(closes) <= n:
        return None
    rets = [closes[i] / closes[i - 1] - 1 for i in range(len(closes) - n, len(closes)) if closes[i - 1]]
    m = sum(rets) / len(rets)
    return math.sqrt(sum((r - m) ** 2 for r in rets) / (len(rets) - 1)) * 100
