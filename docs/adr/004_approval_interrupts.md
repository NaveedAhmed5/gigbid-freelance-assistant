# ADR 004: Durable Checkpointed Human Approval Gates via LangGraph Interrupts

## Context & Problem Statement
Freelance platforms enforce strict terms regarding automated spamming and proposal quality. In addition, platform Connects represent real monetary expenditure. Full autonomous auto-bidding risks catastrophic Connects depletion and policy suspensions if adversarial prompt injections or hallucinations occur.

## Decision
We enforce a mandatory human-in-the-loop approval gate prior to live marketplace submission:
1. `LangGraph interrupt()` pauses execution immediately after `Compliance Guard` validates the proposal draft.
2. State is serialized to a persistent checkpointer (`MemorySaver` or SQLite checkpointer).
3. The human reviewer inspects the proposal in the Proposal Studio with evidence-on-hover, inline critic feedback, and dry-run validation.
4. Resuming the graph with `approve` triggers live submission via the marketplace MCP server; `edit` promotes style diffs into `Style Memory`; `reject` safely halts execution.
5. Server restarts preserve all pending threads without losing progress or double-spending Connects.

## Consequences
- **Positive:** Guarantees zero unauthorized Connects spend, full regulatory compliance, and enables crash recovery.
- **Negative:** Introduces an asynchronous waiting state for end users until approval is submitted.
