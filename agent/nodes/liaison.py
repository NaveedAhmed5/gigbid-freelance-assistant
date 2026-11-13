"""Client Liaison Node: Messaging, intent evaluation, and calendar holds."""

from agent.config import load_agent_config
from agent.handoffs import LiaisonDraft
from agent.mcp_client import get_mcp_client
from agent.prompts import load_prompt


def liaison_node(incoming_message: str, job_title: str = "Enterprise Architecture", persona: str = "ai_ml_engineer") -> LiaisonDraft:
    config = load_agent_config()
    config.resolve_model_for_node("liaison")
    load_prompt("client_liaison.md")

    mcp = get_mcp_client()

    # Call allowed MCP tool get_free_calendar_slots
    free_slots = mcp.call_tool("liaison", "get_free_calendar_slots", {"days_ahead": 3, "duration_minutes": 30})

    lower_msg = incoming_message.lower()
    proposed_hold_ids = []

    if any(k in lower_msg for k in ["call", "meet", "schedule", "interview", "hop on"]):
        intent = "interview_invite"
        if free_slots:
            first_slot = free_slots[0]
            # Place tentative hold via Workspace MCP tool
            mcp.call_tool(
                "liaison",
                "create_tentative_interview_hold",
                {
                    "slot_id": first_slot["slot_id"],
                    "client_name": "Prospective Client",
                    "job_id": "current_job",
                    "notes": "Tentative slot held for client meeting proposal.",
                },
            )
            proposed_hold_ids.append(first_slot["slot_id"])
            response_text = (
                f"Thank you for the invitation! I would be glad to discuss the technical roadmap. "
                f"I have tentatively held {first_slot['start_time']} UTC. Does that time work for your team?"
            )
        else:
            response_text = "I would be delighted to connect. What times this week work best on your calendar?"
    elif "rate" in lower_msg or "budget" in lower_msg:
        intent = "rate_negotiation"
        response_text = (
            "Thank you for asking. Our rate reflects dedicated production-grade delivery with automated verification. "
            "I am happy to discuss milestone structures to fit your budget."
        )
    else:
        intent = "technical_inquiry"
        response_text = (
            "Thanks for your message! We deploy typed modular architectures with comprehensive integration testing. "
            "Let me know if you would like me to detail the specific pipeline design."
        )

    return LiaisonDraft(
        client_message=incoming_message,
        inferred_intent=intent,
        response_draft=response_text,
        calendar_hold_slot_ids=proposed_hold_ids,
        requires_human_approval=True,
    )
