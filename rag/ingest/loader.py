"""RAG Ingestion Engine with Full Metadata & Incremental Hashing."""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field


class DocumentChunk(BaseModel):
    chunk_id: str
    doc_type: str  # cv, case_study, repo_readme, repo_code, review, proposal
    persona: str
    title: str
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    content_hash: str


class IngestionEngine:
    def __init__(self, data_root: Optional[Path] = None):
        self.data_root = data_root or (Path(__file__).resolve().parents[2] / "data" / "personas")
        self.indexed_hashes: Set[str] = set()

    def _hash_content(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def load_persona_corpus(self, persona: str) -> List[DocumentChunk]:
        """Load and chunk all artifacts for a specific persona with incremental hashing."""
        p_dir = self.data_root / persona
        if not p_dir.exists():
            raise FileNotFoundError(f"Persona directory '{p_dir}' not found.")

        chunks: List[DocumentChunk] = []

        # 1. CV
        cv_path = p_dir / "cv.md"
        if cv_path.exists():
            cv_text = cv_path.read_text(encoding="utf-8")
            h = self._hash_content(cv_text)
            chunks.append(
                DocumentChunk(
                    chunk_id=f"cv_{persona}",
                    doc_type="cv",
                    persona=persona,
                    title=f"CV - {persona}",
                    text=cv_text,
                    metadata={"persona": persona, "skills": []},
                    content_hash=h,
                )
            )

        # 2. Case Studies
        cs_file = p_dir / "case_studies.json"
        if cs_file.exists():
            studies = json.loads(cs_file.read_text(encoding="utf-8"))
            for cs in studies:
                text = f"{cs['title']}\nIndustry: {cs['industry']}\nSkills: {', '.join(cs['skills'])}\nOutcome: {cs['summary']} (Metric: {cs['metric_improvement_pct']}%)"
                h = self._hash_content(text)
                chunks.append(
                    DocumentChunk(
                        chunk_id=cs["id"],
                        doc_type="case_study",
                        persona=persona,
                        title=cs["title"],
                        text=text,
                        metadata={
                            "case_study_id": cs["id"],
                            "industry": cs["industry"],
                            "skills": cs["skills"],
                            "metric_improvement_pct": cs["metric_improvement_pct"],
                            "outcome": "won",
                        },
                        content_hash=h,
                    )
                )

        # 3. GitHub Repos
        gh_dir = p_dir / "github_repos"
        if gh_dir.exists():
            for repo_path in gh_dir.iterdir():
                if repo_path.is_dir():
                    readme = repo_path / "README.md"
                    if readme.exists():
                        rm_text = readme.read_text(encoding="utf-8")
                        chunks.append(
                            DocumentChunk(
                                chunk_id=f"gh_readme_{repo_path.name}",
                                doc_type="repo_readme",
                                persona=persona,
                                title=f"README: {repo_path.name}",
                                text=rm_text,
                                metadata={"repo": repo_path.name},
                                content_hash=self._hash_content(rm_text),
                            )
                        )
                    for code_file in repo_path.glob("main.*"):
                        code_text = code_file.read_text(encoding="utf-8")
                        chunks.append(
                            DocumentChunk(
                                chunk_id=f"gh_code_{repo_path.name}",
                                doc_type="repo_code",
                                persona=persona,
                                title=f"Code: {repo_path.name}",
                                text=code_text,
                                metadata={"repo": repo_path.name, "language": code_file.suffix},
                                content_hash=self._hash_content(code_text),
                            )
                        )

        # 4. Past Proposals
        props_file = p_dir / "past_proposals.json"
        if props_file.exists():
            props = json.loads(props_file.read_text(encoding="utf-8"))
            for prop in props:
                prop_text = prop["cover_letter"]
                chunks.append(
                    DocumentChunk(
                        chunk_id=prop["id"],
                        doc_type="proposal",
                        persona=persona,
                        title=f"Proposal {prop['id']} ({prop['outcome']})",
                        text=prop_text,
                        metadata={
                            "proposal_id": prop["id"],
                            "outcome": prop["outcome"],
                            "case_study_id": prop.get("case_study_id"),
                            "industry": prop.get("client_industry"),
                            "skills": prop.get("skills", []),
                            "bid_amount_usd": prop.get("bid_amount_usd"),
                        },
                        content_hash=self._hash_content(prop_text),
                    )
                )

        # 5. Reviews
        revs_file = p_dir / "reviews.json"
        if revs_file.exists():
            revs = json.loads(revs_file.read_text(encoding="utf-8"))
            for r in revs:
                rev_text = f"Review from {r['client_name']}: {r['comment']} (Rating: {r['rating']})"
                chunks.append(
                    DocumentChunk(
                        chunk_id=r["review_id"],
                        doc_type="review",
                        persona=persona,
                        title=f"Review: {r['client_name']}",
                        text=rev_text,
                        metadata={"rating": r["rating"]},
                        content_hash=self._hash_content(rev_text),
                    )
                )

        return chunks
