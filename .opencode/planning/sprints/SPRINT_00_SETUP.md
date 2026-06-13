# Sprint 00: Project Setup

**Duration:** Days 1-5 | **Goal:** Monorepo skeleton, infrastructure, database schema

## Tasks

### Day 1: Repository Initialization
- [ ] Create monorepo directory structure
- [ ] Initialize `Makefile` with dev commands
- [ ] Create `.env.example` with all config vars
- [ ] Initialize `pnpm-workspace.yaml` for TypeScript packages
- [ ] Create root `package.json` with workspace config

### Day 2: Docker Infrastructure
- [ ] Create `docker-compose.yml` with PostgreSQL 16
- [ ] Add Redis 7 service
- [ ] Add Qdrant service
- [ ] Add Ollama service with GPU support
- [ ] Configure health checks for all services
- [ ] Create `docker-compose.override.yml` for dev overrides

### Day 3: Database Schema
- [ ] Create `scripts/init-db.sql` with all 12 tables
- [ ] Add indexes for queries
- [ ] Initialize Alembic for Python migrations
- [ ] Initialize golang-migrate for Go migrations
- [ ] Test schema creation and teardown

### Day 4: Tooling Setup
- [ ] Configure Ruff for Python linting
- [ ] Configure ESLint + Prettier for TypeScript
- [ ] Configure golangci-lint for Go
- [ ] Configure mypy for Python type checking
- [ ] Configure TypeScript strict mode
- [ ] Add pre-commit hooks (optional)

### Day 5: CI Pipeline + Seed Data
- [ ] Create `.github/workflows/ci.yml`
- [ ] Add schema validation job
- [ ] Add Python test job
- [ ] Add Go test job
- [ ] Add frontend build job
- [ ] Create `scripts/seed-demo.sh` with sample data
- [ ] Test full setup: `make docker-up && make seed-demo`

## Definition of Done
- [ ] `make docker-up` starts all 4 services
- [ ] All healthchecks pass within 30 seconds
- [ ] `make seed-demo` populates sample data
- [ ] `make lint` passes on all services
- [ ] `make test` passes on core-protocol schemas
- [ ] CI pipeline runs on clean checkout

## Risks
- **GPU not available:** Ollama runs on CPU (slower but works)
- **Docker version conflicts:** Use Docker Compose v2+

## Retro Notes
- _To be filled after sprint completion_
