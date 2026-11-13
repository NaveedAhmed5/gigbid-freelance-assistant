# Phase 7: Part C (2/2) — Durable LangGraph Graphs, Interrupts, Memory Promotion & R&D Question C

## Objectives
1. Implement `agent/memory/store.py` & `promotion_rules.py`:
   - Store and retrieve `style_memory` (derived from user edits diffs) and `outcome_memory` (derived from won proposals).
   - Strict promotion rules: only promote validated learning; never dump raw tool outputs.
2. Implement `agent/graphs/bid_graph.py`:
   - Parallel execution: `Job Analyst`, `Risk Assessor`, `Fit Matcher`.
   - Gate: `BidDecision` routing (`BID` proceeds to `pricing`, `SKIP` terminates gracefully).
   - Pipeline: `pricing` -> `writer` -> `verifier` -> `critic` (feedback loop to writer, max 2 iterations) -> `compliance` -> `dry_run` -> human approval gate (`interrupt()`).
   - Budget guardrails: Step & token tracking leading to `needs_attention` state if limits exceeded.
   - Persistent checkpointer (SQLite/Memory) enabling crash-recovery and resume on approval.
3. Implement `agent/graphs/conversation_graph.py`:
   - Handles incoming client messages, evaluates intent, crafts draft response, proposes tentative calendar holds via Workspace MCP server, and interrupts for approval.
4. Implement and run `evals/runners/multi_agent_eval.py` (R&D Question C):
   - Benchmark 50 dev jobs comparing: Single ReAct Agent vs Prebuilt Supervisor vs Hand-Built StateGraph.
   - Output `evals/results/rd_question_c.json` and `evals/results/rd_question_c.csv`.
5. Verification:
   - Run `tests/integration/test_graphs_durability.py`.

