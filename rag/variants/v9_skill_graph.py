"""Variant V9: GraphRAG Multi-Hop Skill-Project-Outcome Traversal."""

from typing import List, Tuple

from rag.index.graph import SkillKnowledgeGraph
from rag.ingest.loader import DocumentChunk


class VariantV9SkillGraph:
    def __init__(self, graph_index: SkillKnowledgeGraph):
        self.graph_index = graph_index

    def retrieve(self, query: str, k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        # Extract probable skill terms
        tokens = [t.strip(",.()") for t in query.split() if len(t) > 2]
        return self.graph_index.traverse_related_evidence(query_skills=tokens, k=k)
