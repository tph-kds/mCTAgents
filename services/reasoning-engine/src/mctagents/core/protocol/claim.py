from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import ClaimStatus, ClaimType, EvidenceStatus


class ClaimScores(BaseModel):
    logic: float = Field(default=0.0, ge=0.0, le=1.0)
    evidence: float = Field(default=0.0, ge=0.0, le=1.0)
    feasibility: float = Field(default=0.0, ge=0.0, le=1.0)
    critic_resistance: float = Field(default=0.0, ge=0.0, le=1.0)
    risk_adjusted: float = Field(default=0.0, ge=0.0, le=1.0)
    final: float = Field(default=0.0, ge=0.0, le=1.0)


class Claim(BaseModel):
    id: str = Field(..., description="Unique identifier (UUID)")
    run_id: str = Field(..., description="Reference to the parent run (UUID)")
    author_agent_id: str = Field(..., max_length=64)
    text: str = Field(..., description="The claim statement")
    claim_type: ClaimType = ClaimType.GENERAL
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    status: ClaimStatus = ClaimStatus.PROPOSED
    requires_evidence: bool = False
    evidence_status: EvidenceStatus = EvidenceStatus.UNSUPPORTED
    parent_claim_id: str | None = Field(
        default=None, description="UUID of the claim this is a revision of"
    )
    rejection_reason: str | None = None
    scores: ClaimScores | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
