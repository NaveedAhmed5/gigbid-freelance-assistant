from mcp_servers.marketplace.server import create_marketplace_mcp_server


def test_marketplace_server_idempotency_and_dry_run():
    server = create_marketplace_mcp_server()

    # Test search_jobs
    jobs = server.call_tool("search_jobs", {"limit": 5})
    assert len(jobs) > 0
    target_job = jobs[0]

    # Test dry run submission
    dry_run_res = server.call_tool(
        "submit_proposal",
        {
            "job_id": target_job["id"],
            "freelancer_id": "freelancer_test",
            "cover_letter": "Tailored proposal text with metric proof points.",
            "bid_amount_usd": 1500.0,
            "estimated_duration": "1 month",
            "idempotency_key": "idem_key_001",
            "dry_run": True,
        },
    )
    assert dry_run_res["dry_run"] is True
    assert dry_run_res["status"] == "VALIDATED"

    # Test live submission with idempotency key
    live_res_1 = server.call_tool(
        "submit_proposal",
        {
            "job_id": target_job["id"],
            "freelancer_id": "freelancer_test",
            "cover_letter": "Tailored proposal text with metric proof points.",
            "bid_amount_usd": 1500.0,
            "estimated_duration": "1 month",
            "idempotency_key": "idem_key_002",
            "dry_run": False,
        },
    )
    assert live_res_1["status"] == "SUBMITTED"
    assert "submission_id" in live_res_1

    # Resubmit with identical idempotency key -> Must return cached result without double charging
    live_res_2 = server.call_tool(
        "submit_proposal",
        {
            "job_id": target_job["id"],
            "freelancer_id": "freelancer_test",
            "cover_letter": "Different proposal text",
            "bid_amount_usd": 2000.0,
            "estimated_duration": "2 months",
            "idempotency_key": "idem_key_002",
            "dry_run": False,
        },
    )
    assert live_res_2["submission_id"] == live_res_1["submission_id"]
    assert live_res_2["bid_amount_usd"] == live_res_1["bid_amount_usd"]

