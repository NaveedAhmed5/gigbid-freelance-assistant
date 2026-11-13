# Phase 10: Part E, Guardrails, Signature Extension, CI Workflows & Final Report Documentation

## Objectives
1. Implement `agent/guardrails.py`:
   - PII scrubber for sensitive client/contractor data (emails, phone numbers, payment IDs) before logging or sending to models.
   - XML untrusted input delimiters and prompt-injection defense mechanisms.
   - Run `evals/runners/injection_eval.py` -> generate `evals/results/injection_defense.json`.
2. Run `evals/runners/budget_and_outcomes_eval.py` (wired to `make eval`) -> generate `evals/results/budget_and_outcomes.json`.
3. Implement Signature Extension X2: Proposal Experiments (A/B testing in GigSim with two-proportion z-test and p-values) in `evals/runners/extension_ab_test.py` -> generate `evals/results/extension_ab_test.json` and document in `docs/EXTENSION.md`.
4. Implement GitHub Actions workflows:
   - `.github/workflows/ci.yml`: Linter, type check, unit & integration tests, immutability check on `gigsim/`, no inline prompts check.
   - `.github/workflows/eval.yml`: Evaluation runner and metric gate enforcement.
5. Create comprehensive documentation in `docs/`:
   - `docs/ARCHITECTURE.md`: Complete system architecture and LangGraph design.
   - `docs/adr/001_mcp_boundary.md`, `002_langgraph_statemachine.md`, `003_hybrid_rag_routing.md`, `004_approval_interrupts.md`.
   - `docs/RUNBOOK.md`: Local setup, Docker deployment, and troubleshooting.
   - `docs/AI_USAGE.md`: Statement of AI assistance and development methodology.
   - `docs/RD_REPORT.md`: Comprehensive 10-section R&D engineering report synthesizing all experimental results (R&D Question A, B, C, and Extension X2).
6. Verification:
   - Full test suite passes via `pytest`.
   - All evaluation artifacts exist in `evals/results/`.
