# mCTAgents Runtime for Pydantic AI

## Installation

```bash
pip install mctagents-runtime-pydantic-ai
```

## Usage

### mCTAgents as a Pydantic AI Tool

```python
from mctagents_runtimes.pydantic_ai import MCTAgentsTool

tool = MCTAgentsTool(api_url="http://localhost:8080")

result = await tool.run(
    problem="Should we adopt microservices?",
    mode="balanced_reasoning",
)

print(f"Run ID: {result['run_id']}")
print(f"Claims: {len(result['claims'])}")
print(f"Status: {result['status']}")
```

### Context Manager

```python
with MCTAgentsTool(api_url="http://localhost:8080") as tool:
    result = await tool.run("Problem statement here")
    for claim in result["claims"]:
        print(f"  {claim['status']}: {claim['text']}")
```

### Configuration

```python
from mctagents_runtimes.pydantic_ai import MCTAgentsTool, MCTAgentsToolConfig

config = MCTAgentsToolConfig(
    api_url="http://localhost:8080",
    api_key="optional-api-key",
    mode="deep_deliberation",
)
tool = MCTAgentsTool(config=config)
```

## How It Works

1. Creates an mCTAgents run via the Python SDK
2. Streams all events until completion
3. Returns the run ID, claims, events, and status
4. Claims are returned as dicts matching the CCSR protocol schema
