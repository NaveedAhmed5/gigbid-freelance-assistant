"""Variant V7: Hypothetical Document Embeddings (HyDE)."""

from typing import List, Tuple

from rag.index.dense import DenseVectorIndex
from rag.ingest.loader import DocumentChunk


class VariantV7HyDE:
    def __init__(self, dense_index: DenseVectorIndex):
        self.dense_index = dense_index

    def _generate_hypothetical_proposal(self, query: str) -> str:
        """Construct synthetic ideal winning proposal based on query keywords."""
        words = query.split()
        key_skills = [w for w in words if len(w) > 4][:4]
        return (
            f"I have extensive enterprise experience delivering {' '.join(key_skills)}. "
            f"In a similar project, we deployed high-throughput architecture achieving "
            f"sub-50ms latency and 45% measurable ROI. Verified in production."
        )

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        hypothetical_doc = self._generate_hypothetical_proposal(query)
        # Search using both original query and hypothetical proposal
        direct_results = self.dense_index.search(query, k=k)
        hyde_results = self.dense_index.search(hypothetical_doc, k=k)

        # Merge results
        merged = {}
        for c, s in direct_results:
            merged[c.chunk_id] = (c, s * 0.4)
        for c, s in hyde_results:
            if c.chunk_id in merged:
                ec, es = merged[c.chunk_id]
                merged[c.chunk_id] = (ec, es + s * 0.6)
            else:
                merged[c.chunk_id] = (c, s * 0.6)

        ranked = sorted(merged.values(), key=lambda x: x[1], reverse=True)
        return ranked[:k]
