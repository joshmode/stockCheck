import unittest
from stock_tracker.risk.manager import RiskManager

class TestRisk(unittest.TestCase):
    def test_risk_calculation(self):
        manager = RiskManager()

        # Test LONG
        # Price 100. ATR 5.
        # Stop = 100 - (5*2) = 90
        # Target = 100 + (5*3) = 115
        # RR = 25/10 = 2.5? No.
        # Target dist = 15. Stop dist = 10. RR = 1.5.

        risk = manager.calculate_risk(100.0, 5.0, "LONG")
        self.assertEqual(risk.stop_loss, 90.0)
        self.assertEqual(risk.target, 115.0)
        self.assertEqual(risk.risk_reward_ratio, 1.5)

        # Test SHORT
        # Price 100. ATR 5.
        # Stop = 100 + 10 = 110
        # Target = 100 - 15 = 85

        risk = manager.calculate_risk(100.0, 5.0, "SHORT")
        self.assertEqual(risk.stop_loss, 110.0)
        self.assertEqual(risk.target, 85.0)
        self.assertEqual(risk.risk_reward_ratio, 1.5)

        # Test Invalid ATR (<=0) -> Fallback 2%
        # Price 100. ATR 0.
        # Fallback ATR = 2.
        # Stop = 100 - 4 = 96
        # Target = 100 + 6 = 106 (3 * 2)

        risk = manager.calculate_risk(100.0, 0.0, "LONG")
        self.assertEqual(risk.stop_loss, 96.0)
        self.assertEqual(risk.target, 106.0)
        self.assertEqual(risk.risk_reward_ratio, 1.5)

        # Test Invalid Direction
        risk = manager.calculate_risk(100.0, 5.0, "NEUTRAL")
        self.assertEqual(risk.stop_loss, 0.0)

if __name__ == '__main__':
    unittest.main()
