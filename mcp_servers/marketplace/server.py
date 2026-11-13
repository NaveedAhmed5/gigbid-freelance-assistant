"""Marketplace MCP Server with Idempotency, Rate Limiting, Audit Logs, and Safety Annotations."""

import json
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from mcp_servers.protocol import BaseMCPServer, MCPToolAnnotation

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
AUDIT_LOG_FILE = Path(__file__).resolve().parents[2] / "data" / "processed" / "marketplace_audit.log"


class SubmitProposalInput(BaseModel):
    job_id: str
    freelancer_id: str
    cover_letter: str
    bid_amount_usd: float
    estimated_duration: str
    screening_answers: Dict[str, str] = Field(default_factory=dict)
    idempotency_key: str = Field(description="Unique key to prevent duplicate submissions and double-spending connects.")
    dry_run: bool = Field(default=False, description="If true, simulates validation without committing connects or submission.")
    trace_id: Optional[str] = None


class ProposalDraftInput(BaseModel):
    job_id: str
    freelancer_id: str
    cover_letter: str
    bid_amount_usd: float
    estimated_duration: str
    screening_answers: Dict[str, str] = Field(default_factory=dict)
    draft_id: Optional[str] = None


class SendMessageInput(BaseModel):
    thread_id: str
    sender_id: str
    recipient_id: str
    text: str
    idempotency_key: Optional[str] = None
    dry_run: bool = False
    trace_id: Optional[str] = None


class MarketplaceMCPServer(BaseMCPServer):
    def __init__(self, name: str = "marketplace-mcp-server", version: str = "1.0.0"):
        super().__init__(name, version)
        self.idempotency_store: Dict[str, Dict[str, Any]] = {}
        self.rate_limiter_store: Dict[str, List[float]] = {}  # user -> timestamps
        self.rate_limit_max_requests: int = 60
        self.rate_limit_window_sec: float = 60.0
        self.drafts: Dict[str, Dict[str, Any]] = {}
        self.active_jobs_cache: Dict[str, Dict[str, Any]] = {}
        self._load_jobs()
        self._register_all_tools()

    def _load_jobs(self):
        job_file = DATA_DIR / "processed" / "job_stream.json"
        if job_file.exists():
            jobs = json.loads(job_file.read_text(encoding="utf-8"))
            for j in jobs:
                self.active_jobs_cache[j["id"]] = j

    def _check_rate_limit(self, user_id: str):
        now = time.time()
        window_start = now - self.rate_limit_window_sec
        history = self.rate_limiter_store.setdefault(user_id, [])
        valid_history = [t for t in history if t > window_start]
        self.rate_limiter_store[user_id] = valid_history
        if len(valid_history) >= self.rate_limit_max_requests:
            raise PermissionError(f"Rate limit exceeded for user '{user_id}'. Max {self.rate_limit_max_requests} req/min.")
        self.rate_limiter_store[user_id].append(now)

    def _write_audit_log(self, user: str, tool: str, arguments: Dict[str, Any], result: Any, trace_id: Optional[str]):
        AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "user": user,
            "tool": tool,
            "arguments": arguments,
            "result_summary": str(result)[:300],
            "trace_id": trace_id or str(uuid.uuid4()),
        }
        with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")

    def _register_all_tools(self):
        # 1. search_jobs (read-only)
        self.register_tool(
            name="search_jobs",
            description="Search available job postings in the marketplace.",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "category": {"type": "string"},
                    "limit": {"type": "integer", "default": 20},
                },
            },
            handler=self.tool_search_jobs,
            annotations=MCPToolAnnotation(readOnlyHint=True, idempotentHint=True),
        )

        # 2. get_job (read-only)
        self.register_tool(
            name="get_job",
            description="Get full job details and requirements by job ID.",
            input_schema={
                "type": "object",
                "properties": {"job_id": {"type": "string"}},
                "required": ["job_id"],
            },
            handler=self.tool_get_job,
            annotations=MCPToolAnnotation(readOnlyHint=True, idempotentHint=True),
        )

        # 3. get_client_history (read-only)
        self.register_tool(
            name="get_client_history",
            description="Retrieve client spending history, hire rate, and reviews.",
            input_schema={
                "type": "object",
                "properties": {"client_id": {"type": "string"}},
                "required": ["client_id"],
            },
            handler=self.tool_get_client_history,
            annotations=MCPToolAnnotation(readOnlyHint=True, idempotentHint=True),
        )

        # 4. get_connects_balance (read-only)
        self.register_tool(
            name="get_connects_balance",
            description="Get remaining Connects balance for a freelancer.",
            input_schema={
                "type": "object",
                "properties": {"freelancer_id": {"type": "string", "default": "freelancer_1"}},
            },
            handler=self.tool_get_connects_balance,
            annotations=MCPToolAnnotation(readOnlyHint=True, idempotentHint=True),
        )

        # 5. list_messages (read-only)
        self.register_tool(
            name="list_messages",
            description="List message thread conversation history.",
            input_schema={
                "type": "object",
                "properties": {"thread_id": {"type": "string"}},
                "required": ["thread_id"],
            },
            handler=self.tool_list_messages,
            annotations=MCPToolAnnotation(readOnlyHint=True, idempotentHint=True),
        )

        # 6. create_proposal_draft (safe write / draft)
        self.register_tool(
            name="create_proposal_draft",
            description="Save or update a proposal draft without deducting connects.",
            input_schema=ProposalDraftInput.model_json_schema(),
            handler=self.tool_create_proposal_draft,
            annotations=MCPToolAnnotation(readOnlyHint=False, destructiveHint=False, idempotentHint=True),
        )

        # 7. submit_proposal (destructive write: spends connects)
        self.register_tool(
            name="submit_proposal",
            description="Submit a live proposal to a client. Deducts connects. Requires idempotency_key.",
            input_schema=SubmitProposalInput.model_json_schema(),
            handler=self.tool_submit_proposal,
            annotations=MCPToolAnnotation(readOnlyHint=False, destructiveHint=True, idempotentHint=True),
        )

        # 8. send_message (write)
        self.register_tool(
            name="send_message",
            description="Send a message to a client within an active thread.",
            input_schema=SendMessageInput.model_json_schema(),
            handler=self.tool_send_message,
            annotations=MCPToolAnnotation(readOnlyHint=False, destructiveHint=False, idempotentHint=True),
        )

    # Tool Handlers
    def tool_search_jobs(self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        jobs = list(self.active_jobs_cache.values())
        if category:
            jobs = [j for j in jobs if j.get("category", "").lower() == category.lower()]
        if query:
            q = query.lower()
            jobs = [j for j in jobs if q in j.get("title", "").lower() or q in j.get("description", "").lower()]
        return jobs[:limit]

    def tool_get_job(self, job_id: str) -> Dict[str, Any]:
        if job_id not in self.active_jobs_cache:
            raise KeyError(f"Job {job_id} not found in marketplace.")
        return self.active_jobs_cache[job_id]

    def tool_get_client_history(self, client_id: str) -> Dict[str, Any]:
        return {
            "client_id": client_id,
            "total_spend_usd": 45000.0,
            "hire_rate": 0.78,
            "rating": 4.92,
            "payment_verified": True,
            "open_jobs": 2,
            "completed_contracts": 18,
        }

    def tool_get_connects_balance(self, freelancer_id: str = "freelancer_1") -> Dict[str, Any]:
        return {"freelancer_id": freelancer_id, "balance": 150}

    def tool_list_messages(self, thread_id: str) -> List[Dict[str, Any]]:
        return []

    def tool_create_proposal_draft(self, **kwargs) -> Dict[str, Any]:
        data = ProposalDraftInput(**kwargs)
        draft_id = data.draft_id or f"draft_{uuid.uuid4().hex[:8]}"
        draft_record = {
            "draft_id": draft_id,
            "job_id": data.job_id,
            "freelancer_id": data.freelancer_id,
            "cover_letter": data.cover_letter,
            "bid_amount_usd": data.bid_amount_usd,
            "estimated_duration": data.estimated_duration,
            "screening_answers": data.screening_answers,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "status": "DRAFT",
        }
        self.drafts[draft_id] = draft_record
        return draft_record

    def tool_submit_proposal(self, **kwargs) -> Dict[str, Any]:
        input_data = SubmitProposalInput(**kwargs)
        self._check_rate_limit(input_data.freelancer_id)

        # Idempotency check: if key already used, return stored response immediately
        if input_data.idempotency_key in self.idempotency_store:
            return self.idempotency_store[input_data.idempotency_key]

        job = self.active_jobs_cache.get(input_data.job_id)
        if not job:
            raise KeyError(f"Job '{input_data.job_id}' does not exist.")

        connects_required = job.get("connects_required", 8)

        if input_data.dry_run:
            preview_result = {
                "dry_run": True,
                "status": "VALIDATED",
                "job_id": input_data.job_id,
                "freelancer_id": input_data.freelancer_id,
                "connects_to_deduct": connects_required,
                "bid_amount_usd": input_data.bid_amount_usd,
                "idempotency_key": input_data.idempotency_key,
                "message": "Proposal passed dry-run validation. No connects spent.",
            }
            self._write_audit_log(input_data.freelancer_id, "submit_proposal[dry_run]", input_data.model_dump(), preview_result, input_data.trace_id)
            return preview_result

        # Commit submission
        submission_id = f"sub_{uuid.uuid4().hex[:8]}"
        submission_result = {
            "dry_run": False,
            "submission_id": submission_id,
            "status": "SUBMITTED",
            "job_id": input_data.job_id,
            "freelancer_id": input_data.freelancer_id,
            "connects_spent": connects_required,
            "bid_amount_usd": input_data.bid_amount_usd,
            "submitted_at": datetime.now(timezone.utc).isoformat(),
            "idempotency_key": input_data.idempotency_key,
        }

        # Store for idempotency
        self.idempotency_store[input_data.idempotency_key] = submission_result
        self._write_audit_log(input_data.freelancer_id, "submit_proposal", input_data.model_dump(), submission_result, input_data.trace_id)
        return submission_result

    def tool_send_message(self, **kwargs) -> Dict[str, Any]:
        input_data = SendMessageInput(**kwargs)
        self._check_rate_limit(input_data.sender_id)

        if input_data.idempotency_key and input_data.idempotency_key in self.idempotency_store:
            return self.idempotency_store[input_data.idempotency_key]

        if input_data.dry_run:
            res = {
                "dry_run": True,
                "thread_id": input_data.thread_id,
                "sender_id": input_data.sender_id,
                "recipient_id": input_data.recipient_id,
                "status": "VALIDATED",
                "message": "Message passed dry run check.",
            }
            return res

        msg_id = f"msg_{uuid.uuid4().hex[:8]}"
        res = {
            "dry_run": False,
            "message_id": msg_id,
            "thread_id": input_data.thread_id,
            "sender_id": input_data.sender_id,
            "recipient_id": input_data.recipient_id,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "status": "SENT",
        }
        if input_data.idempotency_key:
            self.idempotency_store[input_data.idempotency_key] = res
        self._write_audit_log(input_data.sender_id, "send_message", input_data.model_dump(), res, input_data.trace_id)
        return res


def create_marketplace_mcp_server() -> MarketplaceMCPServer:
    return MarketplaceMCPServer()
