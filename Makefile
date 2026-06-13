.PHONY: dev test lint format docker-up docker-down seed-demo migrate benchmark-smoke benchmark-full setup-dev

# =============================================================================
# Development
# =============================================================================

dev:
	docker compose -f docker-compose.yml -f docker-compose.override.yml up

dev-d:
	docker compose -f docker-compose.yml -f docker-compose.override.yml up -d

setup-dev: docker-up
	@echo "Waiting for services to be healthy..."
	@sleep 10
	$(MAKE) seed-demo
	@echo "Development environment ready!"

# =============================================================================
# Docker
# =============================================================================

docker-up:
	docker compose up -d

docker-down:
	docker compose down

docker-restart:
	docker compose restart

docker-logs:
	docker compose logs -f

docker-ps:
	docker compose ps

# =============================================================================
# Testing
# =============================================================================

test: test-protocol test-reasoning test-api-gateway test-studio

test-protocol:
	cd packages/core-protocol && pnpm test

test-reasoning:
	cd services/reasoning-engine && python -m pytest -v

test-reasoning-unit:
	cd services/reasoning-engine && python -m pytest tests/unit/ -v

test-reasoning-integration:
	cd services/reasoning-engine && python -m pytest tests/integration/ -v

test-reasoning-single:
	@echo "Usage: make test-reasoning-single FILE=tests/unit/test_claim.py"
	cd services/reasoning-engine && python -m pytest $(FILE) -v

test-api-gateway:
	cd services/api-gateway && go test ./...

test-studio:
	cd apps/studio && pnpm test

test-evidence:
	cd services/evidence-service && python -m pytest -v

test-benchmarks:
	cd benchmarks && python -m pytest tests/ -v

# =============================================================================
# Linting & Formatting
# =============================================================================

lint: lint-python lint-typescript lint-go

lint-python:
	ruff check services/reasoning-engine/
	ruff check services/evidence-service/

lint-typescript:
	cd packages/core-protocol && pnpm lint
	cd apps/studio && pnpm lint

lint-go:
	cd services/api-gateway && golangci-lint run
	cd services/model-gateway && golangci-lint run

format: format-python format-typescript format-go

format-python:
	ruff format services/reasoning-engine/ services/evidence-service/
	ruff check --fix services/reasoning-engine/ services/evidence-service/

format-typescript:
	cd packages/core-protocol && pnpm format
	cd apps/studio && pnpm format

format-go:
	gofmt -w services/api-gateway/
	gofmt -w services/model-gateway/

# =============================================================================
# Type Checking
# =============================================================================

typecheck: typecheck-python typecheck-typescript

typecheck-python:
	cd services/reasoning-engine && mypy src/
	cd services/evidence-service && mypy src/

typecheck-typescript:
	cd packages/core-protocol && pnpm typecheck
	cd apps/studio && pnpm typecheck

# =============================================================================
# Database
# =============================================================================

migrate:
	cd services/reasoning-engine && alembic upgrade head

migrate-create:
	@echo "Usage: make migrate-create MESSAGE='add claims table'"
	cd services/reasoning-engine && alembic revision --autogenerate -m "$(MESSAGE)"

# =============================================================================
# Seed Data
# =============================================================================

seed-demo:
	bash scripts/seed-demo.sh

# =============================================================================
# Benchmarks
# =============================================================================

benchmark-smoke:
	cd benchmarks && python -m pytest smoke/ -v

benchmark-full:
	cd benchmarks && python -m pytest -v

# =============================================================================
# Build
# =============================================================================

build: build-protocol build-reasoning build-api-gateway build-studio

build-protocol:
	cd packages/core-protocol && pnpm build

build-reasoning:
	cd services/reasoning-engine && python -m build

build-api-gateway:
	cd services/api-gateway && go build -o bin/api-gateway ./cmd/api-gateway

build-studio:
	cd apps/studio && pnpm build

# =============================================================================
# Clean
# =============================================================================

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name node_modules -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .next -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
