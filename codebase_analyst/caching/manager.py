"""
Advanced cache manager with prefix-based caching and LRU eviction.
Complements the semantic cache with structured key management.
"""
import hashlib
import time
from typing import Any, Optional, Dict
from collections import OrderedDict

class CachedPrefix:
    """Represents a cached prefix for faster lookups"""
    def __init__(self, prefix: str, value: Any, ttl: Optional[int] = None):
        self.prefix = prefix
        self.value = value
        self.created_at = time.time()
        self.ttl = ttl
        self.access_count = 0
        self.last_accessed = time.time()
    
    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return (time.time() - self.created_at) > self.ttl
    
    def access(self):
        self.access_count += 1
        self.last_accessed = time.time()

class CacheManager:
    """
    Advanced cache manager with:
    - Prefix-based caching for common query patterns
    - LRU eviction policy
    - TTL support
    - Statistics tracking
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: Optional[int] = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.cache: OrderedDict[str, CachedPrefix] = OrderedDict()
        self.hits = 0
        self.misses = 0
    
    def _make_key(self, key: str) -> str:
        """Generate cache key"""
        return hashlib.md5(key.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        cache_key = self._make_key(key)
        
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            
            if entry.is_expired():
                del self.cache[cache_key]
                self.misses += 1
                return None
            
            # Move to end (LRU)
            self.cache.move_to_end(cache_key)
            entry.access()
            self.hits += 1
            return entry.value
        
        self.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """Set value in cache"""
        cache_key = self._make_key(key)
        
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size and cache_key not in self.cache:
            self.cache.popitem(last=False)
        
        ttl = ttl if ttl is not None else self.default_ttl
        self.cache[cache_key] = CachedPrefix(key, value, ttl)
        self.cache.move_to_end(cache_key)
    
    def invalidate(self, key: str):
        """Invalidate specific cache entry"""
        cache_key = self._make_key(key)
        if cache_key in self.cache:
            del self.cache[cache_key]
    
    def invalidate_prefix(self, prefix: str):
        """Invalidate all entries matching prefix"""
        to_remove = [k for k, v in self.cache.items() if v.prefix.startswith(prefix)]
        for k in to_remove:
            del self.cache[k]
    
    def clear(self):
        """Clear entire cache"""
        self.cache.clear()
        self.hits = 0
        self.misses = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0.0
        
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'total_requests': total
        }
