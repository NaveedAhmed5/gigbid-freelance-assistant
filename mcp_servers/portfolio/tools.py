"""Portfolio MCP Server Tools."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "personas"


class SearchEvidenceInput(BaseModel):
    requirement: str = Field(description="Client requirement, question, or keyword to match.")
    k: int = Field(default=3, description="Number of evidence items to return.")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Optional filters like persona or industry.")


class EvidenceItem(BaseModel):
    id: str
    persona: str
    title: str
    industry: str
    skills: List[str]
    summary: str
    metric_improvement_pct: float
    relevance_score: float


def search_evidence(requirement: str, k: int = 3, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """Search portfolio case studies for matching evidence against a client requirement."""
    req_terms = {t.lower() for t in requirement.replace(",", " ").split() if len(t) > 2}
    results = []

    target_personas = [filters["persona"]] if (filters and "persona" in filters) else ["ai_ml_engineer", "fullstack_web_dev", "data_analyst"]

    for p in target_personas:
        cs_file = DATA_DIR / p / "case_studies.json"
        if not cs_file.exists():
            continue
        case_studies = json.loads(cs_file.read_text(encoding="utf-8"))

        for cs in case_studies:
            if filters and "industry" in filters and filters["industry"].lower() != cs["industry"].lower():
                continue

            text_corpus = f"{cs['title']} {cs['summary']} {' '.join(cs['skills'])} {cs['industry']}".lower()
            matches = sum(1 for term in req_terms if term in text_corpus)
            score = round(matches / max(1, len(req_terms)), 3)

            results.append({
                "id": cs["id"],
                "persona": p,
                "title": cs["title"],
                "industry": cs["industry"],
                "skills": cs["skills"],
                "summary": cs["summary"],
                "metric_improvement_pct": cs["metric_improvement_pct"],
                "relevance_score": score,
            })

    results.sort(key=lambda x: (x["relevance_score"], x["metric_improvement_pct"]), reverse=True)
    return results[:k]


def get_case_study(id: str) -> Dict[str, Any]:
    """Retrieve full details and architecture of a specific case study by ID."""
    for p in ["ai_ml_engineer", "fullstack_web_dev", "data_analyst"]:
        cs_file = DATA_DIR / p / "case_studies.json"
        if not cs_file.exists():
            continue
        case_studies = json.loads(cs_file.read_text(encoding="utf-8"))
        for cs in case_studies:
            if cs["id"] == id:
                md_path = DATA_DIR / p / "case_studies" / f"{id}.md"
                markdown_body = md_path.read_text(encoding="utf-8") if md_path.exists() else cs["summary"]
                return {
                    "id": cs["id"],
                    "persona": p,
                    "title": cs["title"],
                    "industry": cs["industry"],
                    "skills": cs["skills"],
                    "metric_improvement_pct": cs["metric_improvement_pct"],
                    "summary": cs["summary"],
                    "content": markdown_body,
                }
    raise KeyError(f"Case study '{id}' not found in any persona corpus.")


def list_skills(persona: str) -> List[str]:
    """List verified technical skills for a specific persona."""
    cv_file = DATA_DIR / persona / "cv.md"
    if not cv_file.exists():
        raise KeyError(f"Persona '{persona}' not found.")
    cs_file = DATA_DIR / persona / "case_studies.json"
    skills = set()
    if cs_file.exists():
        studies = json.loads(cs_file.read_text(encoding="utf-8"))
        for s in studies:
            skills.update(s.get("skills", []))
    return sorted(list(skills))
