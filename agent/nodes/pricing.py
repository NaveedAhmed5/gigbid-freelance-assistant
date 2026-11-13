"""Pricing Strategist Node: Pricing optimization, margin calculations, and Connects ROI."""

from typing import Tuple

from agent.config import load_agent_config
from agent.handoffs import BidDecision, FitReport, JobSpec, PriceQuote, RiskReport
from agent.mcp_client import get_mcp_client
from agent.prompts import load_prompt


def pricing_node(
    job_spec: JobSpec,
    fit_report: FitReport,
    risk_report: RiskReport,
    persona: str = "ai_ml_engineer",
) -> Tuple[BidDecision, PriceQuote]:
    config = load_agent_config()
    config.resolve_model_for_node("pricing")
    load_prompt("pricing_strategist.md")

    mcp = get_mcp_client()
    balance_info = mcp.call_tool(
        "pricing", "get_connects_balance", {"freelancer_id": "freelancer_1"}
    )
    balance_info.get("balance", 120)

    # 1. Gate: Decide BID vs SKIP
    if not risk_report.is_safe:
        bid_decision = BidDecision(
            decision="SKIP",
            rationale=f"Rejected due to high security or policy risk: {risk_report.summary}",
            priority_score=0.0,
            rejection_reasons=risk_report.flags,
        )
        quote = PriceQuote(
            pricing_strategy="market_rate",
            bid_amount_usd=0.0,
            estimated_duration="N/A",
            connects_required=0,
            expected_roi_ratio=0.0,
            rationale="Skipped execution; no quote generated.",
        )
        return bid_decision, quote

    if fit_report.coverage_score < 0.40:
        bid_decision = BidDecision(
            decision="SKIP",
            rationale=f"Skill coverage too low ({int(fit_report.coverage_score * 100)}%). Connects preserved.",
            priority_score=0.2,
            rejection_reasons=["Insufficient technical alignment with core persona competencies."],
        )
        quote = PriceQuote(
            pricing_strategy="market_rate",
            bid_amount_usd=0.0,
            estimated_duration="N/A",
            connects_required=0,
            expected_roi_ratio=0.0,
            rationale="Skipped execution; no quote generated.",
        )
        return bid_decision, quote

    # 2. Approved to BID: Calculate optimal pricing
    bid_decision = BidDecision(
        decision="BID",
        rationale="Strong fit and verified low security risk. Positive projected Connects ROI.",
        priority_score=round(fit_report.coverage_score * (1.0 - risk_report.risk_score), 2),
        rejection_reasons=[],
    )

    base_budget = job_spec.client_budget_usd or 2500.0
    # Price close to client budget with healthy margin
    bid_amount = round(base_budget * 0.95, 2)
    connects_cost = 8
    expected_roi = round(bid_amount / (connects_cost * 1.5), 1)

    quote = PriceQuote(
        pricing_strategy="value_based",
        bid_amount_usd=bid_amount,
        estimated_duration=job_spec.timeline or "1 month",
        connects_required=connects_cost,
        expected_roi_ratio=expected_roi,
        rationale=f"Targeted at 95% of client budget (${bid_amount}) to optimize winning probability and margin.",
    )

    return bid_decision, quote
