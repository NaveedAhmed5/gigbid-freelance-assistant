"""Variant V4: Outcome-Aware Evidence Boosting."""

from typing import List, Tuple

from rag.index.dense import DenseVectorIndex
from rag.index.sparse import BM25Index
from rag.ingest.loader import DocumentChunk
from rag.variants.v3_rerank import VariantV3Rerank


class VariantV4OutcomeAware:
    def __init__(self, dense_index: DenseVectorIndex, bm25_index: BM25Index):
        self.reranker = VariantV3Rerank(dense_index, bm25_index)

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        candidates = self.reranker.retrieve(query, k=k * 2)
        outcome_adjusted: List[Tuple[DocumentChunk, float]] = []

        for chunk, base_score in candidates:
            multiplier = 1.0
            meta = chunk.metadata

            # Boost proven won outcomes
            if meta.get("outcome") == "won":
                multiplier += 0.35
            elif meta.get("outcome") == "replied":
                multiplier += 0.15
            elif meta.get("outcome") == "ignored":
                multiplier -= 0.25

            # Boost projects with high metric improvements
            metric = meta.get("metric_improvement_pct")
            if metric and metric > 25.0:
                multiplier += 0.15

            adjusted_score = round(base_score * multiplier, 4)
            outcome_adjusted.append((chunk, adjusted_score))

        outcome_adjusted.sort(key=lambda x: x[1], reverse=True)
        return outcome_adjusted[:k]
