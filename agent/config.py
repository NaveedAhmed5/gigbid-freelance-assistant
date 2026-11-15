"""Agent configuration loader and dynamic model resolver."""

from pathlib import Path
from typing import Dict, Optional

import yaml
from pydantic import BaseModel, Field

CONFIG_PATH = Path(__file__).resolve().parent / "config.yaml"


class NodeRoute(BaseModel):
    role: str
    open_model: str
    paid_model: str
    temperature: float = 0.2
    max_tokens: int = 2048


class ProfileConfig(BaseModel):
    description: str
    provider: str = "groq"
    base_url: Optional[str] = None
    default_llm: str
    reasoning_llm: Optional[str] = None
    embedding_model: str
    reranker_model: str
    deterministic_fallback: bool = True
    models: Dict[str, str] = Field(default_factory=dict)


class Budgets(BaseModel):
    max_steps_per_thread: int = 25
    max_tokens_per_thread: int = 35000
    p95_latency_budget_sec: float = 30.0
    cost_budget_usd: float = 0.05
    max_critic_loops: int = 2


class PlatformRules(BaseModel):
    prohibit_contact_before_contract: bool = True
    prohibit_off_platform_payment: bool = True
    prohibit_free_work_samples: bool = True
    prohibit_fabricated_experience: bool = True
    require_explicit_human_approval_for_submission: bool = True
    max_unsupported_claim_tolerance: int = 0


class AgentConfig(BaseModel):
    version: str
    active_profile: str
    profiles: Dict[str, ProfileConfig]
    node_routing: Dict[str, NodeRoute]
    budgets: Budgets
    active_rag_variant: str = "v4_outcome_aware"
    marketplace_adapter: str = "gigsim"
    platform_rules: PlatformRules

    def get_active_profile(self) -> ProfileConfig:
        if self.active_profile not in self.profiles:
            raise ValueError(f"Active profile '{self.active_profile}' not found in configuration.")
        return self.profiles[self.active_profile]

    def resolve_model_for_node(self, node_name: str, profile_override: Optional[str] = None) -> str:
        profile_key = profile_override or self.active_profile
        if node_name not in self.node_routing:
            raise KeyError(f"Node '{node_name}' not defined in node_routing.")
        route = self.node_routing[node_name]
        return route.open_model if profile_key == "open" else route.paid_model

    def resolve_embedding_model(self) -> str:
        return self.get_active_profile().embedding_model

    def resolve_reranker_model(self) -> str:
        return self.get_active_profile().reranker_model


def load_agent_config(path: Optional[Path] = None) -> AgentConfig:
    target_path = path or CONFIG_PATH
    if not target_path.exists():
        raise FileNotFoundError(f"Configuration file not found at: {target_path}")
    with open(target_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return AgentConfig(**data)
