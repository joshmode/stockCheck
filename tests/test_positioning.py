import unittest
from stock_tracker.positioning.manager import PositionManager
from stock_tracker.regime.classifier import MarketRegime
from stock_tracker.core.models import IndicatorState

class TestPositioning(unittest.TestCase):
    def test_recommendation(self):
        manager = PositionManager()
        ind = IndicatorState(ema20=100.0, rsi=50.0)

        # Test Bullish Swing (Score > 0.4, Bull Regime)
        # Price 99 < EMA 100 * 1.02 -> Pullback Entry
        rec = manager.recommend(0.5, MarketRegime.BULL_TREND, ind, [], 99.0)
        self.assertEqual(rec.action, "BUY")
        self.assertEqual(rec.type, "LONG_SWING")
        self.assertEqual(rec.entry_signal, "PULLBACK_EMA20")

        # Test Bearish Swing (Score < -0.4, Bear Regime)
        # Price 101 > EMA 100 * 0.98 -> Pullback Entry (Short)
        rec = manager.recommend(-0.6, MarketRegime.BEAR_TREND, ind, [], 101.0)
        self.assertEqual(rec.action, "SELL")
        self.assertEqual(rec.type, "SHORT_SWING")
        self.assertEqual(rec.entry_signal, "PULLBACK_EMA20")

        # Test Neutral (Score 0.4) -> HOLD
        rec = manager.recommend(0.4, MarketRegime.BULL_TREND, ind, [], 100.0)
        self.assertEqual(rec.action, "HOLD")
        self.assertEqual(rec.type, "NEUTRAL")

if __name__ == '__main__':
    unittest.main()
