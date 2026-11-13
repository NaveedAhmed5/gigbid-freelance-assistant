# ADR 002: Hand-Built StateGraph with Typed Handoffs over Single ReAct / Prebuilt Supervisors

## Context & Problem Statement
In R&D Question C, we evaluated three multi-agent coordination architectures:
1. Single ReAct Agent
2. Prebuilt Hierarchical LLM Supervisor
3. Hand-Built LangGraph StateGraph with parallel fan-out and typed handoffs.

The single ReAct loop suffered from tool-calling loops, step budget overruns (22%), and high token consumption (24.8k tokens). Prebuilt supervisors suffered from degraded coordination when delegating via natural language text.

## Decision
We architected a custom LangGraph StateGraph featuring:
- Parallel fan-out for independent analysis (`Analyst`, `Risk Assessor`, `Fit Matcher`).
- Strongly typed Pydantic handoff schemas (`JobSpec`, `RiskReport`, `FitReport`, `BidDecision`, `PriceQuote`, `ProposalDraft`, `Critique`, `ComplianceVerdict`).
- Bounded feedback loops between Writer and Critic (capped at 2 iterations).
- Hard step and token budget checks that route to `needs_attention` if limits are exceeded.

## Consequences
- **Positive:** 100% compliance adherence, 45% reduction in token consumption (13.5k tokens vs 24.8k for ReAct), and deterministic execution flow.
- **Negative:** Requires explicit graph topology definition and typed schemas upfront.

