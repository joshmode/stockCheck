import unittest
import math
from stock_tracker.decay.aging import SignalDecay

class TestDecay(unittest.TestCase):
    def test_decay_calculation(self):
        decay = SignalDecay()

        # Test 0 days old
        score = 1.0
        self.assertAlmostEqual(decay.calculate_decay(score, 0), 1.0)

        # Test half life (5.0 default)
        # e^(-ln(2)/5 * 5) = e^(-ln(2)) = 0.5
        self.assertAlmostEqual(decay.calculate_decay(score, 5.0, half_life=5.0), 0.5)

        # Test 10 days (2 half lives) -> 0.25
        self.assertAlmostEqual(decay.calculate_decay(score, 10.0, half_life=5.0), 0.25)

        # Test negative days (should return original score)
        self.assertEqual(decay.calculate_decay(score, -1.0), 1.0)

if __name__ == '__main__':
    unittest.main()
