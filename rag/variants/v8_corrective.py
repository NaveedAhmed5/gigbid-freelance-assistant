"""Variant V8: Corrective Retrieval-Augmented Generation (CRAG)."""

from typing import List, Tuple

from rag.index.dense import DenseVectorIndex
from rag.ingest.loader import DocumentChunk


class VariantV8Corrective:
    def __init__(self, dense_index: DenseVectorIndex, threshold: float = 0.35):
        self.dense_index = dense_index
        self.threshold = threshold

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        initial_results = self.dense_index.search(query, k=k)

        # Grade retrieval confidence
        avg_score = (
            sum(s for _, s in initial_results) / len(initial_results) if initial_results else 0.0
        )

        if avg_score >= self.threshold:
            return initial_results

        # Corrective fallback: query reformulation
        tokens = [t for t in query.split() if len(t) > 3]
        broad_query = " ".join(tokens[:3]) if tokens else query
        fallback_results = self.dense_index.search(broad_query, k=k)
        return fallback_results if fallback_results else initial_results
