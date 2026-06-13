#!/bin/bash
# =============================================================================
# mCTAgents - Development Setup Script
# =============================================================================
# This script sets up the development environment from scratch

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}=== mCTAgents Development Setup ===${NC}"

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"

if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}Node.js is not installed. Installing via nvm...${NC}"
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
    nvm install 20
    nvm use 20
fi

if ! command -v pnpm &> /dev/null; then
    echo -e "${YELLOW}pnpm is not installed. Installing...${NC}"
    npm install -g pnpm
fi

if ! command -v go &> /dev/null; then
    echo -e "${YELLOW}Go is not installed. Please install Go 1.22+ first.${NC}"
    echo -e "Visit: https://go.dev/dl/"
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.11+ first.${NC}"
    exit 1
fi

echo -e "${GREEN}Prerequisites check passed!${NC}"

# Copy .env if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env created!${NC}"
fi

# Start infrastructure services
echo -e "${YELLOW}Starting infrastructure services...${NC}"
docker compose up -d postgres redis qdrant ollama

# Wait for services to be healthy
echo -e "${YELLOW}Waiting for services to be healthy...${NC}"
sleep 15

# Check health
echo -e "${YELLOW}Checking service health...${NC}"
docker compose ps

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
cd services/reasoning-engine && pip install -e ".[dev]" && cd ../..
cd services/evidence-service && pip install -e ".[dev]" && cd ../..

# Install Node.js dependencies
echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
cd packages/core-protocol && pnpm install && cd ../..
cd apps/studio && pnpm install && cd ../..

# Pull Ollama models
echo -e "${YELLOW}Pulling Ollama models...${NC}"
docker compose exec -T ollama ollama pull qwen2.5:7b || echo -e "${YELLOW}Warning: Could not pull qwen2.5:7b${NC}"
docker compose exec -T ollama ollama pull nomic-embed-text || echo -e "${YELLOW}Warning: Could not pull nomic-embed-text${NC}"

# Seed demo data
echo -e "${YELLOW}Seeding demo data...${NC}"
bash scripts/seed-demo.sh

echo -e "${GREEN}=== Development setup completed! ===${NC}"
echo -e "${GREEN}You can now run:${NC}"
echo -e "  make dev          # Start all services with hot reload"
echo -e "  make test         # Run all tests"
echo -e "  make lint         # Run all linters"
