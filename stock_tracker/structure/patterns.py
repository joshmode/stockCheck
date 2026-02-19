from typing import List
from stock_tracker.core.models import SwingPoint, SwingType

class PatternRecognizer:
    def detect_patterns(self, swings: List[SwingPoint]) -> List[str]:
        patterns = []
        n = len(swings)
        if n < 3:
            return patterns

        s1 = swings[-3]
        s2 = swings[-2]
        s3 = swings[-1]

        if s1.type == SwingType.HIGH and s2.type == SwingType.LOW and s3.type == SwingType.HIGH:
            if self.check_level(s1.price, s3.price):
                patterns.append("POTENTIAL_DOUBLE_TOP")

        if s1.type == SwingType.LOW and s2.type == SwingType.HIGH and s3.type == SwingType.LOW:
            if self.check_level(s1.price, s3.price):
                patterns.append("POTENTIAL_DOUBLE_BOTTOM")

        if n >= 4:
            s0 = swings[-4]

            if s0.type == SwingType.HIGH and s1.type == SwingType.LOW and s2.type == SwingType.HIGH and s3.type == SwingType.LOW:
                if self.check_level(s0.price, s2.price):
                    if s3.price < s1.price:
                        patterns.append("DOUBLE_TOP_BREAKOUT")

            if s0.type == SwingType.LOW and s1.type == SwingType.HIGH and s2.type == SwingType.LOW and s3.type == SwingType.HIGH:
                if self.check_level(s0.price, s2.price):
                    if s3.price > s1.price:
                        patterns.append("DOUBLE_BOTTOM_BREAKOUT")

        if n >= 5:
            s_a = swings[-5]
            s_c = swings[-3]
            s_e = swings[-1]

            if (s_a.type == SwingType.HIGH and s_c.type == SwingType.HIGH and s_e.type == SwingType.HIGH):
                is_head = s_c.price > s_a.price and s_c.price > s_e.price
                shoulders_aligned = self.check_level(s_a.price, s_e.price, tolerance=0.05)
                if is_head and shoulders_aligned:
                    patterns.append("POTENTIAL_HEAD_AND_SHOULDERS")

            if (s_a.type == SwingType.LOW and s_c.type == SwingType.LOW and s_e.type == SwingType.LOW):
                is_head = s_c.price < s_a.price and s_c.price < s_e.price
                shoulders_aligned = self.check_level(s_a.price, s_e.price, tolerance=0.05)
                if is_head and shoulders_aligned:
                    patterns.append("POTENTIAL_INVERSE_HEAD_AND_SHOULDERS")

        return patterns

    def check_level(self, price1: float, price2: float, tolerance: float = 0.03) -> bool:
        diff = abs(price1 - price2)
        avg = (price1 + price2) / 2
        return (diff / avg) < tolerance

    def detect_trend(self, swings: List[SwingPoint]) -> str:
        if len(swings) < 4:
            return "NEUTRAL"

        highs = [s for s in swings if s.type == SwingType.HIGH]
        lows = [s for s in swings if s.type == SwingType.LOW]

        if len(highs) < 2 or len(lows) < 2:
            return "NEUTRAL"

        last_high = highs[-1]
        prev_high = highs[-2]
        last_low = lows[-1]
        prev_low = lows[-2]

        if last_high.price > prev_high.price and last_low.price > prev_low.price:
            return "UPTREND"
        elif last_high.price < prev_high.price and last_low.price < prev_low.price:
            return "DOWNTREND"

        return "SIDEWAYS"
