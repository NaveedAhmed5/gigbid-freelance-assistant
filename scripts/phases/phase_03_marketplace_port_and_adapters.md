# Phase 3: Part A (2/2) — Marketplace Port, Live Upwork & GitHub Adapters, Client Discipline & R&D Question A

## Objectives
1. Implement `agent/marketplace_port.py` (Abstract Port interface).
2. Implement Adapters:
   - `mcp_servers/marketplace/adapters/gigsim.py` (Connecting to local GigSim MCP/REST engine).
   - `mcp_servers/marketplace/adapters/upwork_live.py` (Connecting to Upwork MCP endpoint `https://mcp.upwork.com/mcp` with OAuth 2.1 encrypted token store and draft-only write safety enforcement).
3. Implement `agent/mcp_client.py`:
   - Enforce strict per-agent tool allowlists (Scout, Analyst, Risk, Matcher, Pricing, Writer, Verifier, Critic, Compliance, Liaison).
   - MCP client with timeout, bounded retries with exponential backoff.
   - Degraded Mode handling (queuing work, raising graceful status to UI when server is unreachable).
4. Document `docs/TOOLS.md` with complete tool matrix and third-party security trust rationale.
5. Implement and run `evals/runners/tool_granularity_eval.py` (R&D Question A):
   - Benchmark 40 tasks across Fine-Grained vs Coarse vs Optimized tools.
   - Output `evals/results/rd_question_a.json` and `evals/results/rd_question_a.csv`.
6. Verification:
   - Unit tests for client discipline and adapters in `tests/unit/test_marketplace_adapters.py`.

