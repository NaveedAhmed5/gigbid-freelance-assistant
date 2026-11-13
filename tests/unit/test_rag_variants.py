from rag.retriever import RAGRetriever

ALL_VARIANTS = [
    "v0_naive",
    "v1_decomposition",
    "v2_hybrid",
    "v3_rerank",
    "v4_outcome_aware",
    "v5_multivector",
    "v6_contextual",
    "v7_hyde",
    "v8_corrective",
    "v9_skill_graph",
]


def test_rag_retriever_all_variants():
    retriever = RAGRetriever(persona="ai_ml_engineer")
    assert len(retriever.chunks) > 0, "No chunks ingested for persona ai_ml_engineer"

    query = "Looking for PyTorch engineer to build high-throughput enterprise RAG pipeline."

    for variant_key in ALL_VARIANTS:
        results = retriever.retrieve(query=query, k=3, variant_override=variant_key)
        assert len(results) > 0, f"Variant {variant_key} returned 0 results"
        top_chunk, score = results[0]
        assert top_chunk.chunk_id, f"Variant {variant_key} missing chunk_id"
        assert score is not None, f"Variant {variant_key} missing score"


def test_rag_retriever_active_variant_from_config():
    retriever = RAGRetriever(persona="ai_ml_engineer")
    # In config.yaml, active_rag_variant is v4_outcome_aware
    results = retriever.retrieve(query="FastAPI distributed vector search", k=3)
    assert len(results) > 0
    # Outcomes in v4 should prioritize won/replied outcomes
    top_chunk, score = results[0]
    assert score > 0

