"""GigSim Data Models and Schemas."""

from datetime import datetime, timezone
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ClientReview(BaseModel):
    freelancer_name: str
    rating: float
    comment: str
    date: str


class ClientProfile(BaseModel):
    id: str
    name: str
    industry: str
    country: str
    total_spend_usd: float
    hire_rate: float
    jobs_posted: int
    open_jobs: int
    rating: float
    payment_verified: bool
    reviews: List[ClientReview] = Field(default_factory=list)
    # Hidden preferences used strictly by simulator engine
    must_have_skills: List[str] = Field(default_factory=list)
    budget_ceiling: float = 10000.0
    dislike_generic_openings: bool = True
    responsiveness: float = 0.85


class JobPosting(BaseModel):
    id: str
    title: str
    description: str
    client_id: str
    client: Optional[ClientProfile] = None
    category: str
    subcategory: str
    skills: List[str] = Field(default_factory=list)
    job_type: str  # "fixed_price" or "hourly"
    budget_usd: Optional[float] = None
    hourly_rate_range: Optional[List[float]] = None  # [min, max]
    duration: str  # e.g., "1 to 3 months", "Less than 1 month"
    experience_level: str  # "Entry", "Intermediate", "Expert"
    connects_required: int = 8
    posted_at: str
    is_active: bool = True
    is_scam: bool = False
    has_injection: bool = False
    scam_reason: Optional[str] = None
    screening_questions: List[str] = Field(default_factory=list)


class ProposalSubmission(BaseModel):
    id: str
    job_id: str
    freelancer_id: str
    cover_letter: str
    bid_amount_usd: float
    estimated_duration: str
    screening_answers: Dict[str, str] = Field(default_factory=dict)
    attachments: List[str] = Field(default_factory=list)
    submitted_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: str = "SUBMITTED"  # SUBMITTED, VIEWED, REPLIED, INTERVIEW, HIRED, REJECTED
    client_feedback: Optional[str] = None
    connects_spent: int = 8


class Message(BaseModel):
    id: str
    thread_id: str
    sender_id: str  # freelancer_id or client_id
    recipient_id: str
    text: str
    sent_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    is_read: bool = False


class ConnectsBalance(BaseModel):
    freelancer_id: str
    balance: int = 120
    last_updated: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ClientEvaluationResult(BaseModel):
    proposal_id: str
    decision: str  # VIEWED, REPLIED, INTERVIEW, HIRED, REJECTED
    reasons: List[str] = Field(default_factory=list)
    match_score: float
    simulated_reply: Optional[str] = None
