"""Proposals Router: Proposal draft retrieval, editing, and pipeline stages."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from apps.api.auth.security import get_current_user
from apps.api.schemas.models import ProposalDraftUpdate
from apps.api.state_manager import get_api_state

router = APIRouter(prefix="/proposals", tags=["Proposals"])


@router.get("")
def list_proposals(current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    state = get_api_state()
    return list(state.proposals.values())


@router.get("/{job_id}")
def get_proposal(job_id: str, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    state = get_api_state()
    # Check pending approvals first
    if job_id in state.pending_approvals:
        return state.pending_approvals[job_id]
    if f"prop_{job_id}" in state.proposals:
        return state.proposals[f"prop_{job_id}"]
    raise HTTPException(status_code=404, detail="Proposal not found for this job ID.")


@router.patch("/{job_id}")
def update_proposal_draft(
    job_id: str, update: ProposalDraftUpdate, current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    state = get_api_state()
    if job_id not in state.pending_approvals:
        raise HTTPException(status_code=404, detail="No active editable proposal found for this job ID.")
    approval = state.pending_approvals[job_id]
    if approval.get("proposal_draft"):
        approval["proposal_draft"]["cover_letter"] = update.cover_letter
    return approval
