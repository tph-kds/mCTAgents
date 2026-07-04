import pytest
from mctagents.core.protocol.thinking_step import ThinkingStep


def test_thinking_step_creation():
    step = ThinkingStep(
        step_type="reasoning",
        content="Analyzing the claim structure...",
        agent_id="architect_agent",
    )
    assert step.step_type == "reasoning"
    assert step.content == "Analyzing the claim structure..."
    assert step.agent_id == "architect_agent"
    assert step.tool_name is None
    assert step.tool_args is None
    assert step.duration_ms is None


def test_thinking_step_tool_call():
    step = ThinkingStep(
        step_type="tool_call",
        content="Searching for evidence...",
        agent_id="evidence_agent",
        tool_name="vector_search",
        tool_args={"query": "microservices security", "top_k": 5},
    )
    assert step.tool_name == "vector_search"
    assert step.tool_args == {"query": "microservices security", "top_k": 5}
