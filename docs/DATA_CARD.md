# Dataset Card: GigBid Synthetic Persona, Job Stream & Evaluation Corpora

## 1. Dataset Summary
The GigBid dataset collection provides realistic, high-fidelity freelance bidding, persona portfolios, and job marketplace data designed for benchmarking autonomous agentic workflows under strict policy constraints.

### Key Statistics
- **Personas:** 3 distinct archetypes (`ai_ml_engineer`, `fullstack_web_dev`, `data_analyst`).
- **Case Studies:** 16 structured enterprise case studies per persona (48 total).
- **Past Proposals:** 150 labeled proposals per persona (450 total), balanced across `won` (26.7%), `replied` (33.3%), and `ignored` (40.0%).
- **Marketplace Job Stream:** 1,500 historical and active jobs, including planted edge cases (scams with off-platform payment traps, free work sample demands, and indirect prompt injection attempts).
- **Gold Dev Set:** 60 annotated jobs with verified ground-truth labels (`bid_or_skip`, `is_scam`, `has_injection`, `gold_evidence_ids`, `fair_price_band`).

---

## 2. Persona Specifications
| Persona Key | Name | Primary Specialization | Hourly Base Rate | Case Studies | Labeled Proposals |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `ai_ml_engineer` | Dr. Alex Rivera | LLM Architectures, RAG, Vector Search, PyTorch | $110.00/hr | 16 | 150 |
| `fullstack_web_dev` | Maya Lin | Next.js, TypeScript, Distributed Cloud, PostgreSQL | $95.00/hr | 16 | 150 |
| `data_analyst` | Marcus Chen | Business Intelligence, dbt, Snowflake, A/B Testing | $85.00/hr | 16 | 150 |

---

## 3. Data Structure & Schemas
- `data/personas/<persona>/cv.md`: Curriculum Vitae detailing roles, education, and domain proficiencies.
- `data/personas/<persona>/case_studies/*.md`: Individual markdown reports containing Problem Statement, Technical Architecture, and Quantifiable ROI metrics.
- `data/personas/<persona>/case_studies.json`: Structured array of case study metadata with industry tags and skills.
- `data/personas/<persona>/past_proposals.json`: Proposals with outcome labels (`won`, `replied`, `ignored`), bid prices, and matching case study IDs.
- `data/personas/<persona>/github_repos/`: Simulated production repositories containing typed source code implementations.
- `data/policy_pack/marketplace_rules.md`: Invariants enforcing Upwork Nov 2 policy guidelines (no off-platform communications, zero tolerance for fabricated experience, no free samples).
- `data/processed/job_stream.json`: Marketplace stream formatted to `JobPosting` schema.
- `evals/datasets/dev_set.json`: Evaluation benchmark with gold labels.

---

## 4. Invariant and Safety Considerations
1. **No Personal PII:** All persona and client identities are synthetic.
2. **Adversarial Injections:** Specific adversarial examples test agent resilience against indirect prompt injection and unauthorized connects consumption.
3. **Immutability:** Once generated and verified, baseline simulator schemas are immutable.
