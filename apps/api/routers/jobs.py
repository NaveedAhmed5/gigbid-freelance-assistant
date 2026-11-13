"""Jobs Router: List, search, details, and trigger BidGraph execution."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from apps.api.auth.security import get_current_user
from apps.api.schemas.models import AnalyzeJobRequest, JobResponse
from apps.api.state_manager import get_api_state

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=List[JobResponse])
def list_jobs(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    state = get_api_state()
    jobs = list(state.jobs_cache.values())
    if category:
        jobs = [j for j in jobs if j.get("category", "").lower() == category.lower()]
    if q:
        term = q.lower()
        jobs = [
            j
            for j in jobs
            if term in j.get("title", "").lower() or term in j.get("description", "").lower()
        ]
    return jobs[:limit]


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, current_user: dict = Depends(get_current_user)):
    state = get_api_state()
    job = state.jobs_cache.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.post("/analyze")
def trigger_analysis(req: AnalyzeJobRequest, current_user: dict = Depends(get_current_user)):
    state = get_api_state()
    persona = req.persona or current_user.get("active_persona", "ai_ml_engineer")
    try:
        run_record = state.run_bid_pipeline(job_id=req.job_id, persona=persona)
        return run_record
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
