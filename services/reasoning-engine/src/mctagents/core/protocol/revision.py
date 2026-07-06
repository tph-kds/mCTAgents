from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import RevisionType


class Revision(BaseModel):
    id: str = Field(..., description="Unique identifier (UUID)")
    run_id: str = Field(..., description="Reference to the parent run (UUID)")
    old_claim_id: str = Field(
        ..., description="Original claim before revision (UUID)",
    )
    new_claim_id: str = Field(
        ..., description="Revised claim after revision (UUID)",
    )
    reason: str = Field(..., description="Explanation of why the revision was made")
    revision_type: RevisionType = RevisionType.OBJECTION_DRIVEN
    improvement_score: float | None = Field(
        default=None, ge=0.0, le=1.0, description="Measured improvement",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
