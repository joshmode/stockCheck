import unittest
from stock_tracker.cache.manager import LRUCache

class TestCache(unittest.TestCase):
    def test_lru_cache(self):
        cache = LRUCache(capacity=3)

        cache.put("A", 1)
        cache.put("B", 2)
        cache.put("C", 3)

        self.assertEqual(cache.get("A"), 1)
        # Order: B, C, A

        cache.put("D", 4)
        # B should be evicted
        self.assertIsNone(cache.get("B"))
        self.assertEqual(cache.get("A"), 1)
        self.assertEqual(cache.get("C"), 3)
        self.assertEqual(cache.get("D"), 4)

        # Update existing
        cache.put("C", 30)
        # Order: A, D, C
        self.assertEqual(cache.get("C"), 30)

        cache.put("E", 5)
        # A should be evicted
        self.assertIsNone(cache.get("A"))
        self.assertEqual(cache.get("D"), 4)
        self.assertEqual(cache.get("C"), 30)
        self.assertEqual(cache.get("E"), 5)

if __name__ == '__main__':
    unittest.main()
