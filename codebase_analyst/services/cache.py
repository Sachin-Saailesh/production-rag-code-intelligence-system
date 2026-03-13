"""
Redis-backed semantic cache with version-aware keys.
Falls back to in-memory LRU cache when Redis is unavailable.
"""
import hashlib
import json
import logging
import time
from typing import Any, Optional, Dict

from ..config import settings
from ..monitoring.metrics import metrics

logger = logging.getLogger(__name__)


def _get_redis():
    """Lazily connect to Redis; returns None if unavailable."""
    try:
        import redis
        client = redis.from_url(settings.redis_url, decode_responses=True)
        client.ping()
        return client
    except Exception as e:
        logger.warning("Redis unavailable (%s) — using in-memory cache", e)
        return None


class SemanticCache:
    """
    Cache query results keyed on (query, repo_name, index_version).
    Uses Redis when available, otherwise falls back to in-memory dict.
    """

    def __init__(self):
        self._redis = _get_redis()
        self._memory: Dict[str, Dict[str, Any]] = {}
        self._hits = 0
        self._misses = 0

    def _make_key(self, query: str, repo_name: str = "", index_version: str = "") -> str:
        raw = f"{query.strip().lower()}|{repo_name}|{index_version}"
        return f"ca:cache:{hashlib.sha256(raw.encode()).hexdigest()}"

    def get(
        self, query: str, repo_name: str = "", index_version: str = ""
    ) -> Optional[Dict[str, Any]]:
        key = self._make_key(query, repo_name, index_version)

        if self._redis:
            try:
                data = self._redis.get(key)
                if data:
                    self._hits += 1
                    metrics.record_cache_hit()
                    return json.loads(data)
            except Exception as e:
                logger.warning("Redis GET error: %s", e)

        # In-memory fallback
        if key in self._memory:
            entry = self._memory[key]
            # TTL check
            if time.time() - entry.get("_ts", 0) < settings.cache_ttl:
                self._hits += 1
                metrics.record_cache_hit()
                return entry.get("value")
            else:
                del self._memory[key]

        self._misses += 1
        metrics.record_cache_miss()
        return None

    def set(
        self,
        query: str,
        value: Dict[str, Any],
        repo_name: str = "",
        index_version: str = "",
    ) -> None:
        key = self._make_key(query, repo_name, index_version)
        serialized = json.dumps(value, default=str)

        if self._redis:
            try:
                self._redis.setex(key, settings.cache_ttl, serialized)
                return
            except Exception as e:
                logger.warning("Redis SET error: %s", e)

        # In-memory fallback
        self._memory[key] = {"value": value, "_ts": time.time()}
        # Simple eviction if too large
        if len(self._memory) > 1000:
            oldest = next(iter(self._memory))
            del self._memory[oldest]

    def invalidate(self, query: str, repo_name: str = "", index_version: str = "") -> None:
        key = self._make_key(query, repo_name, index_version)
        if self._redis:
            try:
                self._redis.delete(key)
            except Exception:
                pass
        self._memory.pop(key, None)

    def flush(self) -> None:
        if self._redis:
            try:
                for key in self._redis.scan_iter("ca:cache:*"):
                    self._redis.delete(key)
            except Exception:
                pass
        self._memory.clear()

    @property
    def stats(self) -> Dict[str, Any]:
        total = self._hits + self._misses
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0.0,
            "backend": "redis" if self._redis else "memory",
        }
