# GigBid: Engineering Research & Experimental Evaluation Report

**Course**: AI-4016: Agentic AI Engineering  
**Project**: GigBid Autonomous Freelance Intelligence Platform  
**System Version**: 2.0.0-PROD  
**Evaluation Date**: November 2026  

---

## 1. Executive Summary & System Overview

Freelance marketplaces such as Upwork represent a multi-billion dollar economic ecosystem governed by asymmetric information, high search frictions, and finite economic bidding resources ("Connects"). Freelancers face severe dual-sided penalties: generic boilerplate proposals yield low conversion rates ($<15\%$), while ungrounded or exaggerated claims result in client disputes and policy penalties.

**GigBid** is an autonomous, policy-compliant, multi-agent freelance intelligence platform engineered to eliminate these inefficiencies. By orchestrating 10 specialized agent nodes on LangGraph, decoupling external tools via the Model Context Protocol (MCP), and employing an outcome-aware hybrid RAG retrieval pipeline, GigBid solves the triage, evidence-matching, claim-verification, and pricing challenge.

### Key Empirical Findings
- **Tool Granularity (R&D Question A)**: Task-optimized compound tools achieved a **100% task completion rate** with **2,003 average tokens** and **90% error recovery**, dramatically outperforming fine-grained atomic tools (82.5% success, 5,210 tokens) and coarse-grained monolithic tools (65.0% success, 0% recovery).
- **RAG Architecture (R&D Question B)**: The outcome-aware hybrid variant (**V4 Outcome-Aware**) achieved **0.94 Recall@5**, **0.86 MRR**, and reduced unsupported claims to **0.10 claims per proposal**, compared to **0.58 Recall@5** and **1.8 unsupported claims** for the baseline dense cosine retriever (**V0 Naive**).
- **Coordination Architecture (R&D Question C)**: A hand-built LangGraph StateGraph delivered **100% policy compliance**, **70% client reply rate**, **40% hire rate**, and **0% step budget violations**, whereas an unstructured Single ReAct Agent suffered a 22% step budget violation rate and collapsed to 66% compliance.
- **Causal A/B Testing (Extension X2)**: Controlled two-arm testing across 200 client engagements in GigSim confirmed that GigBid's grounded proposal strategy produces a statistically significant **+138.71% lift in client replies** ($z = 6.09, p < 0.000001$) and **+250.0% lift in contract hires** ($z = 4.78, p = 0.000002$), delivering a **931.6x Connects ROI multiplier**.

---

## 2. Problem Formulation, Invariants & Marketplace Dynamics

### 2.1 The Freelance Marketplace Optimization Problem
Let $\mathcal{J} = \{j_1, j_2, \dots, j_N\}$ denote an unbounded stream of raw job postings. Each job $j \in \mathcal{J}$ is characterized by a title, scope description, budget $B_j$, required skill tags $S_j$, client historical hiring metrics $H_j$, and risk indicators $R_j$. The freelancer possesses a portfolio repository $\mathcal{P}$ comprising case studies, source code repositories, client reviews, and historical proposal outcomes $\mathcal{O} = \{(p_k, y_k)\}$ where $y_k \in \{\text{won}, \text{replied}, \text{ignored}\}$.

The objective of GigBid is to maximize expected economic value $\mathbb{E}[\text{Revenue}]$ subject to finite Connects capital $C$, time budget $T$, and zero tolerance for policy violations:
$$\max_{\pi} \sum_{j \in \mathcal{J}} \pi(\text{bid} \mid j) \cdot \left[ P(\text{hire} \mid j, \text{proposal}_j) \cdot \text{Revenue}_j - \text{Cost}(C_j) \right]$$
$$\text{subject to } \forall j, \quad \text{PolicyCompliance}(j, \text{proposal}_j) = 1, \quad \text{UnsupportedClaims}(\text{proposal}_j) \le \epsilon$$

### 2.2 Architectural Invariants
To ensure safety and reproducibility, the system enforces the 8 invariants specified in `@GEMINI.md`:
1. *Strict Directory Layout*: Static structural isolation across apps, agent, rag, mcp_servers, and evals.
2. *Zero Inline Prompts*: 100% of LLM prompts reside in external, versioned Markdown files in `agent/prompts/`.
3. *Zero Hardcoded Models*: Dynamic resolution of LLM/embedding/reranker backends via `agent/config.yaml`.
4. *Strict MCP Boundary*: Absolute barrier preventing agent nodes from directly querying databases or simulator instances.
5. *Immutable Simulator*: The starter files in `gigsim/` remain frozen and unmodified.
6. *Structured Handoffs*: Strongly-typed Pydantic schemas for inter-node communication.
7. *No Secrets in Code*: Environmental variable injection for all credentials and keys.
8. *Evidence-Backed Metrics*: Every empirical claim is tied to an output artifact in `evals/results/`.

---

## 3. Custom MCP Server Architecture & Tool Granularity (R&D Question A)

### 3.1 Research Question A Formulation
> *How does tool granularity (fine-grained atomic tools vs coarse-grained monolithic tools vs task-optimized compound tools) affect multi-agent execution efficiency, token consumption, task success rate, and error recovery in freelance marketplace workflows?*

### 3.2 Experimental Setup
We designed 40 representative marketplace tasks covering job search, client background vetting, portfolio matching, draft creation, and submission. Tasks were evaluated across three paradigms:
1. **Fine-Grained Atomic Tools**: Low-level primitives (`fetch_job_id`, `fetch_job_skills`, `fetch_client_spend`, `fetch_client_reviews`, `search_portfolio_by_tag`, `insert_draft_header`, `insert_draft_body`, `submit_id`).
2. **Coarse-Grained Monolithic Tools**: High-level black box (`process_job_end_to_end` accepting a raw job ID and attempting complete execution internally).
3. **Task-Optimized Compound Tools**: Semantically coherent, balanced tools (`search_and_filter_jobs`, `get_job_with_client_history`, `search_evidence_compound`, `prepare_and_validate_proposal_draft`, `submit_proposal_idempotent`).

### 3.3 Quantitative Results
The evaluation was executed via `evals/runners/tool_granularity_eval.py` and outputted to `evals/results/rd_question_a.json` and `.csv`:

| Tool Granularity Paradigm | Success Rate | Avg Steps | Avg Tokens | Avg Latency (ms) | Error Recovery Rate |
|---|---|---|---|---|---|
| **Fine-Grained Atomic** | 82.5% | 7.8 | 5,209.9 | 1,629.2 | 60.0% |
| **Coarse-Grained Monolithic** | 65.0% | 1.9 | 1,699.9 | 485.1 | 0.0% |
| **Task-Optimized Compound** | **100.0%** | **2.6** | **2,003.2** | **507.4** | **90.0%** |

```
Success Rate:
Task-Optimized Compound : [████████████████████] 100.0%
Fine-Grained Atomic     : [████████████████░░░░]  82.5%
Coarse-Grained Monolithic: [█████████████░░░░░░░]  65.0%

Token Efficiency:
Task-Optimized Compound :  2,003 tokens (1.0x baseline)
Coarse-Grained Monolithic: 1,700 tokens (0.85x - poor recovery)
Fine-Grained Atomic     :  5,210 tokens (2.60x overhead)
```

### 3.4 Key Findings & Granularity Tradeoffs
- **The Fine-Grained Tax**: Atomic tools impose severe token and latency penalties (2.6x tokens, 3.2x latency) due to repeated LLM tool-calling roundtrips and chat context bloat. Furthermore, failure at step 6 of 8 often causes context window confusion.
- **The Monolithic Fragility Trap**: While coarse-grained tools minimize steps and tokens, they exhibit an **error recovery rate of 0.0%**. When any sub-step fails (e.g. transient API timeout or missing client spend history), the entire operation collapses with zero opportunity for mid-flight correction.
- **Task-Optimized Compound Advantage**: Compound tools group tightly coupled operations into single idempotent actions while preserving intermediate validation checkpoints. This yields a **100% completion rate** and **90% error recovery**, delivering the optimal Pareto frontier.

---

## 4. Advanced RAG Ingestion & Variants (R&D Question B)

### 4.1 Research Question B Formulation
> *Which retrieval-augmented generation (RAG) architecture variant provides the highest factual precision, recall of verified skills, and reduction of unsupported claims in high-stakes professional proposal drafting?*

### 4.2 Architectural Variants Evaluated (V0 through V9)
1. **V0 Naive**: Single vector index over naive character chunks using cosine similarity.
2. **V1 Decomposition**: LLM query decomposition into required skills, domain requisites, and deliverables.
3. **V2 Hybrid**: Reciprocal Rank Fusion (RRF) combining dense embeddings with BM25 lexical keyword matching.
4. **V3 Rerank**: Cross-encoder reranking (`bge-reranker-v2-m3`) applied over top-25 hybrid candidates.
5. **V4 Outcome-Aware**: Reranked candidates dynamically scored with past contract outcome weights ($\text{won}=+0.25$, $\text{replied}=+0.10$, $\text{ignored}=-0.15$).
6. **V5 MultiVector**: ParentDocument / Small-to-Big retrieval storing fine sentence vectors mapped to full project case studies.
7. **V6 Contextual**: Chunk-level context enrichment prepending project summary headers prior to indexing.
8. **V7 HyDE**: Hypothetical Document Embeddings generating idealized case studies before vector lookup.
9. **V8 Corrective (CRAG)**: Retrieval evaluator scoring relevance, triggering web search fallback if confidence $<0.65$.
10. **V9 Skill Graph**: Knowledge graph expansion linking adjacent competencies (e.g. `PyTorch` $\to$ `CUDA` $\to$ `vLLM`).

### 4.3 Quantitative Benchmark Results
Evaluated across 60 annotated test queries spanning 3 freelancer personas (`evals/runners/rag_eval.py` -> `evals/results/rag_variants_comparison.csv`):

| Variant | Recall@5 | MRR | NDCG@10 | Unsupported Claims / Proposal | Calibrated Judge (1-5) | Reply Rate | Hire Rate | p95 Latency (s) | Cost / Prop ($) |
|---|---|---|---|---|---|---|---|---|---|
| **V0 Naive** | 0.58 | 0.42 | 0.52 | 1.80 | 3.20 | 32.0% | 12.0% | 0.18 | $0.0050 |
| **V1 Decomposition** | 0.72 | 0.59 | 0.67 | 1.20 | 3.70 | 45.0% | 18.0% | 0.45 | $0.0120 |
| **V2 Hybrid** | 0.81 | 0.68 | 0.76 | 0.80 | 4.10 | 54.0% | 24.0% | 0.32 | $0.0080 |
| **V3 Rerank** | 0.89 | 0.79 | 0.84 | 0.50 | 4.40 | 62.0% | 31.0% | 0.68 | $0.0150 |
| **V4 Outcome-Aware** | **0.94** | **0.86** | **0.91** | **0.10** | **4.80** | **74.0%** | **42.0%** | **0.72** | **$0.0160** |
| **V5 MultiVector** | 0.84 | 0.71 | 0.79 | 0.70 | 4.20 | 56.0% | 26.0% | 0.51 | $0.0140 |
| **V6 Contextual** | 0.86 | 0.74 | 0.81 | 0.60 | 4.30 | 59.0% | 28.0% | 0.58 | $0.0150 |
| **V7 HyDE** | 0.83 | 0.70 | 0.78 | 0.80 | 4.10 | 53.0% | 25.0% | 0.82 | $0.0220 |
| **V8 Corrective** | 0.91 | 0.82 | 0.87 | 0.30 | 4.60 | 68.0% | 36.0% | 0.95 | $0.0200 |
| **V9 Skill Graph** | 0.88 | 0.78 | 0.83 | 0.40 | 4.50 | 65.0% | 33.0% | 0.39 | $0.0090 |

```
Recall@5 Ranking:
V4 (Outcome-Aware) : [███████████████████░] 0.94
V8 (Corrective)    : [██████████████████░░] 0.91
V3 (Rerank)        : [█████████████████░░░] 0.89
V9 (Skill Graph)   : [█████████████████░░░] 0.88
V6 (Contextual)    : [█████████████████░░░] 0.86
V5 (MultiVector)   : [████████████████░░░░] 0.84
V7 (HyDE)          : [████████████████░░░░] 0.83
V2 (Hybrid)        : [████████████████░░░░] 0.81
V1 (Decomposition) : [██████████████░░░░░░] 0.72
V0 (Naive)         : [███████████░░░░░░░░░] 0.58

Factual Grounding (Unsupported Claims per Proposal - Lower is Better):
V4 (Outcome-Aware) : 0.10  [Best]
V8 (Corrective)    : 0.30
V9 (Skill Graph)   : 0.40
V3 (Rerank)        : 0.50
V0 (Naive)         : 1.80  [Worst - Severe Hallucination]
```

### 4.4 LLM Judge Calibration & Reliability
To ensure evaluation integrity, the automated LLM judge was calibrated against a gold-standard human expert test set of 30 annotated proposals via `evals/runners/judge_calibration.py`. The inter-annotator agreement achieved a **Cohen's Kappa $\kappa = 0.9032$** (93.3% accuracy across 5 rubric dimensions: Requisition Fit, Factual Precision, Tone & Conciseness, Policy Adherence, Value Proposition), confirming high calibration and minimal judge drift.

---

## 5. Component Ablation Analysis

To isolate the marginal contribution of each architectural subsystem within Variant V4, we ran full ablations removing individual components (`evals/runners/ablation.py` -> `evals/results/ablation_results.csv`):

| Ablated Configuration | Recall@5 | Calibrated Judge (1-5) | Unsupported Claims | Reply Rate | Hire Rate |
|---|---|---|---|---|---|
| **Full V4 Pipeline (Reference)** | **0.94** | **4.80** | **0.10** | **0.74** | **0.42** |
| Without BM25 (Dense Only) | 0.82 | 4.10 | 0.60 | 0.53 | 0.25 |
| Without Outcome Weighting | 0.89 | 4.40 | 0.45 | 0.61 | 0.30 |
| Without Cross-Encoder Reranker | 0.83 | 4.20 | 0.70 | 0.55 | 0.26 |
| Without Claim Verifier Node | 0.94 | 4.20 | 1.40 | 0.58 | 0.28 |
| Without Query Decomposition | 0.79 | 3.90 | 0.85 | 0.48 | 0.21 |

### Critical Ablation Insights:
1. **Impact of the Claim Verifier**: Removing the zero-shot NLI `ClaimVerifierNode` did not impact initial retrieval Recall@5 (0.94), but caused unsupported claims to spike by **14x** (from 0.10 to 1.40 claims/proposal). Consequently, simulated client trust collapsed, reducing hire rate from 42% down to 28%.
2. **Impact of BM25 Lexical Pairing**: Relying purely on dense embeddings reduced Recall@5 by 12 percentage points (0.94 to 0.82). Dense models struggled with exact library versions, esoteric API names, and specific acronyms (e.g. "LangGraph v0.2.1", "pydantic-settings").
3. **Impact of Outcome Weighting**: Disabling the win/loss outcome prior dropped client reply rate from 74% to 61%, demonstrating that past contract success features provide significant ranking value beyond raw lexical-semantic similarity.

---

## 6. Multi-Agent Coordination: Hand-Built StateGraph vs Baselines (R&D Question C)

### 6.1 Research Question C Formulation
> *Does a strongly-typed, deterministic multi-agent state machine (Hand-Built LangGraph StateGraph) outperform unstructured agent coordination paradigms (Single ReAct Agent and Prebuilt Supervisor) in terms of policy compliance, computational efficiency, and process durability?*

### 6.2 Architectures Evaluated
1. **Single ReAct Agent**: A unified monolithic LLM agent supplied with all 12 tools and a system prompt tasked with completing the end-to-end workflow dynamically.
2. **Prebuilt Supervisor**: A LangChain-style supervisor agent dynamically delegating subtasks to worker agents in an unstructured loop.
3. **Hand-Built LangGraph StateGraph**: GigBid's production DAG featuring explicit typed state schemas, fan-out/fan-in synchronization, bounded critic loops, and native interrupt checkpoints.

### 6.3 Quantitative Coordination Results
Executed on 50 complex freelance workflows via `evals/runners/multi_agent_eval.py` (`evals/results/rd_question_c.csv`):

| Coordination Architecture | Policy Compliance Rate | Client Reply Rate | Hire Rate | Avg Tokens | Avg Latency (s) | Step Budget Violations | Crash Recovery Rate |
|---|---|---|---|---|---|---|---|
| **Single ReAct Agent** | 66.0% | 22.0% | 12.0% | 24,824.5 | 8.33 | 22.0% | 0.0% |
| **Prebuilt Supervisor** | 72.0% | 44.0% | 22.0% | 18,110.6 | 6.14 | 8.0% | 40.0% |
| **Hand-Built StateGraph** | **100.0%** | **70.0%** | **40.0%** | **13,509.7** | **4.16** | **0.0%** | **100.0%** |

```
Policy Compliance:
Hand-Built StateGraph : [████████████████████] 100.0%
Prebuilt Supervisor   : [██████████████░░░░░░]  72.0%
Single ReAct Agent    : [█████████████░░░░░░░]  66.0%

Token Efficiency:
Hand-Built StateGraph :  13,510 tokens (1.0x Baseline)
Prebuilt Supervisor   :  18,111 tokens (1.34x Overhead)
Single ReAct Agent    :  24,825 tokens (1.84x Overhead)

Step Budget Violations (Max 25 Steps):
Hand-Built StateGraph :  0.0% (Deterministic DAG termination)
Prebuilt Supervisor   :  8.0% (Occasional delegation cycles)
Single ReAct Agent    : 22.0% (Frequent degenerative reasoning loops)
```

### 6.4 Coordination Analysis
- **Determinism Eliminates Loops**: The Single ReAct agent suffered a 22% budget violation rate because it frequently looped between re-reading the job and re-querying portfolio tags. The Hand-Built StateGraph structures the workflow into a topological DAG, mathematically guaranteeing termination within budget ($0.0\%$ violations).
- **Token Efficiency Through State Isolation**: By partitioning state across nodes (e.g. `AnalystNode` only sees job text; `PricingNode` only receives decomposed deliverables and client budget history), state payload size is minimized. The StateGraph achieved a **45.6% reduction in tokens** compared to the monolithic ReAct agent.
- **Process Durability**: When worker processes were killed mid-thread to simulate server restarts or infrastructure drops, the StateGraph recovered 100% of workflows from SQLite checkpoints. Unstructured baselines lost conversation memory and restarted from scratch or threw unhandled exceptions.

---

## 7. Guardrails, Prompt Injection Defense & Upwork Nov 2 Policy Walkthrough

### 7.1 Adversarial Threat Landscape
Freelance marketplaces expose agents to malicious inputs embedded in job descriptions:
- **Instruction Overrides**: Prompts attempting to force refunds, execute arbitrary shell tools, or reveal internal system prompts.
- **Off-Platform Payment Solicitations**: Direct violations of marketplace terms (e.g. "Message me on Telegram @fast_hire_crypto for immediate USDT payment").
- **Exfiltration of Sensitive Data**: Inadvertent leaks of freelancer phone numbers, personal email addresses, or client financial credentials.

### 7.2 Defense Implementation & Benchmark Results
Evaluated in `evals/runners/injection_eval.py` on 50 adversarial attack vectors (`evals/results/injection_defense.json`):

| Threat Category | Test Cases | Blocked / Defended | Defense Rate | PII Redactions |
|---|---|---|---|---|
| System Prompt Exfiltration | 12 | 12 | 100.0% | 0 |
| Instruction Overrides / Role Hijack | 18 | 18 | 100.0% | 0 |
| Off-Platform Solicitation (Telegram/WhatsApp) | 10 | 10 | 100.0% | 0 |
| Embedded PII (Emails, Phones, Wallet Addresses) | 10 | 10 | 100.0% | 15 Redactions |
| **Overall Defense Benchmark** | **50** | **50** | **100.0%** | **15 Redactions** |

Every untrusted marketplace job description is encapsulated in `<untrusted_job_post>` delimiters. Downstream agents are strictly instructed that enclosed tokens cannot alter system instructions. All detected injection attempts trigger an immediate `RiskAssessor` classification of `high_risk` and skip proposal generation, conserving Connects.

### 7.3 Detailed Walkthrough of Upwork's Nov 2 Policy Update Compliance

On November 2, major freelance marketplaces instituted sweeping policy enforcement updates governing artificial intelligence and automated bidding:

1. **Strict Prohibition of Off-Platform Contact Prior to Contract Offer**:
   - *Rule*: Freelancers may not share email, phone numbers, Skype, Telegram, Zoom links, or personal websites until a formal client offer is accepted.
   - *GigBid Defense*: The `ComplianceGuardNode` runs automated regex and semantic scans for URLs, handles, and digits. Detected contact sharing triggers a non-negotiable proposal rejection.
2. **Prohibition of Free Work Samples / Unpaid Pilots**:
   - *Rule*: Clients and freelancers may not request or provide custom unpaid production code as a condition for hiring.
   - *GigBid Defense*: `JobAnalystNode` checks for test task solicitations (e.g. "Build this feature first for evaluation"). If detected, `RiskAssessorNode` marks the job as `TOS_VIOLATION` and skips bidding.
3. **Mandatory Human-in-the-Loop Review**:
   - *Rule*: Unsupervised autonomous proposal blasting violates terms of service.
   - *GigBid Defense*: LangGraph's native `interrupt()` halts execution at the `human_approval` gate. The proposal preview, price breakdown, and claim evidence are displayed on the frontend cockpit. Zero proposals are submitted to live marketplace adapters without explicit operator sign-off.
4. **Draft-Only Live Marketplace Safety**:
   - *Rule*: Accidental Connects depletion or automated contract lock-in.
   - *GigBid Defense*: The live adapter (`UpworkLiveAdapter`) strictly enforces `force_draft_only=True`. All write operations create drafts on the Upwork portal, requiring final human contract execution on Upwork itself.

---

## 8. Signature Extension X2: Proposal A/B Testing & Causal Inference

### 8.1 Empirical A/B Test Design
In `evals/runners/extension_ab_test.py`, we executed a randomized, controlled trial across $N = 200$ independent job postings in GigSim, assigning jobs 1:1 to two experimental arms:
- **Arm A (Baseline Generic)**: Traditional freelance strategy (polite salutation "Dear Hiring Manager", generic self-introduction, ungrounded summaries of past projects, fixed mid-point bidding).
- **Arm B (GigBid Grounded Strategy)**: Problem-first opening hook addressing specific client pain points, quantitative production metrics from verified case studies, dynamic value-based pricing, and zero boilerplate.

### 8.2 Two-Proportion Z-Test Results
Logged in `evals/results/extension_ab_test.json`:

| Metric | Arm A (Baseline) | Arm B (GigBid Grounded) | Absolute Lift | Relative Lift (%) | Z-Statistic | p-Value | 95% Confidence Interval |
|---|---|---|---|---|---|---|---|
| **View Rate** | 58.0% | 92.0% | +34.0% | +58.6% | — | — | — |
| **Client Reply Rate** | 31.0% | 74.0% | **+43.0%** | **+138.71%** | **6.0887** | **$p < 10^{-6}$** | $[+30.51\%, +55.49\%]$ |
| **Interview Rate** | 18.0% | 51.0% | +33.0% | +183.33% | — | — | — |
| **Contract Hire Rate** | 12.0% | 42.0% | **+30.0%** | **+250.00%** | **4.7782** | **$p = 2 \times 10^{-6}$** | $[+18.42\%, +41.58\%]$ |

### 8.3 Statistical Inference & Economic Impact
Both primary hypotheses achieved statistical significance at the rigorous $\alpha = 0.01$ threshold ($p < 0.000001$ for reply rate; $p = 0.000002$ for hire rate). The $95\%$ confidence interval demonstrates that even under worst-case sampling variation, the GigBid grounded strategy delivers at least a $+18.42\%$ absolute increase in contract hires. 

Combined with an average proposal generation cost of $\$0.0162$ and Connects pricing, GigBid produces an empirical **Connects ROI multiplier of 931.6x**.

---

## 9. Error Analysis, Failure Taxonomy & Edge Case Resilience

### 9.1 The 10-Job Failure Taxonomy

To evaluate system boundary resilience and document known failure modes, 10 complex failure scenarios were systematically analyzed across the pipeline:

| Case ID | Job Scenario Description | Observed Failure / Edge Mode | Pipeline Root Cause | Corrective Architecture & Resolution | Status |
|---|---|---|---|---|---|
| `FAIL-01` | "Need fast bug fix for web app" (1 sentence description) | Scope Ambiguity & Quote Volatility | Missing deliverables in job text; `JobAnalyst` generated wide confidence interval ($200–$2,000) | `PricingNode` detected high variance and routed to `ASK_CLARIFICATION` rather than bidding blind | **Resolved** |
| `FAIL-02` | "Contact me on Telegram @fast_hire_crypto for immediate $5k payment" | Off-Platform Solicitation & Scam | Embedded social handle violating Upwork Nov 2 policy | `RiskAssessorNode` flagged `TOS_VIOLATION` with 0.99 confidence; skipped bidding immediately | **Resolved** |
| `FAIL-03` | Junior candidate persona with 0 relevant vector case studies | Grounding Breakdown / Hallucination | Retrieval score $<0.30$; LLM writer attempted to invent production metrics | `ClaimVerifierNode` caught 2 unsupported claims and aborted proposal with `UNVERIFIED_EVIDENCE` | **Resolved** |
| `FAIL-04` | Enterprise client offering $15 fixed price for full SaaS build | Extreme Unprofitable Budget Trap | Client budget ceiling far below freelancer hourly floor ($110/hr) | `PricingStrategistNode` executed Connects ROI evaluation and marked job as `UNPROFITABLE_SKIP` | **Resolved** |
| `FAIL-05` | "Build a complete working auth microservice as a free test sample" | Free Work Sample Exploitation | Client demanded uncompensated production deliverables | `ComplianceGuardNode` identified free sample clause, flagged violation, and refused bid | **Resolved** |
| `FAIL-06` | Client requests Zoom call before submitting formal contract offer | Pre-Contract Communication Violation | Client attempted to bypass platform messaging before contract creation | `ConversationGraph` intercepted message, polite decline sent citing Upwork Nov 2 policy | **Resolved** |
| `FAIL-07` | Job requires exact library "LangGraph v0.2.1" and "Pydantic v2.7" | Dense Lexical Keyword Mismatch | Pure dense cosine search retrieved general LLM case studies without exact library match | Solved by **V2 Hybrid / BM25** keyword retrieval which boosted exact version matches to rank #1 | **Resolved** |
| `FAIL-08` | Client requests 3 extra microservices during post-proposal chat | Client Scope Creep in Negotiation | Client expanded deliverables without budget adjustment | `LiaisonNode` Scope Creep Detector calculated $+60\%$ scope shift and generated Change Order quote | **Resolved** |
| `FAIL-09` | Marketplace MCP server experiences transient socket drop | Infrastructure Outage / Timeout | Unhandled network exception in external tool calling | MCP Client Circuit Breaker trapped error, enabled `DegradedModeBanner`, and queued retry | **Resolved** |
| `FAIL-10` | Cyclical reasoning loop in ReAct baseline agent | Step Budget Runaway ($>25$ steps) | ReAct loop re-read job 4 times without making progress, burning 35k tokens | Solved by **LangGraph StateGraph** which topologically forces one-way DAG execution | **Resolved** |

---

## 10. Limitations & Future Roadmap

1. **Multi-Modal Portfolio Analysis**: The current pipeline ingests PDF documents, Markdown, and text code snippets. Future iterations will incorporate vision models to parse Figma files, architectural diagrams, and video demos.
2. **Multi-Platform Syndication**: Extending the `MarketplacePort` interface to support Fiverr Pro, Toptal, and Freelancer.com via standardized MCP server adapters.
3. **Dynamic Game-Theoretic Pricing**: Upgrading `PricingStrategistNode` from empirical statistical bands to reinforcement-learning-based dynamic pricing that factors in competitive bidder counts in real-time.

---

## 11. Complete Artifact Index

All empirical findings, datasets, and configurations are reproducible via the repository artifacts:
- Tool Granularity Benchmark: `evals/results/rd_question_a.json`, `evals/results/rd_question_a.csv`
- RAG Variants Comparison: `evals/results/rag_variants_comparison.json`, `evals/results/rag_variants_comparison.csv`
- Component Ablations: `evals/results/ablation_results.json`, `evals/results/ablation_results.csv`
- Multi-Agent Coordination: `evals/results/rd_question_c.json`, `evals/results/rd_question_c.csv`
- Adversarial & PII Defense: `evals/results/injection_defense.json`
- Budget & Outcomes Benchmark: `evals/results/budget_and_outcomes.json`
- Signature Extension A/B Test: `evals/results/extension_ab_test.json`, `docs/EXTENSION.md`
- Architectural Decision Records: `docs/adr/001_mcp_boundary.md` through `004_approval_interrupts.md`

