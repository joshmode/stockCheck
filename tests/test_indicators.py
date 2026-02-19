import unittest
from stock_tracker.indicators.streaming import EMA, RSI, ATR

class TestIndicators(unittest.TestCase):
    def test_ema(self):
        ema = EMA(2) # Multiplier = 2/3 = 0.666
        self.assertAlmostEqual(ema.update(10), 10.0)
        self.assertAlmostEqual(ema.update(20), 16.6666666, places=5)
        self.assertAlmostEqual(ema.update(30), 25.5555555, places=5)

    def test_rsi(self):
        rsi = RSI(2)
        # P1=10 -> None (Need prev price)
        self.assertIsNone(rsi.update(10))
        # P2=11 -> Gain=1, Loss=0 -> Accum: G=1, L=0, Count=1 -> None (Need period samples)
        self.assertIsNone(rsi.update(11))
        # P3=12 -> Gain=1, Loss=0 -> Accum: G=2, L=0, Count=2 -> AvgG=1, AvgL=0 -> RSI=100
        self.assertEqual(rsi.update(12), 100.0)
        # P4=11 -> Change=-1 -> Gain=0, Loss=1. AvgG=(1*(1)+0)/2 = 0.5. AvgL=(0*(1)+1)/2 = 0.5. RS=1. RSI=50.
        self.assertEqual(rsi.update(11), 50.0)

    def test_atr(self):
        atr = ATR(2)
        # H=10, L=8, C=9. TR=2. Accum=2. Count=1. None.
        self.assertIsNone(atr.update(10, 8, 9))
        # H=11, L=9, C=10. PrevC=9. TR=max(2, 2, 0)=2. Accum=4. Count=2. ATR=2.
        self.assertEqual(atr.update(11, 9, 10), 2.0)
        # H=12, L=10, C=11. PrevC=10. TR=2. ATR=(2*1 + 2)/2 = 2.
        self.assertEqual(atr.update(12, 10, 11), 2.0)

if __name__ == '__main__':
    unittest.main()
