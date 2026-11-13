# Phase 8: Part D (1/2) & Part E (1/2) — FastAPI Backend, SSE Streaming, Auth & Background Worker

## Objectives
1. Implement `apps/api/`:
   - `auth/`: Multi-tenant auth, preloaded Reviewer account (`reviewer@gigbid.ai`), persona selector, Fernet encryption for OAuth tokens.
   - `routers/`:
     - `auth.py`: Token issue, user info, active persona.
     - `jobs.py`: List, search, detail, trigger analysis.
     - `proposals.py`: List, get, update drafts.
     - `approvals.py`: Resume interrupted LangGraph runs (`approve`, `edit`, `reject`).
     - `messages.py`: Conversation threads and replies.
     - `runs.py`: Trace inspection, checkpoint replay, execution steps.
     - `analytics.py`: Real-time funnel metrics, spend, win rates, budget usage.
     - `settings.py`: Autonomy levels, model profiles, adapter toggle, memory viewer & deletion.
   - `streaming.py`: SSE endpoint broadcasting live agent thought steps and state transitions.
2. Implement `worker/tasks.py`:
   - Background worker for automatic job scouting, scheduled sync, and batch processing.
3. Generate TypeScript API client definitions in `apps/web/src/lib/api/client.ts`.
4. Verification:
   - Run tests in `tests/integration/test_api_routes.py`.
