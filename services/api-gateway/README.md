# API Gateway

Go service providing the REST/SSE API for mCTAgents.

## Overview

The API gateway acts as the entry point for all client requests, proxying to the reasoning engine and evidence service backends.

## Architecture

```
internal/
├── config/         Environment-based configuration
├── handlers/       HTTP handlers with backend proxying
├── server/         Chi router setup
└── streaming/      SSE hub for event streaming
```

## Development

```bash
# Build
go build ./...

# Test
go test ./...

# Lint
go vet ./...
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/v1/runs` | Create a reasoning run |
| `GET` | `/v1/runs/{id}` | Get run details |
| `GET` | `/v1/runs/{id}/events` | Stream events (SSE) |
| `POST` | `/v1/runs/{id}/cancel` | Cancel a run |
| `GET` | `/v1/runs/{id}/claims` | List claims |
| `GET` | `/v1/runs/{id}/evidence` | List evidence |
| `GET` | `/v1/runs/{id}/claim-graph` | Get full claim graph |
| `POST` | `/v1/documents` | Upload a document |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LISTEN_ADDR` | `:8080` | Listen address |
| `REASONING_ENGINE_URL` | `http://localhost:8000` | Backend reasoning engine |
| `EVIDENCE_SERVICE_URL` | `http://localhost:8001` | Backend evidence service |
| `LOG_LEVEL` | `info` | Log level |
