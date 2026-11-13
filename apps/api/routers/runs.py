"""Runs Router: Live Agent Run Viewer, execution trace, and checkpoint replay."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from apps.api.auth.security import get_current_user
from apps.api.state_manager import get_api_state

router = APIRouter(prefix="/runs", tags=["Runs"])


@router.get("")
def list_runs(current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    state = get_api_state()
    return list(state.runs.values())


@router.get("/{run_id}")
def get_run_detail(run_id: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    state = get_api_state()
    run = state.runs.get(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    return run


@router.get("/{run_id}/dag")
def get_run_dag(run_id: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    """Return nodes and edges for DAG visualization."""
    return {
        "nodes": [
            {"id": "analyst", "label": "Job Analyst", "type": "agent"},
            {"id": "risk", "label": "Risk Assessor", "type": "agent"},
            {"id": "matcher", "label": "Fit Matcher", "type": "agent"},
            {"id": "pricing", "label": "Pricing Strategist", "type": "gate"},
            {"id": "writer", "label": "Proposal Writer", "type": "agent"},
            {"id": "verifier", "label": "Claim Verifier", "type": "safety"},
            {"id": "critic", "label": "Proposal Critic", "type": "feedback"},
            {"id": "compliance", "label": "Compliance Guard", "type": "safety"},
            {"id": "human_approval", "label": "Human Approval", "type": "gate"},
            {"id": "submit_live", "label": "Live Submission", "type": "action"},
        ],
        "edges": [
            {"from": "analyst", "to": "pricing"},
            {"from": "risk", "to": "pricing"},
            {"from": "matcher", "to": "pricing"},
            {"from": "pricing", "to": "writer"},
            {"from": "writer", "to": "verifier"},
            {"from": "verifier", "to": "critic"},
            {"from": "critic", "to": "compliance"},
            {"from": "compliance", "to": "human_approval"},
            {"from": "human_approval", "to": "submit_live"},
        ],
    }
