from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import EvidencePolicy, RunMode, RunStatus


class BudgetConfig(BaseModel):
    max_claims: int | None = Field(default=None, ge=1)
    max_evidence_per_claim: int | None = Field(default=None, ge=0)
    max_objections_per_claim: int | None = Field(default=None, ge=0)
    max_revisions_per_claim: int | None = Field(default=None, ge=0)
    max_rounds: int | None = Field(default=None, ge=1)
    token_budget: int | None = Field(default=None, ge=0)
    time_budget_seconds: int | None = Field(default=None, ge=0)


class Run(BaseModel):
    id: str = Field(..., description="Unique identifier (UUID)")
    tenant_id: str = Field(
        default="00000000-0000-0000-0000-000000000000",
        description="Tenant UUID",
    )
    status: RunStatus = RunStatus.QUEUED
    mode: RunMode = RunMode.BALANCED_REASONING
    evidence_policy: EvidencePolicy = EvidencePolicy.REQUIRED_FOR_MAJOR_CLAIMS
    budget_config: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None
