# Agent Development Skill

## Purpose

Build and test individual agents for the CCSR workflow.

## When to Use

- Creating a new agent role
- Modifying agent behavior
- Testing agent responses
- Optimizing agent prompts

## Agent Structure

```python
from pydantic import BaseModel
from typing import Protocol

class Agent(Protocol):
    name: str
    role: str
    
    async def act(self, context: AgentContext) -> AgentResult:
        """Perform the agent's action."""
        ...
```

## Agent Context

```python
class AgentContext(BaseModel):
    run_id: str
    problem_frame: ProblemFrame
    claims: list[Claim]
    evidence: list[Evidence]
    objections: list[Objection]
    history: list[Event]
```

## Prompt Engineering

- Use structured prompts with clear role definition
- Include examples of expected output format
- Specify output schema explicitly
- Use few-shot learning for complex tasks

## Testing Agents

```python
import pytest

@pytest.mark.asyncio
async def test_architect_proposes_claims():
    engine = create_test_engine()
    frame = ProblemFrame(
        run_id="test",
        normalized_problem="Test problem"
    )
    
    claims = await engine.architect.propose(frame)
    
    assert len(claims) > 0
    assert all(c.status == "proposed" for c in claims)
```

## Model Selection

| Agent | Recommended Model |
|-------|------------------|
| Architect | qwen2.5:14b |
| Evidence | qwen2.5:14b |
| Critic | qwen2.5:14b |
| Judge | qwen2.5:14b |
| Synthesizer | qwen2.5:14b |

## Best Practices

1. Keep agent prompts focused and specific
2. Use structured output formats (JSON)
3. Validate outputs against protocol schemas
4. Log all agent actions for debugging
5. Test agents in isolation before integration
