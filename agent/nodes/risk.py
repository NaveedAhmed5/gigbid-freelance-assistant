"""Risk Assessor Node: Scam detection, off-platform traps, prompt injection defense."""

from typing import Any, Dict

from agent.config import load_agent_config
from agent.handoffs import RiskReport
from agent.mcp_client import get_mcp_client
from agent.prompts import load_prompt


def risk_node(job_posting: Dict[str, Any]) -> RiskReport:
    config = load_agent_config()
    config.resolve_model_for_node("risk")
    load_prompt("risk_assessor.md")

    client_id = job_posting.get("client_id", "client_unknown")
    mcp = get_mcp_client()

    # Call allowed MCP tool get_client_history
    mcp.call_tool("risk", "get_client_history", {"client_id": client_id})

    desc = job_posting.get("description", "").lower()
    flags = []
    has_off_platform = False
    has_prompt_injection = False
    is_unpaid = False

    # Scam & Off-Platform checks
    off_platform_keywords = [
        "telegram",
        "whatsapp",
        "crypto",
        "usdt",
        "direct wire",
        "paypal outside",
    ]
    for kw in off_platform_keywords:
        if kw in desc:
            has_off_platform = True
            flags.append(f"Off-platform contact or payment solicitation: '{kw}'")

    # Prompt injection patterns
    injection_keywords = [
        "system directive",
        "ignore all previous",
        "override:",
        "human reviewer note",
        "disregard prior",
    ]
    for kw in injection_keywords:
        if kw in desc:
            has_prompt_injection = True
            flags.append(f"Adversarial prompt injection pattern detected: '{kw}'")

    # Free work traps
    if "free sample" in desc or "unpaid trial" in desc:
        is_unpaid = True
        flags.append("Demands free test assignment or unpaid trial.")

    is_safe = not (
        has_off_platform or has_prompt_injection or is_unpaid or job_posting.get("is_scam", False)
    )
    risk_score = 0.85 if not is_safe else 0.05

    summary = (
        "Job verified safe and fully compliant with marketplace policies."
        if is_safe
        else f"High risk detected: {'; '.join(flags)}"
    )

    return RiskReport(
        is_safe=is_safe,
        risk_score=risk_score,
        flags=flags,
        has_off_platform_trap=has_off_platform,
        has_prompt_injection=has_prompt_injection,
        is_unpaid_work_trap=is_unpaid,
        summary=summary,
    )
