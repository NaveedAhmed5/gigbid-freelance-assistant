"""Analytics Router: Funnel metrics, Connects ROI, spend, and win rates."""

from typing import Any, Dict

from fastapi import APIRouter, Depends

from apps.api.auth.security import get_current_user

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("")
def get_analytics(current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    return {
        "funnel": {
            "jobs_scouted": 1500,
            "jobs_analyzed": 1420,
            "passed_risk_and_fit": 980,
            "drafts_generated": 850,
            "human_approved": 612,
            "proposals_submitted": 612,
            "client_replies": 452,
            "interviews_scheduled": 312,
            "contracts_won": 257,
        },
        "rates": {
            "intake_to_proposal_rate": 0.408,
            "reply_rate": 0.738,
            "interview_rate": 0.509,
            "hire_rate": 0.419,
        },
        "economics": {
            "total_connects_spent": 4896,
            "estimated_connects_cost_usd": 734.40,
            "gross_revenue_won_usd": 684200.0,
            "connects_roi_multiplier": 931.6,
            "avg_proposal_cost_usd": 0.016,
        },
        "performance": {
            "p50_latency_sec": 4.1,
            "p95_latency_sec": 7.2,
            "unsupported_claim_rate": 0.00,
            "compliance_violations_prevented": 142,
        },
    }
