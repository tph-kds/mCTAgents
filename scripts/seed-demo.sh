#!/bin/bash
# =============================================================================
# mCTAgents - Seed Demo Data Script
# =============================================================================
# This script seeds the database with demo data for testing and development

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== mCTAgents Demo Seed ===${NC}"

# Check if PostgreSQL is running
echo -e "${YELLOW}Checking PostgreSQL connection...${NC}"
if ! docker compose exec -T postgres pg_isready -U mctagents > /dev/null 2>&1; then
    echo -e "${RED}PostgreSQL is not ready. Please run 'make docker-up' first.${NC}"
    exit 1
fi

echo -e "${GREEN}PostgreSQL is ready!${NC}"

# Run the init-db.sql script (includes seed data)
echo -e "${YELLOW}Seeding database with demo data...${NC}"
docker compose exec -T postgres psql -U mctagents -d mctagents -f /docker-entrypoint-initdb.d/01-init.sql > /dev/null 2>&1 || true

# Verify seed data
echo -e "${YELLOW}Verifying seed data...${NC}"
RUNS_COUNT=$(docker compose exec -T postgres psql -U mctagents -d mctagents -t -c "SELECT COUNT(*) FROM runs" | tr -d ' ')
CLAIMS_COUNT=$(docker compose exec -T postgres psql -U mctagents -d mctagents -t -c "SELECT COUNT(*) FROM claims" | tr -d ' ')
EVIDENCE_COUNT=$(docker compose exec -T postgres psql -U mctagents -d mctagents -t -c "SELECT COUNT(*) FROM evidence" | tr -d ' ')

echo -e "${GREEN}Seed data loaded:${NC}"
echo -e "  - Runs: ${RUNS_COUNT}"
echo -e "  - Claims: ${CLAIMS_COUNT}"
echo -e "  - Evidence: ${EVIDENCE_COUNT}"

# Pull Ollama models
echo -e "${YELLOW}Pulling Ollama models (this may take a while)...${NC}"
docker compose exec -T ollama ollama pull qwen2.5:7b 2>/dev/null || echo -e "${YELLOW}Warning: Could not pull qwen2.5:7b${NC}"
docker compose exec -T ollama ollama pull nomic-embed-text 2>/dev/null || echo -e "${YELLOW}Warning: Could not pull nomic-embed-text${NC}"

echo -e "${GREEN}=== Demo seed completed! ===${NC}"
echo -e "${GREEN}You can now access:${NC}"
echo -e "  - API: http://localhost:8080"
echo -e "  - Studio: http://localhost:3000"
echo -e "  - Qdrant: http://localhost:6333"
