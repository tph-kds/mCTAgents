from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import Severity


class Objection(BaseModel):
    id: str = Field(..., description="Unique identifier (UUID)")
    run_id: str = Field(..., description="Reference to the parent run (UUID)")
    target_claim_id: str = Field(
        ..., description="Claim being objected to (UUID)"
    )
    author_agent_id: str = Field(..., max_length=64)
    reason: str = Field(..., description="Explanation of the objection")
    severity: Severity = Severity.MEDIUM
    requested_fix: str | None = Field(
        default=None, description="Suggested resolution"
    )
    resolved: bool = False
    resolution_claim_id: str | None = Field(
        default=None, description="Claim that resolves this objection (UUID)"
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
