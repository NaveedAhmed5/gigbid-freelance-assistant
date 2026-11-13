"""ConversationGraph: Client Messaging, Scheduling & Approval Workflow."""

from typing import Any, Dict, Optional

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from agent.nodes.liaison import liaison_node
from agent.state import ConversationGraphState, TraceStep


def node_liaison_draft(state: ConversationGraphState) -> Dict[str, Any]:
    draft = liaison_node(incoming_message=state["incoming_message"])
    step: TraceStep = {
        "step_number": 1,
        "node_name": "liaison",
        "action_type": "DRAFT_REPLY",
        "tokens_consumed": 380,
        "latency_ms": 110.0,
        "output_summary": f"Intent={draft.inferred_intent}, Holds={draft.calendar_hold_slot_ids}",
    }
    return {
        "liaison_draft": draft,
        "status": "AWAITING_APPROVAL",
        "total_tokens_used": 380,
        "trace_steps": [step],
    }


def node_conversation_human_gate(state: ConversationGraphState) -> Dict[str, Any]:
    draft = state["liaison_draft"]
    approval_payload = {
        "thread_id": state["thread_id"],
        "client_id": state["client_id"],
        "proposed_reply": draft.response_draft if draft else "",
        "calendar_holds": draft.calendar_hold_slot_ids if draft else [],
    }

    # Pause execution for human review
    response = interrupt({"type": "MESSAGE_APPROVAL_REQUIRED", "data": approval_payload})
    is_approved = response.get("approved", False) if isinstance(response, dict) else False

    step: TraceStep = {
        "step_number": 2,
        "node_name": "human_gate",
        "action_type": "APPROVAL_DECISION",
        "tokens_consumed": 20,
        "latency_ms": 5.0,
        "output_summary": f"Human approved message: {is_approved}",
    }
    return {
        "is_approved_by_human": is_approved,
        "status": "APPROVED" if is_approved else "REJECTED_BY_USER",
        "total_tokens_used": 20,
        "trace_steps": [step],
    }


def node_send_reply(state: ConversationGraphState) -> Dict[str, Any]:
    step: TraceStep = {
        "step_number": 3,
        "node_name": "send_reply",
        "action_type": "MESSAGE_SENT",
        "tokens_consumed": 150,
        "latency_ms": 80.0,
        "output_summary": "Message dispatched to client thread.",
    }
    return {
        "status": "COMPLETED",
        "total_tokens_used": 150,
        "trace_steps": [step],
    }


def route_after_conversation_approval(state: ConversationGraphState) -> str:
    if state.get("is_approved_by_human"):
        return "send_reply"
    return "end"


def build_conversation_graph(checkpointer: Optional[Any] = None) -> Any:
    workflow = StateGraph(ConversationGraphState)

    workflow.add_node("liaison_draft", node_liaison_draft)
    workflow.add_node("human_gate", node_conversation_human_gate)
    workflow.add_node("send_reply", node_send_reply)

    workflow.add_edge(START, "liaison_draft")
    workflow.add_edge("liaison_draft", "human_gate")
    workflow.add_conditional_edges(
        "human_gate",
        route_after_conversation_approval,
        {"send_reply": "send_reply", "end": END},
    )
    workflow.add_edge("send_reply", END)

    cp = checkpointer if checkpointer is not None else MemorySaver()
    return workflow.compile(checkpointer=cp)
