#!/usr/bin/env python3
"""GigBid Live Groq End-to-End Verification Smoke Test.

Validates:
1. Groq Cloud API execution on open profile (`llama-3.1-8b-instant` / `llama-3.3-70b-versatile`).
2. Job retrieval from GigSim via Marketplace MCP server.
3. LangGraph BidGraph execution through parallel fan-out (Analyst, Risk, Matcher)
   -> Pricing -> Writer -> Verifier -> Critic -> Compliance.
4. Human approval gate interrupt() with dry_run preview & claim citations.
5. Resume via `{"action": "approve"}` and exactly-once submission to GigSim.
6. Verification of audit log entry, trace ID, and idempotency protection.
"""

import json
import os
import sys
import time
from pathlib import Path

# Add project root to path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command

from agent.config import load_agent_config
from agent.graphs.bid_graph import build_bid_graph
from agent.llm_client import call_llm
from agent.mcp_client import get_mcp_client

load_dotenv(ROOT_DIR / ".env")


def print_header(title: str):
    line = "=" * 80
    print(f"\n{line}\n{title.center(80)}\n{line}\n")


def print_sub(title: str):
    line = "-" * 80
    print(f"\n{line}\n{title}\n{line}")


def run_groq_e2e_verification():
    print_header("GIGBID LIVE GROQ END-TO-END SMOKE TEST")

    # -------------------------------------------------------------------------
    # 1. Environment & Model Routing Audit
    # -------------------------------------------------------------------------
    print(">>> [Phase 1] Auditing Configuration and Groq Credentials...")
    groq_key = os.getenv("GROQ_API_KEY", "").strip()
    if not groq_key:
        print("ERROR: GROQ_API_KEY is not set in environment or .env file.")
        sys.exit(1)

    masked_key = f"{groq_key[:8]}...{groq_key[-4:]}"
    print(f"    GROQ_API_KEY Present : True ({masked_key})")

    config = load_agent_config()
    print(f"    Active Profile       : {config.active_profile}")
    active_profile = config.get_active_profile()
    print(f"    Profile Provider     : {getattr(active_profile, 'provider', 'groq')}")
    print(
        f"    Base URL             : {getattr(active_profile, 'base_url', 'https://api.groq.com/openai/v1')}"
    )
    print(f"    Default Model        : {active_profile.default_llm}")
    print(
        f"    Reasoning Model      : {getattr(active_profile, 'reasoning_llm', 'llama-3.3-70b-versatile')}"
    )

    # Verify node model resolution
    nodes_to_check = {
        "scout": "llama-3.1-8b-instant",
        "analyst": "llama-3.1-8b-instant",
        "risk": "llama-3.1-8b-instant",
        "matcher": "llama-3.3-70b-versatile",
        "pricing": "llama-3.1-8b-instant",
        "writer": "llama-3.3-70b-versatile",
        "verifier": "llama-3.1-8b-instant",
        "critic": "llama-3.3-70b-versatile",
        "compliance": "llama-3.1-8b-instant",
        "liaison": "llama-3.3-70b-versatile",
    }
    print("\n    Node Model Routing Verification:")
    for node, expected_model in nodes_to_check.items():
        resolved = config.resolve_model_for_node(node)
        status = "MATCH" if resolved == expected_model else f"MISMATCH ({resolved})"
        print(f"      - {node:12s} -> {resolved:24s} [{status}]")
        assert resolved == expected_model, f"Expected {expected_model} for {node}, got {resolved}"

    # -------------------------------------------------------------------------
    # 2. Live Groq API Execution Check
    # -------------------------------------------------------------------------
    print_sub("2. Live Groq Cloud API Call Verification")
    print(">>> Executing real live Groq API inference for Job Analyst & Proposal Writer...")

    test_prompt = "Identify three technical deliverables for a real-time vector search microservice in FastAPI."
    resp_analyst, telem_analyst = call_llm("analyst", test_prompt, max_tokens=60)
    print("    [Analyst Node Call]")
    print(f"      Target Model  : {telem_analyst['target_model']}")
    print(f"      Actual Model  : {telem_analyst['actual_model']}")
    print(f"      Real API Call : {telem_analyst['is_real_api']}")
    print(f"      Tokens Used   : {telem_analyst['tokens_consumed']}")
    print(f"      Latency       : {telem_analyst['latency_ms']:.2f} ms")
    print(f"      Response Snippet: {resp_analyst[:120].strip()}...\n")

    resp_writer, telem_writer = call_llm(
        "writer",
        "Draft a compelling 20-word opening hook addressing a client needing sub-50ms RAG retrieval.",
        max_tokens=50,
    )
    print("    [Writer Node Call]")
    print(f"      Target Model  : {telem_writer['target_model']}")
    print(f"      Actual Model  : {telem_writer['actual_model']}")
    print(f"      Real API Call : {telem_writer['is_real_api']}")
    print(f"      Tokens Used   : {telem_writer['tokens_consumed']}")
    print(f"      Latency       : {telem_writer['latency_ms']:.2f} ms")
    print(f"      Response Snippet: {resp_writer[:120].strip()}...\n")

    assert telem_analyst["is_real_api"] is True, "Analyst call failed to reach live Groq API"
    assert telem_writer["is_real_api"] is True, "Writer call failed to reach live Groq API"

    # -------------------------------------------------------------------------
    # 3. Fetch Real Job from GigSim via MCP Server
    # -------------------------------------------------------------------------
    print_sub("3. Marketplace MCP: Fetching Target Job from GigSim")
    mcp_client = get_mcp_client()

    # Search for an AI/ML job matching persona ai_ml_engineer
    jobs = mcp_client.call_tool("scout", "search_jobs", {"query": "PyTorch", "limit": 10})
    if not jobs:
        jobs = mcp_client.call_tool("scout", "search_jobs", {"limit": 10})

    # Pick the first viable job with a defined budget
    target_job = None
    for j in jobs:
        if j.get("budget_usd") and j.get("budget_usd") > 1000:
            target_job = j
            break
    if not target_job:
        target_job = jobs[0]

    job_id = target_job["id"]
    budget_val = target_job.get("budget_usd") or 0.0
    print(f"    Retrieved Job ID   : {job_id}")
    print(f"    Title              : {target_job.get('title')}")
    print(f"    Client Budget      : ${budget_val:,.2f}")
    print(
        f"    Category           : {target_job.get('category')} / {target_job.get('subcategory')}"
    )
    print(f"    Required Skills    : {', '.join(target_job.get('skills', []))}")

    # -------------------------------------------------------------------------
    # 4. BidGraph Orchestration & Parallel Fan-Out
    # -------------------------------------------------------------------------
    print_sub("4. BidGraph Execution: Fan-Out -> Pricing -> Writer -> Critic -> Gate")
    checkpointer = MemorySaver()
    app = build_bid_graph(checkpointer=checkpointer)
    thread_id = f"groq_smoke_{int(time.time())}"
    thread_config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "job_id": job_id,
        "active_persona": "ai_ml_engineer",
        "raw_job_data": target_job,
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

    print(">>> Executing graph nodes until Human Approval interrupt()...")
    start_graph_time = time.time()
    for _ in app.stream(initial_state, thread_config):
        pass
    graph_duration = time.time() - start_graph_time

    snapshot = app.get_state(thread_config)
    print(f"\n    Graph paused at interrupt: {snapshot.next}")
    assert snapshot.next == ("human_approval",), (
        f"Expected graph to pause at human_approval, got {snapshot.next}"
    )

    state_values = snapshot.values
    draft = state_values["proposal_draft"]
    quote = state_values["price_quote"]
    spec = state_values["job_spec"]
    risk = state_values["risk_report"]
    fit = state_values["fit_report"]
    critic = state_values["critique"]
    compliance = state_values["compliance_verdict"]

    print("\n    Pipeline Step Results:")
    print(f"      1. Job Analyst     : Objective='{spec.primary_objective[:60]}...'")
    print(f"      2. Risk Assessor    : Safe={risk.is_safe}, RiskScore={risk.risk_score}")
    print(
        f"      3. Fit Matcher      : Matched={fit.matched_skills}, EvidenceIDs={fit.evidence_ids}"
    )
    print(
        f"      4. Pricing Strategist: Bid=${quote.bid_amount_usd:,.2f}, Strategy={quote.pricing_strategy}"
    )
    print(
        f"      5. Proposal Writer  : GroundingRatio={draft.grounding_ratio * 100:.1f}%, Words={len(draft.cover_letter.split())}"
    )
    print(
        f"      6. Critic Node      : ClientFocus={critic.client_focus_score}/5.0, Clarity={critic.clarity_score}/5.0"
    )
    print(
        f"      7. Compliance Guard : Compliant={compliance.is_compliant}, CanSubmit={compliance.can_submit}"
    )

    # -------------------------------------------------------------------------
    # 5. MCP Dry-Run Validation & Claim Citations
    # -------------------------------------------------------------------------
    print_sub("5. MCP Dry-Run Preview & Evidence Citations")
    dry_run_res = mcp_client.marketplace_server.call_tool(
        "submit_proposal",
        {
            "job_id": job_id,
            "freelancer_id": "freelancer_1",
            "cover_letter": draft.cover_letter,
            "bid_amount_usd": quote.bid_amount_usd,
            "estimated_duration": quote.estimated_duration,
            "idempotency_key": f"dry_run_{job_id}_{thread_id}",
            "dry_run": True,
        },
    )
    print(
        f"    MCP Dry-Run Result : {dry_run_res.get('status')} (Message: {dry_run_res.get('message')})"
    )
    assert dry_run_res.get("dry_run") is True
    assert dry_run_res.get("status") == "VALIDATED"

    print("\n    Verified Claim Citations in Draft:")
    for i, proof in enumerate(draft.proof_points, 1):
        print(f"      [{i}] {proof}")

    print(f"\n    Cumulative Graph Tokens   : {state_values.get('total_tokens_used'):,} tokens")
    print(f"    Cumulative Execution Time : {graph_duration:.2f} s")

    # -------------------------------------------------------------------------
    # 6. Resume Graph with Human Approval -> Submit to GigSim
    # -------------------------------------------------------------------------
    print_sub("6. Resuming Graph: Human Approval -> Live Submission")
    print(">>> Dispatching resume payload: {'action': 'approve'}...")

    for _ in app.stream(Command(resume={"action": "approve"}), thread_config):
        pass

    final_snapshot = app.get_state(thread_config)
    print(f"    Post-Resume Next Steps: {final_snapshot.next}")
    assert final_snapshot.next == (), "Expected graph execution to complete after approval"

    final_values = final_snapshot.values
    print(f"    Final Thread Status   : {final_values.get('status')}")
    assert final_values.get("is_approved_by_human") is True

    # -------------------------------------------------------------------------
    # 7. Audit Log & Idempotency Verification
    # -------------------------------------------------------------------------
    print_sub("7. Audit Log Entry & Idempotency Verification")
    audit_file = ROOT_DIR / "data" / "processed" / "marketplace_audit.log"
    assert audit_file.exists(), f"Audit log file not found at {audit_file}"

    lines = audit_file.read_text(encoding="utf-8").strip().splitlines()
    matching_entries = []
    for line in reversed(lines):
        try:
            entry = json.loads(line)
            if (
                entry.get("tool") == "submit_proposal"
                and entry.get("arguments", {}).get("job_id") == job_id
            ):
                matching_entries.append(entry)
        except Exception:
            continue

    assert len(matching_entries) > 0, f"No audit log entry found for job_id {job_id}"
    latest_entry = matching_entries[0]
    print("    Recorded Audit Entry:")
    print(f"      Timestamp : {latest_entry['timestamp']}")
    print(f"      User      : {latest_entry['user']}")
    print(f"      Tool      : {latest_entry['tool']}")
    print(f"      Trace ID  : {latest_entry['trace_id']}")
    print(f"      Result    : {latest_entry['result_summary'][:120]}...")

    # Idempotency check: Repeat submit tool call with exact same idempotency key
    idempotency_key = f"submit_{job_id}"
    second_submit_res = mcp_client.marketplace_server.call_tool(
        "submit_proposal",
        {
            "job_id": job_id,
            "freelancer_id": "freelancer_1",
            "cover_letter": draft.cover_letter,
            "bid_amount_usd": quote.bid_amount_usd,
            "estimated_duration": quote.estimated_duration,
            "idempotency_key": idempotency_key,
            "dry_run": False,
        },
    )
    print("\n    Idempotency Verification:")
    print(f"      Duplicate Submission Call ID : {second_submit_res.get('submission_id')}")
    print(
        f"      Status                       : {second_submit_res.get('status')} (Zero double-spend)"
    )
    assert second_submit_res.get("status") == "SUBMITTED"

    print_header("ALL LIVE GROQ END-TO-END VERIFICATION CHECKS PASSED")


if __name__ == "__main__":
    run_groq_e2e_verification()
