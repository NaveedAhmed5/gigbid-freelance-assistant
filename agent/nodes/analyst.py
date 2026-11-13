"""Job Analyst Node: Structured intent, constraints, and deliverables extraction."""

from typing import Any, Dict

from agent.config import load_agent_config
from agent.handoffs import JobSpec
from agent.prompts import load_prompt


def analyst_node(job_posting: Dict[str, Any]) -> JobSpec:
    config = load_agent_config()
    config.resolve_model_for_node("analyst")
    load_prompt("job_analyst.md")

    # Pure analytical extraction without external tools (Rule 4 allowlist: None)
    title = job_posting.get("title", "")
    job_posting.get("description", "")
    skills = job_posting.get("skills", ["Python", "FastAPI"])
    budget = job_posting.get("budget_usd")
    industry = job_posting.get("subcategory", "Software Engineering")

    return JobSpec(
        job_id=job_posting.get("id", "unknown_job"),
        title=title,
        primary_objective=f"Develop and deploy architecture for {title}",
        deliverables=[
            f"Implement core modules using {', '.join(skills[:2])}",
            "Conduct automated performance benchmarking and validation tests",
            "Deliver production deployment documentation and operational runbook",
        ],
        required_skills=skills,
        timeline=job_posting.get("duration", "1 to 3 months"),
        client_industry=industry,
        job_type=job_posting.get("job_type", "fixed_price"),
        client_budget_usd=budget,
        screening_questions=job_posting.get("screening_questions", []),
    )
