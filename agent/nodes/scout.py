"""Scout Agent Node: Fast intake and coarse relevance filter."""

from typing import Any, Dict

from agent.config import load_agent_config
from agent.mcp_client import get_mcp_client
from agent.prompts import load_prompt


def scout_node(job_posting: Dict[str, Any], persona: str = "ai_ml_engineer") -> Dict[str, Any]:
    config = load_agent_config()
    model = config.resolve_model_for_node("scout")
    load_prompt("scout_filter.md")

    # Use MCP client for tool call (Scout is allowed search_jobs, get_job, get_connects_balance)
    client = get_mcp_client()
    balance = client.call_tool("scout", "get_connects_balance", {"freelancer_id": "freelancer_1"})

    # Evaluate relevance
    title = job_posting.get("title", "")
    desc = job_posting.get("description", "")
    job_posting.get("category", "")

    # Coarse filter
    is_relevant = len(title) > 5 and len(desc) > 20
    if "logo" in title.lower() and persona == "ai_ml_engineer":
        is_relevant = False

    return {
        "node": "scout",
        "model_used": model,
        "is_relevant": is_relevant,
        "job_id": job_posting.get("id"),
        "connects_available": balance.get("balance", 0),
    }
