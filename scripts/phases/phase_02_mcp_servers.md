# Phase 2: Part A (1/2) — Custom MCP Servers (portfolio, marketplace, workspace)

## Objectives
1. Implement `mcp_servers/portfolio/`:
   - Fast MCP server with tools: `search_evidence(requirement, k, filters)`, `get_case_study(id)`, `list_skills(persona)`.
   - Resource templates: `portfolio://case/{id}`, `portfolio://proposal/{id}`.
   - Prompt templates: `"Answer a screening question from my portfolio"`, `"Summarize relevant portfolio evidence"`.
   - Dedicated `mcp_servers/portfolio/README.md` for standalone installation.

2. Implement `mcp_servers/marketplace/`:
   - Read tools: `search_jobs`, `get_job`, `get_client_history`, `get_connects_balance`, `list_messages`.
   - Write tools: `create_proposal_draft`, `submit_proposal`, `send_message`.
   - Strict Pydantic input/output schemas with MCP annotations (`readOnlyHint`, `destructiveHint`, `idempotentHint`).
   - Idempotency key deduplication store (prevents double submission / double Connects spend).
   - Dry run preview mode (`dry_run=True`).
   - Bearer token authentication check & per-user sliding-window rate limiter.
   - Append-only structured audit log (`user`, `tool`, `arguments`, `result`, `trace_id`).

3. Implement `mcp_servers/workspace/`:
   - Tools: `get_free_calendar_slots`, `create_tentative_interview_hold`, `create_email_draft`.

4. Verification:
   - Add unit tests in `mcp_servers/*/tests/`.
   - Add schema snapshot contract test in `tests/contract/test_mcp_schemas.py`.
   - Run `pytest`.
