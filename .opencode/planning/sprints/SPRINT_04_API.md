# Sprint 04: API Gateway

**Duration:** Days 10-18 | **Goal:** Go REST API, SSE streaming, authentication, rate limiting

## Tasks

### Day 10-12: Server Setup + Routes
- [ ] Initialize Go module
- [ ] Set up chi router
- [ ] Create `POST /v1/runs` endpoint
- [ ] Create `GET /v1/runs/{run_id}` endpoint
- [ ] Create `GET /v1/runs/{run_id}/events` (SSE)
- [ ] Create `POST /v1/runs/{run_id}/cancel` endpoint
- [ ] Create `GET /v1/runs/{run_id}/claim-graph` endpoint
- [ ] Create `GET /v1/runs/{run_id}/evaluation` endpoint
- [ ] Create `GET /v1/runs/{run_id}/claims` endpoint
- [ ] Create `GET /v1/claims/{claim_id}` endpoint
- [ ] Create `GET /v1/claims/{claim_id}/lineage` endpoint
- [ ] Create `GET /v1/runs/{run_id}/evidence` endpoint
- [ ] Create `POST /v1/documents` endpoint
- [ ] Create `GET /health` endpoint
- [ ] Write handler tests

### Day 13-14: SSE Streaming
- [ ] Implement `SSEHub` with client management
- [ ] Implement `Subscribe()`, `Publish()`, `Unsubscribe()`
- [ ] Implement `HandleSSE()` handler with streaming
- [ ] Handle client disconnect gracefully
- [ ] Integrate with reasoning engine event emission
- [ ] Test SSE delivery and reconnection

### Day 15-16: Middleware
- [ ] Implement `Recovery` middleware (panic recovery)
- [ ] Implement `Logging` middleware (request/response)
- [ ] Implement `CORS` middleware
- [ ] Implement `RateLimit` middleware (per-tenant)
- [ ] Implement `Auth` middleware (API key + Bearer token)
- [ ] Write middleware tests

### Day 17-18: Storage + Integration
- [ ] Implement PostgreSQL queries for runs, claims, evidence
- [ ] Implement input validation against protocol schemas
- [ ] Integrate with reasoning engine service
- [ ] Run full integration test (HTTP → PostgreSQL)
- [ ] Test graceful shutdown
- [ ] Write Dockerfile

## Definition of Done
- [ ] All REST endpoints implemented and returning correct responses
- [ ] SSE streaming delivers events in real-time
- [ ] Authentication blocks unauthorized requests
- [ ] Rate limiting prevents abuse
- [ ] All handlers validate input against protocol schemas
- [ ] Graceful shutdown handles in-flight requests

## Risks
- **SSE connection limits:** Use connection pooling
- **PostgreSQL connection limits:** Use connection pooling

## Retro Notes
- _To be filled after sprint completion_
