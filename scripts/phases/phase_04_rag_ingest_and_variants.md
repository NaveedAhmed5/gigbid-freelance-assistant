# Phase 4: Part B (1/2) — Advanced RAG Ingestion & Variants (V0–V9)

## Objectives
1. Implement `rag/ingest/`:
   - Loaders for PDF/Markdown CVs, Case studies, GitHub repositories (README & code), reviews, and past proposals.
   - Preserves rich metadata and supports incremental re-indexing.
2. Implement `rag/index/`:
   - Dense vector index (configurable local fallback embedding / BGE-M3).
   - BM25 lexical index.
   - NetworkX multi-relational graph index (skills, projects, client industries, outcomes).
3. Implement 10 RAG Variants in `rag/variants/`:
   - `v0_naive.py`: Dense cosine similarity on full job post.
   - `v1_decomposition.py`: Per-requirement sub-query decomposition and reciprocal merge.
   - `v2_hybrid.py`: BM25 lexical + Dense embedding with Reciprocal Rank Fusion (RRF).
   - `v3_rerank.py`: Cross-encoder reranker over hybrid candidates.
   - `v4_outcome_aware.py`: Weighted boosting for evidence from `won`/`replied` past proposals.
   - `v5_multivector.py`: Separate child vectors for summaries, code, and READMEs, grouped by parent project.
   - `v6_contextual.py`: Prepends document-level contextual summary header to chunks before embedding.
   - `v7_hyde.py`: Generates hypothetical winning proposal, embeds it, and retrieves matching evidence.
   - `v8_corrective.py`: Evaluator checks retrieval relevance; falls back or reformulates query if below threshold.
   - `v9_skill_graph.py`: GraphRAG traversal connecting requirements -> skills -> projects -> outcomes.
4. Wire `rag/retriever.py` to route queries to active variant in `agent/config.yaml`.
5. Verification:
   - Run tests in `tests/unit/test_rag_variants.py`.
