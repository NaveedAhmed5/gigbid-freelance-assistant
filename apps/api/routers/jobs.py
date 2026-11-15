"""Jobs Router: List, search, details, sync with live Upwork MCP, and trigger BidGraph execution."""

import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from agent.nodes.scout import scout_node
from apps.api.auth.security import get_current_user
from apps.api.db import clear_dummy_seed_jobs, get_all_jobs, save_jobs
from apps.api.schemas.models import AnalyzeJobRequest, JobResponse
from apps.api.state_manager import get_api_state
from mcp_servers.marketplace.adapters.upwork_live import AuthenticationError, UpworkLiveAdapter

logger = logging.getLogger("gigbid.jobs")
router = APIRouter(prefix="/jobs", tags=["Jobs"])


def _normalize_job_response(j: Dict[str, Any]) -> Dict[str, Any]:
    skills = j.get("skills") or []
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    return {
        "id": str(j.get("id")),
        "title": str(j.get("title", "Untitled Opportunity")),
        "description": str(j.get("description", "")),
        "category": str(j.get("category", "AI/ML & LLM Engineering")),
        "skills": skills,
        "job_type": str(j.get("job_type", "fixed_price")),
        "budget_usd": float(j["budget_usd"]) if j.get("budget_usd") is not None else None,
        "posted_at": str(j.get("posted_at", "2026-11-15T12:00:00Z")),
        "connects_required": int(j.get("connects_required") or 16),
        "is_scam": bool(j.get("is_scam", False)),
        "has_injection": bool(j.get("has_injection", False)),
        "client_id": str(j.get("client_id", "client_upwork_live")),
    }


@router.get("", response_model=List[JobResponse])
def list_jobs(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    sync: bool = Query(False),
    current_user: dict = Depends(get_current_user),
):
    state = get_api_state()
    adapter_name = os.getenv("MARKETPLACE_ADAPTER", "gigsim").lower()

    if adapter_name == "upwork_live":
        # 1. Filter state cache for live Upwork jobs only (strictly exclude dummy job_001..job_010 seed data)
        live_in_cache = [
            j for j in state.jobs_cache.values()
            if j.get("source") == "upwork_live" or (not str(j.get("id", "")).startswith("job_0"))
        ]

        # 2. If in-memory cache has no live jobs, load from SQLite database
        if not live_in_cache:
            db_jobs = get_all_jobs(source="upwork_live")
            for dj in db_jobs:
                state.jobs_cache[dj["id"]] = dj
            live_in_cache = db_jobs

        # 3. If still empty or if sync=True was explicitly requested, try live scan
        if not live_in_cache or sync:
            try:
                adapter = UpworkLiveAdapter()
                scouted = adapter.search_jobs(query=q, category=category, limit=limit)
                if scouted:
                    # Clear out dummy seed jobs from cache & SQLite
                    state.jobs_cache = {
                        k: v for k, v in state.jobs_cache.items()
                        if not str(k).startswith("job_0")
                    }
                    clear_dummy_seed_jobs()
                    for sj in scouted:
                        sj["source"] = "upwork_live"
                        state.jobs_cache[sj["id"]] = sj
                    save_jobs(scouted)
                    live_in_cache = scouted
            except AuthenticationError:
                # Upwork OAuth token missing or rejected - return empty so UI displays connection prompt
                live_in_cache = []
            except Exception as e:
                logger.warning(f"Live Upwork job scan failed: {e}")

        jobs = live_in_cache
    else:
        # Default gigsim mode
        jobs = list(state.jobs_cache.values())

    if category and category.upper() != "ALL":
        jobs = [j for j in jobs if category.lower() in j.get("category", "").lower()]
    if q:
        term = q.lower()
        jobs = [
            j
            for j in jobs
            if term in j.get("title", "").lower() or term in j.get("description", "").lower()
        ]

    return [_normalize_job_response(j) for j in jobs[:limit]]


@router.post("/scan")
@router.post("/sync")
def scan_live_jobs(
    q: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    """Trigger the Scout agent against active marketplace port (Upwork Live MCP or GigSim)."""
    state = get_api_state()
    adapter_name = os.getenv("MARKETPLACE_ADAPTER", "gigsim").lower()

    if adapter_name == "upwork_live":
        adapter = UpworkLiveAdapter()
        try:
            live_jobs = adapter.search_jobs(query=q, category=category, limit=limit)
        except AuthenticationError as e:
            raise HTTPException(
                status_code=401,
                detail=f"Upwork Authentication Required: {e}",
            )
        except Exception as e:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to fetch live Upwork jobs via MCP: {e}",
            )

        # Clear out dummy seed jobs
        state.jobs_cache = {
            k: v for k, v in state.jobs_cache.items()
            if not str(k).startswith("job_0")
        }
        clear_dummy_seed_jobs()

        persona = current_user.get("active_persona", "ai_ml_engineer")
        scouted_jobs = []
        for j in live_jobs:
            j["source"] = "upwork_live"
            scout_result = scout_node(j, persona=persona)
            j["is_scam"] = False
            j["has_injection"] = False
            j["scout_verdict"] = scout_result.get("is_relevant", True)
            state.jobs_cache[j["id"]] = j
            scouted_jobs.append(j)

        save_jobs(scouted_jobs)
        return {
            "status": "ok",
            "message": f"Successfully scouted and synced {len(scouted_jobs)} live Upwork jobs.",
            "count": len(scouted_jobs),
            "jobs": [_normalize_job_response(j) for j in scouted_jobs],
        }
    else:
        # GigSim mode: return simulated active jobs
        sim_jobs = list(state.jobs_cache.values())
        return {
            "status": "ok",
            "message": "Marketplace adapter is GigSim. Using simulated seed jobs.",
            "count": len(sim_jobs),
            "jobs": [_normalize_job_response(j) for j in sim_jobs],
        }


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, current_user: dict = Depends(get_current_user)):
    state = get_api_state()
    job = state.jobs_cache.get(job_id)
    if not job:
        # Check SQLite
        db_jobs = get_all_jobs()
        matched = next((dj for dj in db_jobs if dj.get("id") == job_id), None)
        if matched:
            job = matched
            state.jobs_cache[job_id] = job
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _normalize_job_response(job)


@router.post("/analyze")
def trigger_analysis(req: AnalyzeJobRequest, current_user: dict = Depends(get_current_user)):
    state = get_api_state()
    persona = req.persona or current_user.get("active_persona", "ai_ml_engineer")
    try:
        run_record = state.run_bid_pipeline(job_id=req.job_id, persona=persona)
        return run_record
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
