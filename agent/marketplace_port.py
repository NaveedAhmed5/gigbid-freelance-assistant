"""Marketplace Port Abstract Interface.

Rule 4: Agents and LangGraph nodes MUST NEVER import or call gigsim, databases,
or local files directly. All external reads/writes go through MCP tools via
agent/mcp_client.py and agent/marketplace_port.py.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class MarketplacePort(ABC):
    @abstractmethod
    def search_jobs(
        self, query: Optional[str] = None, category: Optional[str] = None, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search available jobs."""
        pass

    @abstractmethod
    def get_job(self, job_id: str) -> Dict[str, Any]:
        """Fetch full job details."""
        pass

    @abstractmethod
    def get_client_history(self, client_id: str) -> Dict[str, Any]:
        """Fetch client spending, hire rate, and reviews."""
        pass

    @abstractmethod
    def get_connects_balance(self, freelancer_id: str = "freelancer_1") -> Dict[str, Any]:
        """Fetch connects balance."""
        pass

    @abstractmethod
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
        """Create or update a proposal draft without deducting connects."""
        pass

    @abstractmethod
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
        """Submit a proposal with idempotency protection and optional dry run."""
        pass

    @abstractmethod
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
        """Send a message to a client."""
        pass

