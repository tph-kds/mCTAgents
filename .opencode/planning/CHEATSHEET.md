# mCTAgents Quick Reference

## Project At a Glance

**What:** Open-source social reasoning engine where AI agents debate claims to produce transparent, evidence-backed answers.

**How:** CCSR (Claim-Centered Social Reasoning) protocol with structured objects, not chat messages.

**Why:** Transparent, auditable, benchmarkable reasoning that improves with debate.

---

## Agent Society

```
User Problem
    ↓
┌─────────────┐
│ ProblemFramer│ → ProblemFrame
└──────┬──────┘
       ↓
┌─────────────┐
│  Architect   │ → Claims (3-5)
└──────┬──────┘
       ↓
┌─────────────┐
│  Evidence    │ → Evidence attached to claims
└──────┬──────┘
       ↓
┌─────────────┐
│   Critic     │ → Objections
└──────┬──────┘
       ↓
┌─────────────┐
│  Architect   │ → Revised Claims
└──────┬──────┘
       ↓
┌─────────────┐
│    Judge     │ → Accept/Reject/Uncertain
└──────┬──────┘
       ↓ (if more debate needed, loop back)
┌─────────────┐
│ Synthesizer  │ → Final Answer
└─────────────┘
```

## Core Objects

| Object | Purpose |
|--------|---------|
| ProblemFrame | Normalized problem definition |
| Claim | A proposition (the core object) |
| Evidence | Source-backed support/attack |
| Objection | A challenge against a claim |
| Revision | Claim improvement |
| Decision | Judge accept/reject output |
| FinalAnswer | Synthesized answer |

## Claim Status Flow

```
proposed → evidence_requested → supported → challenged
    → revision_required → revised → accepted | rejected | uncertain
```

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js, TypeScript, Tailwind, React Flow |
| API Gateway | Go, chi router, SSE |
| Reasoning Engine | Python, FastAPI, Pydantic |
| Model Gateway | Go, Ollama, OpenAI-compatible |
| Evidence Service | Python, Qdrant, PyMuPDF |
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Vector DB | Qdrant |
| LLM | Ollama (local-first) |

## Key Commands

```bash
make dev              # Start all services
make test             # Run all tests
make lint             # Run all linters
make seed-demo        # Populate demo data
make docker-up        # Start Docker Compose
make docker-down      # Stop Docker Compose
```

## Testing

```bash
# Python
pytest                          # All tests
pytest tests/unit/              # Unit only
pytest tests/unit/test_claim.py # Single file
pytest -x                       # Stop on first failure

# Go
go test ./...

# TypeScript
pnpm test
```

## API Endpoints

```
POST /v1/runs                    Create run
GET  /v1/runs/{id}               Get run
GET  /v1/runs/{id}/events        SSE stream
POST /v1/runs/{id}/cancel        Cancel run
GET  /v1/runs/{id}/claim-graph   Get claim graph
GET  /v1/runs/{id}/claims        List claims
GET  /v1/runs/{id}/evidence      List evidence
POST /v1/documents               Upload document
GET  /health                     Health check
```

## Invariants

1. Final answers reference accepted claims only
2. High-confidence claims need evidence
3. Rejected claims have reasons
4. Revisions link old and new claims
5. Tool results are traceable
6. Final answers declare risks

## File Structure

```
mctagents/
├── AGENTS.md                  # Agent instructions
├── planning/                  # Implementation plan
│   ├── IMPLEMENTATION_PLAN.md # Full 4000+ line plan
│   ├── ROADMAP.md             # Timeline
│   ├── decisions/             # ADRs
│   └── STEP_*.md              # Step breakdowns
├── rules/                     # Coding rules
├── skills/                    # Agent skills
├── packages/core-protocol/    # Schemas + types
├── services/
│   ├── api-gateway/           # Go REST/SSE
│   ├── reasoning-engine/      # Python agents
│   ├── model-gateway/         # Go LLM proxy
│   └── evidence-service/      # Python RAG
├── apps/studio/               # Next.js frontend
└── benchmarks/                # Evaluation suite
```
