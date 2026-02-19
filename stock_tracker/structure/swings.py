from typing import Optional
from stock_tracker.core.models import Candle, SwingPoint, SwingType

class SwingDetector:
    def __init__(self, threshold: float = 0.03):
        self.threshold = threshold
        self.mode: Optional[str] = None
        self.potential: Optional[SwingPoint] = None
        self.last_swing: Optional[SwingPoint] = None

    def update(self, candle: Candle, index: int) -> Optional[SwingPoint]:
        if self.mode is None:
            self.mode = "UP"
            self.potential = SwingPoint(candle.high, index, candle.timestamp, SwingType.HIGH)
            return None

        confirmed = None

        if self.mode == "UP":
            if candle.high > self.potential.price:
                self.potential = SwingPoint(candle.high, index, candle.timestamp, SwingType.HIGH)
            elif candle.low < self.potential.price * (1 - self.threshold):
                confirmed = self.potential
                self.last_swing = confirmed

                self.mode = "DOWN"
                self.potential = SwingPoint(candle.low, index, candle.timestamp, SwingType.LOW)

        elif self.mode == "DOWN":
            if candle.low < self.potential.price:
                self.potential = SwingPoint(candle.low, index, candle.timestamp, SwingType.LOW)
            elif candle.high > self.potential.price * (1 + self.threshold):
                confirmed = self.potential
                self.last_swing = confirmed

                self.mode = "UP"
                self.potential = SwingPoint(candle.high, index, candle.timestamp, SwingType.HIGH)

        return confirmed
