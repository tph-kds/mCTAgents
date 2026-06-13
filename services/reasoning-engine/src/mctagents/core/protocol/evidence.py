from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import SourceType


class Evidence(BaseModel):
    id: str = Field(..., description="Unique identifier (UUID)")
    run_id: str = Field(..., description="Reference to the parent run (UUID)")
    source_type: SourceType
    source_ref: str | None = Field(
        default=None, description="Reference URI or path to the source"
    )
    summary: str = Field(..., description="Brief summary of the evidence")
    full_text: str | None = Field(default=None, description="Full text content")
    reliability_score: float = Field(default=0.5, ge=0.0, le=1.0)
    source_authority: float | None = Field(default=None, ge=0.0, le=1.0)
    recency: float | None = Field(default=None, ge=0.0, le=1.0)
    specificity: float | None = Field(default=None, ge=0.0, le=1.0)
    independence: float | None = Field(default=None, ge=0.0, le=1.0)
    retrieval_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    chunk_id: str | None = Field(
        default=None, description="Reference to document chunk (UUID)"
    )
    document_id: str | None = Field(
        default=None, description="Reference to source document (UUID)"
    )
    supports_claim_ids: list[str] = Field(
        default_factory=list, description="Claim IDs this evidence supports"
    )
    attacks_claim_ids: list[str] = Field(
        default_factory=list, description="Claim IDs this evidence attacks"
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
