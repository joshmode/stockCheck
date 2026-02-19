from dataclasses import dataclass
from typing import Optional
from stock_tracker.core.models import Candle

@dataclass
class VolumeSignal:
    status: str
    trend: str
    evr: float
    climax_detected: bool

class VolumeAnalyzer:
    def analyze(self, candle: Candle, avg_volume: float, prev_close: float, atr: float) -> VolumeSignal:
        if avg_volume <= 0 or atr <= 0:
             return VolumeSignal("NORMAL", "NEUTRAL", 0.0, False)

        price_change = candle.close - prev_close
        abs_change = abs(price_change)

        vol_ratio = candle.volume / avg_volume
        status = "NORMAL"
        climax = False

        if vol_ratio > 3.0:
            status = "CLIMAX"
            climax = True
        elif vol_ratio > 1.5:
            status = "SPIKE"
        elif vol_ratio < 0.5:
            status = "LOW"

        trend = "NEUTRAL"
        if vol_ratio > 1.0:
            if price_change > 0:
                trend = "ACCUMULATION"
            elif price_change < 0:
                trend = "DISTRIBUTION"

        price_norm = abs_change / atr
        vol_norm = vol_ratio

        evr = 0.0
        if vol_norm > 0:
            evr = price_norm / vol_norm

        return VolumeSignal(status, trend, evr, climax)
