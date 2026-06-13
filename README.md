# mCTAgents

> An open-source social reasoning engine where a society of AI agents debate, challenge, and refine claims to produce transparent, evidence-backed answers.

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![CI](https://github.com/anomalyco/mCTAgents/actions/workflows/ci.yml/badge.svg)](https://github.com/anomalyco/mCTAgents/actions)

## What is mCTAgents?

mCTAgents implements a **Claim-Centered Social Reasoning (CCSR)** protocol. Instead of a single AI model answering questions, a society of specialized agents collaboratively:

1. **Frame** the problem and identify key dimensions
2. **Propose** structured claims with confidence scores
3. **Attach** evidence from documents and knowledge bases
4. **Challenge** weak reasoning through adversarial debate
5. **Revise** claims based on objections
6. **Synthesize** a final, auditable answer

This produces reasoning that is **transparent**, **inspectable**, and **reproducible**.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Studio    │────▶│  API Gateway │────▶│   Reasoning  │
│  (Next.js)  │◀────│    (Go)      │◀────│    Engine    │
└─────────────┘     └──────────────┘     │   (Python)   │
                                          └──────┬───────┘
                                                 │
                    ┌────────────────────────────┼────────────────────┐
                    │                            │                    │
              ┌─────▼─────┐              ┌───────▼───────┐    ┌──────▼──────┐
              │   Model   │              │   Evidence    │    │  PostgreSQL │
              │  Gateway  │              │   Service     │    │   + Qdrant  │
              │   (Go)    │              │   (Python)    │    │             │
              └─────┬─────┘              └───────────────┘    └─────────────┘
                    │
              ┌─────▼─────┐
              │   Ollama  │
              │  (Local)  │
              └───────────┘
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Ollama (for local LLM inference)

### 1. Start everything

```bash
make dev
```

This starts all services with hot-reload for development.

### 2. Pull required models

```bash
ollama pull qwen2.5:7b
ollama pull deepseek-r1:7b
ollama pull nomic-embed-text
```

### 3. Open the Studio

Navigate to [http://localhost:3000](http://localhost:3000) to start a reasoning session.

### 4. Create a run via API

```bash
curl -X POST http://localhost:8080/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"problem": "Should we adopt microservices for our payment system?"}'
```

## Project Structure

```
mctagents/
├── apps/studio/               Next.js frontend
├── services/
│   ├── api-gateway/           Go REST/SSE API
│   ├── reasoning-engine/      Python agent workflow
│   ├── model-gateway/         Go model provider abstraction
│   └── evidence-service/      Python document retrieval
├── packages/
│   ├── core-protocol/         JSON schemas + TypeScript types
│   ├── ts-sdk/                TypeScript SDK
│   └── py-sdk/                Python SDK
├── benchmarks/                Evaluation benchmarks
├── examples/                  Example use cases
├── deployments/               K8s, Helm configs
└── scripts/                   Utility scripts
```

## Agent Roles

| Agent | Role | Responsibility |
|-------|------|----------------|
| **ProblemFramer** | Problem Analyst | Normalizes input, identifies constraints, sets risk level |
| **Architect** | Claim Proposer | Proposes structured claims with evidence requirements |
| **Evidence** | Researcher | Attaches evidence to claims, scores reliability |
| **Critic** | Adversarial Reviewer | Challenges weak claims, raises objections |
| **Judge** | Arbiter | Evaluates claims, decides acceptance/rejection |
| **Synthesizer** | Answer Compiler | Produces final answer from accepted claims |

## Development

### Running Tests

```bash
# All tests
make test

# Python tests only
pytest services/reasoning-engine/tests/
pytest services/evidence-service/tests/

# Go tests
cd services/api-gateway && go test ./...

# Benchmarks
make benchmark-smoke
```

### Linting

```bash
make lint
```

### Building

```bash
make build
```

## Configuration

Copy `.env.example` to `.env` and customize:

```bash
cp .env.example .env
```

Key settings:

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API endpoint |
| `DEFAULT_CHAT_MODEL` | `qwen2.5:7b` | Model for agent reasoning |
| `DEFAULT_EMBEDDING_MODEL` | `nomic-embed-text` | Model for text embeddings |
| `POSTGRES_PASSWORD` | `devpassword` | Database password |

## Protocol

The core protocol defines these structured objects:

- **ProblemFrame** - Normalized problem description
- **Claim** - A structured assertion with confidence and status
- **Evidence** - Supporting or attacking information
- **Objection** - A challenge to a claim
- **Revision** - A revised version of a claim
- **Decision** - Judge's acceptance/rejection decision
- **FinalAnswer** - Synthesized answer with risks

All objects are defined as JSON schemas in `packages/core-protocol/schemas/`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Apache License 2.0 - see [LICENSE](LICENSE)
