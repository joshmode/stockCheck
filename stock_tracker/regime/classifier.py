from enum import Enum
from stock_tracker.core.models import IndicatorState

class MarketRegime(Enum):
    BULL_TREND = "BULL_TREND"
    BEAR_TREND = "BEAR_TREND"
    RANGE = "RANGE"
    VOLATILE = "VOLATILE"
    TRANSITION = "TRANSITION"
    UNKNOWN = "UNKNOWN"

class RegimeClassifier:
    def classify(self, data: IndicatorState) -> MarketRegime:
        if (data.ema20 is None or data.ema50 is None or data.adx is None):
            return MarketRegime.UNKNOWN

        strength = data.adx
        trending = strength > 15.0

        if trending:
            if data.ema20 > data.ema50:
                return MarketRegime.BULL_TREND
            elif data.ema20 < data.ema50:
                return MarketRegime.BEAR_TREND

        if strength > 10.0:
            if data.ema20 > data.ema50:
                return MarketRegime.BULL_TREND
            elif data.ema20 < data.ema50:
                return MarketRegime.BEAR_TREND

        if data.rsi and 40 <= data.rsi <= 60:
            return MarketRegime.RANGE

        return MarketRegime.RANGE
