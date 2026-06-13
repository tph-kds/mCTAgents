from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Decision(BaseModel):
    id: str = Field(..., description="Unique identifier (UUID)")
    run_id: str = Field(..., description="Reference to the parent run (UUID)")
    accepted_claim_ids: list[str] = Field(
        default_factory=list, description="Claims accepted by the judge"
    )
    rejected_claim_ids: list[str] = Field(
        default_factory=list, description="Claims rejected by the judge"
    )
    uncertain_claim_ids: list[str] = Field(
        default_factory=list, description="Claims with uncertain verdict"
    )
    score_breakdown: dict[str, Any] = Field(
        default_factory=dict, description="Per-claim score details"
    )
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    needs_more_debate: bool = False
    extra_debate_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
