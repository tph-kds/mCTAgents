# REST API Reference

## Base URL

```
http://localhost:8080
```

## Authentication

Currently disabled. When enabled, use the `X-API-Key` header.

## Endpoints

### Health Check

```
GET /health
```

**Response:**
```json
{"status": "ok", "service": "api-gateway"}
```

### Create Run

```
POST /v1/runs
```

**Request:**
```json
{
  "problem": "Should we adopt microservices?",
  "mode": "balanced_reasoning",
  "evidence_policy": "required_for_major_claims",
  "budget": {
    "max_rounds": 3,
    "max_tokens": 12000,
    "max_model_calls": 16
  }
}
```

**Response:**
```json
{
  "run_id": "run_abc123",
  "status": "queued",
  "events_url": "/v1/runs/run_abc123/events"
}
```

### Get Run

```
GET /v1/runs/{run_id}
```

**Response:**
```json
{
  "run_id": "run_abc123",
  "status": "completed",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

### Stream Events (SSE)

```
GET /v1/runs/{run_id}/events
```

**Event Format:**
```
event: claim_created
data: {"event_id":"evt_001","run_id":"run_abc123","type":"claim_created","sequence":1,"agent_id":"architect","payload":{"claim_id":"c1","text":"..."},"created_at":"2024-01-15T10:30:01Z"}

```

**Event Types:**
- `run_started` - Run begins processing
- `agent_started` - Agent begins work
- `agent_completed` - Agent finishes work
- `claim_created` - New claim proposed
- `claim_revised` - Claim updated
- `evidence_attached` - Evidence linked to claim
- `objection_raised` - Critic challenges claim
- `judge_accepted` - Judge accepts claims
- `run_completed` - Run finished
- `run_failed` - Run encountered error

### Cancel Run

```
POST /v1/runs/{run_id}/cancel
```

**Response:**
```json
{"status": "cancelled"}
```

### List Claims

```
GET /v1/runs/{run_id}/claims
```

**Response:**
```json
{
  "claims": [
    {
      "id": "c1",
      "run_id": "run_abc123",
      "author_agent_id": "architect",
      "text": "...",
      "confidence": 0.8,
      "status": "accepted"
    }
  ]
}
```

### List Evidence

```
GET /v1/runs/{run_id}/evidence
```

### Get Claim Graph

```
GET /v1/runs/{run_id}/claim-graph
```

**Response:**
```json
{
  "run_id": "run_abc123",
  "claims": [...],
  "evidence": [...]
}
```

### Upload Document

```
POST /v1/documents
Content-Type: multipart/form-data
```

**Request:** Multipart form with `file` field.

**Response:**
```json
{
  "document_id": "doc_abc123",
  "filename": "research.pdf",
  "size": 1024000
}
```

### Search Evidence

```
POST /v1/search
```

**Request:**
```json
{
  "query": "microservices deployment frequency",
  "top_k": 5,
  "source_type": "uploaded_document"
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "chunk_001",
      "score": 0.89,
      "content": "...",
      "heading": "Deployment Results",
      "reliability_score": 0.85
    }
  ],
  "query": "microservices deployment frequency",
  "total": 5
}
```

## Error Responses

All errors follow the format:
```json
{"error": "description of the error"}
```

| Status | Description |
|--------|-------------|
| 400 | Bad request (missing fields, invalid JSON) |
| 404 | Resource not found |
| 500 | Internal server error |
| 502 | Backend service unavailable |
