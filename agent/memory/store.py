"""Persistent Memory Store for Style & Outcome Memories."""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.memory.promotion_rules import (
    MemoryCandidate,
    evaluate_outcome_promotion,
    evaluate_style_promotion,
)

MEMORY_FILE = Path(__file__).resolve().parents[2] / "data" / "processed" / "agent_memory.json"


class AgentMemoryStore:
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or MEMORY_FILE
        self.style_memory: Dict[str, Dict[str, Any]] = {}
        self.outcome_memory: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self):
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                self.style_memory = data.get("style", {})
                self.outcome_memory = data.get("outcome", {})
            except Exception:
                pass

    def _save(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"style": self.style_memory, "outcome": self.outcome_memory}
        self.storage_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def promote_candidate(self, candidate: MemoryCandidate) -> Optional[str]:
        """Evaluate and conditionally promote a candidate according to strict promotion rules."""
        if candidate.category == "style":
            decision = evaluate_style_promotion(candidate)
        else:
            decision = evaluate_outcome_promotion(candidate)

        if not decision.promoted or not decision.promoted_key or not decision.promoted_content:
            return None

        record = {
            "key": decision.promoted_key,
            "category": decision.memory_type,
            "content": decision.promoted_content,
            "promoted_at": datetime.now(timezone.utc).isoformat(),
            "source_id": candidate.source_id,
            "metadata": candidate.metadata,
        }

        if decision.memory_type == "style":
            self.style_memory[decision.promoted_key] = record
        else:
            self.outcome_memory[decision.promoted_key] = record

        self._save()
        return decision.promoted_key

    def retrieve_memory_context(self, industry: Optional[str] = None, skills: Optional[List[str]] = None) -> str:
        """Retrieve relevant style and outcome memories formatted as context for prompt injection."""
        lines = []

        if self.style_memory:
            lines.append("### Relevant Style Memories (Learned from User Edits):")
            for item in list(self.style_memory.values())[-3:]:
                lines.append(f"- {item['content']}")

        if self.outcome_memory:
            lines.append("### Relevant Outcome Memories (Validated Winning Patterns):")
            for item in list(self.outcome_memory.values())[-3:]:
                lines.append(f"- {item['content']}")

        return "\n".join(lines) if lines else "No prior memory context recorded."

    def list_memories(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "style": list(self.style_memory.values()),
            "outcome": list(self.outcome_memory.values()),
        }

    def delete_memory(self, memory_key: str) -> bool:
        deleted = False
        if memory_key in self.style_memory:
            del self.style_memory[memory_key]
            deleted = True
        if memory_key in self.outcome_memory:
            del self.outcome_memory[memory_key]
            deleted = True
        if deleted:
            self._save()
        return deleted


_global_memory_store: Optional[AgentMemoryStore] = None


def get_memory_store() -> AgentMemoryStore:
    global _global_memory_store
    if _global_memory_store is None:
        _global_memory_store = AgentMemoryStore()
    return _global_memory_store
