"""GigSim FastAPI Marketplace Simulator Service."""

from typing import List, Optional

from fastapi import FastAPI, HTTPException, Query

from gigsim.engine import GigSimEngine
from gigsim.models import (
    ClientProfile,
    ConnectsBalance,
    JobPosting,
    Message,
    ProposalSubmission,
)

app = FastAPI(
    title="GigSim Marketplace Simulator",
    description="Upwork-like freelance marketplace simulator for autonomous agent research.",
    version="1.0.0",
)

# Global engine instance
engine = GigSimEngine()


@app.get("/health")
def health():
    return {"status": "ok", "service": "gigsim", "version": "1.0.0"}


@app.post("/reset")
def reset_simulator():
    engine.reset()
    return {"status": "reset_successful"}


@app.get("/jobs", response_model=List[JobPosting])
def list_jobs(
    q: Optional[str] = Query(None, description="Search term in title or description"),
    category: Optional[str] = Query(None, description="Category filter"),
    skills: Optional[List[str]] = Query(None, description="Skills filter"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    return engine.search_jobs(query=q, category=category, skills=skills, limit=limit, offset=offset)


@app.get("/jobs/{job_id}", response_model=JobPosting)
def get_job(job_id: str):
    job = engine.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/clients/{client_id}", response_model=ClientProfile)
def get_client(client_id: str):
    client = engine.clients.get(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@app.get("/connects/balance", response_model=ConnectsBalance)
def get_connects_balance(freelancer_id: str = "freelancer_1"):
    return engine.get_or_create_connects(freelancer_id)


@app.post("/connects/purchase", response_model=ConnectsBalance)
def purchase_connects(freelancer_id: str, amount: int = 50):
    balance = engine.get_or_create_connects(freelancer_id)
    balance.balance += amount
    return balance


@app.post("/proposals", response_model=ProposalSubmission)
def submit_proposal(proposal: ProposalSubmission):
    try:
        updated_proposal, eval_res = engine.submit_proposal(proposal)
        return updated_proposal
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/proposals/{proposal_id}", response_model=ProposalSubmission)
def get_proposal(proposal_id: str):
    prop = engine.proposals.get(proposal_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return prop


@app.get("/proposals", response_model=List[ProposalSubmission])
def list_proposals(freelancer_id: Optional[str] = None):
    props = list(engine.proposals.values())
    if freelancer_id:
        props = [p for p in props if p.freelancer_id == freelancer_id]
    return props


@app.get("/messages", response_model=List[Message])
def list_messages(thread_id: str):
    return engine.messages.get(thread_id, [])


@app.post("/messages", response_model=Message)
def send_message(message: Message):
    engine.messages.setdefault(message.thread_id, []).append(message)
    return message
