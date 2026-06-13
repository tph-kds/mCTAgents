# Architecture Overview

## System Architecture

mCTAgents is a microservices-based system with the following components:

```
┌──────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Studio    │  │  Playground │  │  Python/TS SDK      │  │
│  │  (Next.js)  │  │  (Next.js)  │  │  (Client Library)   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │                │                    │
          ▼                ▼                    ▼
┌──────────────────────────────────────────────────────────────┐
│                      API Gateway (Go)                        │
│              REST API + SSE Event Streaming                  │
│              Port 8080                                       │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌─────────────────────┐    ┌──────────────────────────────────┐
│  Reasoning Engine   │    │       Evidence Service           │
│    (Python)         │    │         (Python)                 │
│  Port 8000          │    │       Port 8001                  │
│                     │    │                                  │
│  ┌───────────────┐  │    │  ┌──────────┐  ┌──────────────┐ │
│  │ State Machine │  │    │  │ Parser   │  │ Vector Store │ │
│  │ 6 Agents      │  │    │  │ Chunker  │  │ (Qdrant)     │ │
│  │ Debate Ctrl   │  │    │  │ Pipeline │  │ Scorer       │ │
│  └───────────────┘  │    │  └──────────┘  └──────────────┘ │
└──────────┬──────────┘    └──────────┬───────────────────────┘
           │                          │
           ▼                          ▼
┌─────────────────────┐    ┌──────────────────────┐
│   Model Gateway     │    │     PostgreSQL       │
│     (Go)            │    │   Port 5432          │
│   Port 8090         │    │   12 tables          │
│                     │    └──────────────────────┘
│  ┌───────────────┐  │
│  │ Ollama        │  │    ┌──────────────────────┐
│  │ OpenAI-compat │  │    │      Redis           │
│  │ Circuit Break │  │    │   Port 6379          │
│  └───────────────┘  │    │   Event Bus          │
└─────────────────────┘    └──────────────────────┘
```

## Data Flow

1. **Client** sends a problem statement to **API Gateway**
2. **API Gateway** forwards to **Reasoning Engine**
3. **Reasoning Engine** runs the CCSR workflow:
   - ProblemFramer normalizes the input
   - Architect proposes claims
   - EvidenceAgent attaches evidence (calls Evidence Service)
   - Critic raises objections
   - Judge evaluates and decides
   - Synthesizer produces final answer
4. **Events** stream back via SSE through API Gateway to Client
5. **All objects** are persisted to PostgreSQL

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| API Gateway language | Go | High throughput, low latency for SSE streaming |
| Reasoning Engine language | Python | Rich AI/ML ecosystem, Pydantic for validation |
| Vector store | Qdrant | Easy setup, good performance, open source |
| Database | PostgreSQL | Structured data, JSONB for flexible fields |
| Event streaming | SSE | Simple, browser-native, no extra infrastructure |
| Model provider | Ollama (default) | Local-first, no API keys required |

## Service Communication

- **API Gateway → Reasoning Engine**: HTTP REST (synchronous)
- **API Gateway → Evidence Service**: HTTP REST (synchronous)
- **Reasoning Engine → Model Gateway**: HTTP REST (synchronous)
- **Reasoning Engine → Evidence Service**: HTTP REST (synchronous)
- **Client → API Gateway**: HTTP REST + SSE (streaming)

## Scalability

- **Stateless services** (API Gateway, Evidence Service) can scale horizontally
- **Reasoning Engine** is per-request (each run is independent)
- **PostgreSQL** can be replaced with a managed service
- **Redis** can be clustered for high availability
- **Qdrant** supports distributed deployment

## Resilience

- **Circuit breaker** in Model Gateway prevents cascade failures
- **Health checks** on all services
- **Graceful shutdown** with request draining
- **Retry logic** in SDK clients
