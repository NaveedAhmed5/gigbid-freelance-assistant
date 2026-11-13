"""Variant V0: Naive Dense Cosine Retrieval."""

from typing import List, Tuple

from rag.index.dense import DenseVectorIndex
from rag.ingest.loader import DocumentChunk


class VariantV0Naive:
    def __init__(self, dense_index: DenseVectorIndex):
        self.dense_index = dense_index

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        return self.dense_index.search(query, k=k)
