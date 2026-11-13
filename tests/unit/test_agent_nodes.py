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
from agent.nodes.analyst import analyst_node
from agent.nodes.compliance import compliance_node
from agent.nodes.critic import critic_node
from agent.nodes.liaison import liaison_node
from agent.nodes.matcher import matcher_node
from agent.nodes.pricing import pricing_node
from agent.nodes.risk import risk_node
from agent.nodes.scout import scout_node
from agent.nodes.verifier import verifier_node
from agent.nodes.writer import writer_node
from agent.prompts import verify_no_inline_prompts


def test_rule_2_prompt_verification():
    """Verify that all prompts are externalized in agent/prompts/."""
    assert verify_no_inline_prompts() is True


def test_agent_nodes_end_to_end_handoffs():
    sample_job = {
        "id": "job_test_42",
        "title": "Build PyTorch Enterprise RAG Pipeline",
        "description": "Looking for senior PyTorch and FastAPI expert for enterprise RAG system.",
        "skills": ["Python", "PyTorch", "FastAPI", "Vector Search"],
        "budget_usd": 3500.0,
        "duration": "1 month",
        "category": "AI/ML",
        "subcategory": "Healthcare",
        "client_id": "client_88",
    }

    # 1. Scout
    scout_res = scout_node(sample_job, persona="ai_ml_engineer")
    assert scout_res["is_relevant"] is True

    # 2. Analyst -> JobSpec
    spec = analyst_node(sample_job)
    assert isinstance(spec, JobSpec)
    assert "PyTorch" in spec.required_skills

    # 3. Risk -> RiskReport
    risk = risk_node(sample_job)
    assert isinstance(risk, RiskReport)
    assert risk.is_safe is True

    # 4. Matcher -> FitReport
    fit = matcher_node(spec, persona="ai_ml_engineer")
    assert isinstance(fit, FitReport)
    assert fit.coverage_score > 0.4

    # 5. Pricing -> BidDecision & PriceQuote
    decision, quote = pricing_node(spec, fit, risk, persona="ai_ml_engineer")
    assert isinstance(decision, BidDecision)
    assert isinstance(quote, PriceQuote)
    assert decision.decision == "BID"
    assert quote.bid_amount_usd > 0

    # 6. Writer -> ProposalDraft
    draft = writer_node(spec, fit, quote, iteration=1)
    assert isinstance(draft, ProposalDraft)
    assert "PyTorch" in draft.cover_letter

    # 7. Verifier -> ProposalDraft (sanitized)
    verified_draft = verifier_node(draft, fit)
    assert isinstance(verified_draft, ProposalDraft)
    assert verified_draft.grounding_ratio > 0

    # 8. Critic -> Critique
    critique = critic_node(verified_draft)
    assert isinstance(critique, Critique)
    assert critique.client_focus_score >= 3.0

    # 9. Compliance -> ComplianceVerdict
    verdict = compliance_node(verified_draft)
    assert isinstance(verdict, ComplianceVerdict)
    assert verdict.is_compliant is True
    assert verdict.can_submit is True

    # 10. Liaison -> LiaisonDraft
    liaison_draft = liaison_node(
        "Can we hop on a call tomorrow to discuss this?", job_title=spec.title
    )
    assert isinstance(liaison_draft, LiaisonDraft)
    assert liaison_draft.inferred_intent == "interview_invite"
    assert len(liaison_draft.calendar_hold_slot_ids) > 0
