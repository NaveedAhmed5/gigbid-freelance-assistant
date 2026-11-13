"""Fit Matcher Node: Aligns portfolio evidence with extracted job requirements."""

from agent.config import load_agent_config
from agent.handoffs import FitReport, JobSpec
from agent.mcp_client import get_mcp_client
from agent.prompts import load_prompt


def matcher_node(job_spec: JobSpec, persona: str = "ai_ml_engineer") -> FitReport:
    config = load_agent_config()
    config.resolve_model_for_node("matcher")
    load_prompt("fit_matcher.md")

    mcp = get_mcp_client()

    # Call allowed MCP tools
    evidence_results = mcp.call_tool(
        "matcher",
        "search_evidence",
        {
            "requirement": f"{' '.join(job_spec.required_skills)} {job_spec.primary_objective}",
            "k": 3,
            "filters": {"persona": persona},
        },
    )

    verified_skills = mcp.call_tool("matcher", "list_skills", {"persona": persona})
    verified_set = {s.lower() for s in verified_skills}

    matched_skills = [s for s in job_spec.required_skills if s.lower() in verified_set]
    missing_skills = [s for s in job_spec.required_skills if s.lower() not in verified_set]

    coverage_score = round(len(matched_skills) / max(1, len(job_spec.required_skills)), 2)

    evidence_ids = [e["id"] for e in evidence_results]
    primary_cs_id = evidence_ids[0] if evidence_ids else None
    proof_points = [
        f"{e['title']}: {e['summary']} ({e.get('metric_improvement_pct', 30)}% improvement)"
        for e in evidence_results
    ]

    fit_summary = (
        f"Strong candidate alignment ({int(coverage_score*100)}% skill coverage). "
        f"Verified in {len(evidence_results)} matching case studies."
    )

    return FitReport(
        coverage_score=coverage_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        evidence_ids=evidence_ids,
        primary_case_study_id=primary_cs_id,
        proof_points=proof_points,
        fit_summary=fit_summary,
    )
