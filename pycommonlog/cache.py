"""
Caching utilities for commonlog providers
"""
import time
import threading
from typing import Dict, Optional, Tuple, Any


class InMemoryCache:
    """
    Thread-safe in-memory cache with automatic cleanup of expired entries.
    """

    def __init__(self):
        self._cache: Dict[str, Tuple[Any, float]] = {}  # key -> (value, expiry_timestamp)
        self._lock = threading.RLock()
        # Clean up expired entries every 5 minutes
        self._cleanup_thread = threading.Thread(target=self._cleanup_worker, daemon=True)
        self._cleanup_thread.start()

    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache.

        Args:
            key: Cache key

        Returns:
            Cached value if found and not expired, None otherwise
        """
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    return value
                else:
                    # Value expired, remove it
                    del self._cache[key]
            return None

    def set(self, key: str, value: Any, expire_seconds: int):
        """
        Set a value in the cache with expiration.

        Args:
            key: Cache key
            value: Value to cache
            expire_seconds: Expiration time in seconds
        """
        with self._lock:
            expiry = time.time() + expire_seconds
            self._cache[key] = (value, expiry)

    def delete(self, key: str):
        """
        Delete a value from the cache.

        Args:
            key: Cache key to delete
        """
        with self._lock:
            self._cache.pop(key, None)

    def _cleanup_worker(self):
        """Background thread to clean up expired entries"""
        while True:
            time.sleep(300)  # Clean up every 5 minutes
            self._cleanup_expired()

    def _cleanup_expired(self):
        """Remove expired entries from cache"""
        with self._lock:
            current_time = time.time()
            expired_keys = [
                key for key, (_, expiry) in self._cache.items()
                if current_time >= expiry
            ]
            for key in expired_keys:
                del self._cache[key]
            if expired_keys:
                print(f"[Cache] Cleaned up {len(expired_keys)} expired entries from memory cache")


# Global cache instance
_memory_cache = InMemoryCache()


def get_memory_cache() -> InMemoryCache:
    """
    Get the global in-memory cache instance.

    Returns:
        Global InMemoryCache instance
    """
    return _memory_cache