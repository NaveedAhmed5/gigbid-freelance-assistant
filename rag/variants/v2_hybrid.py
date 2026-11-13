"""Variant V2: Hybrid Lexical (BM25) + Dense with Reciprocal Rank Fusion (RRF)."""

from typing import Dict, List, Tuple

from rag.index.dense import DenseVectorIndex
from rag.index.sparse import BM25Index
from rag.ingest.loader import DocumentChunk


class VariantV2Hybrid:
    def __init__(self, dense_index: DenseVectorIndex, bm25_index: BM25Index, rrf_c: int = 60):
        self.dense_index = dense_index
        self.bm25_index = bm25_index
        self.rrf_c = rrf_c

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        dense_results = self.dense_index.search(query, k=k * 2)
        sparse_results = self.bm25_index.search(query, k=k * 2)

        rrf_scores: Dict[str, Tuple[DocumentChunk, float]] = {}

        # Dense ranks
        for rank, (chunk, _) in enumerate(dense_results, 1):
            score = 1.0 / (self.rrf_c + rank)
            rrf_scores[chunk.chunk_id] = (chunk, score)

        # Sparse ranks
        for rank, (chunk, _) in enumerate(sparse_results, 1):
            score = 1.0 / (self.rrf_c + rank)
            if chunk.chunk_id in rrf_scores:
                existing_c, existing_s = rrf_scores[chunk.chunk_id]
                rrf_scores[chunk.chunk_id] = (existing_c, existing_s + score)
            else:
                rrf_scores[chunk.chunk_id] = (chunk, score)

        ranked = sorted(rrf_scores.values(), key=lambda x: x[1], reverse=True)
        return ranked[:k]
