"""Typed Pydantic Handoff Models for LangGraph Agent Nodes.

Rule 6: LangGraph nodes exchange typed Pydantic models from agent/handoffs.py,
never unstructured prose.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class JobSpec(BaseModel):
    job_id: str
    title: str
    primary_objective: str
    deliverables: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    timeline: str
    client_industry: str
    job_type: str
    client_budget_usd: Optional[float] = None
    screening_questions: List[str] = Field(default_factory=list)


class RiskReport(BaseModel):
    is_safe: bool
    risk_score: float = Field(ge=0.0, le=1.0, description="0.0 = completely safe, 1.0 = critical risk")
    flags: List[str] = Field(default_factory=list)
    has_off_platform_trap: bool = False
    has_prompt_injection: bool = False
    is_unpaid_work_trap: bool = False
    summary: str


class FitReport(BaseModel):
    coverage_score: float = Field(ge=0.0, le=1.0)
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    evidence_ids: List[str] = Field(default_factory=list)
    primary_case_study_id: Optional[str] = None
    proof_points: List[str] = Field(default_factory=list)
    fit_summary: str


class BidDecision(BaseModel):
    decision: str  # "BID" or "SKIP"
    rationale: str
    priority_score: float = Field(ge=0.0, le=1.0)
    rejection_reasons: List[str] = Field(default_factory=list)


class PriceQuote(BaseModel):
    pricing_strategy: str  # "value_based", "market_rate", "fixed_milestone"
    bid_amount_usd: float
    estimated_duration: str
    connects_required: int = 8
    expected_roi_ratio: float = 1.0
    rationale: str


class ProposalDraft(BaseModel):
    cover_letter: str
    opening_hook: str
    technical_solution: str
    proof_points: List[str] = Field(default_factory=list)
    screening_answers: Dict[str, str] = Field(default_factory=dict)
    iteration_count: int = 0
    grounding_ratio: float = 1.0


class Critique(BaseModel):
    client_focus_score: float = Field(ge=1.0, le=5.0)
    clarity_score: float = Field(ge=1.0, le=5.0)
    feedback: str
    requires_revision: bool = False
    suggested_improvements: List[str] = Field(default_factory=list)


class ComplianceVerdict(BaseModel):
    is_compliant: bool
    violations: List[str] = Field(default_factory=list)
    nov_2_policy_verified: bool = True
    terms_checked: List[str] = Field(default_factory=list)
    can_submit: bool = False
    summary: str


class LiaisonDraft(BaseModel):
    client_message: str
    inferred_intent: str  # "interview_invite", "technical_inquiry", "rate_negotiation", "general"
    response_draft: str
    calendar_hold_slot_ids: List[str] = Field(default_factory=list)
    requires_human_approval: bool = True
