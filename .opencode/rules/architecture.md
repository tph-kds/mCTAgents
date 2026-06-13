# Architecture Rules

## Core Principles

1. **Claim-Centered:** All reasoning revolves around Claims, not messages
2. **Structured Objects:** Never pass raw strings; always use typed objects
3. **Local-First:** Ollama is the default model provider
4. **Event-Driven:** Use SSE for real-time streaming to UI
5. **Inspectable:** All reasoning steps must be traceable
6. **Protocol-First:** Core protocol schemas are the source of truth

## Protocol Objects

All agents must operate on these structured objects:
- `ProblemFrame` - Defines what agents are solving
- `Claim` - A proposition that can be supported/attacked/revised
- `Evidence` - Source-backed support or attack item
- `Objection` - A challenge against a claim
- `Revision` - A claim improvement from objections/evidence
- `Decision` - Judge output selecting accepted/rejected claims
- `FinalAnswer` - Synthesized answer referencing accepted claims

## Workflow

1. User submits problem
2. API creates run
3. Reasoning engine frames problem
4. Architect agent proposes claims
5. Evidence agent attaches evidence or marks unsupported
6. Critic agent creates objections
7. Architect revises claims
8. Judge scores and accepts/rejects claims
9. Synthesizer creates final answer
10. UI streams events and shows timeline

## Required Invariants

1. Final answers must reference accepted claims
2. High-confidence claims need evidence or explicit uncertainty
3. Every rejected claim needs a rejection reason
4. Every revision must link old claim and new claim
5. Every tool result must be traceable to a tool call
6. Every final answer must declare remaining risks

## Service Boundaries

- **API Gateway (Go):** HTTP routing, authentication, rate limiting
- **Reasoning Engine (Python):** CCSR workflow, agent orchestration
- **Model Gateway:** Provider abstraction (Ollama, OpenAI-compatible)
- **Evidence Service (Python):** Document retrieval, RAG
- **Core Protocol:** JSON schemas, TypeScript types

## Data Flow

```
Client -> API Gateway -> Reasoning Engine -> Model Gateway
                |              |
                v              v
            Postgres        Ollama
                |
                v
            SSE Events -> Studio UI
```
