"""GigBid FastAPI Application Entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.routers import (
    analytics,
    approvals,
    auth,
    jobs,
    messages,
    proposals,
    runs,
    settings,
)
from apps.api.streaming import router as streaming_router

app = FastAPI(
    title="GigBid Autonomous Bidding API",
    description="Multi-agent freelance intake, proposal generation, and client lifecycle backend.",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(auth.router)
app.include_router(jobs.router)
app.include_router(proposals.router)
app.include_router(approvals.router)
app.include_router(messages.router)
app.include_router(runs.router)
app.include_router(analytics.router)
app.include_router(settings.router)
app.include_router(streaming_router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "gigbid-api", "version": "1.0.0"}
