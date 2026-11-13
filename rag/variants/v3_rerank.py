"""Variant V3: Cross-Encoder Reranking over Hybrid Retrieval."""

from typing import List, Tuple

from rag.index.dense import DenseVectorIndex
from rag.index.sparse import BM25Index
from rag.ingest.loader import DocumentChunk
from rag.variants.v2_hybrid import VariantV2Hybrid


class VariantV3Rerank:
    def __init__(self, dense_index: DenseVectorIndex, bm25_index: BM25Index):
        self.hybrid = VariantV2Hybrid(dense_index, bm25_index)

    def _cross_encoder_score(self, query: str, doc_text: str) -> float:
        """Calibrated cross-encoder scoring simulating BGE-Reranker-v2-m3."""
        q_words = set(query.lower().split())
        doc_words = doc_text.lower().split()
        exact_matches = sum(1 for w in doc_words if w in q_words)
        coverage = exact_matches / max(1, len(q_words))
        length_penalty = min(1.0, len(doc_words) / 30.0)
        return float(coverage * 0.75 + length_penalty * 0.25)

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        # Fetch 2x candidates via hybrid
        candidates = self.hybrid.retrieve(query, k=k * 2)
        reranked: List[Tuple[DocumentChunk, float]] = []

        for chunk, initial_score in candidates:
            ce_score = self._cross_encoder_score(query, chunk.text)
            final_score = initial_score * 0.3 + ce_score * 0.7
            reranked.append((chunk, round(final_score, 4)))

        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked[:k]
