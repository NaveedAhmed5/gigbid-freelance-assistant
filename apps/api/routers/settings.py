"""Settings Router: Autonomy levels, adapter toggle, and Memory Viewer."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException

from agent.config import load_agent_config
from agent.memory.store import get_memory_store
from apps.api.auth.security import get_current_user
from apps.api.schemas.models import SettingsResponse, SettingsUpdateRequest

router = APIRouter(prefix="/settings", tags=["Settings"])

CURRENT_SETTINGS = {
    "autonomy_level": "semi_autonomous",
    "active_profile": "open",
    "marketplace_adapter": "gigsim",
    "max_critic_loops": 2,
}


@router.get("", response_model=SettingsResponse)
def get_settings(current_user: dict = Depends(get_current_user)):
    config = load_agent_config()
    mem_store = get_memory_store()
    mems = mem_store.list_memories()

    return SettingsResponse(
        autonomy_level=CURRENT_SETTINGS["autonomy_level"],
        active_profile=config.active_profile,
        marketplace_adapter=config.marketplace_adapter,
        max_critic_loops=config.budgets.max_critic_loops,
        open_model_default=config.profiles["open"].default_llm,
        paid_model_default=config.profiles["paid"].default_llm,
        style_memories_count=len(mems["style"]),
        outcome_memories_count=len(mems["outcome"]),
    )


@router.patch("", response_model=SettingsResponse)
def update_settings(req: SettingsUpdateRequest, current_user: dict = Depends(get_current_user)):
    CURRENT_SETTINGS["autonomy_level"] = req.autonomy_level
    CURRENT_SETTINGS["active_profile"] = req.active_profile
    CURRENT_SETTINGS["marketplace_adapter"] = req.marketplace_adapter
    CURRENT_SETTINGS["max_critic_loops"] = req.max_critic_loops
    return get_settings(current_user=current_user)


@router.get("/memories")
def list_memories(current_user: dict = Depends(get_current_user)) -> Dict[str, List[Dict[str, Any]]]:
    mem_store = get_memory_store()
    return mem_store.list_memories()


@router.delete("/memories/{memory_key}")
def delete_memory(memory_key: str, current_user: dict = Depends(get_current_user)):
    mem_store = get_memory_store()
    deleted = mem_store.delete_memory(memory_key)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory key not found.")
    return {"status": "deleted", "memory_key": memory_key}
