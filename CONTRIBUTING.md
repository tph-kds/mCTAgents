# Contributing to mCTAgents

Thank you for your interest in contributing to mCTAgents! This guide will help you get started.

## Getting Started

1. **Fork** the repository
2. **Clone** your fork: `git clone https://github.com/your-username/mCTAgents.git`
3. **Run** the setup script: `bash scripts/setup-dev.sh`
4. **Start** development: `make dev`

## Development Workflow

1. Create a feature branch: `git checkout -b feat/my-feature`
2. Make your changes following the code style guidelines
3. Run `make lint` to check formatting
4. Run `make test` to run all tests
5. Commit with conventional commits: `feat: add my feature`
6. Push and create a pull request

## Code Style

### Python
- **Formatter/Linter:** Ruff
- **Type Checker:** mypy
- **Style:** PEP 8, max 88 char lines
- **Naming:** `snake_case` for functions/variables, `PascalCase` for classes
- **Type hints** on all function signatures
- **Pydantic v2** for data models

### TypeScript
- **Formatter:** Prettier
- **Linter:** ESLint
- **Type Checker:** TypeScript strict mode
- **Style:** `camelCase` for functions/variables, `PascalCase` for components/types

### Go
- **Formatter:** gofmt
- **Linter:** golangci-lint
- **Style:** Follow Effective Go conventions
- **Errors:** Always handle explicitly

## Testing

### Python Tests
```bash
cd services/reasoning-engine
pytest                          # Run all tests
pytest tests/unit/              # Unit tests only
pytest tests/unit/test_claim.py # Single test file
pytest tests/unit/test_claim.py::test_claim_validation -v  # Single test
```

### Go Tests
```bash
cd services/api-gateway
go test ./...
```

### TypeScript Tests
```bash
cd apps/studio
pnpm test
```

## Commit Convention

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation
- `test:` adding tests
- `refactor:` code restructuring
- `chore:` maintenance
- `perf:` performance improvement

Examples:
```
feat: add claim graph visualization component
fix: resolve SSE reconnection issue in useSSE hook
docs: update API documentation for /v1/runs endpoint
test: add unit tests for evidence reliability scorer
```

## Pull Request Guidelines

1. PRs should be focused on a single change
2. Include tests for new functionality
3. Update documentation if needed
4. Ensure CI passes
5. Keep PRs small and reviewable

## Reporting Issues

- Use GitHub issue templates
- Include reproduction steps
- Include environment details
- Be descriptive and specific

## Code of Conduct

Be respectful, inclusive, and constructive. We are building this project together.

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
