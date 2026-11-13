# Phase 5: Part B (2/2) — Claim Verification, Judge Calibration, RAG Evaluation & R&D Question B

## Objectives
1. Implement `rag/verify.py`:
   - Decomposes proposal into atomic factual claims.
   - Evaluates each claim against retrieved evidence (`supported`, `partly_supported`, `unsupported`).
   - Automatically sanitizes/rewrites unsupported statements before passing draft to the Critic node.
   - Tracks metrics: `unsupported_claims_before` and `unsupported_claims_after`.
2. Implement `evals/runners/judge_calibration.py`:
   - Calibrates LLM judge against 30 human-labeled gold ratings using `agent/prompts/judge_rubric.md`.
   - Calculates Cohen's kappa ($\kappa$).
   - Outputs `evals/results/judge_calibration.json`.
3. Implement `evals/runners/rag_eval.py` and `evals/runners/ablation.py`:
   - Benchmarks Variants `V0` through `V9` across all 3 personas.
   - Computes: `Recall@5`, `MRR`, `nDCG@10`, `unsupported_claims_per_proposal`, calibrated `judge_score`, `gigsim_reply_rate`, `gigsim_hire_rate`, `p50_latency_s`, `p95_latency_s`, `cost_per_proposal_usd`.
   - Generates `evals/results/rag_variants_comparison.json` & `.csv` and `evals/results/ablation_results.json` & `.csv`.
4. Verification:
   - Run tests in `tests/unit/test_claim_verification.py`.

