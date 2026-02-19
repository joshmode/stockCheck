from typing import Optional, Tuple
from collections import deque
import math

class EMA:
    def __init__(self, period: int):
        self.period = period
        self.multiplier = 2 / (period + 1)
        self.value: Optional[float] = None

    def update(self, price: float) -> float:
        if self.value is None:
            self.value = price
        else:
            self.value = (price - self.value) * self.multiplier + self.value
        return self.value

class RSI:
    def __init__(self, period: int = 14):
        self.period = period
        self.avg_gain: Optional[float] = None
        self.avg_loss: Optional[float] = None
        self.last_price: Optional[float] = None
        self.value: Optional[float] = None

        self.count = 0
        self.accum_gain = 0.0
        self.accum_loss = 0.0

    def update(self, price: float) -> Optional[float]:
        if self.last_price is None:
            self.last_price = price
            return None

        change = price - self.last_price
        gain = max(change, 0.0)
        loss = max(-change, 0.0)
        self.last_price = price

        if self.avg_gain is None:
            self.accum_gain += gain
            self.accum_loss += loss
            self.count += 1

            if self.count < self.period:
                return None

            self.avg_gain = self.accum_gain / self.period
            self.avg_loss = self.accum_loss / self.period
        else:
            self.avg_gain = (self.avg_gain * (self.period - 1) + gain) / self.period
            self.avg_loss = (self.avg_loss * (self.period - 1) + loss) / self.period

        if self.avg_loss == 0:
            self.value = 100.0 if self.avg_gain > 0 else 50.0
        else:
            rs = self.avg_gain / self.avg_loss
            self.value = 100.0 - (100.0 / (1.0 + rs))

        return self.value

class ATR:
    def __init__(self, period: int = 14):
        self.period = period
        self.value: Optional[float] = None
        self.last_close: Optional[float] = None
        self.count = 0
        self.accum_tr = 0.0

    def update(self, high: float, low: float, close: float) -> Optional[float]:
        if self.last_close is None:
            tr = high - low
        else:
            tr = max(high - low, abs(high - self.last_close), abs(low - self.last_close))

        self.last_close = close

        if self.value is None:
            self.accum_tr += tr
            self.count += 1
            if self.count == self.period:
                self.value = self.accum_tr / self.period
        else:
            self.value = (self.value * (self.period - 1) + tr) / self.period

        return self.value

class MACD:
    def __init__(self, fast_period=12, slow_period=26, signal_period=9):
        self.fast_ema = EMA(fast_period)
        self.slow_ema = EMA(slow_period)
        self.signal_ema = EMA(signal_period)

        self.macd_line: Optional[float] = None
        self.signal_line: Optional[float] = None
        self.histogram: Optional[float] = None

    def update(self, price: float) -> Tuple[Optional[float], Optional[float], Optional[float]]:
        fast = self.fast_ema.update(price)
        slow = self.slow_ema.update(price)

        self.macd_line = fast - slow
        self.signal_line = self.signal_ema.update(self.macd_line)

        if self.signal_line is not None:
             self.histogram = self.macd_line - self.signal_line

        return self.macd_line, self.signal_line, self.histogram

class VWAP:
    def __init__(self):
        self.cum_vol = 0.0
        self.cum_vol_price = 0.0
        self.value: Optional[float] = None

    def update(self, high: float, low: float, close: float, volume: float) -> float:
        typical_price = (high + low + close) / 3
        self.cum_vol += volume
        self.cum_vol_price += typical_price * volume

        if self.cum_vol > 0:
            self.value = self.cum_vol_price / self.cum_vol
        else:
            self.value = typical_price

        return self.value

class OBV:
    def __init__(self):
        self.value: float = 0.0
        self.last_close: Optional[float] = None

    def update(self, close: float, volume: float) -> float:
        if self.last_close is not None:
            if close > self.last_close:
                self.value += volume
            elif close < self.last_close:
                self.value -= volume

        self.last_close = close
        return self.value

class BollingerBands:
    def __init__(self, period: int = 20, std_dev: float = 2.0):
        self.period = period
        self.std_dev = std_dev
        self.prices = deque(maxlen=period)
        self.sum_price = 0.0
        self.sum_sq_price = 0.0
        self.upper: Optional[float] = None
        self.lower: Optional[float] = None
        self.width: Optional[float] = None
        self.basis: Optional[float] = None

    def update(self, price: float) -> Tuple[Optional[float], Optional[float], Optional[float], Optional[float]]:
        if len(self.prices) == self.period:
            old = self.prices.popleft()
            self.sum_price -= old
            self.sum_sq_price -= old * old

        self.prices.append(price)
        self.sum_price += price
        self.sum_sq_price += price * price

        if len(self.prices) < self.period:
            return None, None, None, None

        mean = self.sum_price / self.period
        variance = (self.sum_sq_price / self.period) - (mean * mean)
        variance = max(0.0, variance)
        std = math.sqrt(variance)

        self.basis = mean
        self.upper = mean + (self.std_dev * std)
        self.lower = mean - (self.std_dev * std)
        self.width = (self.upper - self.lower) / mean if mean != 0 else 0

        return self.upper, self.lower, self.basis, self.width

class ADX:
    def __init__(self, period: int = 14):
        self.period = period
        self.last_high: Optional[float] = None
        self.last_low: Optional[float] = None
        self.last_close: Optional[float] = None

        self.smooth_atr: Optional[float] = None
        self.smooth_plus: Optional[float] = None
        self.smooth_minus: Optional[float] = None

        self.adx_smooth: Optional[float] = None
        self.value: Optional[float] = None

        self.count = 0
        self.accum_tr = 0.0
        self.accum_plus = 0.0
        self.accum_minus = 0.0

    def smooth(self, prev, curr):
        return (prev * (self.period - 1) + curr) / self.period

    def update(self, high: float, low: float, close: float) -> Optional[float]:
        if self.last_close is None:
            self.last_high = high
            self.last_low = low
            self.last_close = close
            return None

        tr = max(high - low, abs(high - self.last_close), abs(low - self.last_close))

        up_move = high - self.last_high
        down_move = self.last_low - low

        plus_dm = up_move if (up_move > down_move and up_move > 0) else 0.0
        minus_dm = down_move if (down_move > up_move and down_move > 0) else 0.0

        self.last_high = high
        self.last_low = low
        self.last_close = close

        if self.smooth_atr is None:
            self.accum_tr += tr
            self.accum_plus += plus_dm
            self.accum_minus += minus_dm
            self.count += 1

            if self.count == self.period:
                self.smooth_atr = self.accum_tr / self.period
                self.smooth_plus = self.accum_plus / self.period
                self.smooth_minus = self.accum_minus / self.period

                val = self.smooth_plus + self.smooth_minus
                dx = (abs(self.smooth_plus - self.smooth_minus) / val * 100) if val != 0 else 0
                self.adx_smooth = dx
                self.value = self.adx_smooth
        else:
            self.smooth_atr = self.smooth(self.smooth_atr, tr)
            self.smooth_plus = self.smooth(self.smooth_plus, plus_dm)
            self.smooth_minus = self.smooth(self.smooth_minus, minus_dm)

            val = self.smooth_plus + self.smooth_minus
            dx = (abs(self.smooth_plus - self.smooth_minus) / val * 100) if val != 0 else 0

            if self.adx_smooth is None:
                 self.adx_smooth = dx
            else:
                 self.adx_smooth = self.smooth(self.adx_smooth, dx)

            self.value = self.adx_smooth

        return self.value
