"""Variant V1: Per-Requirement Query Decomposition & Merge."""

from typing import Dict, List, Tuple

from rag.index.dense import DenseVectorIndex
from rag.ingest.loader import DocumentChunk


class VariantV1Decomposition:
    def __init__(self, dense_index: DenseVectorIndex):
        self.dense_index = dense_index

    def _decompose_query(self, query: str) -> List[str]:
        # Split complex query into distinct clauses/sentences
        sentences = [s.strip() for s in query.replace(";", ".").split(".") if len(s.strip()) > 8]
        return sentences if sentences else [query]

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        subqueries = self._decompose_query(query)
        merged_scores: Dict[str, Tuple[DocumentChunk, float]] = {}

        for sq in subqueries:
            sub_results = self.dense_index.search(sq, k=k)
            for chunk, score in sub_results:
                if chunk.chunk_id not in merged_scores:
                    merged_scores[chunk.chunk_id] = (chunk, score)
                else:
                    # Accumulate score across decomposed requirements
                    existing_chunk, existing_score = merged_scores[chunk.chunk_id]
                    merged_scores[chunk.chunk_id] = (existing_chunk, existing_score + score)

        ranked = sorted(merged_scores.values(), key=lambda x: x[1], reverse=True)
        return ranked[:k]
