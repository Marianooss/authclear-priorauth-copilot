"""
a2a_agent/models.py — A2A Agent task models

Pydantic models for task lifecycle and A2A protocol.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel, Field

from shared.models.prior_auth import PriorAuthDraft


class TaskState(str, Enum):
    """Task lifecycle states."""

    SUBMITTED = "submitted"
    WORKING = "working"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    NEEDS_CLARIFICATION = "needs_clarification"


class TaskInput(BaseModel):
    """Input data for a prior auth task."""

    fhir_bundle: dict
    requested_item: str
    payer: str = "generic"
    urgency: str = "standard"  # standard | urgent | emergency
    submitter_npi: str | None = None
    additional_context: str | None = None  # For multi-turn continuation


class TaskMessage(BaseModel):
    """A message in the task conversation."""

    role: str  # user | agent
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Task(BaseModel):
    """
    A prior authorization task.

    Represents the full lifecycle of a prior auth request from submission to completion.
    """

    id: str
    state: TaskState = TaskState.SUBMITTED
    input: TaskInput | None = None  # Set by handler after parsing message
    messages: list[TaskMessage] = Field(default_factory=list)
    result: PriorAuthDraft | None = None
    error: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime

    def __init__(self, **data):
        """Initialize task with expiration time."""
        if "expires_at" not in data:
            from a2a_agent.config import settings
            data["expires_at"] = datetime.utcnow() + timedelta(hours=settings.task_ttl_hours)
        super().__init__(**data)

    class Config:
        json_schema_extra = {
            "example": {
                "id": "task-abc123",
                "state": "completed",
                "input": {
                    "fhir_bundle": {"resourceType": "Bundle"},
                    "requested_item": "Ozempic",
                    "payer": "generic"
                },
                "messages": [
                    {
                        "role": "user",
                        "content": "Please generate prior auth for Ozempic",
                        "timestamp": "2024-03-30T12:00:00Z"
                    }
                ]
            }
        }


class SendTaskRequest(BaseModel):
    """
    POST /tasks/send request body.

    Conforms to A2A protocol specification.
    """

    id: str | None = None  # None = new task, str = continue existing
    message: TaskMessage

    class Config:
        json_schema_extra = {
            "example": {
                "message": {
                    "role": "user",
                    "content": '{"fhir_bundle": {...}, "requested_item": "Ozempic", "payer": "generic"}'
                }
            }
        }


class SendTaskResponse(BaseModel):
    """
    POST /tasks/send response body.

    Conforms to A2A protocol specification.
    """

    task: Task

    class Config:
        json_schema_extra = {
            "example": {
                "task": {
                    "id": "task-abc123",
                    "state": "working",
                    "created_at": "2024-03-30T12:00:00Z"
                }
            }
        }
