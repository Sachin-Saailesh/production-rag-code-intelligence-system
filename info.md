# Project Info: LinkedIn Post & Resume Drafts

## 📸 Recommended Screenshots for LinkedIn
To make your post visually engaging and prove the system works, capture these specific screenshots from your deployed Vercel app:

1. **The Ingestion Progress Stream (Action Shot)**
   - Start indexing `encode/httpx`.
   - Take a screenshot while the progress bar is actively moving, showing the "Parsing and chunking X files..." or "Computing dense vector embeddings..." real-time SSE stream.
   - *Why:* Proves the streaming architecture and real-time frontend/backend connection.

2. **A Deep Architectural Query (Results Shot)**
   - Ask a complex technical question like: *"How does the AsyncClient handle connection pooling?"*
   - Take a screenshot of the detailed LLM answer alongside the **File Citations** and **Thinking Steps** on the side/bottom.
   - *Why:* Demonstrates data intuition, accurate RAG retrieval, and clean UI design.

3. **The Multi-Repo / Settings Sidebar (System Shot)**
   - Take a screenshot showing the sidebar where multiple repositories are listed, or the tools pipeline page.
   - *Why:* Highlights multi-tenant architectural foresight.

---

## 📝 LinkedIn Post Draft

**Hook:** 
Most AI coding tutorials teach you how to build a RAG app in a Jupyter notebook. Very few teach you how to design a scalable software architecture capable of ingesting and understanding enterprise-scale codebases.

**Body:**
Last spring, I built a prototype for an AI Codebase Intelligence System. Recently, I decided to pull it out of the archives, completely overhaul the architecture, and launch it to production: https://production-rag-code-intelligence-sy-ebon.vercel.app/

Taking this from a local script to a deployed, multi-tenant web application was a massive exercise in what I call **Systemic Engineering**—the ability to build stable, infinitely scalable software around an AI model, rather than just developing the model in isolation.

A few architectural milestones from the redesign:

🔹 **Systemic Engineering:** I rewrote the core ingestion pipeline into a flat-memory streaming generator. By parsing, chunking, and embedding one file at a time, the architecture scales linearly. It can effortlessly ingest 10,000+ file repositories without locking up resources or encountering memory spikes.
🔹 **Data Intuition:** Standard NLP text splitters destroy programming context. I implemented `tree-sitter` to parse the Abstract Syntax Tree (AST), ensuring code is chunked cleanly at logical function and class boundaries, drastically improving LLM retrieval accuracy. 
🔹 **Architectural Foresight:** Built a production-grade Hybrid Retrieval engine natively fusing Dense embeddings (Qdrant & OpenAI `text-embedding-3-small`) with Sparse lexical matching (BM25/TF-IDF). This ensures perfect results for both deep architectural concepts and exact variable name lookups.
🔹 **Translation:** Built a dynamic fallback priority queue where the system gracefully degrades if Redis caching or Cohere reranking API limits are ever hit, ensuring the core chat experience remains uninterrupted for the end user.

It's one thing to build an LLM workflow; it's another to engineer a resilient, scalable system around it. 

If you want to test the architecture, I recommend pasting in `https://github.com/encode/httpx.git` to see the real-time vectorization pipeline in action!

#SoftwareEngineering #SystemDesign #AI #RAG #MachineLearning #WebDevelopment #Backend

---

## 📄 Resume Draft (Bullet Points)

**AI Codebase Intelligence Platform (Full-Stack / AI Engineer)** 
*React, FastAPI, Qdrant, Redis, OpenAI, Tree-sitter*
* Architected and deployed a multi-tenant Production RAG application capable of ingesting remote Git repositories, parsing structural ASTs, and answering complex architectural codebase queries.
* **Systemic Engineering:** Engineered a highly-optimized, flat-memory data streaming pipeline for code ingestion that parses, chunks, and embeddings files individually, allowing the system to scale linearly and process 10,000+ file repositories without memory spikes.
* **Data Intuition & Retrieval:** Replaced basic string chunking with `tree-sitter` AST parsing to preserve function semantics, and implemented a Hybrid Search engine combining Dense (Qdrant/OpenAI) and Sparse (BM25/TF-IDF) vector retrieval to maximize citation accuracy.
* **Architectural Foresight:** Designed the system for graceful degradation and enterprise scaling; implemented dynamic fallback queues for Redis caching and Cohere reranking, and established strict multi-tenant data isolation using namespaced Qdrant collections.
* **Validation & UI:** Built a responsive React/Vite frontend with Server-Sent Events (SSE) to stream real-time granular ingestion progress, optimizing the developer experience while preventing connection timeouts during massive repository scans.
