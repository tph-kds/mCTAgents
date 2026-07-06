"""Tests for ArchitectAgent thinking step emissions."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from mctagents.agents.architect import ArchitectAgent
from mctagents.agents.base import AgentContext
from mctagents.core.protocol import Claim, ClaimStatus, ClaimType


@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    provider.chat = AsyncMock(
        return_value=MagicMock(
            content='{"claims": [], "revisions": []}'
        )
    )
    return provider


@pytest.mark.asyncio
async def test_architect_emits_thinking_steps_on_propose(mock_provider):
    agent = ArchitectAgent(model_provider=mock_provider)
    context = AgentContext(
        run_id="test-run",
        problem_frame=MagicMock(
            original_input="Test problem",
            normalized_problem="Test problem",
            constraints=["c1"],
            risk_level=MagicMock(value="medium"),
            domain="test",
        ),
        claims=[],
        evidence=[],
        objections=[],
    )

    result = await agent.act(context)

    assert len(result.thinking_steps) > 0
    assert any(s.step_type == "reasoning" for s in result.thinking_steps)
    step_contents = [s.content for s in result.thinking_steps]
    assert any("Analyzing problem" in c for c in step_contents)
    assert any("propose" in c.lower() for c in step_contents)


@pytest.mark.asyncio
async def test_architect_emits_thinking_steps_on_revise(mock_provider):
    agent = ArchitectAgent(model_provider=mock_provider)
    challenged_claim = Claim(
        id="claim-1",
        run_id="test-run",
        author_agent_id="architect_agent",
        text="Challenged claim",
        claim_type=ClaimType.GENERAL,
        confidence=0.5,
        status=ClaimStatus.CHALLENGED,
        requires_evidence=False,
    )
    context = AgentContext(
        run_id="test-run",
        problem_frame=MagicMock(
            original_input="Test problem",
            normalized_problem="Test problem",
            constraints=[],
            risk_level=MagicMock(value="medium"),
            domain="test",
        ),
        claims=[challenged_claim],
        evidence=[],
        objections=[],
    )

    result = await agent.act(context)

    assert len(result.thinking_steps) > 0
    step_contents = [s.content for s in result.thinking_steps]
    assert any("Analyzing problem" in c for c in step_contents)
    assert any("revise" in c.lower() for c in step_contents)


@pytest.mark.asyncio
async def test_thinking_steps_have_sequence_numbers(mock_provider):
    agent = ArchitectAgent(model_provider=mock_provider)
    context = AgentContext(
        run_id="test-run",
        problem_frame=MagicMock(
            original_input="Test problem",
            normalized_problem="Test problem",
            constraints=[],
            risk_level=MagicMock(value="medium"),
            domain="test",
        ),
        claims=[],
        evidence=[],
        objections=[],
    )

    result = await agent.act(context)

    sequences = [s.sequence for s in result.thinking_steps]
    assert sequences == list(range(len(result.thinking_steps)))


@pytest.mark.asyncio
async def test_thinking_steps_include_agent_id(mock_provider):
    agent = ArchitectAgent(model_provider=mock_provider)
    context = AgentContext(
        run_id="test-run",
        problem_frame=MagicMock(
            original_input="Test problem",
            normalized_problem="Test problem",
            constraints=[],
            risk_level=MagicMock(value="medium"),
            domain="test",
        ),
        claims=[],
        evidence=[],
        objections=[],
    )

    result = await agent.act(context)

    for step in result.thinking_steps:
        assert step.agent_id == "architect_agent"
