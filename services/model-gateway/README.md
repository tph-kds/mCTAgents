# Model Gateway

Go service providing a unified interface to LLM providers.

## Overview

The model gateway abstracts different LLM providers (Ollama, OpenAI-compatible APIs) behind a single API, with circuit breaker protection and automatic failover.

## Development

```bash
go build ./...
go test ./...
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/v1/chat` | Chat completion |
| `POST` | `/v1/chat/stream` | Streaming chat completion |
| `POST` | `/v1/embed` | Generate embeddings |
| `GET` | `/v1/models` | List available models |
