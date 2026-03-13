"""
Prometheus-based monitoring for the Codebase Analyst.
Tracks requests, latency, cache hits, retrieval, rerank, indexing, and system metrics.
"""
from prometheus_client import Counter, Histogram, Gauge
import psutil
import time


# --- Request Metrics ---
query_counter = Counter(
    "codebase_analyst_queries_total",
    "Total queries processed",
    ["status"],
)

query_latency = Histogram(
    "codebase_analyst_query_latency_seconds",
    "End-to-end query latency",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0],
)

http_requests = Counter(
    "codebase_analyst_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_latency = Histogram(
    "codebase_analyst_http_latency_seconds",
    "HTTP request latency",
    ["method", "endpoint"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

# --- LLM Metrics ---
llm_latency = Histogram(
    "codebase_analyst_llm_latency_seconds",
    "LLM call latency",
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0],
)

# --- Retrieval Metrics ---
retrieval_latency = Histogram(
    "codebase_analyst_retrieval_latency_seconds",
    "Retrieval latency",
)

chunks_retrieved = Histogram(
    "codebase_analyst_chunks_retrieved",
    "Chunks retrieved per query",
    buckets=[1, 3, 5, 10, 20, 50],
)

# --- Rerank Metrics ---
rerank_latency_hist = Histogram(
    "codebase_analyst_rerank_latency_seconds",
    "Cohere rerank latency",
    buckets=[0.05, 0.1, 0.25, 0.5, 1.0, 2.0],
)

# --- Cache Metrics ---
cache_hits = Counter("codebase_analyst_cache_hits_total", "Cache hits")
cache_misses = Counter("codebase_analyst_cache_misses_total", "Cache misses")

# --- Indexing Metrics ---
indexing_runs = Counter("codebase_analyst_indexing_runs_total", "Indexing runs")
indexed_files = Counter("codebase_analyst_indexed_files_total", "Files indexed")
indexed_chunks = Counter("codebase_analyst_indexed_chunks_total", "Chunks indexed")
embedding_latency = Histogram(
    "codebase_analyst_embedding_latency_seconds",
    "Embedding generation latency",
    buckets=[0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0],
)

# --- System Metrics ---
cpu_usage = Gauge("codebase_analyst_cpu_percent", "CPU usage percentage")
memory_usage = Gauge("codebase_analyst_memory_mb", "Memory usage in MB")


class MetricsCollector:
    """Centralized metrics collection."""

    def __init__(self):
        self.start_time = time.time()

    def record_query(self, status: str = "success"):
        query_counter.labels(status=status).inc()

    def record_query_latency(self, latency: float):
        query_latency.observe(latency)

    def record_http_request(self, method: str, endpoint: str, status_code: int, latency: float):
        http_requests.labels(method=method, endpoint=endpoint, status_code=str(status_code)).inc()
        http_latency.labels(method=method, endpoint=endpoint).observe(latency)

    def record_llm_latency(self, latency: float):
        llm_latency.observe(latency)

    def record_cache_hit(self):
        cache_hits.inc()

    def record_cache_miss(self):
        cache_misses.inc()

    def record_retrieval(self, latency: float, num_chunks: int):
        retrieval_latency.observe(latency)
        chunks_retrieved.observe(num_chunks)

    def record_rerank_latency(self, latency: float):
        rerank_latency_hist.observe(latency)

    def record_indexing(self, num_files: int, num_chunks: int):
        indexing_runs.inc()
        indexed_files.inc(num_files)
        indexed_chunks.inc(num_chunks)

    def record_embedding_latency(self, latency: float):
        embedding_latency.observe(latency)

    def update_system_metrics(self):
        cpu_usage.set(psutil.cpu_percent())
        memory_usage.set(psutil.Process().memory_info().rss / 1024 / 1024)

    def get_cache_hit_rate(self) -> float:
        hits = cache_hits._value.get()
        misses = cache_misses._value.get()
        total = hits + misses
        return hits / total if total > 0 else 0.0


metrics = MetricsCollector()
