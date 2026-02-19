import unittest
from datetime import datetime
from stock_tracker.core.models import Candle
from stock_tracker.data.store import TickerData

class TestData(unittest.TestCase):
    def test_store_incremental_update(self):
        store = TickerData("TEST", max_len=5)

        for i in range(5):
            c = Candle(
                timestamp=datetime.now(),
                open=100.0+i, high=105.0+i, low=95.0+i, close=100.0+i, volume=1000.0
            )
            store.add_candle(c)

        self.assertEqual(len(store.candles), 5)
        self.assertEqual(store.get_latest_candle().close, 104.0)

        c6 = Candle(timestamp=datetime.now(), open=110.0, high=115.0, low=105.0, close=110.0, volume=1000.0)
        store.add_candle(c6)

        self.assertEqual(len(store.candles), 5)
        self.assertEqual(store.candles[0].close, 101.0)
        self.assertEqual(store.get_latest_candle().close, 110.0)

        latest_ind = store.get_latest_indicators()
        self.assertIsNotNone(latest_ind.ema20)

if __name__ == '__main__':
    unittest.main()
