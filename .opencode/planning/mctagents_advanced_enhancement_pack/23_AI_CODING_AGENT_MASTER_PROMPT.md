# Master Prompt for AI Coding Agent to Build mCTAgents MVP

## Purpose

Use this prompt in an AI coding tool to start implementing the MVP.

## Prompt

You are an expert AI systems architect and full-stack engineer. Build the MVP of **mCTAgents**, an open-source social reasoning engine for AI-native products.

The project must implement a claim-centered social reasoning workflow, not a normal chatbot. Agents must operate on structured objects:

```text
ProblemFrame, Claim, Evidence, Objection, Revision, Decision, FinalAnswer
```

## Required MVP architecture

```text
apps/studio               Next.js frontend
services/api-gateway      Go REST/SSE API
services/reasoning-engine Python agent workflow
services/model-gateway    provider abstraction with Ollama first
services/evidence-service simple document retrieval placeholder
packages/core-protocol    JSON schemas and TypeScript types
```

## Required workflow

```text
User submits problem
API creates run
Reasoning engine frames problem
Architect agent proposes claims
Evidence agent attaches evidence or marks unsupported
Critic agent creates objections
Architect revises claims
Judge scores and accepts/rejects claims
Synthesizer creates final answer
UI streams events and shows timeline
```

## Required event stream

Implement SSE endpoint:

```http
GET /v1/runs/{run_id}/events
```

Events:

```text
run_started
problem_framed
claim_created
evidence_attached
objection_created
claim_revised
judge_scored
final_answer_created
run_completed
```

## Required UI

Build:

```text
NewSessionForm
AgentSocietyBar
DebateTimeline
ClaimGraphPanel
EvidenceBoard
FinalAnswerPanel
```

## Required quality rules

```text
No raw hidden reasoning in UI.
Show safe structured summaries only.
Validate JSON outputs.
Store all claims/evidence/objections in Postgres.
Use Ollama as default model provider.
Use Docker Compose for local run.
```

## Deliverables

```text
working docker-compose.yml
README.md quickstart
API docs
seed demo
unit tests for schemas
one successful end-to-end run
```

Start by creating the monorepo structure, then implement the core protocol schemas, then the API, then the reasoning workflow, then streaming UI.
