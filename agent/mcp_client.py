"""MCP Client with Per-Agent Allowlists, Retries, and Degraded Mode.

Rule 4: Agents and LangGraph nodes MUST NEVER import or call gigsim, databases,
or local files directly. All external reads/writes go through MCP tools via
agent/mcp_client.py and agent/marketplace_port.py.
"""

import time
from typing import Any, Dict, List, Optional, Set

from mcp_servers.marketplace.server import create_marketplace_mcp_server
from mcp_servers.portfolio.server import create_portfolio_mcp_server
from mcp_servers.workspace.server import create_workspace_mcp_server

AGENT_TOOL_ALLOWLISTS: Dict[str, Set[str]] = {
    "scout": {"search_jobs", "get_job", "get_connects_balance"},
    "analyst": set(),  # None
    "risk": {"get_job", "get_client_history"},
    "matcher": {"search_evidence", "get_case_study", "list_skills"},
    "pricing": {"get_job", "get_client_history", "get_connects_balance"},
    "writer": {"search_evidence", "get_case_study"},
    "verifier": {"search_evidence", "get_case_study"},
    "critic": {"search_evidence", "get_case_study"},
    "compliance": set(),  # None
    "liaison": {
        "list_messages",
        "send_message",
        "get_free_calendar_slots",
        "create_tentative_interview_hold",
        "create_email_draft",
    },
}


class MCPClient:
    def __init__(self, simulate_network_failure: bool = False):
        self.portfolio_server = create_portfolio_mcp_server()
        self.marketplace_server = create_marketplace_mcp_server()
        self.workspace_server = create_workspace_mcp_server()
        self.simulate_network_failure = simulate_network_failure
        self.degraded_mode: bool = False
        self.queued_requests: List[Dict[str, Any]] = []

    def set_degraded_mode(self, enabled: bool):
        self.degraded_mode = enabled

    def _resolve_server_for_tool(self, tool_name: str):
        if tool_name in self.portfolio_server.tools:
            return self.portfolio_server
        if tool_name in self.marketplace_server.tools:
            return self.marketplace_server
        if tool_name in self.workspace_server.tools:
            return self.workspace_server
        raise KeyError(f"No MCP server registers tool '{tool_name}'.")

    def call_tool(
        self,
        agent_role: str,
        tool_name: str,
        arguments: Dict[str, Any],
        max_retries: int = 3,
        backoff_sec: float = 0.1,
    ) -> Any:
        """Call an MCP tool enforcing agent-level allowlist, retries, and degraded mode."""
        role_key = agent_role.lower()
        allowed_tools = AGENT_TOOL_ALLOWLISTS.get(role_key, set())

        # Enforce Rule 4 and strict client discipline
        if tool_name not in allowed_tools:
            raise PermissionError(
                f"Agent '{agent_role}' is unauthorized to call tool '{tool_name}'. "
                f"Allowed tools for this role: {sorted(list(allowed_tools)) or 'None'}"
            )

        if self.degraded_mode or self.simulate_network_failure:
            # Queue work and return degraded placeholder
            queue_item = {
                "agent": agent_role,
                "tool": tool_name,
                "arguments": arguments,
                "timestamp": time.time(),
            }
            self.queued_requests.append(queue_item)
            return {
                "degraded_mode": True,
                "status": "QUEUED",
                "message": f"Tool '{tool_name}' queued in Degraded Mode due to server unreachability.",
                "queued_item": queue_item,
            }

        server = self._resolve_server_for_tool(tool_name)

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                return server.call_tool(tool_name, arguments)
            except Exception as e:
                last_error = e
                if attempt < max_retries:
                    time.sleep(backoff_sec * (2 ** (attempt - 1)))
                else:
                    break

        # If retries exhausted, switch to Degraded Mode
        self.degraded_mode = True
        queue_item = {
            "agent": agent_role,
            "tool": tool_name,
            "arguments": arguments,
            "error": str(last_error),
        }
        self.queued_requests.append(queue_item)
        return {
            "degraded_mode": True,
            "status": "QUEUED_ON_FAILURE",
            "error": str(last_error),
            "message": f"Server call failed after {max_retries} attempts; degraded fallback active.",
        }


# Global singleton client instance
_global_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    global _global_client
    if _global_client is None:
        _global_client = MCPClient()
    return _global_client
