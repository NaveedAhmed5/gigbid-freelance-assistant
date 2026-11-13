# Phase 1: GigSim Simulator, 3 Persona Corpora, Policy Pack & Dev Dataset

## Objectives
1. Implement `gigsim/`:
   - FastAPI simulator + in-memory/SQLite state engine.
   - Jobs, clients with histories (`spend_usd`, `hire_rate`, `reviews`), user Connects balance, proposal drafts, submitted proposals, messages, rate-limit simulation.
   - Simulated client engine with hidden preferences (`must_have_skills`, `budget_ceiling`, `dislike_generic_openings`, `view_prob`, `reply_prob`, `interview_prob`, `hire_prob`).
   - Freeze indicator / check to ensure CI enforces immutability.

2. Implement `scripts/seed_data.py` (wired to `make seed`):
   - 3 Persona Corpora in `data/personas/{ai_ml_engineer,fullstack_web_dev,data_analyst}/`:
     - CV (markdown + pdf representation)
     - 15+ Case studies per persona
     - GitHub repo READMEs and realistic code snippets
     - Client reviews with ratings
     - 150 past proposals per persona labeled `won`, `replied`, `ignored` with metadata (persona, type, project, skills, date, client_industry, outcome).
   - Marketplace policy pack in `data/policy_pack/marketplace_rules.md`.
   - Realistic Job Stream (~1,500 historical jobs for pricing stats + active stream with duplicates, scams, and prompt injection attacks).
   - Golden Dev Dataset in `evals/datasets/dev_set.json` with ground truth labels (`bid_or_skip`, `is_scam`, `has_injection`, `gold_evidence_ids`, `fair_price_band`).

3. Document `docs/DATA_CARD.md`.
4. Verification:
   - Run `tests/unit/test_phase1_data_and_gigsim.py` with pytest.

