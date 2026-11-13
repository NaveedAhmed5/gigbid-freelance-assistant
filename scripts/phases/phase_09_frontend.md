# Phase 9: Part D (2/2) — Next.js Frontend (All 9 Screens) & Playwright E2E Tests

## Objectives
1. Implement full Next.js App Router UI in `apps/web/`:
   - `/onboarding`: Persona selection & credentials setup.
   - `/inbox`: Filterable, rank-ordered job inbox with match scores.
   - `/jobs/[id]`: Job Detail view with requirement-to-evidence matrix.
   - `/studio/[id]`: Proposal Studio with evidence-on-hover, inline critic & compliance alerts, single-paragraph regeneration, and dry-run approval bar.
   - `/pipeline`: Kanban board tracking proposals across Draft, Approval, Submitted, Replied, Won, Lost.
   - `/messages`: Client messaging interface with calendar hold chips.
   - `/runs/[id]`: Live Agent Run Viewer showing graph DAG, token budgets, and streaming steps.
   - `/analytics`: Funnel charts, Connects ROI, and latency distribution.
   - `/settings`: Autonomy configuration, model toggles, and Style/Outcome Memory Viewer.
   - Global `DegradedModeBanner` alerting users if MCP servers or external APIs disconnect.
2. Implement Playwright E2E test specs in `apps/web/tests/e2e/`:
   - Test 1: Onboarding and persona selection.
   - Test 2: Approving a proposal draft.
   - Test 3: Rejecting a proposal draft with feedback.
   - Test 4: Editing proposal text and updating diff memory.
   - Test 5: Degraded mode banner display on simulator disconnect.
3. Verification:
   - Ensure `npm run build` or Next.js typecheck / component tests pass.

