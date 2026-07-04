from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from mctagents.core.protocol import (
    Claim,
    Evidence,
    Event,
    Objection,
    ProblemFrame,
    Revision,
)
from mctagents.core.protocol.thinking_step import ThinkingStep

if TYPE_CHECKING:
    from mctagents.services.model_gateway.base import ModelProvider


@dataclass
class AgentContext:
    """Shared state passed to every agent during a run."""

    run_id: str
    problem_frame: ProblemFrame | None = None
    claims: list[Claim] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    objections: list[Objection] = field(default_factory=list)
    revisions: list[Revision] = field(default_factory=list)
    debate_round: int = 0
    budget_remaining: dict[str, int] = field(
        default_factory=lambda: {"max_tokens": 12000}
    )
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass
class AgentResult:
    """Output produced by a single agent invocation."""

    agent_id: str
    claims: list[Claim] = field(default_factory=list)
    evidence: list[Evidence] = field(default_factory=list)
    objections: list[Objection] = field(default_factory=list)
    revisions: list[dict[str, str]] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    thinking_steps: list[ThinkingStep] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


class BaseAgent(ABC):
    """Abstract base for all CCSR agent roles."""

    agent_id: str = "base"
    role: str = "Base"
    capabilities: list[str] = []

    def __init__(self, model_provider: ModelProvider) -> None:
        self._model_provider = model_provider

    @abstractmethod
    async def act(self, context: AgentContext) -> AgentResult:
        ...

    def _build_messages(
        self, system_prompt: str, user_prompt: str
    ) -> list:
        from mctagents.services.model_gateway.base import ChatMessage

        return [
            ChatMessage(role="system", content=system_prompt),
            ChatMessage(role="user", content=user_prompt),
        ]
