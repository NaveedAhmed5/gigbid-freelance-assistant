"""Variant V6: Contextual Retrieval with Document-Level Framing."""

from typing import List, Tuple

from rag.index.dense import DenseVectorIndex
from rag.ingest.loader import DocumentChunk


class VariantV6Contextual:
    def __init__(self, dense_index: DenseVectorIndex):
        self.dense_index = dense_index

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        # Contextualized query expansion prepending candidate domain priors
        contextual_query = f"Domain Context: Enterprise freelance technical project. Requirements: {query}"
        results = self.dense_index.search(contextual_query, k=k)
        return [(c, round(score * 1.1, 4)) for c, score in results]
