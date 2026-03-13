# Changelog — Production RAG Code Intelligence System

## 2026-03-11: Full Production Upgrade

### Summary
Complete refactor of the Codebase Analyst from a notebook-based prototype into a production-grade RAG code intelligence system.

---

### New Files

| File | Description |
|------|-------------|
| `.env.example` | Environment variable template with all configurable settings |
| `Dockerfile` | Production container image (Python 3.11 + git) |
| `docker-compose.yml` | Full stack: app, Qdrant, Redis, Prometheus, Grafana |
| `codebase_analyst/models/schemas.py` | Pydantic API request/response schemas |
| `codebase_analyst/models/domain.py` | Internal domain models (CodeChunk, RetrievedCandidate, QueryClassification) |
| `codebase_analyst/services/rerank.py` | Cohere Rerank integration with graceful degradation |
| `codebase_analyst/services/cache.py` | Redis-backed semantic cache with version-aware keys |
| `codebase_analyst/services/retrieval.py` | Full retrieval pipeline: classify→dense→sparse→symbol→graph→fuse→rerank |
| `codebase_analyst/services/answering.py` | Grounded answer generation with citations |
| `codebase_analyst/api/routes/query.py` | POST /api/query endpoint |
| `codebase_analyst/api/routes/ingest.py` | POST /api/ingest endpoint |
| `codebase_analyst/api/routes/health.py` | GET /health and /ready endpoints |
| `codebase_analyst/cli/ingest.py` | CLI: `python -m codebase_analyst.cli.ingest` |
| `codebase_analyst/cli/ask.py` | CLI: `python -m codebase_analyst.cli.ask` |
| `monitoring/prometheus.yml` | Prometheus scrape configuration |
| `monitoring/grafana/dashboards/codebase_analyst.json` | Grafana dashboard (11 panels) |
| `monitoring/grafana/provisioning/datasources/prometheus.yml` | Grafana datasource config |
| `monitoring/grafana/provisioning/dashboards/default.yml` | Grafana dashboard provider config |
| `tests/test_config.py` | Config loading tests |
| `tests/test_chunker.py` | Code chunker tests |
| `tests/test_retrieval.py` | Retrieval pipeline tests |
| `tests/test_cache.py` | Cache behavior tests |

### Modified Files

| File | Changes |
|------|---------|
| `main.py` | Replaced CLI entrypoint with FastAPI app + CORS + metrics middleware |
| `config.py` | Replaced `dataclass` with Pydantic `BaseSettings`, removed Colab detection |
| `llm/provider.py` | Added dual OpenAI + Azure OpenAI support with lazy initialization |
| `ingestion/processor.py` | Added content hashing, incremental re-indexing, git metadata extraction |
| `ingestion/chunker.py` | Structure-aware chunking at function/class boundaries |
| `ingestion/parser.py` | Expanded tree-sitter support (9 languages), improved symbol extraction |
| `indexing/vector_store.py` | Replaced pickle store with Qdrant client + in-memory fallback |
| `indexing/embedding.py` | Updated config imports |
| `indexing/cache.py` | Updated to use logging instead of print |
| `retrieval/sparse.py` | Replaced print with logging |
| `monitoring/metrics.py` | Added HTTP, rerank, indexing, embedding latency metrics |
| `ui/gradio_app.py` | Updated to use new service architecture |
| `core.py` | Refactored to system component manager with `run_ingestion()` and `get_system_components()` |
| `requirements.txt` | Added pydantic-settings, qdrant-client, redis, pytest; organized by category |
| `README.md` | Complete rewrite reflecting new architecture |

### Deleted Files

| File | Reason |
|------|--------|
| `codebase-analyst-optimized.ipynb` | Logic migrated to Python modules |
| `codebase-analyst-old` | Obsolete notebook JSON |

### Design Decisions

1. **Graceful degradation**: Qdrant, Redis, Cohere all fall back silently — system works with just OPENAI_API_KEY
2. **Incremental indexing**: SHA256 content hashing skips unchanged files on re-index
3. **Pydantic Settings**: `.env` auto-loading with type validation
4. **Query classification**: Pattern-based routing (symbol/semantic/architecture/dependency/config)
5. **Version-aware cache keys**: Include repo_name + commit_sha to prevent stale answers
