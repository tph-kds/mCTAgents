# Production Deployment

## Docker Compose (Production)

For production deployments without hot-reload:

```bash
docker compose up -d
```

This uses the production targets in each Dockerfile.

## Kubernetes

### Prerequisites

- Kubernetes cluster (1.25+)
- kubectl configured
- Helm 3.x (for Helm deployments)

### Quick Deploy with kubectl

```bash
# Create namespace and secrets
kubectl apply -f deployments/k8s/namespace.yaml
kubectl apply -f deployments/k8s/secrets.yaml

# Deploy infrastructure
kubectl apply -f deployments/k8s/postgres.yaml

# Deploy application services
kubectl apply -f deployments/k8s/api-gateway.yaml
kubectl apply -f deployments/k8s/reasoning-engine.yaml
kubectl apply -f deployments/k8s/evidence-service.yaml
kubectl apply -f deployments/k8s/model-gateway.yaml
```

### Deploy with Helm

```bash
helm install mctagents deployments/helm/mctagents \
  --namespace mctagents \
  --create-namespace \
  --set secrets.postgresPassword=your-secure-password
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://mctagents:devpassword@localhost:5432/mctagents` |
| `OLLAMA_BASE_URL` | Ollama API URL | `http://localhost:11434` |
| `DEFAULT_CHAT_MODEL` | Chat model name | `qwen2.5:7b` |
| `DEFAULT_REASONING_MODEL` | Reasoning model | `deepseek-r1:7b` |
| `DEFAULT_EMBEDDING_MODEL` | Embedding model | `nomic-embed-text` |

### Resource Requirements

| Service | CPU Request | Memory Request | CPU Limit | Memory Limit |
|---------|-------------|----------------|-----------|--------------|
| API Gateway | 100m | 128Mi | 500m | 256Mi |
| Reasoning Engine | 250m | 512Mi | 1000m | 2Gi |
| Evidence Service | 100m | 256Mi | 500m | 1Gi |
| Model Gateway | 100m | 128Mi | 500m | 256Mi |

## Scaling

### Horizontal Pod Autoscaler

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: api-gateway
  namespace: mctagents
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-gateway
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

## Monitoring

### Health Checks

All services expose `/health` endpoints:
- API Gateway: `GET http://localhost:8080/health`
- Reasoning Engine: `GET http://localhost:8000/health`
- Evidence Service: `GET http://localhost:8001/health`

### Prometheus Metrics

TODO: Add OpenTelemetry instrumentation for metrics export.
