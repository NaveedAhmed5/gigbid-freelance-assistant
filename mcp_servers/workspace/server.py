"""Workspace MCP Server: Calendar, Scheduling, and Draft Communications."""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from mcp_servers.protocol import BaseMCPServer, MCPToolAnnotation


class FreeSlot(BaseModel):
    slot_id: str
    start_time: str
    end_time: str
    timezone: str = "UTC"


class TentativeHoldInput(BaseModel):
    slot_id: str
    client_name: str
    job_id: str
    notes: Optional[str] = None


class EmailDraftInput(BaseModel):
    recipient: str
    subject: str
    body: str
    category: str = "interview_followup"


class WorkspaceMCPServer(BaseMCPServer):
    def __init__(self, name: str = "workspace-mcp-server", version: str = "1.0.0"):
        super().__init__(name, version)
        self.holds: Dict[str, Dict[str, Any]] = {}
        self.email_drafts: Dict[str, Dict[str, Any]] = {}
        self._register_tools()

    def _register_tools(self):
        self.register_tool(
            name="get_free_calendar_slots",
            description="Find upcoming free 30-minute calendar slots for scheduling client calls.",
            input_schema={
                "type": "object",
                "properties": {
                    "days_ahead": {"type": "integer", "default": 5},
                    "duration_minutes": {"type": "integer", "default": 30},
                },
            },
            handler=self.tool_get_free_calendar_slots,
            annotations=MCPToolAnnotation(readOnlyHint=True, idempotentHint=True),
        )

        self.register_tool(
            name="create_tentative_interview_hold",
            description="Place a tentative hold on the candidate's calendar for a proposed client interview.",
            input_schema=TentativeHoldInput.model_json_schema(),
            handler=self.tool_create_tentative_interview_hold,
            annotations=MCPToolAnnotation(
                readOnlyHint=False, destructiveHint=False, idempotentHint=True
            ),
        )

        self.register_tool(
            name="create_email_draft",
            description="Create an email draft in the candidate's workspace without sending.",
            input_schema=EmailDraftInput.model_json_schema(),
            handler=self.tool_create_email_draft,
            annotations=MCPToolAnnotation(
                readOnlyHint=False, destructiveHint=False, idempotentHint=True
            ),
        )

    def tool_get_free_calendar_slots(
        self, days_ahead: int = 5, duration_minutes: int = 30
    ) -> List[Dict[str, Any]]:
        now = datetime.now(timezone.utc)
        slots = []
        for d in range(1, days_ahead + 1):
            day_target = now + timedelta(days=d)
            if day_target.weekday() < 5:  # Monday to Friday
                for hour in [14, 16, 18]:  # 2pm, 4pm, 6pm UTC
                    start = day_target.replace(hour=hour, minute=0, second=0, microsecond=0)
                    end = start + timedelta(minutes=duration_minutes)
                    slot_id = f"slot_{start.strftime('%Y%m%d_%H%M')}"
                    if slot_id not in self.holds:
                        slots.append(
                            {
                                "slot_id": slot_id,
                                "start_time": start.isoformat(),
                                "end_time": end.isoformat(),
                                "timezone": "UTC",
                            }
                        )
        return slots[:6]

    def tool_create_tentative_interview_hold(self, **kwargs) -> Dict[str, Any]:
        data = TentativeHoldInput(**kwargs)
        hold_id = f"hold_{uuid.uuid4().hex[:8]}"
        hold_record = {
            "hold_id": hold_id,
            "slot_id": data.slot_id,
            "client_name": data.client_name,
            "job_id": data.job_id,
            "notes": data.notes,
            "status": "TENTATIVE",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.holds[data.slot_id] = hold_record
        return hold_record

    def tool_create_email_draft(self, **kwargs) -> Dict[str, Any]:
        data = EmailDraftInput(**kwargs)
        draft_id = f"draft_{uuid.uuid4().hex[:8]}"
        draft_record = {
            "draft_id": draft_id,
            "recipient": data.recipient,
            "subject": data.subject,
            "body": data.body,
            "category": data.category,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "DRAFT",
        }
        self.email_drafts[draft_id] = draft_record
        return draft_record


def create_workspace_mcp_server() -> WorkspaceMCPServer:
    return WorkspaceMCPServer()
