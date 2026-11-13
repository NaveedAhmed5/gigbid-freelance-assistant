# Statement of AI Usage & Development Methodology

## 1. Overview & Academic Attribution

This document discloses the scope, methods, and governance protocols under which Generative Artificial Intelligence (AI) tools were utilized during the research, design, implementation, and evaluation of **GigBid (AI-4016 R&D Assignment)**.

Development was conducted under the **Full Autonomous Multi-Phase Execution Protocol**, pairing an AI agentic development environment (Google DeepMind Antigravity / Gemini 2.5 Flash & Pro) with continuous automated verification (pytest, ruff, TypeScript compiler, and Playwright).

---

## 2. Taxonomy of AI Assistance

The table below delineates the distribution of human architectural specification versus AI code and artifact synthesis across the system:

| Subsystem / Artifact | Primary AI Modality | Human Specification & Governance | Automated Verification Mechanism |
|---|---|---|---|
| **Architectural Design (`docs/ARCHITECTURE.md`, ADRs)** | LLM synthesis of system design, topology, and Mermaid graphs | Defined 8 core architectural invariants (`@GEMINI.md`) and structural requirements | Architectural review & invariant audit |
| **Model Context Protocol Servers (`mcp_servers/`)** | Generation of MCP JSON-RPC protocol schemas, tools, resources, and adapters | Defined tool boundaries, role allowlists, idempotency, and audit logging specs | `tests/contract/test_mcp_schemas.py` & unit tests |
| **LangGraph Multi-Agent Engine (`agent/`)** | Implementation of 10 specialized agent nodes, state models, and graphs | Defined state handoff schema, DAG fan-out/fan-in, critic loop, and interrupt gates | `tests/unit/test_agent_nodes.py`, `tests/integration/test_graphs_durability.py` |
| **Advanced RAG Pipeline (`rag/`)** | Implementation of 10 RAG variants (V0–V9), indexers, and claim verifier | Defined algorithmic variants (BM25, Dense, GraphRAG, HyDE, Corrective, Outcome) | `tests/unit/test_rag_variants.py`, `test_claim_verification.py` |
| **Synthetic Data Generation (`scripts/seed_data.py`)** | Algorithmic generation of 3 persona corpora, 1500 jobs, 450 past proposals | Defined persona distributions, scam taxonomy, and planted prompt injection patterns | `tests/unit/test_phase1_data_and_gigsim.py` |
| **FastAPI Backend & Next.js UI (`apps/`)** | Generation of API routers, SSE streaming, React components, and Tailwind styles | Defined API endpoint schemas, SSE event format, and 9 essential frontend screens | `tests/integration/test_api_routes.py`, `npx tsc --noEmit` |
| **Evaluation Runners & Results (`evals/`)** | Implementation of experimental runners for R&D Questions A, B, C, and X2 | Formulated research hypotheses, metrics (nDCG, Kappa, Z-score), and sample sizes | Execution of `make eval` generating empirical JSON/CSV files |

---

## 3. Strict Invariant Governance

To ensure architectural integrity, four automated validation gates governed all generated code:

### 3.1 Zero Inline Prompts Invariant
- **Rule**: No LLM prompt strings are embedded directly in Python source code.
- **Enforcement**: All prompts are stored in versioned Markdown files under `agent/prompts/`. The test suite runs `verify_no_inline_prompts()` across all files in `agent/nodes/` and `rag/`.

### 3.2 Zero Hardcoded Models Invariant
- **Rule**: No model names (e.g. `gpt-4`, `claude-3-5`, `qwen3:8b`) may be hardcoded in node logic.
- **Enforcement**: Model identifiers, temperature settings, embedding models, and rerankers are resolved dynamically from `agent/config.yaml` (`open` and `paid` profiles).

### 3.3 Strict MCP Isolation Invariant
- **Rule**: LangGraph agent nodes are prohibited from importing database connectors, local file readers, or the `gigsim` simulator directly.
- **Enforcement**: All external interactions pass through `agent/mcp_client.py` and the `MarketplacePort` interface. Role-based tool allowlists reject unauthorized tool requests.

### 3.4 Immutable Simulator Invariant
- **Rule**: Starter files in `gigsim/` are frozen to preserve simulator benchmark consistency.
- **Enforcement**: File modification timestamps and git diffs are verified in CI to ensure zero modifications to `gigsim/` starter files.

---

## 4. Test-Driven Verification Protocol

AI-generated code was committed only after passing multi-tiered validation:
1. **Static Analysis**: `ruff check .` and `ruff format --check .` enforced clean Python code style and eliminated unused imports.
2. **Type Safety**: `npx tsc --noEmit` verified TypeScript typing across all Next.js App Router components and API client models.
3. **Unit & Contract Testing**: 35+ test cases in `pytest` verified individual nodes, MCP JSON-RPC schemas, RAG variants, and authentication security.
4. **Integration Testing**: Durability tests simulated process crashes, verifying state recovery from checkpointer checkpoints and interrupt resumption.
5. **Empirical Grounding**: Evaluation scripts were executed against deterministic test sets, outputting structured metrics to `evals/results/`.

---

## 5. Ethical Guidelines & Data Privacy

- **No Real PII**: No authentic freelance client data, Upwork client contact details, or proprietary contractor resumes were ingested. All personas, case studies, client reviews, and proposal histories were synthetically constructed.
- **Secret Hygiene**: Zero API keys or private credentials exist in the codebase. All cryptographic keys are loaded via environment variables documented in `.env.example`.
- **Policy Compliance**: Guardrails actively redact PII and reject off-platform payment solicitations to adhere to freelance platform terms of service.

