from langgraph.checkpoint.memory import MemorySaver

from agent.graphs.bid_graph import build_bid_graph
from agent.graphs.conversation_graph import build_conversation_graph
from agent.memory.promotion_rules import MemoryCandidate
from agent.memory.store import AgentMemoryStore


def test_bid_graph_execution_interrupt_and_resume():
    checkpointer = MemorySaver()
    app = build_bid_graph(checkpointer=checkpointer)

    thread_config = {"configurable": {"thread_id": "test_thread_001"}}

    sample_job = {
        "id": "job_durable_101",
        "title": "Build PyTorch Enterprise RAG Pipeline",
        "description": "Looking for senior PyTorch expert for enterprise RAG system with sub-50ms latency.",
        "skills": ["Python", "PyTorch", "FastAPI"],
        "budget_usd": 3500.0,
        "duration": "1 month",
        "category": "AI/ML",
        "subcategory": "Healthcare",
        "client_id": "client_99",
    }

    initial_state = {
        "job_id": sample_job["id"],
        "active_persona": "ai_ml_engineer",
        "raw_job_data": sample_job,
        "job_spec": None,
        "risk_report": None,
        "fit_report": None,
        "bid_decision": None,
        "price_quote": None,
        "proposal_draft": None,
        "critique": None,
        "compliance_verdict": None,
        "critic_loop_count": 0,
        "is_approved_by_human": False,
        "status": "IN_PROGRESS",
        "total_tokens_used": 0,
        "total_steps_executed": 0,
        "trace_steps": [],
        "style_memory_keys": [],
        "outcome_memory_keys": [],
        "memory_context": "",
    }

    # Step 1: Run graph until human approval interrupt
    for _ in app.stream(initial_state, thread_config):
        pass

    # Verify that the graph paused at the human approval gate
    current_snapshot = app.get_state(thread_config)
    assert current_snapshot.next == ("human_approval",)
    assert current_snapshot.values["status"] == "AWAITING_APPROVAL"
    assert current_snapshot.values["compliance_verdict"].can_submit is True

    # Step 2: Resume with human approval
    for _ in app.stream(None, thread_config):
        pass

    # Check updated state after resuming
    final_snapshot = app.get_state(thread_config)
    assert final_snapshot.values["job_id"] == "job_durable_101"


def test_conversation_graph_interrupt_and_resume():
    checkpointer = MemorySaver()
    app = build_conversation_graph(checkpointer=checkpointer)

    thread_config = {"configurable": {"thread_id": "conv_thread_001"}}
    initial_state = {
        "thread_id": "conv_thread_001",
        "client_id": "client_55",
        "job_id": "job_42",
        "incoming_message": "Hi, we loved your proposal! Can we schedule a quick call tomorrow at 2pm?",
        "liaison_draft": None,
        "is_approved_by_human": False,
        "status": "IN_PROGRESS",
        "total_tokens_used": 0,
        "trace_steps": [],
    }

    # Run until interrupt
    for _ in app.stream(initial_state, thread_config):
        pass

    snapshot = app.get_state(thread_config)
    assert snapshot.next == ("human_gate",)
    assert snapshot.values["status"] == "AWAITING_APPROVAL"
    assert snapshot.values["liaison_draft"].inferred_intent == "interview_invite"


def test_memory_store_promotion_rules(tmp_path):
    store = AgentMemoryStore(storage_path=tmp_path / "memory.json")

    # 1. Style memory promotion candidate
    style_cand = MemoryCandidate(
        category="style",
        source_id="edit_01",
        original_text="I am writing to apply for your job because I have great skills in Python and PyTorch.",
        edited_text="We architected a high-throughput PyTorch pipeline delivering 42% latency reduction.",
    )
    style_key = store.promote_candidate(style_cand)
    assert style_key is not None
    assert "style_edit_01" in style_key

    # 2. Outcome memory promotion candidate (won outcome)
    outcome_cand = MemoryCandidate(
        category="outcome",
        source_id="job_won_99",
        original_text="Hi team — your objective for PyTorch enterprise RAG directly matches our deployment.",
        outcome="won",
        metadata={"industry": "Healthcare"},
    )
    outcome_key = store.promote_candidate(outcome_cand)
    assert outcome_key is not None

    # 3. Retrieve context
    ctx = store.retrieve_memory_context()
    assert "Relevant Style Memories" in ctx
    assert "Relevant Outcome Memories" in ctx

    # 4. Delete memory
    assert store.delete_memory(style_key) is True
    assert store.delete_memory(style_key) is False
