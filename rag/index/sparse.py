"""BM25 Lexical Index using Rank-BM25."""

import re
from typing import List, Tuple

from rank_bm25 import BM25Okapi

from rag.ingest.loader import DocumentChunk


def tokenize(text: str) -> List[str]:
    return [t for t in re.findall(r"\w+", text.lower()) if len(t) > 1]


class BM25Index:
    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.bm25: BM25Okapi | None = None

    def build_index(self, chunks: List[DocumentChunk]):
        self.chunks = chunks
        if not chunks:
            self.bm25 = None
            return
        corpus = [tokenize(c.text) for c in chunks]
        self.bm25 = BM25Okapi(corpus)

    def search(self, query: str, k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        if not self.bm25 or len(self.chunks) == 0:
            return []
        tokenized_q = tokenize(query)
        if not tokenized_q:
            return []
        scores = self.bm25.get_scores(tokenized_q)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [(self.chunks[i], float(scores[i])) for i in top_indices]
