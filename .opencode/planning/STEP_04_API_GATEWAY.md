# STEP 4: API Gateway

**Timeline:** Days 10-18 | **Complexity:** 3/5 | **Dependencies:** STEPs 0, 1

## Goal

Go REST/SSE API handling HTTP routing, authentication, rate limiting, and real-time event streaming.

## REST Endpoints

```
POST   /v1/runs                        # Create a new run
GET    /v1/runs/{run_id}               # Get run status
GET    /v1/runs/{run_id}/events        # SSE event stream
POST   /v1/runs/{run_id}/cancel        # Cancel a run
GET    /v1/runs/{run_id}/claim-graph   # Get claim graph
GET    /v1/runs/{run_id}/evaluation    # Get evaluation
GET    /v1/runs/{run_id}/claims        # List claims
GET    /v1/claims/{claim_id}           # Get claim details
GET    /v1/claims/{claim_id}/lineage   # Get claim history
GET    /v1/runs/{run_id}/evidence      # List evidence
POST   /v1/documents                   # Upload document
GET    /health                         # Health check
```

## SSE Event Types

```
run_started, problem_framed, claim_created,
evidence_attached, objection_created, claim_revised,
judge_scored, final_answer_created, run_completed
```

## Middleware Stack

1. **Recovery** - Panic recovery
2. **Logging** - Request/response logging
3. **CORS** - Cross-origin resource sharing
4. **Rate Limit** - Per-tenant rate limiting
5. **Auth** - API key or Bearer token

## Files
```
services/api-gateway/
├── internal/server/     # Routes, handlers
├── internal/streaming/  # SSE hub
├── internal/handlers/   # Runs, events, claims, evidence
├── internal/middleware/  # Auth, rate limit, CORS
└── internal/storage/    # PostgreSQL queries
```

## Success Criteria
- [ ] All REST endpoints implemented
- [ ] SSE streaming delivers events real-time
- [ ] Authentication blocks unauthorized requests
- [ ] Rate limiting prevents abuse
- [ ] Input validation against protocol schemas
- [ ] Graceful shutdown
