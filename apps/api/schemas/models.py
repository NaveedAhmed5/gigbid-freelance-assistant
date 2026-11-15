"""Pydantic Schemas for GigBid REST & SSE Endpoints."""

from typing import List, Optional

from pydantic import BaseModel


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    active_persona: str


class UserResponse(BaseModel):
    user_id: str
    email: str
    role: str
    tenant_id: str
    active_persona: str


class SwitchPersonaRequest(BaseModel):
    persona: str  # ai_ml_engineer, fullstack_web_dev, data_analyst


class JobResponse(BaseModel):
    id: str
    title: str
    description: str
    category: str
    skills: List[str]
    job_type: str
    budget_usd: Optional[float] = None
    posted_at: str
    connects_required: int = 8
    is_scam: bool = False
    has_injection: bool = False
    client_id: str


class AnalyzeJobRequest(BaseModel):
    job_id: str
    persona: Optional[str] = None


class ProposalDraftUpdate(BaseModel):
    cover_letter: str
    bid_amount_usd: Optional[float] = None
    estimated_duration: Optional[str] = None


class ApprovalDecisionRequest(BaseModel):
    job_id: str
    action: str  # "approve", "edit", "reject"
    edited_cover_letter: Optional[str] = None
    feedback: Optional[str] = None


class MessageSendRequest(BaseModel):
    thread_id: str
    recipient_id: str
    text: str


class SettingsUpdateRequest(BaseModel):
    autonomy_level: str  # "semi_autonomous", "full_autonomous", "manual_approval"
    active_profile: str  # "open", "paid"
    marketplace_adapter: str  # "gigsim", "upwork_live"
    max_critic_loops: int = 2


class SettingsResponse(BaseModel):
    autonomy_level: str
    active_profile: str
    marketplace_adapter: str
    max_critic_loops: int
    open_model_default: str
    paid_model_default: str
    style_memories_count: int
    outcome_memories_count: int
    upwork_connected: bool = False
