"""Messages Router: Client message threads, reply dispatch, and scheduling holds."""

from typing import Any, Dict, List

from fastapi import APIRouter, Depends

from apps.api.auth.security import get_current_user
from apps.api.schemas.models import MessageSendRequest
from apps.api.state_manager import get_api_state

router = APIRouter(prefix="/messages", tags=["Messages"])


@router.get("")
def list_threads(current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    return [
        {
            "thread_id": "thread_demo_01",
            "client_name": "HealthAI Technologies",
            "last_message": "Hi, we loved your proposal! Can we schedule a quick call tomorrow at 2pm?",
            "unread_count": 1,
            "has_calendar_hold": True,
        }
    ]


@router.get("/{thread_id}")
def get_thread_messages(thread_id: str, current_user: dict = Depends(get_current_user)) -> List[Dict[str, Any]]:
    return [
        {
            "id": "msg_001",
            "sender": "client",
            "text": "Hi, we loved your proposal! Can we schedule a quick call tomorrow at 2pm?",
            "timestamp": "2026-11-13T12:30:00Z",
        }
    ]


@router.post("/send")
def send_message(req: MessageSendRequest, current_user: dict = Depends(get_current_user)) -> Dict[str, Any]:
    state = get_api_state()
    msg_record = {
        "thread_id": req.thread_id,
        "recipient_id": req.recipient_id,
        "text": req.text,
        "status": "SENT",
    }
    state.messages.setdefault(req.thread_id, []).append(msg_record)
    return msg_record
