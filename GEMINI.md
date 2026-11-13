# GigBid (AI-4016) Workspace Rules & Architectural Invariants

1. **Strict Directory Layout**: Never rename or move required folders (`apps/web`, `apps/api`, `agent`, `rag`, `mcp_servers`, `worker`, `gigsim`, `data`, `evals`, `tests`, `infra`, `.github/workflows`, `docs`).
2. **Zero Inline Prompts**: Every LLM prompt MUST live in a versioned `.md` file inside `agent/prompts/`. Python files in `agent/nodes/` and `rag/` must load prompts from disk.
3. **Zero Hardcoded Models**: Every node's LLM, embedding model, and reranker MUST be resolved dynamically from `agent/config.yaml` (`open` and `paid` profiles).
4. **Strict MCP Boundary**: Agents and LangGraph nodes MUST NEVER import or call `gigsim`, databases, or local files directly. All external reads/writes go through MCP tools via `agent/mcp_client.py` and `agent/marketplace_port.py`.
5. **Immutable Simulator**: Never modify existing starter files inside `gigsim/` once initialized.
6. **Structured Handoffs**: LangGraph nodes exchange typed Pydantic models from `agent/handoffs.py`, never unstructured prose.
7. **No Secrets in Code**: All API keys, DB URIs, and encryption keys come from environment variables documented in `.env.example`.
8. **Evidence-Backed Metrics**: Every evaluation script must output structured JSON/CSV to `evals/results/`.