# Security Model

## Overview

mCTAgents is designed for local-first deployment with Ollama as the default model provider. This means data stays on your infrastructure by default.

## Data Flow Security

### Local-First Architecture

```
Client → API Gateway → Reasoning Engine → Ollama (local)
                    ↘ Evidence Service → Qdrant (local)
                    ↘ PostgreSQL (local)
```

- No data leaves your infrastructure when using Ollama
- All model inference happens locally
- Vector embeddings are stored locally in Qdrant

### When Using Cloud APIs

If configured to use OpenAI-compatible APIs:

- Data flows to the external API provider
- Ensure your organization's data policies allow this
- Consider using Azure OpenAI for enterprise compliance

## Authentication

### API Gateway

When `AUTH_ENABLED=true`:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8080/v1/runs
```

### Service-to-Service

Internal services communicate over the Docker/K8s network without authentication. In production, use:
- Network policies to restrict access
- mTLS for service mesh deployments

## Secrets Management

### Docker Compose

Use `.env` file (never commit to git):

```bash
cp .env.example .env
# Edit .env with secure values
```

### Kubernetes

Use Kubernetes Secrets:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mctagents-secrets
type: Opaque
stringData:
  postgres-password: "secure-password-here"
  api-key: "optional-api-key"
```

## Network Security

### Port Exposure

| Service | Port | Should Expose |
|---------|------|---------------|
| API Gateway | 8080 | Yes (public) |
| Reasoning Engine | 8000 | No (internal) |
| Evidence Service | 8001 | No (internal) |
| Model Gateway | 8090 | No (internal) |
| PostgreSQL | 5432 | No (internal) |
| Qdrant | 6333 | No (internal) |
| Redis | 6379 | No (internal) |
| Ollama | 11434 | No (internal) |

### Firewall Rules

In production, only expose the API Gateway (port 8080) to the internet. All other services should be on an internal network.

## Input Validation

- All protocol objects are validated against JSON schemas
- Pydantic models enforce type safety in Python
- TypeScript types enforce type safety in the frontend
- SQL queries use parameterized statements (asyncpg)

## Rate Limiting

Configure in API Gateway:
- `RATE_LIMIT_RPS`: Requests per second per client (default: 100)

## Audit Logging

All protocol objects are stored with full history in PostgreSQL:
- Every claim, evidence, objection, and revision is persisted
- Events are logged with sequence numbers
- Run metadata tracks creation and completion times
