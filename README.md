# GigBid: Autonomous Multi-Agent Freelance Bidding & Client Lifecycle System

> **AI-4016 R&D Assignment Implementation**  
> An enterprise-grade, deterministic, multi-agent AI system for autonomous freelance job intake, risk analysis, grounded proposal generation, compliance verification, and client lifecycle management.

---

## 🌟 Architectural Overview

GigBid strictly adheres to the invariants defined in [`GEMINI.md`](./GEMINI.md):
1. **Strict Directory Layout**: Modularity maintained across API, Web, Agent Graph, RAG Engine, MCP Servers, and Simulator.
2. **Zero Inline Prompts**: Every prompt is externalized in [`agent/prompts/`](./agent/prompts/).
3. **Zero Hardcoded Models**: Dynamically routed from [`agent/config.yaml`](./agent/config.yaml) across open-weights and commercial API profiles.
4. **Strict MCP Boundary**: Agents communicate with external resources exclusively via Model Context Protocol (MCP) tools and ports.
5. **Immutable Simulator**: The `gigsim/` simulator is frozen and verified in CI.
6. **Structured Handoffs**: All LangGraph nodes exchange typed Pydantic models.
7. **No Secrets in Code**: Sourced from environment variables documented in [`.env.example`](./.env.example).
8. **Evidence-Backed Metrics**: Structured evaluation logs and benchmarks stored in [`evals/results/`](./evals/results/).

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- Node.js 20+ & npm
- Docker & Docker Compose (optional)

### Setup & Run
```bash
# 1. Install Python packages
make install

# 2. Seed data (personas, policy pack, and realistic job stream)
make seed

# 3. Run test suite
make test

# 4. Launch development services
make dev
```

For evaluation benchmarks:
```bash
make eval
```

---

## 📂 Repository Structure
```
├── .github/workflows/   # CI/CD and evaluation gate workflows
├── apps/
│   ├── api/            # FastAPI multi-tenant REST & SSE streaming server
│   └── web/            # Next.js 14 App Router dashboard with Tailwind CSS
├── agent/              # LangGraph state machine, typed nodes, handoffs, config
│   ├── graphs/         # BidGraph and ConversationGraph DAGs
│   ├── nodes/          # 10 specialized agent nodes
│   ├── prompts/        # Externalized Markdown prompt templates
│   ├── memory/         # Style and Outcome memory stores & promotion rules
│   └── guardrails.py   # PII masking & XML prompt injection defense
├── rag/                # Advanced RAG variants (V0 through V9), hybrid index, verification
├── mcp_servers/        # Portfolio, Marketplace, and Workspace MCP servers
├── gigsim/             # Deterministic Upwork freelance marketplace simulator
├── worker/             # Background job scouting worker
├── evals/              # Datasets, benchmark runners, and structured results
├── infra/              # Dockerfiles and Docker Compose configuration
└── docs/               # Architecture, ADRs, Data Card, Runbook, and R&D Report
```
