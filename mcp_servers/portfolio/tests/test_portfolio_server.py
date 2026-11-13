from mcp_servers.portfolio.server import create_portfolio_mcp_server


def test_portfolio_server_tools_and_resources():
    server = create_portfolio_mcp_server()

    # Verify tool registration
    tools = server.list_tools()
    tool_names = {t["name"] for t in tools}
    assert "search_evidence" in tool_names
    assert "get_case_study" in tool_names
    assert "list_skills" in tool_names

    # Test search_evidence tool call
    evidence = server.call_tool(
        "search_evidence",
        {"requirement": "PyTorch RAG enterprise", "k": 2, "filters": {"persona": "ai_ml_engineer"}},
    )
    assert len(evidence) <= 2
    assert len(evidence) > 0
    assert "metric_improvement_pct" in evidence[0]

    # Test get_case_study
    first_cs_id = evidence[0]["id"]
    cs_detail = server.call_tool("get_case_study", {"id": first_cs_id})
    assert cs_detail["id"] == first_cs_id
    assert "content" in cs_detail

    # Test list_skills
    skills = server.call_tool("list_skills", {"persona": "ai_ml_engineer"})
    assert len(skills) > 0

    # Test resource read
    res = server.read_resource(f"portfolio://case/{first_cs_id}")
    assert res["case_id"] == first_cs_id

    # Test prompt get
    prompt_out = server.get_prompt(
        "Answer a screening question from my portfolio",
        {"question": "How do you optimize retrieval latency?", "persona": "ai_ml_engineer"},
    )
    assert "Answer a screening question" or "screening" in prompt_out

