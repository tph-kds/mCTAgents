# Microservices and Durable Workflow Strategy

## 1. Starting principle

Do not begin with too many microservices. Start with a modular service set, then split when boundaries stabilize.

## 2. MVP service set

```text
studio-web
api-gateway
reasoning-engine
model-gateway
evidence-service
postgres
redis
qdrant
ollama
```

## 3. Enhanced service set

```text
api-gateway
identity-service
project-service
run-service
reasoning-engine
debate-policy-service
evidence-service
memory-service
tool-gateway
model-gateway
evaluation-service
trace-service
notification-service
billing/usage-service later
```

## 4. Communication patterns

| Use case | Pattern |
|---|---|
| User creates run | REST |
| UI receives live events | SSE first, WebSocket later |
| Agent step emits event | Event bus |
| Long workflow step | Queue/durable workflow |
| Model call | Internal HTTP/gRPC |
| Tool call | Tool gateway + policy check |
| Trace export | OpenTelemetry |

## 5. Durable execution

Long social reasoning runs can fail halfway due to model errors, retrieval failures, timeouts, or deployment restarts. Add durability progressively:

```text
Phase 1: Postgres run state + retry simple failed calls
Phase 2: outbox/inbox + idempotency keys
Phase 3: durable workflow engine such as Temporal
Phase 4: replayable run recovery and partial resume
```

## 6. Data consistency

Use database-per-domain only after boundaries stabilize. For MVP, one Postgres database with schemas is simpler.

```text
schema_runs
schema_claims
schema_evidence
schema_users
schema_audit
schema_evaluation
```

## 7. Event bus

For local MVP:

```text
Redis Streams or NATS
```

For production:

```text
NATS JetStream for simplicity
Kafka/Redpanda for very high-scale event history
```

## 8. Reliability checklist

```text
- idempotency key for run creation
- idempotency key for agent step execution
- retry policy per tool/model call
- circuit breaker for model providers
- dead-letter queue for failed events
- timeout budget per run
- cancellation API
- health checks and readiness probes
- graceful shutdown for running steps
```
