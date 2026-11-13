import pytest

from agent.marketplace_port import MarketplacePort
from agent.mcp_client import AGENT_TOOL_ALLOWLISTS, MCPClient
from mcp_servers.marketplace.adapters.gigsim import GigSimAdapter
from mcp_servers.marketplace.adapters.upwork_live import EncryptedTokenStore, UpworkLiveAdapter


def test_agent_tool_allowlists_enforcement():
    client = MCPClient()

    # 1. Analyst has zero external tools -> Must raise PermissionError
    assert len(AGENT_TOOL_ALLOWLISTS["analyst"]) == 0
    with pytest.raises(PermissionError) as exc_info:
        client.call_tool("analyst", "search_jobs", {})
    assert "unauthorized to call tool 'search_jobs'" in str(exc_info.value)

    # 2. Scout can call search_jobs
    res = client.call_tool("scout", "search_jobs", {"limit": 2})
    assert isinstance(res, list)

    # 3. Scout CANNOT call submit_proposal
    with pytest.raises(PermissionError):
        client.call_tool("scout", "submit_proposal", {"job_id": "123"})

    # 4. Fit Matcher can call portfolio search_evidence
    res_evidence = client.call_tool("matcher", "search_evidence", {"requirement": "PyTorch", "k": 1})
    assert len(res_evidence) <= 1


def test_mcp_client_degraded_mode():
    client = MCPClient(simulate_network_failure=True)
    res = client.call_tool("scout", "search_jobs", {"query": "test"})
    assert res.get("degraded_mode") is True
    assert res.get("status") == "QUEUED"
    assert len(client.queued_requests) == 1


def test_gigsim_adapter_implements_port():
    adapter = GigSimAdapter()
    assert isinstance(adapter, MarketplacePort)
    jobs = adapter.search_jobs(limit=3)
    assert len(jobs) > 0
    balance = adapter.get_connects_balance()
    assert "balance" in balance


def test_upwork_live_adapter_safety_and_encryption():
    # Test token encryption store
    store = EncryptedTokenStore()
    store.store_token("user_123", "secret_live_oauth_token_xyz")
    retrieved = store.get_token("user_123")
    assert retrieved == "secret_live_oauth_token_xyz"
    assert store.get_token("unknown_user") is None

    # Test adapter
    adapter = UpworkLiveAdapter(token_store=store, force_draft_only=True)
    assert isinstance(adapter, MarketplacePort)

    # Test draft-only safety enforcement
    submission_res = adapter.submit_proposal(
        job_id="live_job_01",
        freelancer_id="user_123",
        cover_letter="Proposal test",
        bid_amount_usd=2500.0,
        estimated_duration="1 month",
        idempotency_key="key_123",
        dry_run=False,
    )
    # Must enforce safety: converted to draft
    assert submission_res.get("status") == "DRAFT"
    assert "UpworkLiveAdapter" in submission_res.get("notice", "")
