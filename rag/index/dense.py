"""Dense Vector Index with Cosine Similarity and Deterministic Fallback."""

import hashlib
from typing import List, Optional, Tuple

import numpy as np

from rag.ingest.loader import DocumentChunk

EMBEDDING_DIM = 256


class DenseVectorIndex:
    def __init__(self, dim: int = EMBEDDING_DIM):
        self.dim = dim
        self.chunks: List[DocumentChunk] = []
        self.vectors: Optional[np.ndarray] = None

    def _embed_text(self, text: str) -> np.ndarray:
        """Deterministic dense embedding generator for CPU benchmarking and fast testing."""
        tokens = text.lower().split()
        vec = np.zeros(self.dim, dtype=np.float32)
        for i, token in enumerate(tokens):
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            weight = 1.0 / (1.0 + np.log(1.0 + i))
            vec[idx] += weight
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def build_index(self, chunks: List[DocumentChunk]):
        self.chunks = chunks
        if not chunks:
            self.vectors = np.empty((0, self.dim), dtype=np.float32)
            return
        vecs = [self._embed_text(c.text) for c in chunks]
        self.vectors = np.vstack(vecs)

    def search(self, query: str, k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        if self.vectors is None or len(self.chunks) == 0:
            return []
        q_vec = self._embed_text(query)
        # Cosine similarity
        scores = np.dot(self.vectors, q_vec)
        top_k_indices = np.argsort(scores)[::-1][:k]
        return [(self.chunks[i], float(scores[i])) for i in top_k_indices]
