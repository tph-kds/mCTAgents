# Reasoning Engine

Python service implementing the CCSR agent workflow.

## Overview

The reasoning engine orchestrates 6 specialized AI agents through a state machine to produce transparent, evidence-backed answers.

## Architecture

```
src/mctagents/
├── core/protocol/     Pydantic models + invariant validators
├── engine/            State machine, debate controller, orchestrator
├── agents/            6 agent implementations
├── services/          Event, storage, and evidence services
└── api/               FastAPI REST API
```

## Development

```bash
# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/unit/ -v

# Lint
ruff check src/
ruff format src/

# Type check
mypy src/
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/v1/runs` | Create a reasoning run |
| `GET` | `/v1/runs/{id}` | Get run status |
| `GET` | `/v1/runs/{id}/events` | Stream events (SSE) |
| `POST` | `/v1/runs/{id}/cancel` | Cancel a run |
| `GET` | `/v1/runs/{id}/claims` | List claims |
| `GET` | `/v1/runs/{id}/evidence` | List evidence |

## Configuration

Environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `DATABASE_URL` | `postgres://...` | PostgreSQL connection |
| `DEFAULT_CHAT_MODEL` | `qwen2.5:7b` | Chat model name |
| `DEFAULT_REASONING_MODEL` | `deepseek-r1:7b` | Reasoning model |
