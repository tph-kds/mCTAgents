"""Pydantic AI runtime adapter for mCTAgents.

Provides two integration patterns:
1. Use mCTAgents as a Pydantic AI tool (run CCSR workflow from Pydantic AI)
2. Use Pydantic AI agents inside mCTAgents (wrap Pydantic AI agents as CCSR agents)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from mctagents_sdk import MCTAgentsClient, ReasoningEvent


@dataclass
class MCTAgentsToolConfig:
    """Configuration for the mCTAgents Pydantic AI tool."""

    api_url: str = "http://localhost:8080"
    api_key: str | None = None
    mode: str = "balanced_reasoning"


class MCTAgentsTool:
    """Pydantic AI tool that runs the mCTAgents CCSR workflow.

    Usage:
        from mctagents_runtimes.pydantic_ai import MCTAgentsTool

        tool = MCTAgentsTool(api_url="http://localhost:8080")

        # Use in a Pydantic AI agent
        result = await tool.run("Should we adopt microservices?")
        print(result["claims"])
    """

    def __init__(self, config: MCTAgentsToolConfig | None = None, **kwargs: Any) -> None:
        if config is None:
            config = MCTAgentsToolConfig(**kwargs)
        self._config = config
        self._client = MCTAgentsClient(
            base_url=config.api_url,
            api_key=config.api_key,
        )

    async def run(
        self,
        problem: str,
        mode: str | None = None,
        budget: dict[str, int] | None = None,
    ) -> dict[str, Any]:
        """Run the mCTAgents CCSR workflow on a problem.

        Args:
            problem: The problem statement to reason about.
            mode: Reasoning mode override.
            budget: Resource budget override.

        Returns:
            Dict with run_id, claims, events, and status.
        """
        run = self._client.create_run(
            problem=problem,
            mode=mode or self._config.mode,
            budget=budget,
        )

        events: list[ReasoningEvent] = []
        for event in self._client.stream_events(run.run_id):
            events.append(event)
            if event.type in ("run_completed", "run_failed"):
                break

        claims = self._client.get_claims(run.run_id)

        return {
            "run_id": run.run_id,
            "claims": claims,
            "events": [
                {"type": e.type, "agent_id": e.agent_id, "payload": e.payload}
                for e in events
            ],
            "status": "completed" if events and events[-1].type == "run_completed" else "failed",
        }

    def close(self) -> None:
        """Close the underlying HTTP client."""
        self._client.close()

    def __enter__(self) -> MCTAgentsTool:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()
