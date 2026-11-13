# Phase 6: Part C (1/2) — LangGraph Typed State, Pydantic Handoffs, Prompts & Agent Nodes

## Objectives
1. Implement `agent/handoffs.py`:
   - Strongly typed Pydantic models: `JobSpec`, `RiskReport`, `FitReport`, `BidDecision`, `PriceQuote`, `ProposalDraft`, `Critique`, `ComplianceVerdict`, `LiaisonDraft`.
2. Implement `agent/state.py`:
   - LangGraph State typed dictionary with annotated reducers.
   - Clean partition of: (1) Graph Execution State, (2) Execution Trace, (3) Long-Term Memory References.
3. Externalize ALL prompts in `agent/prompts/*.md`:
   - `scout_filter.md`, `job_analyst.md`, `risk_assessor.md`, `fit_matcher.md`, `pricing_strategist.md`, `proposal_writer.md`, `claim_verifier.md`, `critic.md`, `compliance_guard.md`, `client_liaison.md`, `judge_rubric.md`.
   - Strictly zero inline prompts in Python files.
4. Implement all 10 Agent Nodes in `agent/nodes/`:
   - `scout.py`, `analyst.py`, `risk.py`, `matcher.py`, `pricing.py`, `writer.py`, `verifier.py`, `critic.py`, `compliance.py`, `liaison.py`.
5. Verification:
   - Run unit tests in `tests/unit/test_agent_nodes.py`.

