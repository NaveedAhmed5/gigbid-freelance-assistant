"""Server-Sent Events (SSE) Streaming for Real-Time Agent Execution Telemetry."""

import asyncio
import json
from typing import AsyncGenerator

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from apps.api.state_manager import get_api_state

router = APIRouter(prefix="/stream", tags=["Streaming"])


async def event_generator(run_id: str) -> AsyncGenerator[str, None]:
    state = get_api_state()
    run = state.runs.get(run_id)

    if not run:
        yield json.dumps({"event": "error", "message": f"Run {run_id} not found."})
        return

    # Stream out existing recorded trace steps
    for step in run.get("trace_steps", []):
        yield json.dumps(
            {
                "event": "node_execution",
                "run_id": run_id,
                "node": step["node_name"],
                "action": step["action_type"],
                "tokens": step["tokens_consumed"],
                "latency_ms": step["latency_ms"],
                "summary": step["output_summary"],
            }
        )
        await asyncio.sleep(0.05)

    # Final event
    yield json.dumps(
        {
            "event": "run_completed",
            "run_id": run_id,
            "status": run.get("status", "COMPLETED"),
        }
    )


@router.get("/{run_id}")
async def stream_run_telemetry(run_id: str):
    return EventSourceResponse(event_generator(run_id))
