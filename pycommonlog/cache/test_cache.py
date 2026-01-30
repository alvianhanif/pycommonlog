"""
Tests for the cache module
"""
import time
import unittest
from pycommonlog.cache import InMemoryCache, get_memory_cache


class TestInMemoryCache(unittest.TestCase):
    def setUp(self):
        self.cache = InMemoryCache()

    def test_set_and_get(self):
        """Test basic set and get operations"""
        self.cache.set("test_key", "test_value", 60)
        value = self.cache.get("test_key")
        self.assertEqual(value, "test_value")

    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist"""
        value = self.cache.get("nonexistent")
        self.assertIsNone(value)

    def test_expiration(self):
        """Test that entries expire correctly"""
        self.cache.set("expire_key", "expire_value", 1)  # 1 second
        time.sleep(1.1)  # Wait for expiration
        value = self.cache.get("expire_key")
        self.assertIsNone(value)

    def test_delete(self):
        """Test deleting entries"""
        self.cache.set("delete_key", "delete_value", 60)
        self.assertEqual(self.cache.get("delete_key"), "delete_value")

        self.cache.delete("delete_key")
        self.assertIsNone(self.cache.get("delete_key"))

    def test_thread_safety(self):
        """Test that the cache is thread-safe"""
        import threading
        import concurrent.futures

        results = []
        errors = []

        def worker(worker_id):
            try:
                # Each worker sets and gets its own key
                key = f"worker_{worker_id}"
                value = f"value_{worker_id}"
                self.cache.set(key, value, 60)

                # Small delay to increase chance of race conditions
                time.sleep(0.01)

                retrieved = self.cache.get(key)
                if retrieved != value:
                    errors.append(f"Worker {worker_id}: expected {value}, got {retrieved}")
                else:
                    results.append(f"Worker {worker_id}: OK")
            except Exception as e:
                errors.append(f"Worker {worker_id}: {e}")

        # Run multiple threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(worker, i) for i in range(10)]
            concurrent.futures.wait(futures)

        self.assertEqual(len(errors), 0, f"Thread safety errors: {errors}")
        self.assertEqual(len(results), 10, "Not all workers completed successfully")


class TestGlobalCache(unittest.TestCase):
    def test_get_memory_cache(self):
        """Test getting the global cache instance"""
        cache = get_memory_cache()
        self.assertIsInstance(cache, InMemoryCache)

    def test_global_cache_persistence(self):
        """Test that the global cache persists across calls"""
        cache1 = get_memory_cache()
        cache2 = get_memory_cache()
        self.assertIs(cache1, cache2, "Global cache should be a singleton")

        # Test that data persists
        cache1.set("global_test", "global_value", 60)
        self.assertEqual(cache2.get("global_test"), "global_value")


if __name__ == '__main__':
    unittest.main()
