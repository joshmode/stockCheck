from collections import deque
from typing import List, Optional, Deque
from stock_tracker.core.models import Candle, IndicatorState, SwingPoint
from stock_tracker.indicators.streaming import EMA, RSI, ATR, MACD, VWAP
from stock_tracker.structure.swings import SwingDetector

class TickerData:
    def __init__(self, ticker: str, max_len: int = 300):
        self.ticker = ticker
        self.max_len = max_len
        self.candles: Deque[Candle] = deque(maxlen=max_len)
        self.indicator_history: Deque[IndicatorState] = deque(maxlen=max_len)

        self.ema20 = EMA(20)
        self.ema50 = EMA(50)
        self.ema200 = EMA(200)
        self.rsi = RSI(14)
        self.atr = ATR(14)
        self.macd = MACD()
        self.vwap = VWAP()

        self.swing_detector = SwingDetector()
        self.swings: List[SwingPoint] = []
        self.candle_count = 0

    def add_candle(self, candle: Candle):
        self.candles.append(candle)
        c = candle.close

        e20 = self.ema20.update(c)
        e50 = self.ema50.update(c)
        e200 = self.ema200.update(c)
        rsi = self.rsi.update(c)
        atr = self.atr.update(candle.high, candle.low, c)
        m, s, h = self.macd.update(c)
        vwap = self.vwap.update(candle.high, candle.low, c, candle.volume)

        state = IndicatorState(
            ema20=e20, ema50=e50, ema200=e200,
            rsi=rsi, atr=atr,
            macd_line=m, macd_signal=s, macd_hist=h,
            vwap=vwap
        )
        self.indicator_history.append(state)

        swing = self.swing_detector.update(candle, self.candle_count)
        if swing:
            self.swings.append(swing)

        self.candle_count += 1

        if len(self.candles) == self.max_len:
             oldest = self.candles[0].timestamp
             while self.swings and self.swings[0].timestamp < oldest:
                 self.swings.pop(0)

    def initialize_history(self, candles: List[Candle]):
        for c in candles:
            self.add_candle(c)

    def get_latest_candle(self) -> Optional[Candle]:
        return self.candles[-1] if self.candles else None

    def get_latest_indicators(self) -> Optional[IndicatorState]:
        return self.indicator_history[-1] if self.indicator_history else None

    def get_all_candles(self) -> List[Candle]:
        return list(self.candles)

    def get_all_indicators(self) -> List[IndicatorState]:
        return list(self.indicator_history)

    def get_swings(self) -> List[SwingPoint]:
        return list(self.swings)
