# GigBid Operational Runbook & Deployment Guide

This runbook provides complete operational procedures for local development, containerized Docker deployment, data seeding, evaluation execution, and disaster recovery.

---

## 1. Quickstart Commands

### Local Python & Node Setup
```bash
# Install Python packages
make install

# Seed personas, policy pack, and job stream
make seed

# Run unit, contract, and integration tests
make test

# Launch API & Web dev servers
make dev
```

### Docker Compose Stack
```bash
# Build and launch GigSim, API, and Web containers
make docker-up

# Stop all containers
make docker-down
```

---

## 2. Ports & Endpoints
| Component | Default Port | Health Endpoint |
| :--- | :--- | :--- |
| **Next.js Web Frontend** | `http://localhost:3000` | `/inbox` |
| **FastAPI Backend API** | `http://localhost:8000` | `http://localhost:8000/health` |
| **GigSim Simulator** | `http://localhost:8001` | `http://localhost:8001/health` |
| **SSE Streaming** | `http://localhost:8000/stream/{run_id}` | Event stream |

---

## 3. Running Benchmarks & Evaluations
Execute the full evaluation suite covering all research questions and extensions:
```bash
make eval
```
This sequentially runs:
1. `evals/runners/tool_granularity_eval.py` (R&D Question A)
2. `evals/runners/judge_calibration.py` (Judge Cohen's Kappa)
3. `evals/runners/rag_eval.py` (R&D Question B: V0-V9 variants)
4. `evals/runners/ablation.py` (Component ablations)
5. `evals/runners/multi_agent_eval.py` (R&D Question C: Architectures)
6. `evals/runners/injection_eval.py` (Prompt injection defense)
7. `evals/runners/budget_and_outcomes_eval.py` (Budgets & GigSim ROI)
8. `evals/runners/extension_ab_test.py` (Signature Extension X2 A/B Testing)

Outputs are written to `evals/results/*.json` and `*.csv`.

---

## 4. Troubleshooting & Degraded Mode
- **Simulator / MCP Disconnect:** The system automatically enters **Degraded Mode**. A warning banner appears on the frontend, and proposal submissions are queued locally without consuming connects.
- **Process Crash During Human Approval:** Because LangGraph state is durable, pending approvals are preserved. Once the backend restarts, fetching `/approvals` restores the exact state and resume thread.
