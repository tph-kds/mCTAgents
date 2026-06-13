# API Contracts and Event Schema

## 1. Public REST API

```http
POST /v1/runs
GET  /v1/runs/{run_id}
GET  /v1/runs/{run_id}/events
POST /v1/runs/{run_id}/cancel
GET  /v1/runs/{run_id}/claim-graph
GET  /v1/runs/{run_id}/evaluation
```

## 2. Create run request

```json
{
  "problem": "Design an open-source social reasoning engine.",
  "mode": "deep_social_reasoning",
  "evidence_policy": "required_for_major_claims",
  "preferred_agents": ["architect", "critic", "evidence", "judge"],
  "budget": {
    "max_tokens": 20000,
    "max_rounds": 2
  }
}
```

## 3. Create run response

```json
{
  "run_id": "run_001",
  "status": "queued",
  "events_url": "/v1/runs/run_001/events"
}
```

## 4. Event schema

```json
{
  "event_id": "evt_001",
  "run_id": "run_001",
  "type": "claim_created",
  "sequence": 12,
  "agent_id": "architect_agent",
  "payload": {
    "claim_id": "claim_001",
    "text": "The system should be protocol-first."
  },
  "created_at": "2026-06-13T00:00:00Z"
}
```

## 5. Event types

```text
run_started
run_failed
run_completed
agent_selected
agent_started
agent_completed
problem_framed
claim_created
evidence_requested
evidence_attached
objection_created
claim_revised
judge_scored
final_answer_created
evaluation_completed
```

## 6. Error model

```json
{
  "error": {
    "code": "MODEL_PROVIDER_TIMEOUT",
    "message": "The selected model provider timed out.",
    "retryable": true,
    "run_id": "run_001",
    "step": "evidence_agent"
  }
}
```
