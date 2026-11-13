"""Typed Graph State with Parallel Reducers for BidGraph and ConversationGraph."""

import operator
from typing import Annotated, Any, Dict, List, Optional

from typing_extensions import TypedDict

from agent.handoffs import (
    BidDecision,
    ComplianceVerdict,
    Critique,
    FitReport,
    JobSpec,
    LiaisonDraft,
    PriceQuote,
    ProposalDraft,
    RiskReport,
)


class TraceStep(TypedDict):
    step_number: int
    node_name: str
    action_type: str
    tokens_consumed: int
    latency_ms: float
    output_summary: str


def merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    res = dict(a)
    res.update(b)
    return res


class BidGraphState(TypedDict):
    # =========================================================================
    # 1. Graph Execution State (Typed Pydantic Handoffs)
    # =========================================================================
    job_id: str
    active_persona: str
    raw_job_data: Dict[str, Any]
    job_spec: Optional[JobSpec]
    risk_report: Optional[RiskReport]
    fit_report: Optional[FitReport]
    bid_decision: Optional[BidDecision]
    price_quote: Optional[PriceQuote]
    proposal_draft: Optional[ProposalDraft]
    critique: Optional[Critique]
    compliance_verdict: Optional[ComplianceVerdict]
    critic_loop_count: int
    is_approved_by_human: bool
    status: str  # "IN_PROGRESS", "NEEDS_ATTENTION", "AWAITING_APPROVAL", "COMPLETED", "REJECTED"

    # =========================================================================
    # 2. Execution Trace (Telemetry, Budgets, Step Progression)
    # =========================================================================
    total_tokens_used: Annotated[int, operator.add]
    total_steps_executed: Annotated[int, operator.add]
    trace_steps: Annotated[List[TraceStep], operator.add]

    # =========================================================================
    # 3. Long-Term Memory References (Style & Outcome Learnings)
    # =========================================================================
    style_memory_keys: List[str]
    outcome_memory_keys: List[str]
    memory_context: str


class ConversationGraphState(TypedDict):
    thread_id: str
    client_id: str
    job_id: str
    incoming_message: str
    liaison_draft: Optional[LiaisonDraft]
    is_approved_by_human: bool
    status: str
    total_tokens_used: Annotated[int, operator.add]
    trace_steps: Annotated[List[TraceStep], operator.add]
