from fastapi.testclient import TestClient

from apps.api.main import app
from worker.tasks import run_worker_once

client = TestClient(app)


def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "ok"


def test_api_auth_lifecycle():
    # Login
    login_res = client.post("/auth/login", json={"email": "reviewer@gigbid.ai", "password": "reviewer-demo-pass"})
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token

    headers = {"Authorization": f"Bearer {token}"}

    # Profile me
    me_res = client.get("/auth/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "reviewer@gigbid.ai"

    # Switch persona
    switch_res = client.post("/auth/switch-persona", json={"persona": "fullstack_web_dev"}, headers=headers)
    assert switch_res.status_code == 200
    assert switch_res.json()["active_persona"] == "fullstack_web_dev"

    # Switch back
    client.post("/auth/switch-persona", json={"persona": "ai_ml_engineer"}, headers=headers)


def test_api_jobs_and_analysis_pipeline():
    # List jobs
    jobs_res = client.get("/jobs?limit=5")
    assert jobs_res.status_code == 200
    jobs = jobs_res.json()
    assert len(jobs) > 0
    test_job_id = jobs[0]["id"]

    # Detail job
    job_detail = client.get(f"/jobs/{test_job_id}")
    assert job_detail.status_code == 200
    assert job_detail.json()["id"] == test_job_id

    # Trigger analysis (BidGraph execution)
    analysis_res = client.post("/jobs/analyze", json={"job_id": test_job_id, "persona": "ai_ml_engineer"})
    assert analysis_res.status_code == 200
    run_rec = analysis_res.json()
    assert "run_id" in run_rec
    assert "trace_steps" in run_rec


def test_api_approvals_and_proposals():
    # Check pending approvals
    approvals_res = client.get("/approvals")
    assert approvals_res.status_code == 200
    approvals = approvals_res.json()

    if approvals:
        target_job_id = approvals[0]["job_id"]
        # Update draft
        patch_res = client.patch(
            f"/proposals/{target_job_id}",
            json={"cover_letter": "Revised tailored proposal with 45% measurable ROI."},
        )
        assert patch_res.status_code == 200

        # Submit approval decision
        dec_res = client.post(
            "/approvals/decision",
            json={
                "job_id": target_job_id,
                "action": "approve",
                "edited_cover_letter": "Revised tailored proposal with 45% measurable ROI.",
            },
        )
        assert dec_res.status_code == 200
        assert dec_res.json()["status"] == "SUBMITTED"


def test_api_runs_and_dag():
    runs_res = client.get("/runs")
    assert runs_res.status_code == 200
    runs = runs_res.json()
    if runs:
        run_id = runs[0]["run_id"]
        detail_res = client.get(f"/runs/{run_id}")
        assert detail_res.status_code == 200
        dag_res = client.get(f"/runs/{run_id}/dag")
        assert dag_res.status_code == 200
        assert "nodes" in dag_res.json()
        assert "edges" in dag_res.json()


def test_api_analytics_and_settings():
    # Analytics
    analytics_res = client.get("/analytics")
    assert analytics_res.status_code == 200
    data = analytics_res.json()
    assert "funnel" in data
    assert "rates" in data

    # Settings
    settings_res = client.get("/settings")
    assert settings_res.status_code == 200
    settings = settings_res.json()
    assert "autonomy_level" in settings

    # Update settings
    patch_res = client.patch(
        "/settings",
        json={
            "autonomy_level": "full_autonomous",
            "active_profile": "open",
            "marketplace_adapter": "gigsim",
            "max_critic_loops": 2,
        },
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["autonomy_level"] == "full_autonomous"

    # Memories
    mem_res = client.get("/settings/memories")
    assert mem_res.status_code == 200


def test_background_worker_execution():
    worker_results = run_worker_once()
    assert isinstance(worker_results, list)
