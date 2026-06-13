# AGENTS.md

This file provides coding agent instructions for the mCTAgents repository.

## Project Overview

mCTAgents is an open-source social reasoning engine implementing a claim-centered
social reasoning protocol (CCSR). Agents operate on structured objects:
`ProblemFrame`, `Claim`, `Evidence`, `Objection`, `Revision`, `Decision`, `FinalAnswer`.

## Monorepo Structure

```
mctagents/
├── apps/studio/               Next.js frontend (TypeScript)
├── apps/playground/           Integration demo
├── services/api-gateway/      Go REST/SSE API
├── services/reasoning-engine/ Python agent workflow
├── services/model-gateway/    Go or Python provider abstraction
├── services/evidence-service/ Python document retrieval
├── packages/core-protocol/    JSON schemas + TypeScript types
├── packages/ts-sdk/           TypeScript SDK
├── packages/py-sdk/           Python SDK
├── runtimes/                  Runtime adapters (LangGraph, Pydantic AI, etc.)
├── examples/                  Example verticals
├── benchmarks/                Evaluation benchmarks
├── deployments/               Docker Compose, K8s, Helm
└── scripts/                   Utility scripts
```

## Build / Lint / Test Commands

### Development
```bash
make dev                    # Start all services locally via Docker Compose
make docker-up              # Start Docker Compose services
make docker-down            # Stop Docker Compose services
make seed-demo              # Seed database with demo data
```

### Testing
```bash
make test                   # Run all tests (unit + integration)
pytest                      # Run all Python tests
pytest tests/unit/          # Run unit tests only
pytest tests/integration/   # Run integration tests only
pytest tests/unit/test_schema.py          # Run single test file
pytest tests/unit/test_schema.py::test_claim_validation  # Run single test
pytest -x                   # Stop on first failure
pytest -v                   # Verbose output
pytest --tb=short           # Shorter tracebacks
```

### Linting / Formatting
```bash
make lint                   # Run all linters
ruff check .                # Lint Python files
ruff check --fix .          # Auto-fix lint issues
ruff format .               # Format Python files
black .                     # Alternative Python formatter
isort .                     # Sort Python imports
mypy .                      # Type check Python
```

### Frontend
```bash
cd apps/studio
npm run dev                 # Start Next.js dev server
npm run build               # Build for production
npm run lint                # Lint TypeScript/React
npm run typecheck           # Type check TypeScript
```

### Go Services
```bash
cd services/api-gateway
go build ./...               # Build Go service
go test ./...                # Run Go tests
go vet ./...                 # Go static analysis
```

### Benchmarks
```bash
make benchmark-smoke        # Quick smoke test
make benchmark-full         # Full benchmark suite
```

## Code Style Guidelines

### Python

**Formatter/Linter:** Ruff (replaces Black, isort, Flake8)
**Type Checker:** mypy
**Min Python Version:** 3.11+

- Use type hints on all function signatures
- Use Pydantic v2 models for data validation and schemas
- Follow PEP 8 with max line length of 88 characters
- Use `snake_case` for functions, variables, and module names
- Use `PascalCase` for classes
- Use `UPPER_SNAKE_CASE` for constants
- Prefer `pathlib.Path` over `os.path`
- Use `async/await` for I/O-bound operations
- Use dataclasses or Pydantic models, never raw dicts for structured data
- Import order: stdlib, third-party, local (enforced by isort/Ruff)

**Error Handling:**
- Use custom exception classes per service
- Never swallow exceptions silently
- Log exceptions with structured context
- Use `try/except` with specific exception types

### TypeScript / Next.js

**Formatter:** Prettier
**Linter:** ESLint
**Type Checker:** TypeScript strict mode

- Use `interface` for object shapes, `type` for unions/intersections
- Use `PascalCase` for components and types
- Use `camelCase` for functions and variables
- Use `UPPER_SNAKE_CASE` for constants
- Prefer named exports over default exports
- Use Zod for runtime schema validation
- Avoid `any` type; use `unknown` and narrow

### Go

**Formatter:** gofmt
**Linter:** golangci-lint

- Follow Effective Go conventions
- Use `camelCase` for unexported, `PascalCase` for exported
- Handle errors explicitly; never use `_` to discard errors
- Use `context.Context` for cancellation and timeouts

### JSON Schemas (Core Protocol)

- All protocol objects must have JSON Schema definitions
- Use `snake_case` for field names in JSON
- All schemas live in `packages/core-protocol/`
- Validate all API inputs/outputs against schemas

## Architecture Principles

1. **Claim-Centered:** All reasoning revolves around Claims, not messages
2. **Structured Objects:** Never pass raw strings; always use typed objects
3. **Local-First:** Ollama is the default model provider
4. **Event-Driven:** Use SSE for real-time streaming to UI
5. **Inspectable:** All reasoning steps must be traceable and replayable
6. **Protocol-First:** Core protocol schemas are the source of truth

## Required Invariants

1. Final answers must reference accepted claims
2. High-confidence claims need evidence or explicit uncertainty
3. Every rejected claim needs a rejection reason
4. Every revision must link old claim and new claim
5. Every tool result must be traceable to a tool call
6. Every final answer must declare remaining risks

## Key Quality Rules

- No raw hidden reasoning in UI; show safe structured summaries only
- Validate all JSON outputs against protocol schemas
- Store all claims/evidence/objections in Postgres
- Use Docker Compose for local development
- All new features require tests before merging

## Git Conventions

- Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- Keep commits focused and atomic
- Reference issue numbers when applicable

## Testing Requirements

- Unit tests for all schema validation logic
- Integration tests for API endpoints
- All PRs must pass CI (schema validation, unit tests, lint)
- Target minimum 80% code coverage for core protocol packages
