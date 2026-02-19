import unittest
from stock_tracker.api.interface import StockTracker, AnalysisReport
from stock_tracker.core.models import Candle
from datetime import datetime

class TestIntegration(unittest.TestCase):
    def test_end_to_end_mock(self):
        tracker = StockTracker()

        def mock_fetch(ticker, days=300):
            candles = []
            for i in range(days):
                c = Candle(
                    timestamp=datetime.now(),
                    open=float(100+i),
                    high=float(105+i),
                    low=float(95+i),
                    close=float(100+i),
                    volume=1000.0
                )
                candles.append(c)
            return candles

        tracker.data.fetch_history = mock_fetch

        report = tracker.analyze("MOCK")

        self.assertIsNotNone(report)
        self.assertEqual(report.ticker, "MOCK")
        self.assertGreater(report.price, 0)
        self.assertIn(report.recommendation, ["BUY", "SELL", "HOLD"])
        self.assertEqual(len(tracker.cache.cache), 1)

if __name__ == '__main__':
    unittest.main()
