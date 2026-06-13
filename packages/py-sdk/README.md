# Python SDK

Client library for the mCTAgents API.

## Installation

```bash
pip install mctagents-sdk
```

## Usage

```python
from mctagents_sdk import MCTAgentsClient

client = MCTAgentsClient(base_url="http://localhost:8080")

# Create a run
run = client.create_run(problem="Should we adopt microservices?")

# Stream events
for event in client.stream_events(run.run_id):
    print(f"[{event.type}] {event.payload}")
    if event.type == "run_completed":
        break

# Get claims
claims = client.get_claims(run.run_id)
```

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
```
