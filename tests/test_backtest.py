import unittest
from stock_tracker.backtest_snapshot.engine import BacktestEngine
from stock_tracker.regime.classifier import MarketRegime

class TestBacktest(unittest.TestCase):
    def test_stats_retrieval(self):
        engine = BacktestEngine()

        # Test Double Top in Bull Trend
        # Base Win Rate 0.65. Modifier 1.2. -> 0.78
        stats = engine.get_stats(["DOUBLE_TOP"], MarketRegime.BULL_TREND)
        self.assertIsNotNone(stats)
        self.assertAlmostEqual(stats.win_rate, 0.78)

        # Test Unknown
        stats = engine.get_stats(["UNKNOWN"], MarketRegime.BULL_TREND)
        self.assertIsNone(stats)

if __name__ == '__main__':
    unittest.main()
