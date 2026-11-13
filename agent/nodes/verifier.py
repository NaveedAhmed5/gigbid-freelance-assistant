"""Claim Verifier Node: Decomposes draft into claims and verifies against evidence."""

from agent.config import load_agent_config
from agent.handoffs import FitReport, ProposalDraft
from agent.mcp_client import get_mcp_client
from rag.verify import verify_claims


def verifier_node(draft: ProposalDraft, fit_report: FitReport) -> ProposalDraft:
    config = load_agent_config()
    config.resolve_model_for_node("verifier")

    mcp = get_mcp_client()

    # Load evidence objects for verification
    evidence_items = []
    for cs_id in fit_report.evidence_ids:
        try:
            cs = mcp.call_tool("verifier", "get_case_study", {"id": cs_id})
            evidence_items.append(cs)
        except Exception:
            pass

    report = verify_claims(draft.cover_letter, evidence_items)

    # Return updated draft with sanitized grounded text
    return ProposalDraft(
        cover_letter=report.sanitized_text,
        opening_hook=draft.opening_hook,
        technical_solution=draft.technical_solution,
        proof_points=draft.proof_points,
        screening_answers=draft.screening_answers,
        iteration_count=draft.iteration_count,
        grounding_ratio=report.grounding_ratio,
    )
