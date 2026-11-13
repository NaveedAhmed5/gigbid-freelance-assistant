# Phase 0: Environment Setup, Directory Structure, Configs & Docker

## Objectives
1. Create complete directory layout:
   - Root: `README.md`, `Makefile`, `pyproject.toml`, `.env.example`, `.gitignore`
   - `apps/web/`: Next.js + TypeScript + Tailwind structure (`src/app/`, `src/components/`, `src/lib/api/`, `tests/e2e/`, `package.json`, `tsconfig.json`, `playwright.config.ts`)
   - `apps/api/`: FastAPI app (`main.py`, `routers/`, `streaming.py`, `auth/`, `schemas/`)
   - `agent/`: State, handoffs, graph nodes, external prompts, memory, mcp client, marketplace port, config, guardrails (`state.py`, `handoffs.py`, `graphs/bid_graph.py`, `graphs/conversation_graph.py`, `nodes/{scout,analyst,risk,matcher,pricing,writer,verifier,critic,compliance,liaison}.py`, `prompts/*.md`, `memory/{store,promotion_rules}.py`, `mcp_client.py`, `marketplace_port.py`, `config.yaml`, `guardrails.py`)
   - `rag/`: Ingestion, indexing, variants V0-V9, retriever, claim verification (`ingest/`, `index/`, `variants/{v0_naive..v9_skill_graph}.py`, `retriever.py`, `verify.py`)
   - `mcp_servers/`: `portfolio/`, `marketplace/`, `workspace/` and tests
   - `worker/`: `tasks.py`
   - `gigsim/`: Simulator engine and API
   - `data/`: `personas/`, `policy_pack/`, `processed/`
   - `evals/`: `datasets/`, `runners/`, `results/`
   - `tests/`: `unit/`, `integration/`, `contract/`
   - `infra/`: `docker/`, `docker-compose.yml`
   - `.github/workflows/`: `ci.yml`, `eval.yml`
   - `docs/`: `ARCHITECTURE.md`, `adr/`, `DATA_CARD.md`, `TOOLS.md`, `RUNBOOK.md`, `EXTENSION.md`, `AI_USAGE.md`, `images/`

2. Configure `pyproject.toml` with dependencies:
   - Python 3.11+
   - fastapi, uvicorn, pydantic>=2.7, pydantic-settings, httpx, sse-starlette, cryptography, pyjwt, langgraph, langchain-core, rank-bm25, networkx, scikit-learn, numpy, pypdf, pytest, pytest-asyncio, ruff.

3. Configure `agent/config.yaml`:
   - Profiles: `open` and `paid`
   - Node-level model routing
   - Budgets (`max_steps_per_thread: 25`, `max_tokens_per_thread: 35000`, `p95_latency_budget_sec: 30`, `cost_budget_usd: 0.05`)
   - Max critic loops: 2
   - `active_rag_variant: "v4_outcome_aware"`
   - `marketplace_adapter: "gigsim"`
   - Policy update platform rules.

4. Populate `.env.example`, `Makefile`, and `infra/docker-compose.yml`.

5. Verification:
   - Run `pytest` to verify imports and configuration loading.

