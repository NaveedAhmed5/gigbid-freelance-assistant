"""GigSim Marketplace Adapter."""

from typing import Any, Dict, List, Optional

from agent.marketplace_port import MarketplacePort
from mcp_servers.marketplace.server import create_marketplace_mcp_server


class GigSimAdapter(MarketplacePort):
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = base_url
        self._server = create_marketplace_mcp_server()

    def search_jobs(
        self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        return self._server.call_tool("search_jobs", {"query": query, "category": category, "limit": limit})

    def get_job(self, job_id: str) -> Dict[str, Any]:
        return self._server.call_tool("get_job", {"job_id": job_id})

    def get_client_history(self, client_id: str) -> Dict[str, Any]:
        return self._server.call_tool("get_client_history", {"client_id": client_id})

    def get_connects_balance(self, freelancer_id: str = "freelancer_1") -> Dict[str, Any]:
        return self._server.call_tool("get_connects_balance", {"freelancer_id": freelancer_id})

    def create_proposal_draft(
        self,
        job_id: str,
        freelancer_id: str,
        cover_letter: str,
        bid_amount_usd: float,
        estimated_duration: str,
        screening_answers: Optional[Dict[str, str]] = None,
        draft_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self._server.call_tool(
            "create_proposal_draft",
            {
                "job_id": job_id,
                "freelancer_id": freelancer_id,
                "cover_letter": cover_letter,
                "bid_amount_usd": bid_amount_usd,
                "estimated_duration": estimated_duration,
                "screening_answers": screening_answers or {},
                "draft_id": draft_id,
            },
        )

    def submit_proposal(
        self,
        job_id: str,
        freelancer_id: str,
        cover_letter: str,
        bid_amount_usd: float,
        estimated_duration: str,
        idempotency_key: str,
        dry_run: bool = False,
        screening_answers: Optional[Dict[str, str]] = None,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self._server.call_tool(
            "submit_proposal",
            {
                "job_id": job_id,
                "freelancer_id": freelancer_id,
                "cover_letter": cover_letter,
                "bid_amount_usd": bid_amount_usd,
                "estimated_duration": estimated_duration,
                "idempotency_key": idempotency_key,
                "dry_run": dry_run,
                "screening_answers": screening_answers or {},
                "trace_id": trace_id,
            },
        )

    def send_message(
        self,
        thread_id: str,
        sender_id: str,
        recipient_id: str,
        text: str,
        idempotency_key: Optional[str] = None,
        dry_run: bool = False,
        trace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        return self._server.call_tool(
            "send_message",
            {
                "thread_id": thread_id,
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "text": text,
                "idempotency_key": idempotency_key,
                "dry_run": dry_run,
                "trace_id": trace_id,
            },
        )
