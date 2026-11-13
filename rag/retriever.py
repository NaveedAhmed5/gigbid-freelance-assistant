"""Unified RAG Retriever Dispatcher & Dynamic Variant Router."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from agent.config import load_agent_config
from rag.index.dense import DenseVectorIndex
from rag.index.graph import SkillKnowledgeGraph
from rag.index.sparse import BM25Index
from rag.ingest.loader import DocumentChunk, IngestionEngine
from rag.variants.v0_naive import VariantV0Naive
from rag.variants.v1_decomposition import VariantV1Decomposition
from rag.variants.v2_hybrid import VariantV2Hybrid
from rag.variants.v3_rerank import VariantV3Rerank
from rag.variants.v4_outcome_aware import VariantV4OutcomeAware
from rag.variants.v5_multivector import VariantV5MultiVector
from rag.variants.v6_contextual import VariantV6Contextual
from rag.variants.v7_hyde import VariantV7HyDE
from rag.variants.v8_corrective import VariantV8Corrective
from rag.variants.v9_skill_graph import VariantV9SkillGraph


class RAGRetriever:
    def __init__(self, persona: str = "ai_ml_engineer", config_path: Optional[Path] = None):
        self.persona = persona
        self.config = load_agent_config(config_path)
        self.ingestion = IngestionEngine()
        self.chunks: List[DocumentChunk] = []

        # Indexes
        self.dense_index = DenseVectorIndex()
        self.bm25_index = BM25Index()
        self.graph_index = SkillKnowledgeGraph()

        # Build corpus
        self.reload_corpus(persona)

        # Initialize variants
        self.variants: Dict[str, Any] = {
            "v0_naive": VariantV0Naive(self.dense_index),
            "v1_decomposition": VariantV1Decomposition(self.dense_index),
            "v2_hybrid": VariantV2Hybrid(self.dense_index, self.bm25_index),
            "v3_rerank": VariantV3Rerank(self.dense_index, self.bm25_index),
            "v4_outcome_aware": VariantV4OutcomeAware(self.dense_index, self.bm25_index),
            "v5_multivector": VariantV5MultiVector(self.dense_index),
            "v6_contextual": VariantV6Contextual(self.dense_index),
            "v7_hyde": VariantV7HyDE(self.dense_index),
            "v8_corrective": VariantV8Corrective(self.dense_index),
            "v9_skill_graph": VariantV9SkillGraph(self.graph_index),
        }

    def reload_corpus(self, persona: str):
        self.persona = persona
        self.chunks = self.ingestion.load_persona_corpus(persona)
        self.dense_index.build_index(self.chunks)
        self.bm25_index.build_index(self.chunks)
        self.graph_index.build_graph(self.chunks)

    def retrieve(
        self, query: str, k: int = 5, variant_override: Optional[str] = None
    ) -> List[Tuple[DocumentChunk, float]]:
        active_variant_key = variant_override or self.config.active_rag_variant
        if active_variant_key not in self.variants:
            raise KeyError(
                f"RAG variant '{active_variant_key}' not found. Available: {list(self.variants.keys())}"
            )
        variant = self.variants[active_variant_key]
        return variant.retrieve(query, k=k)
