import unittest
from datetime import datetime
from stock_tracker.core.models import Candle, SwingPoint, SwingType
from stock_tracker.structure.swings import SwingDetector
from stock_tracker.structure.patterns import PatternRecognizer

class TestStructure(unittest.TestCase):
    def test_swing_detector(self):
        detector = SwingDetector(threshold=0.1)

        c1 = Candle(datetime.now(), 100, 100, 100, 100, 100)
        c2 = Candle(datetime.now(), 110, 110, 110, 110, 100)
        c3 = Candle(datetime.now(), 90, 90, 90, 90, 100)

        s1 = detector.update(c1, 0)
        self.assertIsNone(s1)

        s2 = detector.update(c2, 1)
        self.assertIsNone(s2)

        s3 = detector.update(c3, 2)
        self.assertIsNotNone(s3)
        self.assertEqual(s3.price, 110)
        self.assertEqual(s3.type, SwingType.HIGH)
        self.assertEqual(detector.mode, "DOWN")
        self.assertEqual(detector.potential.price, 90)

    def test_pattern_recognizer(self):
        rec = PatternRecognizer()
        swings = [
            SwingPoint(100, 0, datetime.now(), SwingType.HIGH),
            SwingPoint(80, 1, datetime.now(), SwingType.LOW),
            SwingPoint(101, 2, datetime.now(), SwingType.HIGH),
            SwingPoint(70, 3, datetime.now(), SwingType.LOW),
        ]

        patterns = rec.detect_patterns(swings)
        self.assertIn("DOUBLE_TOP_BREAKOUT", patterns)

if __name__ == '__main__':
    unittest.main()
