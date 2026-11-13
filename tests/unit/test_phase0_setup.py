from pathlib import Path

from agent.config import load_agent_config

REQUIRED_DIRS = [
    "apps/web",
    "apps/api",
    "agent",
    "rag",
    "mcp_servers",
    "worker",
    "gigsim",
    "data",
    "evals",
    "tests",
    "infra",
    ".github/workflows",
    "docs",
]


def test_directory_layout_invariants():
    """Verify that all Rule 1 required directories exist."""
    root = Path(__file__).resolve().parents[2]
    for dir_rel in REQUIRED_DIRS:
        target = root / dir_rel
        assert target.exists() and target.is_dir(), f"Required directory missing: {dir_rel}"


def test_agent_config_and_rule_3():
    """Verify agent configuration, budgets, profiles, and node model resolution."""
    config = load_agent_config()
    assert config.version == "1.0.0"
    assert config.active_profile in ("open", "paid")
    assert "open" in config.profiles
    assert "paid" in config.profiles

    # Check that each required agent node resolves dynamically
    nodes = [
        "scout",
        "analyst",
        "risk",
        "matcher",
        "pricing",
        "writer",
        "verifier",
        "critic",
        "compliance",
        "liaison",
    ]
    for n in nodes:
        open_model = config.resolve_model_for_node(n, profile_override="open")
        paid_model = config.resolve_model_for_node(n, profile_override="paid")
        assert open_model, f"Node {n} missing open_model"
        assert paid_model, f"Node {n} missing paid_model"

    assert config.budgets.max_steps_per_thread == 25
    assert config.budgets.max_tokens_per_thread == 35000
    assert config.budgets.cost_budget_usd == 0.05
    assert config.active_rag_variant == "v4_outcome_aware"
    assert config.marketplace_adapter == "gigsim"


def test_env_example_contains_all_keys():
    """Verify .env.example defines key auth and configuration secrets."""
    root = Path(__file__).resolve().parents[2]
    env_file = root / ".env.example"
    assert env_file.exists()
    content = env_file.read_text(encoding="utf-8")
    assert "JWT_SECRET_KEY" in content
    assert "OAUTH_FERNET_KEY" in content
    assert "GIGSIM_BASE_URL" in content
    assert "MARKETPLACE_ADAPTER" in content
