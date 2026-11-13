from mcp_servers.workspace.server import create_workspace_mcp_server


def test_workspace_server_calendar_and_email():
    server = create_workspace_mcp_server()

    # 1. Get free calendar slots
    slots = server.call_tool("get_free_calendar_slots", {"days_ahead": 3, "duration_minutes": 30})
    assert len(slots) > 0
    slot = slots[0]
    assert "slot_id" in slot

    # 2. Place tentative hold
    hold = server.call_tool(
        "create_tentative_interview_hold",
        {
            "slot_id": slot["slot_id"],
            "client_name": "HealthCorp AI",
            "job_id": "job_001",
            "notes": "Introductory 30-min architecture alignment call.",
        },
    )
    assert hold["status"] == "TENTATIVE"
    assert hold["slot_id"] == slot["slot_id"]

    # 3. Create email draft
    draft = server.call_tool(
        "create_email_draft",
        {
            "recipient": "client@healthcorp.ai",
            "subject": "Follow up regarding Architecture Roadmap",
            "body": "Hi, I have placed a tentative hold on my calendar for our discussion.",
        },
    )
    assert draft["status"] == "DRAFT"
    assert "draft_id" in draft
