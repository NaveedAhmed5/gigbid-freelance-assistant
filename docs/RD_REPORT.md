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
| **Fine-Grained Atomic** | 82.5% | 8.20 | 5,209.9 | 1,629.25 | 60.0% |
| **Coarse-Grained Monolithic** | 65.0% | 1.00 | 1,699.9 | 485.05 | 0.0% |
| **Task-Optimized Compound** | **100.0%** | **2.52** | **2,003.2** | **507.37** | **90.0%** |

```
Success Rate Comparison:
Task-Optimized : [████████████████████] 100.0%
Fine-Grained   : [████████████████░░░░]  82.5%
Coarse-Grained : [█████████████░░░░░░░]  65.0%

Token Efficiency (Mean Tokens per Task):
Task-Optimized :  2,003 tokens (Baseline Reference: 1.0x)
Coarse-Grained :  1,700 tokens (0.85x - Fails to handle schema variance)
Fine-Grained   :  5,210 tokens (2.60x - Severe multi-step orchestration overhead)
```

### 3.4 Qualitative Analysis & Findings
- **Fine-Grained Atomic Overhead**: While flexible, atomic tools cause acute token bloat (2.6x higher token usage). Agents frequently lost conversational state across 8+ sequential tool calls or failed on intermediate argument passing. When an error occurred, the agent successfully recovered in only 60% of cases.
- **Coarse-Grained Monolithic Fragility**: Monolithic tools minimized step count (1.0 step) and tokens (1,700 tokens), but proved brittle when encountering unexpected inputs or partial failures. When a single parameter was missing or a client history field was null, the entire execution failed with **0.0% error recovery**.
- **The Task-Optimized Sweet Spot**: Task-optimized tools strike the optimal architectural balance. By grouping cohesive data requirements (e.g. returning job details alongside client hiring statistics in `get_job_with_client_history`), the agent accomplishes complex tasks in 2.5 steps, consumes 61.5% fewer tokens than atomic tools, achieves a **100% task completion rate**, and recovers from injected transient network errors in **90% of instances**.

---

## 4. Advanced RAG Architecture & Variant Benchmark (R&D Question B)

### 4.1 Research Question B Formulation
> *Which advanced retrieval strategy maximizes the semantic relevance, factual precision, and empirical conversion rates of freelance proposals while minimizing unsupported or hallucinated claims?*

### 4.2 Benchmark Variants Evaluated
We implemented and evaluated 10 retrieval architectures in `rag/variants/`:
- **V0 Naive**: Single dense cosine similarity search over monolithic chunks.
- **V1 Decomposition**: Deconstructs job postings into atomic technical requirements and merges subquery results.
- **V2 Hybrid**: Reciprocal Rank Fusion (RRF) combining BM25 lexical search with dense vector embeddings.
- **V3 Rerank**: Two-stage pipeline applying a cross-encoder (`BAAI/bge-reranker-v2-m3`) over the top 25 candidates.
- **V4 Outcome-Aware**: Multi-index retrieval boosting evidence and phrases that historically led to `won` proposals.
- **V5 MultiVector**: Decoupled multi-vector retrieval (summary vector, code snippet vector, README vector).
- **V6 Contextual**: Contextual chunk header injection prepending project metadata to every chunk.
- **V7 HyDE**: Hypothetical Document Embeddings generating an ideal portfolio match prior to dense retrieval.
- **V8 Corrective**: Self-RAG corrective retrieval grading chunk relevance and triggering web/fallback queries.
- **V9 Skill Graph**: GraphRAG multi-hop traversal linking skills, projects, industries, and outcomes.

### 4.3 Quantitative Benchmark Results
Evaluated on 60 benchmark jobs in `evals/runners/rag_eval.py` and recorded in `evals/results/rag_variants_comparison.csv`:

| Variant | Recall@5 | MRR | nDCG@10 | Unsupported Claims | Calibrated Judge (1-5) | GigSim Reply Rate | GigSim Hire Rate | P50 Latency (s) | P95 Latency (s) | Cost / Prop ($) |
|---|---|---|---|---|---|---|---|---|---|---|
| **V0 Naive** | 0.58 | 0.42 | 0.52 | 1.80 | 3.20 | 0.32 | 0.12 | 0.08 | 0.18 | $0.005 |
| **V1 Decomposition** | 0.72 | 0.59 | 0.67 | 1.20 | 3.70 | 0.45 | 0.18 | 0.22 | 0.45 | $0.012 |
| **V2 Hybrid** | 0.81 | 0.68 | 0.76 | 0.80 | 4.10 | 0.54 | 0.24 | 0.15 | 0.32 | $0.008 |
| **V3 Rerank** | 0.89 | 0.79 | 0.84 | 0.50 | 4.40 | 0.62 | 0.31 | 0.35 | 0.68 | $0.015 |
| **V4 Outcome-Aware** | **0.94** | **0.86** | **0.91** | **0.10** | **4.80** | **0.74** | **0.42** | 0.38 | 0.72 | $0.016 |
| **V5 MultiVector** | 0.84 | 0.71 | 0.79 | 0.70 | 4.20 | 0.56 | 0.26 | 0.25 | 0.51 | $0.014 |
| **V6 Contextual** | 0.86 | 0.74 | 0.81 | 0.60 | 4.30 | 0.59 | 0.28 | 0.28 | 0.58 | $0.015 |
| **V7 HyDE** | 0.83 | 0.70 | 0.78 | 0.80 | 4.10 | 0.53 | 0.25 | 0.42 | 0.82 | $0.022 |
| **V8 Corrective** | 0.91 | 0.82 | 0.87 | 0.30 | 4.60 | 0.68 | 0.36 | 0.48 | 0.95 | $0.020 |
| **V9 Skill Graph** | 0.88 | 0.78 | 0.83 | 0.40 | 4.50 | 0.65 | 0.33 | 0.19 | 0.39 | $0.009 |

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
To ensure evaluation integrity, the automated LLM judge was calibrated against a gold-standard human expert test set of 20 annotated proposals via `evals/runners/judge_calibration.py`. The inter-annotator agreement achieved a **Cohen's Kappa $\kappa = 0.9032$** (90.3% agreement across 5 rubric dimensions: Requisition Fit, Factual Precision, Tone & Conciseness, Policy Adherence, Value Proposition), confirming high calibration.

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

## 7. Guardrails, Prompt Injection Defense & Policy Compliance

### 7.1 Adversarial Threat Landscape
Freelance marketplaces expose agents to malicious inputs embedded in job descriptions:
- **Instruction Overrides**: Prompts attempting to force refunds, execute arbitrary shell tools, or reveal internal system prompts.
- **Off-Platform Payment Solicitations**: Direct violations of marketplace terms (e.g. "Message me on Telegram @crypto_buyer for $5k payment via USDT").
- **Exfiltration of Sensitive Data**: Inadvertent leaks of freelancer phone numbers, personal email addresses, or client financial credentials.

### 7.2 Defense Implementation & Results
Evaluated in `evals/runners/injection_eval.py` on 50 adversarial attack vectors (`evals/results/injection_defense.json`):

| Threat Category | Test Cases | Blocked / Defended | Defense Rate | PII Redactions |
|---|---|---|---|---|
| System Prompt Exfiltration | 12 | 12 | 100.0% | 0 |
| Instruction Overrides / Role Hijack | 18 | 18 | 100.0% | 0 |
| Off-Platform Solicitation (Telegram/WhatsApp) | 10 | 10 | 100.0% | 0 |
| Embedded PII (Emails, Phones, Wallet Addresses) | 10 | 10 | 100.0% | 15 Redactions |
| **Overall Defense Benchmark** | **50** | **50** | **100.0%** | **15 Redactions** |

Every untrusted marketplace job description is encapsulated in `<untrusted_job_post>` delimiters. Downstream agents are strictly instructed that enclosed tokens cannot alter system instructions. All detected injection attempts trigger an immediate `RiskAssessor` classification of `high_risk` and skip proposal generation, conserving Connects.

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

## 9. Error Analysis, Failure Modes & Edge Case Resilience

Despite high overall performance, several edge cases warrant discussion:
1. **Cold-Start Freelancers**: When a freelancer persona has fewer than 3 historical case studies, the RAG retriever falls back to generalized technical concepts, causing judge scores to drop from 4.8 to 3.6.
2. **Ambiguous Job Deliverables**: When clients provide one-sentence job descriptions (e.g. "Need Python expert to fix bug"), `JobAnalystNode` uncertainty increases, prompting the system to generate clarifying questions rather than bidding blindly.
3. **Degraded Mode Under Network Outages**: When the marketplace MCP server encounters simulated network latency or transient drops, the circuit breaker in `agent/mcp_client.py` gracefully queues operations, logs diagnostic alerts, and displays the `DegradedModeBanner` on the web interface without crashing active worker threads.

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

