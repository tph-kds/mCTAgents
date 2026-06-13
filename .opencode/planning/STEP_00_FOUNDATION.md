# STEP 0: Project Foundation

**Timeline:** Days 1-5 | **Complexity:** 3/5 | **Dependencies:** None

## Goal

Create the monorepo skeleton, tooling configuration, and database schema that every subsequent step builds upon.

## What to Build

### Monorepo Structure
```
mctagents/
├── Makefile                    # Unified dev commands
├── docker-compose.yml          # PostgreSQL, Redis, Qdrant, Ollama
├── docker-compose.override.yml # Dev overrides
├── .env.example                # Environment template
├── packages/core-protocol/     # JSON schemas + TypeScript types
├── services/api-gateway/       # Go REST/SSE API
├── services/reasoning-engine/  # Python agent workflow
├── services/model-gateway/     # Go provider abstraction
├── services/evidence-service/  # Python document retrieval
├── apps/studio/                # Next.js frontend
├── deployments/                # Docker Compose, K8s
├── scripts/                    # Utility scripts
└── docs/                       # Documentation
```

### Database Schema (12 Tables)
- `runs` - Social reasoning sessions
- `problem_frames` - Normalized problem definitions
- `claims` - Propositions (the core object)
- `argument_edges` - Relationships between objects
- `evidence` - Source-backed support/attack items
- `objections` - Challenges against claims
- `revisions` - Claim improvements
- `decisions` - Judge accept/reject output
- `final_answers` - Synthesized answers
- `events` - Immutable event log
- `documents` + `document_chunks` - For evidence retrieval
- `audit_logs` + `traces` - Observability

### Infrastructure Services
- PostgreSQL 16 (structured data + JSONB)
- Redis 7 (caching, event bus)
- Qdrant (vector search)
- Ollama (local-first LLM inference)

## Makefile Commands
```bash
make dev           # Start all services
make test          # Run all tests
make lint          # Run all linters
make seed-demo     # Populate demo data
make docker-up     # Start Docker Compose
make docker-down   # Stop Docker Compose
```

## Success Criteria
- [ ] `make docker-up` starts all 4 services
- [ ] All healthchecks pass within 30 seconds
- [ ] `make seed-demo` populates sample data
- [ ] `make lint` passes on all services
- [ ] All JSON schemas are valid JSON Schema Draft 2020-12

## Tech Choices
| Component | Choice | Why |
|-----------|--------|-----|
| Monorepo | Makefile + Docker Compose | Simple, no heavy tooling |
| Database | PostgreSQL 16 | Structured data, JSONB, proven |
| Cache | Redis 7 | Lightweight, sufficient for MVP |
| Vector DB | Qdrant | Open-source, easy Docker deployment |
| LLM | Ollama | Local-first, zero API costs |
| Python pkg | pyproject.toml + uv | Modern, fast |
| Node.js | pnpm workspaces | Efficient monorepo management |
