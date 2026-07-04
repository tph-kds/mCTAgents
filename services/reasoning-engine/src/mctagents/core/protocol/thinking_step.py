from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ThinkingStep(BaseModel):
    """A single reasoning step within an agent's thinking process."""

    step_type: str = Field(
        ...,
        description="Type of step: reasoning, tool_call, tool_result, observation",
    )
    content: str = Field(
        ...,
        description="Text content of this thinking step",
    )
    agent_id: str = Field(
        ...,
        description="Identifier of the agent performing this step",
    )
    tool_name: str | None = Field(
        default=None,
        description="Name of the tool being called, if step_type is tool_call",
    )
    tool_args: dict[str, Any] | None = Field(
        default=None,
        description="Arguments passed to the tool, if step_type is tool_call",
    )
    duration_ms: int | None = Field(
        default=None,
        description="Duration of this step in milliseconds, if measurable",
    )
    sequence: int = Field(
        default=0,
        description="Sequence number within the agent's thinking process",
    )
