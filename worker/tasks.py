"""GigBid Background Worker Tasks: Idempotent job scouting & batch analysis."""

import time
from typing import Any, Dict, List

from agent.mcp_client import get_mcp_client
from apps.api.state_manager import get_api_state


class BackgroundWorker:
    def __init__(self):
        self.processed_job_ids: set = set()
        self.api_state = get_api_state()

    def scout_and_ingest_new_jobs(
        self, limit: int = 10, persona: str = "ai_ml_engineer"
    ) -> List[Dict[str, Any]]:
        """Scout marketplace for unseen jobs and trigger autonomous analysis."""
        client = get_mcp_client()
        jobs = client.call_tool("scout", "search_jobs", {"limit": limit})

        results = []
        for job in jobs:
            job_id = job.get("id")
            if not job_id or job_id in self.processed_job_ids:
                continue

            self.processed_job_ids.add(job_id)
            try:
                run_rec = self.api_state.run_bid_pipeline(job_id=job_id, persona=persona)
                results.append(run_rec)
            except Exception as e:
                results.append({"job_id": job_id, "error": str(e), "status": "FAILED"})

        return results

    def run_worker_loop(self, interval_sec: float = 30.0, max_iterations: int = 1):
        """Worker execution loop."""
        for _ in range(max_iterations):
            self.scout_and_ingest_new_jobs(limit=5)
            if max_iterations > 1:
                time.sleep(interval_sec)


def run_worker_once():
    worker = BackgroundWorker()
    return worker.scout_and_ingest_new_jobs(limit=5)


if __name__ == "__main__":
    run_worker_once()
