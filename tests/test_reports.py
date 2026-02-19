import unittest
from datetime import datetime
from stock_tracker.reports.generator import ReportGenerator
from stock_tracker.api.interface import AnalysisReport
from stock_tracker.regime.classifier import MarketRegime

class TestReports(unittest.TestCase):
    def test_report_generation(self):
        generator = ReportGenerator()

        report_data = AnalysisReport(
            ticker="TEST",
            timestamp=datetime.now(),
            price=150.0,
            recommendation="BUY",
            trade_type="LONG_SWING",
            confidence=0.8,
            target=160.0,
            stop_loss=145.0,
            risk_reward=2.0,
            confidence_interval_low=148.0,
            confidence_interval_high=152.0,
            patterns=["BULL_FLAG"],
            regime=MarketRegime.BULL_TREND,
            sentiment_summary="POSITIVE",
            sentiment_score=0.5,
            rationale="Test Rationale",
            entry_signal="BREAKOUT",
            trend_strength="ADX 30",
            volume_status="NORMAL",
            volume_trend="ACCUMULATION",
            position_size_shares=100,
            position_size_pct=0.05
        )

        text = generator.generate_text_report(report_data)

        self.assertIn("REPORT: TEST", text)
        self.assertIn("RATING: BUY (LONG_SWING)", text)
        self.assertIn("Confidence: 80%", text)
        self.assertTrue("Regime:    BULL_TREND" in text or "Regime: BULL_TREND" in text)
        self.assertIn("Patterns:  BULL_FLAG", text)
        self.assertIn("Price: 150.00", text)

if __name__ == '__main__':
    unittest.main()
