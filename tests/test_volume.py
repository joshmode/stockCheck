import unittest
from datetime import datetime
from stock_tracker.volume.analysis import VolumeAnalyzer
from stock_tracker.core.models import Candle

class TestVolume(unittest.TestCase):
    def test_volume_analysis(self):
        analyzer = VolumeAnalyzer()

        # Test Case 1: Spike Accumulation
        # Avg Vol: 1000
        # Candle Vol: 2500 (> 2.0x -> SPIKE)
        # Price Change: +5 (Close 105, Prev 100) -> ACCUMULATION

        c1 = Candle(datetime.now(), 100, 105, 100, 105, 2500)
        signal = analyzer.analyze(c1, 1000, 100.0, 2.0)
        self.assertEqual(signal.status, "SPIKE")
        self.assertEqual(signal.trend, "ACCUMULATION")

        # Test Case 2: Low Volume Distribution
        # Avg Vol: 1000
        # Candle Vol: 400 (< 0.5x -> LOW)
        # Price Change: -5 (Close 100, Prev 105)
        # Vol > Avg? No. 400 < 1000. So Trend is NEUTRAL

        c2 = Candle(datetime.now(), 105, 105, 100, 100, 400)
        signal = analyzer.analyze(c2, 1000, 105.0, 2.0)
        self.assertEqual(signal.status, "LOW")
        self.assertEqual(signal.trend, "NEUTRAL")

        # Test Case 3: Distribution (High Vol but not Spike)
        # Avg Vol: 1000
        # Vol: 1500 (1.5x, not > 2.0x -> NORMAL? Wait, >1.5 is SPIKE in new logic?)
        # New Logic: > 3.0 CLIMAX, > 1.5 SPIKE.
        # So 1500 / 1000 = 1.5. Exactly 1.5 is NORMAL (if condition is > 1.5).
        # Let's check logic: elif vol_ratio > 1.5: status = "SPIKE"
        # 1.5 is not > 1.5. So NORMAL.

        c3 = Candle(datetime.now(), 105, 105, 100, 100, 1500)
        signal = analyzer.analyze(c3, 1000, 105.0, 2.0)
        self.assertEqual(signal.status, "NORMAL")
        self.assertEqual(signal.trend, "DISTRIBUTION")

if __name__ == '__main__':
    unittest.main()
