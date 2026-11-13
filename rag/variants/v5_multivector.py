"""Variant V5: Multi-Vector Child Chunking with Unified Parent Representation."""

from typing import Dict, List, Tuple

from rag.index.dense import DenseVectorIndex
from rag.ingest.loader import DocumentChunk


class VariantV5MultiVector:
    def __init__(self, dense_index: DenseVectorIndex):
        self.dense_index = dense_index

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        child_results = self.dense_index.search(query, k=k * 3)
        parent_map: Dict[str, Tuple[DocumentChunk, float]] = {}

        for chunk, score in child_results:
            # Group by parent project / case study ID
            parent_key = chunk.metadata.get("case_study_id") or chunk.metadata.get("repo") or chunk.chunk_id
            if parent_key not in parent_map:
                parent_map[parent_key] = (chunk, score)
            else:
                existing_c, existing_s = parent_map[parent_key]
                parent_map[parent_key] = (existing_c, max(existing_s, score) + 0.1)

        ranked = sorted(parent_map.values(), key=lambda x: x[1], reverse=True)
        return ranked[:k]
