# ADR 003: Hybrid Lexical-Dense RAG with Outcome-Aware Evidence Boosting

## Context & Problem Statement
In R&D Question B, we benchmarked 10 RAG variants (`V0` to `V9`) across 3 distinct technical persona corpora (AI/ML, Full-Stack, Data Analyst).
Dense cosine retrieval alone (`V0`) achieved only 58% Recall@5 and frequently missed exact framework names (e.g. `dbt`, `vLLM`, `Snowflake`). Conversely, purely lexical matching failed to capture semantic project intent.

## Decision
We adopted `Variant V4 (Outcome-Aware Boosting)` over a hybrid BM25 + Dense vector retrieval foundation with Reciprocal Rank Fusion (RRF):
1. **Hybrid Retrieval:** Reciprocal Rank Fusion fuses BM25 lexical keyword matches with dense vector embeddings.
2. **Outcome-Aware Multipliers:** Historical winning proposals (`won`) apply a +35% score multiplier to associated case studies and proof points, while `ignored` outcomes apply a -25% penalty.
3. **Claim Verification Sanitization:** Extracted atomic claims are verified against retrieved evidence prior to proposal submission.

## Consequences
- **Positive:** Recall@5 increased from 58% (`V0`) to 94% (`V4`); unsupported claims per proposal dropped from 1.8 to 0.10.
- **Negative:** Slightly increased indexing and retrieval latency (~380ms vs 80ms naive), well within the 30-second system SLA.
