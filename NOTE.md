# NOTE.md - mCTAgents Running Guide

> Step-by-step guide to run the mCTAgents project locally.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Quick Start (Automated)](#2-quick-start-automated)
3. [Manual Setup](#3-manual-setup)
4. [Running Services](#4-running-services)
5. [Using the Application](#5-using-the-application)
6. [Running Tests](#6-running-tests)
7. [API Usage Examples](#7-api-usage-examples)
8. [Troubleshooting](#8-troubleshooting)
9. [Service Ports Reference](#9-service-ports-reference)
10. [Useful Commands](#10-useful-commands)

---

## 1. Prerequisites

You need the following installed on your machine:

| Tool | Version | Install |
|------|---------|---------|
| **Docker** | 24+ | https://docs.docker.com/get-docker/ |
| **Docker Compose** | v2+ | Included with Docker Desktop |
| **Python** | 3.11+ | https://www.python.org/downloads/ |
| **Node.js** | 20+ | https://nodejs.org/ |
| **pnpm** | 8+ | `npm install -g pnpm` |
| **Go** | 1.22+ | https://go.dev/dl/ (optional, for Go services) |

Check what you have:
```bash
docker --version
docker compose version
python3 --version
node --version
pnpm --version
go version          # optional
```

---

## 2. Quick Start (Automated)

The fastest way to get everything running:

```bash
# Clone the repository
git clone https://github.com/anomalyco/mCTAgents.git
cd mCTAgents

# Run the automated setup (checks deps, starts infra, installs packages, seeds data)
bash scripts/setup-dev.sh

# Start all services with hot-reload
make dev
```

That's it! Skip to [Section 5](#5-using-the-application) to start using it.

---

## 3. Manual Setup

If you prefer step-by-step control:

### 3.1 Create Environment File

```bash
cp .env.example .env
```

Edit `.env` if you want to change ports or models. The defaults work for most setups.

### 3.2 Start Infrastructure Services

```bash
docker compose up -d postgres redis qdrant ollama
```

Wait ~15 seconds for services to become healthy. Check with:
```bash
docker compose ps
```

All 4 infrastructure services should show "healthy".

### 3.3 Pull Ollama Models

```bash
# Pull the chat/reasoning model
docker compose exec ollama ollama pull qwen2.5:7b

# Pull the reasoning model
docker compose exec ollama ollama pull deepseek-r1:7b

# Pull the embedding model
docker compose exec ollama ollama pull nomic-embed-text
```

**Note:** `qwen2.5:7b` is ~4.7GB, `deepseek-r1:7b` is ~4.7GB, `nomic-embed-text` is ~274MB.
The first pull takes time. Subsequent starts use cached models.

### 3.4 Seed Database with Demo Data

```bash
bash scripts/seed-demo.sh
```

This runs `scripts/init-db.sql` which creates 12 tables and inserts a demo reasoning session.

### 3.5 Start Application Services

```bash
# Start all services (builds Docker images first time)
docker compose up -d

# Or start with hot-reload for development
make dev
```

First build takes 5-10 minutes. Subsequent starts are fast.

---

## 4. Running Services

### Development Mode (with hot-reload)

```bash
make dev          # Foreground (see logs)
make dev-d        # Background (detached)
```

This uses `docker-compose.override.yml` which:
- Runs Go services with `go run` (auto-recompile)
- Runs Python services with `uvicorn --reload`
- Runs Next.js with `pnpm dev`

### Production Mode

```bash
docker compose up -d
```

This builds optimized Docker images and runs them without hot-reload.

### Check Service Status

```bash
docker compose ps           # Container status
docker compose logs -f      # Follow all logs
docker compose logs api-gateway  # Follow specific service
```

---

## 5. Using the Application

### Studio Frontend (Web UI)

Open: **http://localhost:3000**

1. Click "New Session"
2. Enter a problem statement (e.g., "Should we adopt microservices?")
3. Click "Start Reasoning"
4. Watch agents debate in real-time via the SSE event stream

### Playground (Alternative UI)

Open: **http://localhost:3001** (if running playground app)

### API Directly

```bash
# Health check
curl http://localhost:8080/health

# Create a run
curl -X POST http://localhost:8080/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"problem": "Should we adopt microservices?"}'
```

---

## 6. Running Tests

### All Tests

```bash
make test
```

### Python Tests (Reasoning Engine)

```bash
cd services/reasoning-engine
pip install -e ".[dev]"
pytest tests/unit/ -v           # Unit tests only
pytest tests/ -v                # All tests
pytest tests/unit/test_state_machine.py -v  # Single file
```

### Python Tests (Evidence Service)

```bash
cd services/evidence-service
pip install -e ".[dev]"
pytest tests/ -v
```

### Go Tests (API Gateway)

```bash
cd services/api-gateway
go test ./...
```

### Go Tests (Model Gateway)

```bash
cd services/model-gateway
go test ./...
```

### Frontend Tests

```bash
cd apps/studio
pnpm install
pnpm test
```

### Benchmark Tests

```bash
cd benchmarks
pip install -e .
pytest tests/ -v
pytest smoke/ -v
```

### Linting

```bash
make lint          # All linters
make lint-python   # Python only (ruff)
make lint-go       # Go only (golangci-lint)
```

---

## 7. API Usage Examples

### Create a Run

```bash
curl -X POST http://localhost:8080/v1/runs \
  -H "Content-Type: application/json" \
  -d '{
    "problem": "Should we migrate our monolith to microservices?",
    "mode": "balanced_reasoning",
    "budget": {
      "max_rounds": 2,
      "max_tokens": 12000,
      "max_model_calls": 16
    }
  }'
```

Response:
```json
{
  "run_id": "run_abc123",
  "status": "queued",
  "events_url": "/v1/runs/run_abc123/events"
}
```

### Stream Events (SSE)

```bash
curl -N http://localhost:8080/v1/runs/run_abc123/events
```

Events stream as:
```
event: run_started
data: {"event_id":"...","run_id":"run_abc123","type":"run_started","payload":{"problem":"..."}}

event: agent_started
data: {"event_id":"...","run_id":"run_abc123","type":"agent_started","agent_id":"architect","payload":{"phase":"claim_proposal"}}

event: claim_created
data: {"event_id":"...","run_id":"run_abc123","type":"claim_created","payload":{"claim_id":"c1","text":"..."}}
```

### Get Claims

```bash
curl http://localhost:8080/v1/runs/run_abc123/claims
```

### Get Evidence

```bash
curl http://localhost:8080/v1/runs/run_abc123/evidence
```

### Cancel a Run

```bash
curl -X POST http://localhost:8080/v1/runs/run_abc123/cancel
```

### Upload a Document

```bash
curl -X POST http://localhost:8080/v1/documents \
  -F "file=@research-paper.pdf"
```

### Search Evidence

```bash
curl -X POST http://localhost:8080/v1/search \
  -H "Content-Type: application/json" \
  -d '{"query": "microservices deployment frequency", "top_k": 5}'
```

---

## 8. Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -i :8080

# Change port in .env
echo "API_GATEWAY_PORT=9080" >> .env
```

### Docker Build Fails

```bash
# Clean Docker cache
docker compose down
docker system prune -f

# Rebuild from scratch
docker compose build --no-cache
```

### Ollama Models Not Available

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Pull models manually
docker compose exec ollama ollama pull qwen2.5:7b
docker compose exec ollama ollama pull nomic-embed-text
```

### Database Connection Refused

```bash
# Check PostgreSQL is healthy
docker compose ps postgres

# Check logs
docker compose logs postgres

# Restart PostgreSQL
docker compose restart postgres
```

### Reasoning Engine Won't Start

```bash
# Check logs for import errors
docker compose logs reasoning-engine

# Common fix: reinstall dependencies
cd services/reasoning-engine
pip install -e ".[dev]"
```

### Studio Shows "Disconnected"

1. Check API Gateway is running: `curl http://localhost:8080/health`
2. Check the `NEXT_PUBLIC_API_URL` env var matches the gateway port
3. Open browser dev tools → Network tab → check SSE connection

---

## 9. Service Ports Reference

| Service | Port | URL |
|---------|------|-----|
| **API Gateway** | 8080 | http://localhost:8080 |
| **Reasoning Engine** | 8000 | http://localhost:8000 |
| **Evidence Service** | 8001 | http://localhost:8001 |
| **Model Gateway** | 8090 | http://localhost:8090 |
| **Studio Frontend** | 3000 | http://localhost:3000 |
| **Playground** | 3001 | http://localhost:3001 |
| **PostgreSQL** | 5432 | localhost:5432 |
| **Redis** | 6379 | localhost:6379 |
| **Qdrant** | 6333 | http://localhost:6333 |
| **Ollama** | 11434 | http://localhost:11434 |

---

## 10. Useful Commands

### Docker

```bash
make dev                  # Start all with hot-reload
make dev-d                # Start all in background
make docker-up            # Start without hot-reload
make docker-down          # Stop all services
make docker-restart       # Restart all services
make docker-logs          # Follow all logs
make docker-ps            # Show container status
```

### Testing

```bash
make test                 # Run all tests
make test-reasoning       # Python reasoning engine tests
make test-api-gateway     # Go API gateway tests
make test-studio          # Frontend tests
make test-evidence        # Evidence service tests
make test-benchmarks      # Benchmark tests
```

### Linting & Formatting

```bash
make lint                 # Run all linters
make lint-python          # Python linting (ruff)
make lint-typescript      # TypeScript linting
make lint-go              # Go linting
make format               # Format all code
make typecheck            # Type check all
```

### Benchmarks

```bash
make benchmark-smoke      # Quick smoke test
make benchmark-full       # Full benchmark suite
```

### Database

```bash
make seed-demo            # Seed demo data
make migrate              # Run migrations
```

### Build

```bash
make build                # Build all packages
make build-protocol       # Build core protocol types
make build-studio         # Build Next.js frontend
make build-api-gateway    # Build Go API gateway binary
```

### Cleanup

```bash
make clean                # Remove __pycache__, node_modules, .next, etc.
```

### Python SDK Usage

```python
from mctagents_sdk import MCTAgentsClient

client = MCTAgentsClient(base_url="http://localhost:8080")

# Create and stream a run
run = client.create_run(problem="Should we adopt microservices?")
for event in client.stream_events(run.run_id):
    print(f"[{event.type}] {event.payload}")
    if event.type == "run_completed":
        break
```

### TypeScript SDK Usage

```typescript
import { MCTAgentsClient } from '@mctagents/ts-sdk';

const client = new MCTAgentsClient({ baseUrl: 'http://localhost:8080' });

const run = await client.runs.create({ problem: 'Should we adopt microservices?' });

for await (const event of client.runs.stream(run.run_id)) {
  console.log(`[${event.type}]`, event.payload);
  if (event.type === 'run_completed') break;
}
```

---

## Architecture Recap

```
Client (Studio/SDK)
    │
    ▼
API Gateway (:8080) ─── Go, REST + SSE
    │
    ├──▶ Reasoning Engine (:8000) ─── Python, 6 Agents + State Machine
    │        │
    │        ├──▶ Model Gateway (:8090) ─── Go, Ollama proxy
    │        │        │
    │        │        └──▶ Ollama (:11434) ─── Local LLM inference
    │        │
    │        └──▶ Evidence Service (:8001) ─── Python, vector search
    │                 │
    │                 └──▶ Qdrant (:6333) ─── Vector database
    │
    └──▶ PostgreSQL (:5432) ─── Primary database
```
