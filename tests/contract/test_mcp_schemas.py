from mcp_servers.marketplace.server import create_marketplace_mcp_server
from mcp_servers.portfolio.server import create_portfolio_mcp_server
from mcp_servers.workspace.server import create_workspace_mcp_server


def test_mcp_schema_contract_snapshots():
    """Verify tool signatures, schemas, and annotations for all MCP servers."""
    portfolio_srv = create_portfolio_mcp_server()
    marketplace_srv = create_marketplace_mcp_server()
    workspace_srv = create_workspace_mcp_server()

    # Portfolio tools contract
    p_tools = {t["name"]: t for t in portfolio_srv.list_tools()}
    assert "search_evidence" in p_tools
    assert p_tools["search_evidence"]["annotations"]["readOnlyHint"] is True
    assert "requirement" in p_tools["search_evidence"]["inputSchema"]["properties"]

    # Marketplace tools contract
    m_tools = {t["name"]: t for t in marketplace_srv.list_tools()}
    assert "submit_proposal" in m_tools
    assert m_tools["submit_proposal"]["annotations"]["destructiveHint"] is True
    assert m_tools["submit_proposal"]["annotations"]["idempotentHint"] is True
    assert "idempotency_key" in m_tools["submit_proposal"]["inputSchema"]["properties"]
    assert "dry_run" in m_tools["submit_proposal"]["inputSchema"]["properties"]

    # Workspace tools contract
    w_tools = {t["name"]: t for t in workspace_srv.list_tools()}
    assert "get_free_calendar_slots" in w_tools
    assert "create_tentative_interview_hold" in w_tools
    assert "create_email_draft" in w_tools
    assert w_tools["get_free_calendar_slots"]["annotations"]["readOnlyHint"] is True
