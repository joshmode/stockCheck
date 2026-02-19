import unittest
from stock_tracker.regime.classifier import RegimeClassifier, MarketRegime
from stock_tracker.core.models import IndicatorState

class TestRegime(unittest.TestCase):
    def test_classification(self):
        classifier = RegimeClassifier()

        # Test Bull Trend (EMA 20 > 50 > 200, ADX > 25)
        ind_bull = IndicatorState(ema20=110.0, ema50=105.0, ema200=100.0, adx=30.0)
        self.assertEqual(classifier.classify(ind_bull), MarketRegime.BULL_TREND)

        # Test Bear Trend (EMA 20 < 50 < 200, ADX > 25)
        ind_bear = IndicatorState(ema20=90.0, ema50=95.0, ema200=100.0, adx=30.0)
        self.assertEqual(classifier.classify(ind_bear), MarketRegime.BEAR_TREND)

        # Test Ranging (ADX < 25, EMAs aligned but weak)
        # Note: Updated logic prioritizes EMA alignment, so this might be BULL_TREND if EMAs are separate.
        # But here EMAs are equal (100=100), so definitely RANGE.
        ind_range = IndicatorState(ema20=100.0, ema50=100.0, ema200=100.0, rsi=50.0, adx=15.0)
        self.assertEqual(classifier.classify(ind_range), MarketRegime.RANGE)

        # Test Fallback (Unknown/Ranging)
        # Originally ADX Low -> Range. But with new logic, if EMAs show trend, it's BULL_TREND.
        ind_fallback = IndicatorState(ema20=100.0, ema50=90.0, ema200=95.0, rsi=70.0, adx=15.0)
        self.assertEqual(classifier.classify(ind_fallback), MarketRegime.BULL_TREND)


    def test_zero_indicator_values_are_handled(self):
        classifier = RegimeClassifier()

        # 0.0 values are valid readings and should not be treated as missing.
        ind = IndicatorState(ema20=0.0, ema50=1.0, ema200=2.0, rsi=0.0, adx=30.0)
        # EMA20 < EMA50 (0 < 1) -> Bear Trend
        self.assertEqual(classifier.classify(ind), MarketRegime.BEAR_TREND)

if __name__ == '__main__':
    unittest.main()
