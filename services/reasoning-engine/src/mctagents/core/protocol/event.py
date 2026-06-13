from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import EventType


class Event(BaseModel):
    id: str = Field(..., description="Unique identifier (UUID)")
    event_id: str = Field(
        ..., max_length=128, description="Unique event identifier for idempotency"
    )
    run_id: str = Field(..., description="Reference to the parent run (UUID)")
    sequence: int = Field(..., ge=0, description="Monotonic sequence within the run")
    type: EventType
    agent_id: str | None = Field(default=None, max_length=64)
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
