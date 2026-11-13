"""Portfolio MCP Server Prompt Templates."""

from typing import Optional

from mcp_servers.portfolio.tools import search_evidence


def prompt_answer_screening_question(question: str, persona: Optional[str] = "ai_ml_engineer") -> str:
    """Prompt template: Answer a screening question from my portfolio."""
    evidence = search_evidence(requirement=question, k=2, filters={"persona": persona} if persona else None)
    evidence_text = "\n".join(
        [f"- Project: {e['title']}. Outcome: {e['summary']} (Metric: {e['metric_improvement_pct']}%)" for e in evidence]
    )
    return f"""Please formulate a concise, professional answer to the following screening question:
"{question}"

Base your response strictly on this verified evidence from my portfolio:
{evidence_text}

Rules:
- Be factual and reference the specific metric improvement.
- Do not fabricate details.
- Keep the answer under 100 words.
"""


def prompt_summarize_portfolio_evidence(skill_or_requirement: str, persona: Optional[str] = "ai_ml_engineer") -> str:
    """Prompt template: Summarize relevant portfolio evidence."""
    evidence = search_evidence(requirement=skill_or_requirement, k=3, filters={"persona": persona} if persona else None)
    evidence_text = "\n".join(
        [f"1. {e['title']} ({e['industry']}): {e['summary']} [Skills: {', '.join(e['skills'])}]" for e in evidence]
    )
    return f"""Summarize the candidate's verified capabilities and proof points regarding "{skill_or_requirement}":

Verified Case Studies:
{evidence_text}

Synthesize a bulleted summary demonstrating demonstrated mastery, production outcomes, and relevance.
"""
