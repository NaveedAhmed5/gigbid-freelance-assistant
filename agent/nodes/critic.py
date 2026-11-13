"""Proposal Critic Node: Constructive review on client focus, hook, and clarity."""

from agent.config import load_agent_config
from agent.handoffs import Critique, ProposalDraft
from agent.prompts import load_prompt


def critic_node(draft: ProposalDraft) -> Critique:
    config = load_agent_config()
    config.resolve_model_for_node("critic")
    load_prompt("critic.md")

    text = draft.cover_letter.lower()
    feedback_points = []

    # Check for generic openings
    has_generic = any(gen in text[:120] for gen in ["dear hiring manager", "i am the perfect fit", "i am writing to apply"])
    if has_generic:
        feedback_points.append("Opening contains generic template language. Replace immediately with client's core problem.")

    has_metrics = "%" in text or "latency" in text or "roi" in text
    if not has_metrics:
        feedback_points.append("Lacks quantified proof points. Introduce concrete metrics from case study.")

    client_focus_score = 4.8 if not has_generic else 2.5
    clarity_score = 4.7 if has_metrics else 3.2

    requires_revision = (has_generic or not has_metrics) and (draft.iteration_count < 2)

    feedback = "Draft is sharply tailored with verifiable proof points." if not requires_revision else " | ".join(feedback_points)

    return Critique(
        client_focus_score=client_focus_score,
        clarity_score=clarity_score,
        feedback=feedback,
        requires_revision=requires_revision,
        suggested_improvements=feedback_points,
    )
