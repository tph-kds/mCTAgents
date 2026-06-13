from datetime import datetime

from pydantic import BaseModel, Field

from .enums import RiskLevel


class ProblemFrame(BaseModel):
    id: str = Field(..., description="Unique identifier (UUID)")
    run_id: str = Field(..., description="Reference to the parent run (UUID)")
    original_input: str = Field(..., description="Raw user input")
    normalized_problem: str = Field(..., description="Cleaned problem statement")
    constraints: list[str] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    domain: str | None = Field(default=None, max_length=64)
    requires_business_decision: bool = False
    requires_research: bool = False
    requires_code: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
