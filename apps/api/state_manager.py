"""API State Manager: Bridges LangGraph execution, checkpointer, and REST state."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from langgraph.checkpoint.memory import MemorySaver

from agent.graphs.bid_graph import build_bid_graph
from agent.graphs.conversation_graph import build_conversation_graph

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class APIStateManager:
    def __init__(self):
        self.checkpointer = MemorySaver()
        self.bid_graph = build_bid_graph(checkpointer=self.checkpointer)
        self.conversation_graph = build_conversation_graph(checkpointer=self.checkpointer)
        self.jobs_cache: Dict[str, Dict[str, Any]] = {}
        self.pending_approvals: Dict[str, Dict[str, Any]] = {}
        self.runs: Dict[str, Dict[str, Any]] = {}
        self.proposals: Dict[str, Dict[str, Any]] = {}
        self.messages: Dict[str, List[Dict[str, Any]]] = {}
        self.sse_event_listeners: List[Any] = []
        self._load_seed_jobs()

    def _load_seed_jobs(self):
        job_file = DATA_DIR / "processed" / "job_stream.json"
        if job_file.exists():
            jobs = json.loads(job_file.read_text(encoding="utf-8"))
            for j in jobs:
                self.jobs_cache[j["id"]] = j

    def run_bid_pipeline(self, job_id: str, persona: str = "ai_ml_engineer") -> Dict[str, Any]:
        """Execute BidGraph for a job up to the human approval gate."""
        job_data = self.jobs_cache.get(job_id)
        if not job_data:
            raise KeyError(f"Job {job_id} not found.")

        thread_id = f"thread_{job_id}"
        config = {"configurable": {"thread_id": thread_id}}

        initial_state = {
            "job_id": job_id,
            "active_persona": persona,
            "raw_job_data": job_data,
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

        # Stream and record trace steps
        steps_recorded = []
        for event in self.bid_graph.stream(initial_state, config):
            for node_name, node_update in event.items():
                if isinstance(node_update, dict) and "trace_steps" in node_update:
                    steps_recorded.extend(node_update["trace_steps"])

        snapshot = self.bid_graph.get_state(config)
        vals = snapshot.values

        run_record = {
            "run_id": f"run_{job_id}",
            "job_id": job_id,
            "persona": persona,
            "status": vals.get("status", "COMPLETED"),
            "total_tokens_used": vals.get("total_tokens_used", 0),
            "total_steps": vals.get("total_steps_executed", 0),
            "trace_steps": vals.get("trace_steps", []),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.runs[run_record["run_id"]] = run_record

        # If graph reached human approval gate, record pending approval
        if vals.get("status") == "AWAITING_APPROVAL":
            self.pending_approvals[job_id] = {
                "job_id": job_id,
                "thread_id": thread_id,
                "proposal_draft": vals["proposal_draft"].model_dump()
                if vals.get("proposal_draft")
                else None,
                "price_quote": vals["price_quote"].model_dump()
                if vals.get("price_quote")
                else None,
                "fit_report": vals["fit_report"].model_dump() if vals.get("fit_report") else None,
                "risk_report": vals["risk_report"].model_dump()
                if vals.get("risk_report")
                else None,
                "compliance_verdict": vals["compliance_verdict"].model_dump()
                if vals.get("compliance_verdict")
                else None,
                "status": "PENDING",
            }

        return run_record

    def resume_approval(
        self,
        job_id: str,
        action: str,
        edited_text: Optional[str] = None,
        feedback: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Resume paused LangGraph thread with human approval, edit, or rejection."""
        approval = self.pending_approvals.get(job_id)
        if not approval:
            raise KeyError(f"No pending approval for job {job_id}")

        thread_id = approval["thread_id"]
        config = {"configurable": {"thread_id": thread_id}}

        is_approved = action == "approve"

        # Resume execution
        for _ in self.bid_graph.stream(None, config):
            pass

        self.bid_graph.get_state(config)
        del self.pending_approvals[job_id]

        status_result = "SUBMITTED" if is_approved else "REJECTED_BY_HUMAN"
        result_record = {
            "job_id": job_id,
            "action": action,
            "status": status_result,
            "resumed_at": datetime.now(timezone.utc).isoformat(),
        }
        self.proposals[f"prop_{job_id}"] = result_record
        return result_record


_api_state: Optional[APIStateManager] = None


def get_api_state() -> APIStateManager:
    global _api_state
    if _api_state is None:
        _api_state = APIStateManager()
    return _api_state
