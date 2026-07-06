from pydantic import BaseModel, Field

from .enums import EvidencePolicy, RunMode


class DebatePolicy(BaseModel):
    mode: RunMode = RunMode.BALANCED_REASONING
    evidence_policy: EvidencePolicy = EvidencePolicy.REQUIRED_FOR_MAJOR_CLAIMS
    max_rounds: int = Field(default=3, ge=1, le=20)
    max_claims: int = Field(default=50, ge=1)
    max_evidence_per_claim: int = Field(default=5, ge=0)
    max_objections_per_claim: int = Field(default=3, ge=0)
    max_revisions_per_claim: int = Field(default=2, ge=0)
    confidence_threshold_for_acceptance: float = Field(
        default=0.7, ge=0.0, le=1.0,
    )
    confidence_threshold_for_rejection: float = Field(
        default=0.3, ge=0.0, le=1.0,
    )
    escalation_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Confidence below which claims are escalated for more debate",
    )
    require_evidence_for_high_risk: bool = True
    allow_self_revision: bool = True
    adversarial_depth: int = Field(
        default=2, ge=0, le=5, description="Max depth of attack/counter-attack",
    )
