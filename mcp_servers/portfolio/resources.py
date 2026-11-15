"""Portfolio MCP Server Resource Templates."""

import json
from pathlib import Path
from typing import Any, Dict

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "personas"


def read_case_resource(uri: str) -> Dict[str, Any]:
    """Read a case study resource: portfolio://case/{id}"""
    case_id = uri.replace("portfolio://case/", "").strip()
    for p in ["ai_ml_engineer", "fullstack_web_dev", "data_analyst"]:
        md_file = DATA_DIR / p / "case_studies" / f"{case_id}.md"
        if md_file.exists():
            return {
                "uri": uri,
                "case_id": case_id,
                "persona": p,
                "content": md_file.read_text(encoding="utf-8"),
            }
    raise KeyError(f"Resource uri '{uri}' not found.")


def read_proposal_resource(uri: str) -> Dict[str, Any]:
    """Read a past proposal resource: portfolio://proposal/{id}"""
    prop_id = uri.replace("portfolio://proposal/", "").strip()
    for p in ["ai_ml_engineer", "fullstack_web_dev", "data_analyst"]:
        props_file = DATA_DIR / p / "past_proposals.json"
        if props_file.exists():
            proposals = json.loads(props_file.read_text(encoding="utf-8"))
            for prop in proposals:
                if prop["id"] == prop_id:
                    return {
                        "uri": uri,
                        "proposal_id": prop_id,
                        "persona": p,
                        "outcome": prop["outcome"],
                        "cover_letter": prop["cover_letter"],
                        "case_study_id": prop.get("case_study_id"),
                    }
    raise KeyError(f"Resource uri '{uri}' not found.")
