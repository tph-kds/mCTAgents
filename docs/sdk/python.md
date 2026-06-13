# Python SDK

## Installation

```bash
pip install mctagents-sdk
```

## Quick Start

```python
from mctagents_sdk import MCTAgentsClient

client = MCTAgentsClient(base_url="http://localhost:8080")

# Create a reasoning run
run = client.create_run(
    problem="Should we adopt microservices?",
    mode="balanced_reasoning",
)

print(f"Run created: {run.run_id}")

# Stream events
for event in client.stream_events(run.run_id):
    print(f"[{event.type}] {event.agent_id or 'system'}")

    if event.type == "run_completed":
        break

# Get final claims
claims = client.get_claims(run.run_id)
for claim in claims:
    print(f"  {claim['status']}: {claim['text'][:80]}...")
```

## Context Manager

```python
with MCTAgentsClient(base_url="http://localhost:8080") as client:
    run = client.create_run(problem="...")
    for event in client.stream_events(run.run_id):
        print(f"[{event.type}]")
        if event.type == "run_completed":
            break
# Client is automatically closed
```

## Configuration

```python
client = MCTAgentsClient(
    base_url="http://localhost:8080",  # Required
    api_key="optional-api-key",         # Optional
    timeout=60.0,                       # Request timeout in seconds
)
```

## API Methods

### `client.create_run(problem, mode, evidence_policy, budget)`

Create a new reasoning run. Returns a `Run` object.

### `client.get_run(run_id)`

Get run details. Returns a dict.

### `client.stream_events(run_id)`

Generator that yields `ReasoningEvent` objects.

### `client.get_claims(run_id)`

Get all claims for a run. Returns a list of dicts.

### `client.cancel_run(run_id)`

Cancel a running session.

## Error Handling

```python
import httpx

try:
    run = client.create_run(problem="...")
except httpx.HTTPStatusError as e:
    print(f"HTTP {e.response.status_code}: {e.response.text}")
except httpx.ConnectError:
    print("Cannot connect to server")
```
