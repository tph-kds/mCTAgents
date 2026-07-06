# mCTAgents Deployment Guide

> Complete step-by-step guide to deploy mCTAgents locally, in development, or in production.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Architecture Overview](#2-architecture-overview)
3. [Docker Storage Configuration](#25-docker-storage-configuration-important)
4. [Option A: Local Development (SGLang)](#3-option-a-local-development-sglang)
5. [Option B: Local Development (Ollama)](#4-option-b-local-development-ollama)
6. [Option C: Production Deployment](#5-option-c-production-deployment)
7. [Option D: Kubernetes / Helm](#6-option-d-kubernetes--helm)
8. [Environment Configuration Reference](#7-environment-configuration-reference)
9. [Service Ports Reference](#8-service-ports-reference)
10. [Verifying the Deployment](#9-verifying-the-deployment)
11. [Creating Your First Reasoning Session](#10-creating-your-first-reasoning-session)
12. [Uploading Documents for Evidence](#11-uploading-documents-for-evidence)
13. [Running Benchmarks](#12-running-benchmarks)
14. [Troubleshooting](#13-troubleshooting)
15. [VRAM Optimization Guide](#14-vram-optimization-guide)
16. [Production Hardening](#15-production-hardening)
17. [Backup and Recovery](#16-backup-and-recovery)
18. [Useful Commands Reference](#17-useful-commands-reference)

---

## 1. Prerequisites

### Required

| Tool | Version | Install |
|------|---------|---------|
| **Git** | 2.30+ | `sudo apt install git` |
| **Docker** | 24.0+ | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) |
| **Docker Compose** | v2.20+ | Included with Docker Desktop |

### For GPU-Accelerated Inference (Recommended)

| Tool | Version | Install |
|------|---------|---------|
| **NVIDIA GPU** | 4GB+ VRAM | RTX 3060, RTX 4060, or better |
| **NVIDIA Driver** | 525+ | `sudo ubuntu-drivers autoinstall` |
| **NVIDIA Container Toolkit** | Latest | See [NVIDIA Docker Install](#nvidia-container-toolkit-install) |

### For Manual Development (Without Docker)

| Tool | Version | Install |
|------|---------|---------|
| **Python** | 3.11+ | `pyenv install 3.11` |
| **Node.js** | 20+ | `nvm install 20` |
| **Go** | 1.22+ | `sudo snap install go --classic` |
| **pnpm** | 8+ | `npm install -g pnpm` |

---

## 2. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User's Browser                          │
│                    http://localhost:3000                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP + SSE
┌──────────────────────────▼──────────────────────────────────────┐
│                      API Gateway (Go)                           │
│                    http://localhost:8080                         │
│              Routes requests, streams SSE events                │
└───────┬──────────────────┼──────────────────┬───────────────────┘
        │                  │                  │
┌───────▼──────┐  ┌────────▼────────┐  ┌─────▼──────────┐
│  Reasoning   │  │  Model Gateway  │  │    Evidence    │
│   Engine     │  │     (Go)        │  │    Service     │
│  (Python)    │  │ localhost:8090  │  │   (Python)     │
│localhost:8000│  └────────┬────────┘  │ localhost:8001  │
└───────┬──────┘           │           └─────┬──────────┘
        │                  │                  │
        │           ┌──────▼──────┐    ┌─────▼──────┐
        │           │  SGLang /   │    │   Qdrant   │
        │           │  Ollama     │    │  (Vector)  │
        │           │ :30000/:11434    │  :6333     │
        │           └─────────────┘    └────────────┘
        │
┌───────▼──────────────────────────────────────────────────┐
│                    PostgreSQL                             │
│                   localhost:5432                          │
│            Stores runs, claims, evidence, events          │
└──────────────────────────────────────────────────────────┘
```

### Services Summary

| Service | Language | Port | Purpose |
|---------|----------|------|---------|
| **Studio** | TypeScript (Next.js) | 3000 | 3D visualization UI |
| **API Gateway** | Go | 8080 | REST API + SSE streaming |
| **Reasoning Engine** | Python | 8000 | Agent workflow + CCSR protocol |
| **Model Gateway** | Go | 8090 | LLM provider abstraction |
| **Evidence Service** | Python | 8001 | Document retrieval + RAG |
| **PostgreSQL** | SQL | 5432 | Primary database |
| **Redis** | - | 6379 | Cache + event bus |
| **Qdrant** | - | 6333 | Vector database |
| **SGLang** | Python | 30000 | LLM inference (GPU) |
| **Ollama** | Go | 11434 | LLM inference (alternative) |

---

## 2.5 Docker Storage Configuration (Important)

**If your root partition (`/`) is small**, you must ensure Docker stores data on a larger partition. mCTAgents uses ~5-15GB for Docker volumes (database, vector store, LLM models).

### Check Your Partitions

```bash
df -h / /home
# Example output:
# /dev/nvme1n1p8   19G   17G  814M  96% /      ← root (TOO SMALL)
# /dev/nvme1n1p9   96G   89G  2,4G  98% /home  ← home (USE THIS)
```

### How mCTAgents Handles This

All Docker Compose files use explicit bind mounts via the `DOCKER_DATA_ROOT` variable:

```bash
# .env (already configured)
DOCKER_DATA_ROOT=/home/zyelyhero/mctagents-data

# This creates:
# /home/zyelyhero/mctagents-data/pgdata      ← PostgreSQL
# /home/zyelyhero/mctagents-data/redisdata    ← Redis
# /home/zyelyhero/mctagents-data/qdrant_data  ← Qdrant vectors
# /home/zyelyhero/mctagents-data/ollama_data  ← Ollama models
# /home/zyelyhero/mctagents-data/sglang_data  ← SGLang models
```

### If You Need to Change Docker's Global Data Root

For images, containers, and build cache (not covered by bind mounts):

```bash
# Run with sudo:
sudo bash scripts/fix-docker-storage.sh

# Or manually:
sudo systemctl stop docker
sudo mkdir -p /home/youruser/docker-data
sudo tee /etc/docker/daemon.json << 'EOF'
{
    "default-runtime": "nvidia",
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    },
    "data-root": "/home/youruser/docker-data"
}
EOF
sudo systemctl start docker

# Verify
docker info | grep "Docker Root Dir"
# Should show: Docker Root Dir: /home/youruser/docker-data

# Free root space after confirming
sudo rm -rf /var/lib/docker
```

### Change Storage Location

Edit `.env`:

```bash
# Point to any partition with space
DOCKER_DATA_ROOT=/mnt/fast-ssd/docker-data
```

---

## 3. Option A: Local Development (SGLang)

**Best for:** Systems with NVIDIA GPU (<4GB VRAM supported)

### Step 1: Clone the Repository

```bash
git clone https://github.com/tph-kds/mCTAgents.git
cd mCTAgents
```

### Step 2: Install NVIDIA Container Toolkit

```bash
# Add NVIDIA package repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg

curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker to use NVIDIA runtime
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Verify GPU access in Docker
docker run --rm --gpus all nvidia/cuda:12.0-base nvidia-smi
```

### Step 3: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` if you need to change defaults. The SGLang defaults work out of the box:

```bash
# Key SGLang settings (already in .env.example)
SGLANG_PORT=30000
SGLANG_BASE_URL=http://sglang:30000
SGLANG_MODEL=Qwen/Qwen3-1.7B
SGLANG_CONTEXT_LENGTH=4096
DEFAULT_CHAT_MODEL=Qwen/Qwen3-1.7B
DEFAULT_REASONING_MODEL=Qwen/Qwen3-1.7B
```

### Step 4: Start All Services

```bash
# Start with SGLang profile (includes GPU passthrough)
docker compose --profile sglang up -d
```

This starts 9 services:
- PostgreSQL, Redis, Qdrant (infrastructure)
- SGLang (GPU inference)
- API Gateway, Reasoning Engine, Model Gateway, Evidence Service (backend)
- Studio (frontend)

### Step 5: Wait for Model Download

```bash
# Watch SGLang download the model (~1.3GB)
docker logs -f mctagents-sglang
```

Wait until you see output like:
```
Model loaded successfully
Server is ready to serve requests
```

### Step 6: Verify All Services Are Healthy

```bash
# Check all container statuses
docker compose ps

# Expected: all services "Up" with "(healthy)" status
```

If any service shows "unhealthy", check logs:
```bash
docker logs mctagents-reasoning-engine
docker logs mctagents-api-gateway
docker logs mctagents-sglang
```

### Step 7: Open Studio

```bash
# macOS
open http://localhost:3000

# Linux
xdg-open http://localhost:3000

# Windows
start http://localhost:3000
```

You should see the mCTAgents Studio with the 3D workspace and agent avatars.

### Step 8: Test the API

```bash
curl -X POST http://localhost:8080/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"problem": "Should we adopt microservices for our payment system?"}'
```

You should get a response with a `run_id` and `events_url`.

---

## 4. Option B: Local Development (Ollama)

**Best for:** Systems without GPU, or when you prefer Ollama

### Step 1: Clone and Configure

```bash
git clone https://github.com/tph-kds/mCTAgents.git
cd mCTAgents
cp .env.example .env
```

### Step 2: Update Model Defaults for Ollama

Edit `.env` and change:

```bash
DEFAULT_CHAT_MODEL=qwen2.5:7b
DEFAULT_REASONING_MODEL=deepseek-r1:7b
DEFAULT_EMBEDDING_MODEL=nomic-embed-text
```

### Step 3: Start Services (Without SGLang)

```bash
# Start without the sglang profile
make dev
# Or equivalently:
docker compose -f docker-compose.yml -f docker-compose.override.yml up
```

### Step 4: Pull Ollama Models

In a separate terminal, wait for Ollama to start, then pull models:

```bash
# Wait for Ollama to be ready
sleep 10

# Pull chat model
docker exec mctagents-ollama ollama pull qwen2.5:7b

# Pull reasoning model
docker exec mctagents-ollama ollama pull deepseek-r1:7b

# Pull embedding model
docker exec mctagents-ollama ollama pull nomic-embed-text
```

### Step 5: Verify and Open

```bash
# Check Ollama models
docker exec mctagents-ollama ollama list

# Open Studio
open http://localhost:3000
```

---

## 5. Option C: Production Deployment

**Best for:** Single-server production deployment

### Step 1: Prepare the Server

```bash
# On Ubuntu/Debian
sudo apt update && sudo apt upgrade -y
sudo apt install -y docker.io docker-compose-v2 curl

# Install NVIDIA toolkit (if using GPU)
# See Section 3, Step 2

# Create deployment directory
mkdir -p /opt/mctagents
cd /opt/mctagents
```

### Step 2: Clone and Configure

```bash
git clone https://github.com/tph-kds/mCTAgents.git .
cp .env.example .env
```

Edit `.env` for production:

```bash
# Security: Change default passwords
POSTGRES_PASSWORD=<your-secure-password>

# Models
DEFAULT_CHAT_MODEL=Qwen/Qwen3-1.7B
DEFAULT_REASONING_MODEL=Qwen/Qwen3-1.7B

# Logging: reduce verbosity
LOG_LEVEL=info

# Disable debug features
AUTH_ENABLED=false
```

### Step 3: Use Production Docker Compose

```bash
# Use the production compose file
docker compose -f deployments/docker-compose/docker-compose.prod.yml up -d
```

### Step 4: Enable Authentication (Optional)

Edit `.env`:

```bash
AUTH_ENABLED=true
API_KEY=<your-secure-api-key>
```

Update API requests to include the key:

```bash
curl -X POST http://localhost:8080/v1/runs \
  -H "Content-Type: application/json" \
  -H "X-API-Key: <your-secure-api-key>" \
  -d '{"problem": "Your problem here"}'
```

### Step 5: Set Up Reverse Proxy (Recommended)

Install Nginx and configure as reverse proxy:

```bash
sudo apt install -y nginx
```

Create `/etc/nginx/sites-available/mctagents`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Studio UI
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API Gateway
    location /v1/ {
        proxy_pass http://localhost:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # SSE support
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_buffering off;
        proxy_cache off;
    }
}
```

Enable and restart:

```bash
sudo ln -s /etc/nginx/sites-available/mctagents /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo systemctl restart nginx
```

### Step 6: Set Up SSL (Recommended)

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### Step 7: Configure Firewall

```bash
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

---

## 6. Option D: Kubernetes / Helm

**Best for:** Multi-node clusters, cloud deployments

### Using Helm Chart

```bash
cd deployments/helm/mctagents

# Install with default values
helm install mctagents . -n mctagents --create-namespace

# Install with custom values
helm install mctagents . -n mctagents --create-namespace \
  --set postgresql.auth.password=<your-password> \
  --set reasoningEngine.resources.limits.memory=2Gi \
  --set apiGateway.replicaCount=3
```

### Using Raw Kubernetes Manifests

```bash
cd deployments/k8s

# Create namespace
kubectl apply -f namespace.yaml

# Create secrets
kubectl apply -f secrets.yaml

# Create configmap
kubectl apply -f configmap.yaml

# Deploy infrastructure
kubectl apply -f postgres.yaml
kubectl apply -f redis.yaml

# Deploy services
kubectl apply -f api-gateway.yaml
kubectl apply -f reasoning-engine.yaml
kubectl apply -f model-gateway.yaml
kubectl apply -f evidence-service.yaml

# Check status
kubectl get pods -n mctagents
```

### Expose Studio

```bash
# Port-forward for testing
kubectl port-forward -n mctagents svc/api-gateway 8080:8080

# Or create Ingress
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mctagents-ingress
  namespace: mctagents
spec:
  rules:
  - host: mctagents.your-domain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: api-gateway
            port:
              number: 8080
EOF
```

---

## 7. Environment Configuration Reference

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `POSTGRES_DB` | `mctagents` | Database name |
| `POSTGRES_USER` | `mctagents` | Database user |
| `POSTGRES_PASSWORD` | `devpassword` | **Change in production!** |
| `POSTGRES_PORT` | `5432` | PostgreSQL port |

### Cache

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_PORT` | `6379` | Redis port |

### Vector Database

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_PORT` | `6333` | Qdrant HTTP port |
| `QDRANT_GRPC_PORT` | `6334` | Qdrant gRPC port |

### LLM Provider

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_PORT` | `11434` | Ollama port |
| `SGLANG_PORT` | `30000` | SGLang port |
| `SGLANG_BASE_URL` | `http://sglang:30000` | SGLang internal URL |
| `SGLANG_MODEL` | `Qwen/Qwen3-1.7B` | SGLang model |
| `SGLANG_CONTEXT_LENGTH` | `4096` | Max context window |
| `HF_TOKEN` | (empty) | HuggingFace token for gated models |

### Application Services

| Variable | Default | Description |
|----------|---------|-------------|
| `API_GATEWAY_PORT` | `8080` | API Gateway port |
| `REASONING_ENGINE_PORT` | `8000` | Reasoning Engine port |
| `MODEL_GATEWAY_PORT` | `8090` | Model Gateway port |
| `EVIDENCE_SERVICE_PORT` | `8001` | Evidence Service port |
| `STUDIO_PORT` | `3000` | Studio frontend port |

### Model Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DEFAULT_CHAT_MODEL` | `Qwen/Qwen3-1.7B` | Chat model for agents |
| `DEFAULT_REASONING_MODEL` | `Qwen/Qwen3-1.7B` | Reasoning model for judge/synthesizer |
| `DEFAULT_EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model |

### Budget Limits

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_TOTAL_TOKENS` | `12000` | Max tokens per run |
| `MAX_MODEL_CALLS` | `16` | Max LLM API calls per run |
| `MAX_DEBATE_ROUNDS` | `2` | Max debate rounds |
| `MAX_RUNTIME_SECONDS` | `300` | Max runtime per run |

### Evidence Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CHUNK_SIZE_TOKENS` | `600` | Document chunk size |
| `CHUNK_OVERLAP_TOKENS` | `80` | Chunk overlap |
| `EMBEDDING_DIMENSION` | `768` | Embedding vector dimension |

---

## 8. Service Ports Reference

| Port | Service | Protocol | Purpose |
|------|---------|----------|---------|
| 3000 | Studio | HTTP | Next.js frontend |
| 30000 | SGLang | HTTP | LLM inference API |
| 8080 | API Gateway | HTTP | REST + SSE API |
| 8000 | Reasoning Engine | HTTP | Agent workflow |
| 8090 | Model Gateway | HTTP | LLM provider abstraction |
| 8001 | Evidence Service | HTTP | Document retrieval |
| 5432 | PostgreSQL | TCP | Primary database |
| 6379 | Redis | TCP | Cache + events |
| 6333 | Qdrant | HTTP | Vector search |
| 6334 | Qdrant | gRPC | Vector search (gRPC) |
| 11434 | Ollama | HTTP | LLM inference (alternative) |

---

## 9. Verifying the Deployment

### Health Checks

```bash
# API Gateway
curl http://localhost:8080/health
# Expected: {"status":"ok"}

# Reasoning Engine
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# Evidence Service
curl http://localhost:8001/health
# Expected: {"version":"0.1.0"}

# SGLang (if using)
curl http://localhost:30000/v1/models
# Expected: {"data":[{"id":"Qwen/Qwen3-1.7B",...}]}

# Ollama (if using)
curl http://localhost:11434/api/tags
# Expected: {"models":[{"name":"qwen2.5:7b",...}]}

# Qdrant
curl http://localhost:6333/healthz
# Expected: {"status":"ok"}
```

### Database Verification

```bash
# Connect to PostgreSQL
docker exec -it mctagents-postgres psql -U mctagents -d mctagents

# Check tables
\dt

# Check demo data (if seeded)
SELECT COUNT(*) FROM runs;
SELECT COUNT(*) FROM claims;
SELECT COUNT(*) FROM events;

# Exit
\q
```

### Full Stack Test

```bash
# Create a reasoning run
RESPONSE=$(curl -s -X POST http://localhost:8080/v1/runs \
  -H "Content-Type: application/json" \
  -d '{"problem": "What are the trade-offs of using PostgreSQL vs MongoDB for a social media app?"}')

echo "$RESPONSE" | python3 -m json.tool

# Extract run ID
RUN_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['run_id'])")
echo "Run ID: $RUN_ID"

# Stream events (Ctrl+C to stop)
curl -N http://localhost:8080/v1/runs/$RUN_ID/events
```

---

## 10. Creating Your First Reasoning Session

### Via Studio UI

1. Open `http://localhost:3000`
2. Click **"Start New Session"**
3. Enter a problem statement, e.g.:
   ```
   Should our startup adopt a microservices architecture for the payment processing system?
   We have 15 engineers, handle 5K transactions/minute, and need PCI compliance.
   ```
4. Select a mode:
   - **Balanced** - Good for most problems
   - **Fast** - Quick consensus, fewer rounds
   - **Deep** - Thorough analysis, more rounds
5. Click **"Start Reasoning"**
6. Watch the 3D workspace as agents debate in real-time
7. View thinking traces in the left sidebar
8. Click agent avatars to see their contributions
9. Review the final answer when complete

### Via API

```bash
# Create run
curl -X POST http://localhost:8080/v1/runs \
  -H "Content-Type: application/json" \
  -d '{
    "problem": "Should we adopt microservices for our payment system?",
    "mode": "balanced_reasoning",
    "evidence_policy": "required_for_major_claims",
    "budget": {
      "max_tokens": 12000,
      "max_model_calls": 16,
      "max_debate_rounds": 2
    }
  }'

# Stream events
curl -N http://localhost:8080/v1/runs/{run_id}/events

# Get claims
curl http://localhost:8080/v1/runs/{run_id}/claims

# Get final answer
curl http://localhost:8080/v1/runs/{run_id}/events | \
  python3 -c "import sys, json; events = [json.loads(l) for l in sys.stdin if l.strip()]; \
  final = [e for e in events if e['type'] == 'final_answer_created']; \
  print(json.dumps(final[-1]['payload'], indent=2))"
```

### Via Python SDK

```python
from mctagents_sdk import MCTAgentsClient

client = MCTAgentsClient(api_url="http://localhost:8080")

# Create and stream a run
run = client.create_run(
    problem="Should we adopt microservices for our payment system?",
    mode="balanced_reasoning"
)

for event in client.stream_events(run.run_id):
    print(f"[{event.type}] {event.agent_id}: {event.payload.get('summary', '')}")
    if event.type == "run_completed":
        break

# Get claims
claims = client.get_claims(run.run_id)
for claim in claims:
    print(f"  {claim.status}: {claim.text[:80]}...")
```

---

## 11. Uploading Documents for Evidence

### Upload a Document

```bash
# Upload PDF, DOCX, MD, or TXT
curl -X POST http://localhost:8080/v1/documents \
  -F "file=@./your-document.pdf"
```

### Search for Evidence

```bash
curl -X POST http://localhost:8001/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "microservices security best practices",
    "run_id": "your-run-id",
    "top_k": 5
  }'
```

### Supported Document Formats

| Format | Extension | Parser |
|--------|-----------|--------|
| PDF | `.pdf` | PyMuPDF |
| Word | `.docx` | python-docx |
| Markdown | `.md` | Custom parser |
| Plain Text | `.txt` | Line-by-line |

---

## 12. Running Benchmarks

### Quick Smoke Test

```bash
make benchmark-smoke
```

### Full Benchmark Suite

```bash
make benchmark-full
```

### Custom Benchmark

```bash
cd benchmarks

# Run against specific task
python -m benchmarks run --task tasks/software_architecture.yaml

# Run all tasks
python -m benchmarks run --all --tasks-dir tasks/

# View leaderboard
python -m benchmarks leaderboard --top 10

# Export to Markdown
python -m benchmarks leaderboard --export results/leaderboard.md
```

---

## 13. Troubleshooting

### Service Won't Start

```bash
# Check container logs
docker logs mctagents-reasoning-engine --tail 50
docker logs mctagents-api-gateway --tail 50
docker logs mctagents-sglang --tail 50

# Check if port is already in use
lsof -i :8080
lsof -i :30000

# Kill conflicting process
kill -9 <PID>
```

### Database Connection Refused

```bash
# Check PostgreSQL is running and healthy
docker compose ps postgres

# Check logs
docker logs mctagents-postgres --tail 20

# Test connection directly
docker exec -it mctagents-postgres pg_isready -U mctagents

# Reset database (WARNING: destroys data)
docker compose down -v
docker compose up -d postgres
```

### SGLang GPU Out of Memory

```bash
# Check GPU memory
nvidia-smi

# Reduce context length
# Edit .env:
SGLANG_CONTEXT_LENGTH=2048

# Or reduce memory fraction
# In docker-compose.override.yml, change:
# --mem-fraction-static 0.5

# Restart SGLang
docker compose restart sglang
```

### SGLang Model Download Fails

```bash
# Check internet connectivity
curl -I https://huggingface.co

# Check available disk space
df -h

# Set HuggingFace token for gated models
# Edit .env:
HF_TOKEN=your-token-here

# Restart
docker compose restart sglang
```

### Studio Shows "OFFLINE"

```bash
# Check API Gateway is running
curl http://localhost:8080/health

# Check Studio environment
docker exec mctagents-studio env | grep NEXT_PUBLIC

# Restart Studio
docker compose restart studio
```

### Thinking Traces Not Appearing

```bash
# Verify reasoning engine emits thinking steps
curl -N http://localhost:8080/v1/runs/{run_id}/events | grep agent_started

# Check that events contain thinking_steps
curl -N http://localhost:8080/v1/runs/{run_id}/events | \
  python3 -c "import sys, json; \
  [print(json.loads(l).get('payload',{}).get('thinking_steps','NONE')) \
  for l in sys.stdin if 'agent_started' in l]"
```

### AgentPopover Shows Empty Tabs

This was a known issue that has been fixed. Ensure you're on the latest commit:

```bash
git pull origin main
docker compose build --no-cache studio
docker compose up -d studio
```

---

## 14. VRAM Optimization Guide

### Model Size vs VRAM Usage

| Model | Size | VRAM (FP16) | VRAM (Q4) | Recommended For |
|-------|------|-------------|-----------|-----------------|
| Qwen3-0.5B | 0.4GB | ~1GB | <1GB | Minimal GPU |
| Qwen3-1.7B | 1.3GB | ~3GB | ~1.5GB | 4GB GPU (recommended) |
| Qwen3-4B | 2.5GB | ~5GB | ~3GB | 6GB+ GPU |
| Qwen2.5-7B | 4.4GB | ~9GB | ~5GB | 8GB+ GPU |

### Optimization Strategies

**1. Reduce Context Length**

```bash
# In .env
SGLANG_CONTEXT_LENGTH=2048

# Or in docker-compose.override.yml
command: --context-length 2048
```

**2. Reduce Memory Fraction**

```bash
# In docker-compose.override.yml
command: --mem-fraction-static 0.5
```

**3. Use Quantized Models**

```bash
# In docker-compose.override.yml
command: --model Qwen/Qwen3-1.7B --quantization awq
```

**4. Use Smaller Embedding Model**

```bash
# In .env
DEFAULT_EMBEDDING_MODEL=bge-small-en-v1.5
```

**5. Run Embeddings on CPU**

If VRAM is very tight, run the embedding model on CPU by modifying the evidence service to use a CPU-based embedding library.

### Monitoring GPU Usage

```bash
# Real-time GPU monitoring
watch -n 1 nvidia-smi

# Log GPU usage over time
nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv -l 5 > gpu_log.csv
```

---

## 15. Production Hardening

### Security Checklist

- [ ] Change `POSTGRES_PASSWORD` from default
- [ ] Enable `AUTH_ENABLED=true` and set `API_KEY`
- [ ] Use HTTPS via reverse proxy (Nginx/Caddy)
- [ ] Restrict network access with firewall
- [ ] Don't expose PostgreSQL/Redis/Qdrant ports externally
- [ ] Use Docker secrets for sensitive values
- [ ] Enable Docker Content Trust

### Performance Tuning

```yaml
# docker-compose.prod.yml additions
services:
  reasoning-engine:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

  api-gateway:
    deploy:
      replicas: 3
```

### Logging

```bash
# Centralized logging with Docker
docker compose logs -f --timestamps > /var/log/mctagents.log 2>&1

# Or use structured logging
# Set in .env:
LOG_LEVEL=info
```

### Monitoring

Add health check endpoints to your monitoring system:

```bash
# Prometheus-style metrics (if implemented)
curl http://localhost:8080/metrics

# Custom health check script
#!/bin/bash
SERVICES=("localhost:8080/health" "localhost:8000/health" "localhost:30000/v1/models")
for svc in "${SERVICES[@]}"; do
  if ! curl -sf "http://$svc" > /dev/null; then
    echo "FAIL: $svc"
    exit 1
  fi
done
echo "ALL OK"
```

### Auto-Restart

Docker Compose production files include `restart: unless-stopped`. For systemd:

```bash
cat <<EOF | sudo tee /etc/systemd/system/mctagents.service
[Unit]
Description=mCTAgents
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/mctagents
ExecStart=/usr/bin/docker compose -f deployments/docker-compose/docker-compose.prod.yml up -d
ExecStop=/usr/bin/docker compose -f deployments/docker-compose/docker-compose.prod.yml down

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable mctagents
sudo systemctl start mctagents
```

---

## 16. Backup and Recovery

### Database Backup

```bash
# Backup PostgreSQL
docker exec mctagents-postgres pg_dump -U mctagents mctagents > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore PostgreSQL
cat backup.sql | docker exec -i mctagents-postgres psql -U mctagents mctagents
```

### Volume Backup

```bash
# Backup all bind-mount data directories
DOCKER_DATA_ROOT="${DOCKER_DATA_ROOT:-/home/zyelyhero/mctagents-data}"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

for dir in pgdata redisdata qdrant_data ollama_data sglang_data; do
  tar czf "${BACKUP_DIR}/${dir}.tar.gz" -C "$DOCKER_DATA_ROOT" "$dir" 2>/dev/null || true
done

echo "Backup complete: ${BACKUP_DIR}"
```

### Restore from Backup

```bash
DOCKER_DATA_ROOT="${DOCKER_DATA_ROOT:-/home/zyelyhero/mctagents-data}"
BACKUP_DIR="./backups/YYYYMMDD_HHMMSS"  # Replace with actual backup dir

for dir in pgdata redisdata qdrant_data ollama_data sglang_data; do
  tar xzf "${BACKUP_DIR}/${dir}.tar.gz" -C "$DOCKER_DATA_ROOT" 2>/dev/null || true
done
```

### Full Backup Script

```bash
#!/bin/bash
DOCKER_DATA_ROOT="${DOCKER_DATA_ROOT:-/home/zyelyhero/mctagents-data}"
BACKUP_DIR="/backups/mctagents/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Stop services
docker compose down

# Backup bind-mount data directories
for dir in pgdata redisdata qdrant_data ollama_data sglang_data; do
  tar czf "${BACKUP_DIR}/${dir}.tar.gz" -C "$DOCKER_DATA_ROOT" "$dir" 2>/dev/null || true
done

# Backup .env
cp .env "${BACKUP_DIR}/env.backup"

# Restart services
docker compose up -d

echo "Backup complete: ${BACKUP_DIR}"
```

---

## 17. Useful Commands Reference

### Docker Compose

```bash
# Start all services
make dev                          # Foreground
make dev-d                        # Detached

# Stop all services
docker compose down

# Stop and remove volumes (WARNING: destroys data)
docker compose down -v

# View logs
docker compose logs -f             # All services
docker compose logs -f reasoning-engine  # Single service

# Restart a service
docker compose restart reasoning-engine

# Rebuild after code changes
docker compose build --no-cache reasoning-engine
docker compose up -d reasoning-engine

# Check status
docker compose ps

# Execute command in container
docker exec -it mctagents-reasoning-engine bash
docker exec -it mctagents-postgres psql -U mctagents
```

### Testing

```bash
# Run all tests
make test

# Python tests
cd services/reasoning-engine && python -m pytest -v

# TypeScript tests
cd apps/studio && npm test

# Go tests
cd services/api-gateway && go test ./...

# Linting
make lint

# Format code
make format
```

### Database

```bash
# Connect to PostgreSQL
docker exec -it mctagents-postgres psql -U mctagents -d mctagents

# Useful SQL queries
SELECT id, status, created_at FROM runs ORDER BY created_at DESC LIMIT 10;
SELECT COUNT(*) FROM claims WHERE status = 'accepted';
SELECT COUNT(*) FROM events WHERE type = 'claim_created';

# Run migrations
make migrate
```

### Development

```bash
# Seed demo data
make seed-demo

# Setup full dev environment
./scripts/setup-dev.sh

# Clean build artifacts
make clean
```

---

## Quick Reference Card

```
┌─────────────────────────────────────────────────────────────┐
│                    mCTAgents Quick Reference                 │
├─────────────────────────────────────────────────────────────┤
│  Start:     docker compose --profile sglang up -d           │
│  Stop:      docker compose down                             │
│  Logs:      docker compose logs -f                          │
│  Studio:    http://localhost:3000                            │
│  API:       http://localhost:8080                            │
│  Health:    curl http://localhost:8080/health                │
│  Tests:     make test                                       │
│  Backup:    docker exec mctagents-postgres pg_dump -U mctagents > bkp │
├─────────────────────────────────────────────────────────────┤
│  Ports: 3000=Studio  8080=API  30000=SGLang  5432=Postgres  │
│         8000=Engine  8090=ModelGW  8001=Evidence  6333=Qdrant│
└─────────────────────────────────────────────────────────────┘
```
