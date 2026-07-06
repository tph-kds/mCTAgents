from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class RiskItem(BaseModel):
    description: str
    severity: str = Field(default="medium")
    mitigation: str | None = None


class FinalAnswer(BaseModel):
    id: str = Field(..., description="Unique identifier (UUID)")
    run_id: str = Field(..., description="Reference to the parent run (UUID)")
    answer_text: str = Field(..., description="Synthesized final answer")
    accepted_claim_ids: list[str] = Field(
        default_factory=list, description="Claims referenced by this answer (UUID)",
    )
    rejected_alternatives: list[dict[str, Any]] = Field(
        default_factory=list, description="Rejected alternative answers",
    )
    risks: list[RiskItem] = Field(
        default_factory=list, description="Remaining risks",
    )
    next_steps: list[str] = Field(
        default_factory=list, description="Recommended next steps",
    )
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
