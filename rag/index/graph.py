"""NetworkX Knowledge Graph Index for Skill-Project-Industry-Outcome Traversals."""

from typing import Dict, List, Optional, Tuple

import networkx as nx

from rag.ingest.loader import DocumentChunk


class SkillKnowledgeGraph:
    def __init__(self):
        self.graph = nx.MultiDiGraph()
        self.chunk_map: Dict[str, DocumentChunk] = {}

    def build_graph(self, chunks: List[DocumentChunk]):
        self.graph.clear()
        self.chunk_map.clear()

        for c in chunks:
            self.chunk_map[c.chunk_id] = c
            doc_node = f"doc:{c.chunk_id}"
            self.graph.add_node(doc_node, type=c.doc_type, title=c.title, chunk_id=c.chunk_id)

            # Link skills
            skills = c.metadata.get("skills", [])
            for s in skills:
                skill_node = f"skill:{s.lower()}"
                self.graph.add_node(skill_node, type="skill", name=s)
                self.graph.add_edge(doc_node, skill_node, relation="demonstrates")
                self.graph.add_edge(skill_node, doc_node, relation="demonstrated_by")

            # Link industry
            industry = c.metadata.get("industry")
            if industry:
                ind_node = f"industry:{industry.lower()}"
                self.graph.add_node(ind_node, type="industry", name=industry)
                self.graph.add_edge(doc_node, ind_node, relation="applied_in")
                self.graph.add_edge(ind_node, doc_node, relation="contains_project")

            # Link outcome
            outcome = c.metadata.get("outcome")
            if outcome:
                out_node = f"outcome:{outcome.lower()}"
                self.graph.add_node(out_node, type="outcome", name=outcome)
                self.graph.add_edge(doc_node, out_node, relation="achieved_outcome")

    def traverse_related_evidence(
        self, query_skills: List[str], industry: Optional[str] = None, k: int = 5
    ) -> List[Tuple[DocumentChunk, float]]:
        """Multi-hop traversal: (skills, industry) -> doc nodes -> ranked by graph degree/connectivity."""
        node_scores: Dict[str, float] = {}

        for s in query_skills:
            skill_node = f"skill:{s.lower()}"
            if self.graph.has_node(skill_node):
                # 1-hop to docs
                for _, neighbor, data in self.graph.out_edges(skill_node, data=True):
                    if neighbor.startswith("doc:"):
                        node_scores[neighbor] = node_scores.get(neighbor, 0.0) + 1.0

        if industry:
            ind_node = f"industry:{industry.lower()}"
            if self.graph.has_node(ind_node):
                for _, neighbor in self.graph.out_edges(ind_node):
                    if neighbor.startswith("doc:"):
                        node_scores[neighbor] = node_scores.get(neighbor, 0.0) + 1.5

        # Check outcome bonus
        for doc_node in list(node_scores.keys()):
            for _, target, data in self.graph.out_edges(doc_node, data=True):
                if target == "outcome:won":
                    node_scores[doc_node] += 0.8
                elif target == "outcome:replied":
                    node_scores[doc_node] += 0.3

        # Rank
        sorted_docs = sorted(node_scores.items(), key=lambda x: x[1], reverse=True)[:k]
        results = []
        for doc_node, score in sorted_docs:
            chunk_id = self.graph.nodes[doc_node]["chunk_id"]
            if chunk_id in self.chunk_map:
                results.append((self.chunk_map[chunk_id], score))
        return results
