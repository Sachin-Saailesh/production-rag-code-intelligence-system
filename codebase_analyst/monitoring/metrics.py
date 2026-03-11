"""
Prometheus-based monitoring for the Codebase Analyst.
Tracks requests, latency, cache hits, and system metrics.
"""
from prometheus_client import Counter, Histogram, Gauge, REGISTRY
import psutil
import time
from typing import Optional

# Request Metrics
query_counter = Counter(
    'codebase_analyst_queries_total',
    'Total number of queries processed',
    ['status']
)

query_latency = Histogram(
    'codebase_analyst_query_latency_seconds',
    'Query processing latency in seconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0]
)

llm_latency = Histogram(
    'codebase_analyst_llm_latency_seconds',
    'LLM call latency in seconds',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
)

# Cache Metrics
cache_hits = Counter('codebase_analyst_cache_hits_total', 'Number of cache hits')
cache_misses = Counter('codebase_analyst_cache_misses_total', 'Number of cache misses')

# Retrieval Metrics
retrieval_latency = Histogram(
    'codebase_analyst_retrieval_latency_seconds',
    'Retrieval latency in seconds'
)

chunks_retrieved = Histogram(
    'codebase_analyst_chunks_retrieved',
    'Number of chunks retrieved per query',
    buckets=[1, 3, 5, 10, 20, 50]
)

# System Metrics
cpu_usage = Gauge('codebase_analyst_cpu_percent', 'CPU usage percentage')
memory_usage = Gauge('codebase_analyst_memory_mb', 'Memory usage in MB')

class MetricsCollector:
    """Centralized metrics collection"""
    
    def __init__(self):
        self.start_time = time.time()
        
    def record_query(self, status: str = 'success'):
        """Record a query with status"""
        query_counter.labels(status=status).inc()
    
    def record_query_latency(self, latency: float):
        """Record query processing time"""
        query_latency.observe(latency)
    
    def record_llm_latency(self, latency: float):
        """Record LLM call time"""
        llm_latency.observe(latency)
    
    def record_cache_hit(self):
        """Record cache hit"""
        cache_hits.inc()
    
    def record_cache_miss(self):
        """Record cache miss"""
        cache_misses.inc()
    
    def record_retrieval(self, latency: float, num_chunks: int):
        """Record retrieval metrics"""
        retrieval_latency.observe(latency)
        chunks_retrieved.observe(num_chunks)
    
    def update_system_metrics(self):
        """Update system resource metrics"""
        cpu_usage.set(psutil.cpu_percent())
        memory_usage.set(psutil.Process().memory_info().rss / 1024 / 1024)
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        hits = cache_hits._value.get()
        misses = cache_misses._value.get()
        total = hits + misses
        return hits / total if total > 0 else 0.0

# Global metrics instance
metrics = MetricsCollector()
