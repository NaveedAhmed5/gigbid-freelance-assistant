"""Verification Script for Upwork Live MCP Adapter & Streamable HTTP Connection.

Tests:
1. Retrieval of decrypted OAuth / Personal Bearer token from EncryptedTokenStore.
2. Direct connection to https://mcp.upwork.com/mcp over Streamable HTTP.
3. Discovery and listing of official Upwork MCP tools via session.list_tools().
4. Fetching real jobs via search_jobs() and verifying zero fallback to dummy data.
5. Ingestion of live Upwork jobs into gigbid.db SQLite database.
"""

import logging
import os
import sys
from pathlib import Path

# Add project root to sys.path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apps.api.db import clear_dummy_seed_jobs, get_all_jobs, save_jobs
from mcp_servers.marketplace.adapters.upwork_live import (
    AuthenticationError,
    UpworkLiveAdapter,
    get_token_store,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("test_upwork_live")


def main():
    print("=" * 70)
    print("🚀 GIGBID UPWORK LIVE MCP VERIFICATION & STREAMABLE HTTP TEST")
    print("=" * 70)

    endpoint_url = os.getenv("UPWORK_MCP_URL", "https://mcp.upwork.com/mcp")
    print(f"[*] Target Endpoint: {endpoint_url}")

    store = get_token_store()
    token = store.get_token("usr_reviewer_01") or store.get_token("tenant_default") or os.getenv("UPWORK_ACCESS_TOKEN")

    print(f"[*] Checking Token Store: {'TOKEN FOUND (Decrypted)' if token and not token.startswith('mock_') else 'NO VALID TOKEN'}")

    adapter = UpworkLiveAdapter(endpoint_url=endpoint_url, token_store=store)

    if not token or token.startswith("mock_"):
        print("\n[!] Notice: No live Upwork bearer token is currently configured.")
        print("    Verifying that search_jobs() correctly raises AuthenticationError (Zero Dummy Fallback)...")
        try:
            adapter.search_jobs(query="Python", limit=5)
            print("❌ FAILED: search_jobs() returned data instead of raising AuthenticationError!")
            sys.exit(1)
        except AuthenticationError as e:
            print(f"✅ PASSED: Correctly raised AuthenticationError without returning fake data:\n    -> {e}")

        print("\n" + "=" * 70)
        print("💡 HOW TO COMPLETE REAL LIVE UPWORK CONNECTION:")
        print("   1. Open the Web App: http://localhost:3000/settings")
        print("   2. Under 'Upwork Live MCP Integration', either:")
        print("      a) Click 'Connect Upwork Account (OAuth 2.1)' (requires UPWORK_OAUTH_CLIENT_ID in .env)")
        print("      b) Paste your Upwork bearer token into 'Connect with Upwork Bearer Token directly' and click Save.")
        print("   3. Or set UPWORK_ACCESS_TOKEN=<your-token> in your .env file.")
        print("   4. Re-run: python scripts/test_upwork_live_tools.py")
        print("=" * 70)
        return

    # Real token is available: proceed to query https://mcp.upwork.com/mcp
    print("\n[*] Connecting to Upwork MCP over Streamable HTTP with Bearer token...")
    try:
        print("[*] Calling session.list_tools() against https://mcp.upwork.com/mcp...")
        tools = adapter.list_tools()
        print(f"✅ Discovered {len(tools)} Upwork MCP Tools:")
        for t in tools:
            name = getattr(t, "name", str(t))
            desc = getattr(t, "description", "")
            print(f"   - 🛠️  {name}: {desc[:80]}...")
    except AuthenticationError as e:
        print(f"\n❌ Upwork authentication failed: {e}")
        print("   The access token in the store was rejected by Upwork's remote server.")
        return
    except Exception as e:
        print(f"\n⚠️  Direct list_tools failed ({e}). Proceeding to search_jobs...")

    # Fetch 5 live jobs
    print("\n[*] Querying live Upwork jobs via adapter.search_jobs(query='Python', limit=5)...")
    try:
        live_jobs = adapter.search_jobs(query="Python", limit=5)
        print(f"✅ Fetched {len(live_jobs)} Real Upwork Jobs:")
        for i, j in enumerate(live_jobs, 1):
            print(f"   [{i}] {j['id']} - {j['title']} (Budget: ${j.get('budget_usd')}, Skills: {', '.join(j.get('skills', [])[:3])})")

        # Ingest into SQLite gigbid.db
        print("\n[*] Clearing old dummy seed jobs and saving real jobs to gigbid.db...")
        clear_dummy_seed_jobs()
        save_jobs(live_jobs)
        stored_jobs = get_all_jobs(source="upwork_live")
        print(f"✅ Confirmed {len(stored_jobs)} live Upwork jobs saved in gigbid.db.")

    except AuthenticationError as e:
        print(f"❌ AuthenticationError: {e}")
    except Exception as e:
        print(f"❌ Error during job search: {e}")


if __name__ == "__main__":
    main()
