from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import EdgeEntityType, EdgeType


class ArgumentEdge(BaseModel):
    id: str = Field(..., description="Unique identifier (UUID)")
    run_id: str = Field(..., description="Reference to the parent run (UUID)")
    source_type: EdgeEntityType = Field(
        ..., description="Entity type of the source node"
    )
    source_id: str = Field(..., description="UUID of the source entity")
    target_type: EdgeEntityType = Field(
        ..., description="Entity type of the target node"
    )
    target_id: str = Field(..., description="UUID of the target entity")
    edge_type: EdgeType = Field(..., description="Relationship type")
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
