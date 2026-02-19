import unittest
from stock_tracker.sentiment.analyzer import SentimentAnalyzer

class TestSentiment(unittest.TestCase):
    def test_sentiment_analysis(self):
        analyzer = SentimentAnalyzer()

        # Test Case 1: Positive
        headlines = [
            "Stock surges to record high as earnings are excellent",
            "Analysts upgrade rating to buy",
            "Company announces fantastic new partnership"
        ]
        signal = analyzer.analyze(headlines)
        self.assertEqual(signal.summary, "POSITIVE")
        self.assertGreater(signal.score, 0.1)

        # Test Case 2: Negative
        headlines = [
            "Stock performance is terrible",
            "Earnings are awful and disastrous",
            "Worst company ever"
        ]
        signal = analyzer.analyze(headlines)
        self.assertEqual(signal.summary, "NEGATIVE")
        self.assertLess(signal.score, -0.1)

        # Test Case 3: Neutral/Mixed
        headlines = [
            "Stock opens flat",
            "Market awaits Fed decision",
            "Company to report earnings next week"
        ]
        signal = analyzer.analyze(headlines)
        # Neutral score is usually near 0
        self.assertTrue(-0.1 <= signal.score <= 0.1)
        self.assertEqual(signal.summary, "NEUTRAL")

        # Test Case 4: Empty
        signal = analyzer.analyze([])
        self.assertEqual(signal.score, 0.0)
        self.assertEqual(signal.summary, "NEUTRAL")

if __name__ == '__main__':
    unittest.main()
