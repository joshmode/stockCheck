import unittest
from stock_tracker.scoring.engine import ScoringEngine
from stock_tracker.regime.classifier import MarketRegime
from stock_tracker.volume.analysis import VolumeSignal
from stock_tracker.sentiment.analyzer import SentimentSignal
from stock_tracker.core.models import IndicatorState

class TestScoring(unittest.TestCase):
    def test_calculate_score(self):
        engine = ScoringEngine()

        # Test Case 1: Max Bullish
        regime = MarketRegime.BULL_TREND
        patterns = ["BULL_FLAG"]
        # VolumeSignal(status, trend, evr, climax)
        volume = VolumeSignal("NORMAL", "ACCUMULATION", 2.0, False)
        # SentimentSignal(score, summary, confidence)
        sentiment = SentimentSignal(1.0, "POSITIVE", 1.0)
        # Trend Score: EMA20 > EMA50 -> 1.0.
        indicators = IndicatorState(ema20=110.0, ema50=100.0, ema200=90.0, rsi=60.0, adx=50.0)

        # Expected:
        # Trend: 1.0 * (50/50) = 1.0. Weight 0.35 -> 0.35
        # Momentum: (60-50)/50 = 0.2. Weight 0.20 -> 0.04
        # Volume: Accumulation=1.0. Weight 0.20 -> 0.20
        # Pattern: Bull=1.0. Weight 0.15 -> 0.15
        # Sentiment: 1.0. Weight 0.10 -> 0.10
        # Total: 0.35 + 0.04 + 0.20 + 0.15 + 0.10 = 0.84

        score = engine.calculate_score(regime, patterns, volume, sentiment, indicators)
        self.assertAlmostEqual(score, 0.84, delta=0.01)

        # Test Case 2: Range Reversion
        regime = MarketRegime.RANGE
        patterns = []
        volume = VolumeSignal("NORMAL", "NEUTRAL", 1.0, False)
        sentiment = SentimentSignal(0.0, "NEUTRAL", 0.0)
        # RSI 30 (Oversold). In Range, RSI logic is Mean Reversion.
        # Momentum Score logic: val = (30-50)/50 = -0.4.
        # If Range: momentum_score = -val = 0.4.
        indicators = IndicatorState(rsi=30.0, adx=15.0) # No EMAs -> Trend 0.

        # Expected:
        # Trend: 0.0. Weight 0.10 -> 0.0
        # Momentum: 0.4. Weight 0.40 -> 0.16
        # Volume: 0.0. Weight 0.10 -> 0.0
        # Pattern: 0.0. Weight 0.30 -> 0.0
        # Sentiment: 0.0. Weight 0.10 -> 0.0
        # Total: 0.16

        score = engine.calculate_score(regime, patterns, volume, sentiment, indicators)
        self.assertAlmostEqual(score, 0.16, delta=0.01)

if __name__ == '__main__':
    unittest.main()
