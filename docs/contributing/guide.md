# Contributing to mCTAgents

## Getting Started

1. Fork the repository
2. Clone your fork
3. Run the development setup:

```bash
./scripts/setup-dev.sh
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feat/my-feature
```

Use conventional commit prefixes:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation
- `test:` - Tests
- `refactor:` - Code refactoring
- `chore:` - Maintenance

### 2. Make Changes

Follow the code style guidelines in `AGENTS.md`:

- **Python**: Ruff formatter, mypy strict mode
- **TypeScript**: Prettier, ESLint strict mode
- **Go**: gofmt, golangci-lint

### 3. Run Tests

```bash
# All tests
make test

# Python tests
pytest services/reasoning-engine/tests/
pytest services/evidence-service/tests/

# Go tests
cd services/api-gateway && go test ./...

# Frontend tests
cd apps/studio && pnpm test
```

### 4. Lint and Format

```bash
make lint
make format
```

### 5. Submit PR

- Reference any related issues
- Include a clear description of changes
- Ensure all CI checks pass

## Project Structure

See `AGENTS.md` for the full monorepo structure and conventions.

## Adding a New Agent

1. Create `services/reasoning-engine/src/mctagents/agents/my_agent.py`
2. Implement the `BaseAgent` interface
3. Add to the `ReasoningEngine` orchestrator
4. Write tests in `tests/unit/test_my_agent.py`
5. Update documentation

## Adding a New Protocol Object

1. Add JSON schema in `packages/core-protocol/schemas/`
2. Add TypeScript type in `packages/core-protocol/src/types/`
3. Add Pydantic model in `services/reasoning-engine/src/mctagents/core/protocol/`
4. Add database table in `scripts/init-db.sql`
5. Add invariant validator if needed
6. Write tests
