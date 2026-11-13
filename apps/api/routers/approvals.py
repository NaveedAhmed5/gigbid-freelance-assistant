"""Approvals Router: Resumes paused LangGraph threads upon human action."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from agent.memory.promotion_rules import MemoryCandidate
from agent.memory.store import get_memory_store
from apps.api.auth.security import get_current_user
from apps.api.schemas.models import ApprovalDecisionRequest
from apps.api.state_manager import get_api_state

router = APIRouter(prefix="/approvals", tags=["Approvals"])


@router.get("")
def list_pending_approvals(current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    state = get_api_state()
    return list(state.pending_approvals.values())


@router.post("/decision")
def submit_approval_decision(
    req: ApprovalDecisionRequest, current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    state = get_api_state()
    try:
        # If user edited the draft, check style memory promotion
        if req.action == "edit" and req.edited_cover_letter:
            pending = state.pending_approvals.get(req.job_id)
            if pending and pending.get("proposal_draft"):
                original = pending["proposal_draft"]["cover_letter"]
                mem_store = get_memory_store()
                mem_store.promote_candidate(
                    MemoryCandidate(
                        category="style",
                        source_id=f"edit_{req.job_id}",
                        original_text=original,
                        edited_text=req.edited_cover_letter,
                    )
                )

        result = state.resume_approval(
            job_id=req.job_id,
            action=req.action,
            edited_text=req.edited_cover_letter,
            feedback=req.feedback,
        )
        return result
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
