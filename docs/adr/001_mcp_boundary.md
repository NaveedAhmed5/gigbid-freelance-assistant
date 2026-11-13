# ADR 001: Strict Model Context Protocol (MCP) Boundary for External Integrations

## Context & Problem Statement
Autonomous agents interacting with freelance marketplaces require access to multiple external systems: job streams, client histories, candidate portfolio records, calendar slots, and communication APIs. Direct library imports or unbounded database connections violate isolation boundaries, make auditing difficult, and create security vulnerabilities.

## Decision
We enforce a strict Model Context Protocol (MCP) boundary:
1. All external capabilities are encapsulated within dedicated MCP servers (`portfolio`, `marketplace`, `workspace`).
2. Agents and LangGraph nodes interact with external services exclusively through `agent/mcp_client.py` and `agent/marketplace_port.py`.
3. Each agent role is assigned a static allowlist of permissible MCP tools (e.g. `Analyst` and `Compliance Guard` have zero tools).
4. Destructive tools (e.g. `submit_proposal`) enforce idempotency keys, dry-run simulation mode, and append-only audit logging.

## Consequences
- **Positive:** Guarantees auditability, prevents accidental double Connects spend, enables hot-swapping adapters (GigSim vs Upwork Live), and isolates agent execution.
- **Negative:** Slight serialization overhead per tool call (mitigated by localized Python client dispatch).
