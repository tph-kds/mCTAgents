# mCTAgents: Comprehensive Implementation Plan — Zero to Production

> **Mission:** Build an open-source social reasoning infrastructure where a society of agents can propose claims, attach evidence, challenge assumptions, revise weak reasoning, and converge into a final answer that is transparent, auditable, and benchmarkable.

---

## Table of Contents

- [STEP 0: Project Foundation](#step-0-project-foundation)
- [STEP 1: Core Protocol Layer](#step-1-core-protocol-layer)
- [STEP 2: Model Gateway](#step-2-model-gateway)
- [STEP 3: Reasoning Engine (Python)](#step-3-reasoning-engine-python)
- [STEP 4: API Gateway (Go)](#step-4-api-gateway-go)
- [STEP 5: Evidence Service](#step-5-evidence-service)
- [STEP 6: Frontend (Next.js)](#step-6-frontend-nextjs)
- [STEP 7: SDK Packages](#step-7-sdk-packages)
- [STEP 8: Evaluation & Benchmarks](#step-8-evaluation--benchmarks)
- [STEP 9: Production Readiness](#step-9-production-readiness)
- [STEP 10: Community & Ecosystem](#step-10-community--ecosystem)

---

## STEP 0: Project Foundation

**Estimated Complexity:** 3/5  
**Dependencies:** None (starting point)  
**Timeline:** Days 1–5

### 0.1 What to Build

The foundation creates the monorepo skeleton, tooling configuration, and database schema that every subsequent step builds upon. Nothing can be built without this.

#### Files to Create

```
mctagents/
├── Makefile
├── docker-compose.yml
├── docker-compose.override.yml
├── .env.example
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── release.yml
├── packages/
│   └── core-protocol/
│       ├── package.json
│       ├── tsconfig.json
│       ├── src/
│       │   └── index.ts
│       └── schemas/
│           ├── problem-frame.json
│           ├── claim.json
│           ├── evidence.json
│           ├── objection.json
│           ├── revision.json
│           ├── decision.json
│           ├── final-answer.json
│           ├── event.json
│           ├── run-state.json
│           ├── debate-policy.json
│           └── agent-contract.json
├── services/
│   ├── api-gateway/
│   │   ├── go.mod
│   │   └── go.sum
│   ├── reasoning-engine/
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── mctagents/
│   │   │       ├── __init__.py
│   │   │       └── core/
│   │   └── tests/
│   ├── model-gateway/
│   │   └── go.mod
│   └── evidence-service/
│       └── pyproject.toml
├── apps/
│   ├── studio/
│   │   ├── package.json
│   │   └── tsconfig.json
│   └── playground/
├── deployments/
│   └── docker-compose/
├── scripts/
│   ├── seed-demo.sh
│   └── setup-dev.sh
└── docs/
```

### 0.2 Technology Choices and Why

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Monorepo root | `Makefile` + `docker-compose.yml` | No heavy monorepo tool needed for MVP; Make provides unified commands, Docker Compose orchestrates services |
| Protocol schemas | JSON Schema + TypeScript types | JSON Schema is language-agnostic; TypeScript types enable frontend validation; Python Pydantic models generated from same source |
| Database | PostgreSQL 16 | Structured data, JSONB for flexible fields, proven reliability, native PostGIS if geospatial needed later |
| Message bus | Redis Streams | Lightweight for MVP, sufficient for event streaming, easy to upgrade to NATS/Kafka later |
| Python packaging | `pyproject.toml` with `uv` | Modern Python packaging, fast dependency resolution, compatible with PEP 621 |
| Go modules | `go.mod` | Standard Go dependency management |
| Node.js | `pnpm` workspaces | Efficient monorepo package management, strict dependency resolution |
| Docker | Multi-stage builds | Small images, reproducible builds, dev and prod targets |

### 0.3 Makefile Design

```makefile
# Top-level Makefile
.PHONY: dev test lint docker-up docker-down seed-demo

dev:
	docker compose -f docker-compose.yml -f docker-compose.override.yml up

docker-up:
	docker compose up -d

docker-down:
	docker compose down

test:
	cd packages/core-protocol && pnpm test
	cd services/reasoning-engine && pytest -v
	cd services/api-gateway && go test ./...
	cd apps/studio && pnpm test

lint:
	ruff check services/reasoning-engine/
	ruff check services/evidence-service/
	cd packages/core-protocol && pnpm lint
	cd apps/studio && pnpm lint
	cd services/api-gateway && golangci-lint run

seed-demo:
	bash scripts/seed-demo.sh

benchmark-smoke:
	cd benchmarks && python -m pytest smoke/ -v

format:
	ruff format services/reasoning-engine/ services/evidence-service/
	cd packages/core-protocol && pnpm format
	cd apps/studio && pnpm format
	gofmt -w services/api-gateway/

migrate:
	cd services/reasoning-engine && alembic upgrade head
```

### 0.4 Docker Compose Design

```yaml
# docker-compose.yml
services:
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: mctagents
      POSTGRES_USER: mctagents
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-devpassword}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U mctagents"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://localhost:6333/healthz || exit 1"]
      interval: 10s
      timeout: 5s
      retries: 3

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

volumes:
  pgdata:
  qdrant_data:
  ollama_data:
```

### 0.5 Database Schema Design (PostgreSQL)

```sql
-- Core schema for CCSR protocol objects

-- Run: a single social reasoning session
CREATE TABLE runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
    status VARCHAR(32) NOT NULL DEFAULT 'queued',
    -- queued, framing, debating, judging, synthesizing, completed, failed, cancelled
    mode VARCHAR(64) NOT NULL DEFAULT 'balanced_reasoning',
    evidence_policy VARCHAR(64) NOT NULL DEFAULT 'required_for_major_claims',
    budget_config JSONB NOT NULL DEFAULT '{}',
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ
);

CREATE INDEX idx_runs_tenant ON runs(tenant_id);
CREATE INDEX idx_runs_status ON runs(status);
CREATE INDEX idx_runs_created ON runs(created_at DESC);

-- ProblemFrame: normalized problem definition
CREATE TABLE problem_frames (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    original_input TEXT NOT NULL,
    normalized_problem TEXT NOT NULL,
    constraints JSONB NOT NULL DEFAULT '[]',
    success_criteria JSONB NOT NULL DEFAULT '[]',
    risk_level VARCHAR(16) NOT NULL DEFAULT 'medium',
    domain VARCHAR(64),
    requires_business_decision BOOLEAN DEFAULT FALSE,
    requires_research BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_problem_frames_run ON problem_frames(run_id);

-- Claim: a proposition
CREATE TABLE claims (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    author_agent_id VARCHAR(64) NOT NULL,
    text TEXT NOT NULL,
    claim_type VARCHAR(64) NOT NULL DEFAULT 'general',
    confidence FLOAT NOT NULL DEFAULT 0.5,
    status VARCHAR(32) NOT NULL DEFAULT 'proposed',
    requires_evidence BOOLEAN DEFAULT FALSE,
    evidence_status VARCHAR(32) DEFAULT 'unsupported',
    parent_claim_id UUID REFERENCES claims(id),
    rejection_reason TEXT,
    score_logic FLOAT,
    score_evidence FLOAT,
    score_feasibility FLOAT,
    score_critic_resistance FLOAT,
    score_risk_adjusted FLOAT,
    score_final FLOAT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_claims_run ON claims(run_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_claims_parent ON claims(parent_claim_id);

-- Argument edges: relationships between claims and other objects
CREATE TABLE argument_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    source_type VARCHAR(32) NOT NULL,
    source_id UUID NOT NULL,
    target_type VARCHAR(32) NOT NULL,
    target_id UUID NOT NULL,
    edge_type VARCHAR(32) NOT NULL,
    -- PROPOSED, SUPPORTS, ATTACKS, REVISED_INTO, ACCEPTED, REJECTED, USES, PRODUCED, BACKS
    weight FLOAT DEFAULT 1.0,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_argument_edges_run ON argument_edges(run_id);
CREATE INDEX idx_argument_edges_source ON argument_edges(source_type, source_id);
CREATE INDEX idx_argument_edges_target ON argument_edges(target_type, target_id);

-- Evidence: source-backed support or attack item
CREATE TABLE evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    source_type VARCHAR(64) NOT NULL,
    source_ref TEXT,
    summary TEXT NOT NULL,
    full_text TEXT,
    reliability_score FLOAT NOT NULL DEFAULT 0.5,
    source_authority FLOAT,
    recency FLOAT,
    specificity FLOAT,
    independence FLOAT,
    retrieval_confidence FLOAT,
    chunk_id UUID,
    document_id UUID,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_evidence_run ON evidence(run_id);
CREATE INDEX idx_evidence_document ON evidence(document_id);

-- Objection: a challenge against a claim
CREATE TABLE objections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    target_claim_id UUID NOT NULL REFERENCES claims(id),
    author_agent_id VARCHAR(64) NOT NULL,
    reason TEXT NOT NULL,
    severity VARCHAR(16) NOT NULL DEFAULT 'medium',
    requested_fix TEXT,
    resolved BOOLEAN DEFAULT FALSE,
    resolution_claim_id UUID REFERENCES claims(id),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_objections_run ON objections(run_id);
CREATE INDEX idx_objections_target ON objections(target_claim_id);

-- Revision: claim improvement caused by objections or evidence
CREATE TABLE revisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    old_claim_id UUID NOT NULL REFERENCES claims(id),
    new_claim_id UUID NOT NULL REFERENCES claims(id),
    reason TEXT NOT NULL,
    revision_type VARCHAR(32) NOT NULL DEFAULT 'objection_driven',
    improvement_score FLOAT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_revisions_run ON revisions(run_id);
CREATE INDEX idx_revisions_old_claim ON revisions(old_claim_id);
CREATE INDEX idx_revisions_new_claim ON revisions(new_claim_id);

-- Decision: judge output selecting accepted/rejected claims
CREATE TABLE decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    accepted_claim_ids UUID[] NOT NULL DEFAULT '{}',
    rejected_claim_ids UUID[] NOT NULL DEFAULT '{}',
    uncertain_claim_ids UUID[] NOT NULL DEFAULT '{}',
    score_breakdown JSONB NOT NULL DEFAULT '{}',
    confidence FLOAT NOT NULL DEFAULT 0.5,
    needs_more_debate BOOLEAN DEFAULT FALSE,
    extra_debate_reason TEXT,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_decisions_run ON decisions(run_id);

-- FinalAnswer: synthesized answer referencing accepted claims
CREATE TABLE final_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    answer_text TEXT NOT NULL,
    accepted_claim_ids UUID[] NOT NULL DEFAULT '{}',
    rejected_alternatives JSONB NOT NULL DEFAULT '[]',
    risks JSONB NOT NULL DEFAULT '[]',
    next_steps JSONB NOT NULL DEFAULT '[]',
    confidence FLOAT NOT NULL DEFAULT 0.5,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_final_answers_run ON final_answers(run_id);

-- Events: immutable event log for reasoning trace
CREATE TABLE events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_id VARCHAR(128) NOT NULL UNIQUE,
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    sequence INTEGER NOT NULL,
    type VARCHAR(64) NOT NULL,
    agent_id VARCHAR(64),
    payload JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_events_run ON events(run_id);
CREATE INDEX idx_events_type ON events(type);
CREATE INDEX idx_events_sequence ON events(run_id, sequence);

-- Documents: uploaded documents for evidence retrieval
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
    filename TEXT NOT NULL,
    content_type VARCHAR(128),
    size_bytes BIGINT,
    status VARCHAR(32) NOT NULL DEFAULT 'uploaded',
    chunk_count INTEGER DEFAULT 0,
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_documents_tenant ON documents(tenant_id);

-- Document chunks: for vector search
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    heading TEXT,
    page INTEGER,
    section TEXT,
    token_count INTEGER,
    embedding_id VARCHAR(128),
    metadata JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_document_chunks_document ON document_chunks(document_id);

-- Audit log: immutable audit trail
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL DEFAULT '00000000-0000-0000-0000-000000000000',
    actor VARCHAR(128) NOT NULL,
    action VARCHAR(64) NOT NULL,
    resource_type VARCHAR(64) NOT NULL,
    resource_id UUID,
    details JSONB NOT NULL DEFAULT '{}',
    ip_address INET,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_actor ON audit_logs(actor);
CREATE INDEX idx_audit_logs_created ON audit_logs(created_at DESC);

-- Traces: OpenTelemetry trace spans
CREATE TABLE traces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    trace_id VARCHAR(64) NOT NULL,
    span_id VARCHAR(64) NOT NULL,
    parent_span_id VARCHAR(64),
    operation_name VARCHAR(128) NOT NULL,
    service_name VARCHAR(64) NOT NULL,
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    duration_ms INTEGER,
    status VARCHAR(16) NOT NULL DEFAULT 'ok',
    attributes JSONB NOT NULL DEFAULT '{}',
    events JSONB NOT NULL DEFAULT '[]'
);

CREATE INDEX idx_traces_run ON traces(run_id);
CREATE INDEX idx_traces_trace ON traces(trace_id);
```

### 0.6 Key Implementation Details

1. **Monorepo initialization:** Use `pnpm-workspace.yaml` for TypeScript packages. Each service has its own dependency manifest.
2. **Environment configuration:** `.env.example` documents all required variables. Docker Compose reads `.env` for local overrides.
3. **Database migrations:** Use Alembic for Python services, `golang-migrate` for Go services. Initial migration creates all tables above.
4. **Seed data:** `scripts/seed-demo.sh` creates a sample run with pre-populated claims for quick UI testing.

### 0.7 Testing Strategy

- **Schema validation tests:** Every JSON schema has positive and negative test cases
- **Database migration tests:** Forward and backward migration tests
- **Docker Compose smoke test:** `make docker-up` succeeds, all healthchecks pass
- **Makefile test targets:** All targets execute without error

### 0.8 Success Criteria

- [ ] `make docker-up` starts PostgreSQL, Redis, Qdrant, Ollama
- [ ] All healthchecks pass within 30 seconds
- [ ] `make seed-demo` populates database with sample data
- [ ] `make lint` passes on all services
- [ ] `make test` passes on core-protocol schemas
- [ ] All JSON schemas are valid JSON Schema Draft 2020-12

---

## STEP 1: Core Protocol Layer

**Estimated Complexity:** 3/5  
**Dependencies:** STEP 0  
**Timeline:** Days 3–8 (overlaps with end of STEP 0)

### 1.1 What to Build

The CCSR (Claim-Centered Social Reasoning) protocol defines every structured object in the system. This is the source of truth that all services implement against.

#### Files to Create

```
packages/core-protocol/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts
│   ├── types/
│   │   ├── problem-frame.ts
│   │   ├── claim.ts
│   │   ├── evidence.ts
│   │   ├── objection.ts
│   │   ├── revision.ts
│   │   ├── decision.ts
│   │   ├── final-answer.ts
│   │   ├── event.ts
│   │   ├── run-state.ts
│   │   ├── debate-policy.ts
│   │   ├── agent-contract.ts
│   │   └── index.ts
│   ├── validation/
│   │   ├── validator.ts
│   │   └── schemas.ts
│   └── constants/
│       ├── claim-statuses.ts
│       ├── event-types.ts
│       ├── agent-ids.ts
│       └── index.ts
├── schemas/
│   ├── problem-frame.json
│   ├── claim.json
│   ├── evidence.json
│   ├── objection.json
│   ├── revision.json
│   ├── decision.json
│   ├── final-answer.json
│   ├── event.json
│   ├── run-state.json
│   ├── debate-policy.json
│   └── agent-contract.json
├── tests/
│   ├── validation.test.ts
│   ├── claim.test.ts
│   ├── event.test.ts
│   └── invariants.test.ts
└── scripts/
    └── generate-types.ts
```

### 1.2 Protocol Objects — Complete Definition

#### ProblemFrame

```typescript
interface ProblemFrame {
  id: string;                      // "pf_{uuid}"
  run_id: string;                  // "run_{uuid}"
  original_input: string;
  normalized_problem: string;
  constraints: string[];
  success_criteria: string[];
  risk_level: "low" | "medium" | "high" | "critical";
  domain?: string;
  requires_business_decision: boolean;
  requires_research: boolean;
  requires_code: boolean;
  created_at: string;
}
```

#### Claim

```typescript
interface Claim {
  id: string;                      // "claim_{uuid}"
  run_id: string;
  author_agent_id: string;
  text: string;
  claim_type: ClaimType;
  confidence: number;              // 0.0 to 1.0
  status: ClaimStatus;
  requires_evidence: boolean;
  evidence_status: EvidenceStatus;
  parent_claim_id?: string;
  rejection_reason?: string;
  scores?: ClaimScores;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

type ClaimType =
  | "general"
  | "architecture_decision"
  | "technical_approach"
  | "risk_assessment"
  | "tradeoff_analysis"
  | "recommendation"
  | "factual"
  | "opinion";

type ClaimStatus =
  | "proposed"
  | "evidence_requested"
  | "supported"
  | "challenged"
  | "revision_required"
  | "revised"
  | "accepted"
  | "rejected"
  | "uncertain";

type EvidenceStatus = "unsupported" | "partial" | "supported" | "over-supported";

interface ClaimScores {
  logic: number;
  evidence: number;
  feasibility: number;
  critic_resistance: number;
  risk_adjusted: number;
  final: number;
}
```

#### Evidence

```typescript
interface Evidence {
  id: string;                      // "ev_{uuid}"
  run_id: string;
  source_type: SourceType;
  source_ref?: string;
  summary: string;
  full_text?: string;
  reliability_score: number;
  source_authority?: number;
  recency?: number;
  specificity?: number;
  independence?: number;
  retrieval_confidence?: number;
  supports_claim_ids: string[];
  attacks_claim_ids: string[];
  chunk_id?: string;
  document_id?: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

type SourceType =
  | "uploaded_document"
  | "official_documentation"
  | "web_source"
  | "academic_paper"
  | "github_repository"
  | "code_execution_result"
  | "database_result"
  | "internal_memory"
  | "human_confirmation"
  | "benchmark_result";
```

#### Objection

```typescript
interface Objection {
  id: string;                      // "obj_{uuid}"
  run_id: string;
  target_claim_id: string;
  author_agent_id: string;
  reason: string;
  severity: "low" | "medium" | "high" | "critical";
  requested_fix?: string;
  resolved: boolean;
  resolution_claim_id?: string;
  metadata: Record<string, unknown>;
  created_at: string;
}
```

#### Revision

```typescript
interface Revision {
  id: string;                      // "rev_{uuid}"
  run_id: string;
  old_claim_id: string;
  new_claim_id: string;
  reason: string;
  revision_type: RevisionType;
  improvement_score?: number;
  metadata: Record<string, unknown>;
  created_at: string;
}

type RevisionType =
  | "objection_driven"
  | "evidence_driven"
  | "judge_feedback"
  | "self_improvement";
```

#### Decision

```typescript
interface Decision {
  id: string;                      // "dec_{uuid}"
  run_id: string;
  accepted_claim_ids: string[];
  rejected_claim_ids: string[];
  uncertain_claim_ids: string[];
  score_breakdown: Record<string, number>;
  confidence: number;
  needs_more_debate: boolean;
  extra_debate_reason?: string;
  metadata: Record<string, unknown>;
  created_at: string;
}
```

#### FinalAnswer

```typescript
interface FinalAnswer {
  id: string;                      // "fa_{uuid}"
  run_id: string;
  answer_text: string;
  accepted_claim_ids: string[];
  rejected_alternatives: RejectedAlternative[];
  risks: RiskItem[];
  next_steps: string[];
  confidence: number;
  metadata: Record<string, unknown>;
  created_at: string;
}

interface RejectedAlternative {
  claim_id: string;
  reason: string;
}

interface RiskItem {
  description: string;
  severity: "low" | "medium" | "high";
  mitigation?: string;
}
```

#### Event

```typescript
interface ReasoningEvent {
  event_id: string;
  run_id: string;
  sequence: number;
  type: EventType;
  agent_id?: string;
  payload: EventPayload;
  created_at: string;
}

type EventType =
  | "run_started"
  | "run_failed"
  | "run_completed"
  | "run_cancelled"
  | "agent_selected"
  | "agent_started"
  | "agent_completed"
  | "agent_error"
  | "problem_framed"
  | "claim_created"
  | "claim_updated"
  | "evidence_requested"
  | "evidence_attached"
  | "objection_created"
  | "objection_resolved"
  | "claim_revised"
  | "judge_scored"
  | "judge_escalated"
  | "final_answer_created"
  | "evaluation_completed"
  | "tool_called"
  | "tool_result";
```

#### DebatePolicy

```typescript
interface DebatePolicy {
  id: string;
  name: string;
  agents: string[];
  max_rounds: number;
  require_evidence: EvidenceRequirement;
  judge_confidence_threshold: number;
  escalation_threshold: number;
  max_tokens: number;
  max_model_calls: number;
  max_tool_calls: number;
  max_runtime_seconds: number;
  use_case: string;
}

type EvidenceRequirement =
  | "none"
  | "optional"
  | "required_for_major_claims"
  | "required_for_all"
  | "strict";
```

### 1.3 JSON Schema Validation

Each protocol object has a JSON Schema in `packages/core-protocol/schemas/`. Example for Claim:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://mctagents.dev/schemas/claim.json",
  "title": "Claim",
  "description": "A proposition that can be supported, attacked, revised, accepted, or rejected.",
  "type": "object",
  "required": ["id", "run_id", "author_agent_id", "text", "claim_type", "confidence", "status", "created_at", "updated_at"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^claim_[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"
    },
    "run_id": {
      "type": "string",
      "pattern": "^run_[0-9a-f]{8}-"
    },
    "author_agent_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 64
    },
    "text": {
      "type": "string",
      "minLength": 1,
      "maxLength": 10000
    },
    "claim_type": {
      "type": "string",
      "enum": ["general", "architecture_decision", "technical_approach", "risk_assessment", "tradeoff_analysis", "recommendation", "factual", "opinion"]
    },
    "confidence": {
      "type": "number",
      "minimum": 0.0,
      "maximum": 1.0
    },
    "status": {
      "type": "string",
      "enum": ["proposed", "evidence_requested", "supported", "challenged", "revision_required", "revised", "accepted", "rejected", "uncertain"]
    },
    "requires_evidence": { "type": "boolean" },
    "evidence_status": {
      "type": "string",
      "enum": ["unsupported", "partial", "supported", "over-supported"]
    },
    "parent_claim_id": { "type": ["string", "null"] },
    "rejection_reason": { "type": ["string", "null"] },
    "metadata": { "type": "object" },
    "created_at": { "type": "string", "format": "date-time" },
    "updated_at": { "type": "string", "format": "date-time" }
  }
}
```

### 1.4 TypeScript Type Generation

Types are hand-written in `src/types/` for developer experience. A script can optionally validate they match JSON Schemas:

```typescript
// packages/core-protocol/src/types/claim.ts
export interface Claim {
  id: string;
  run_id: string;
  author_agent_id: string;
  text: string;
  claim_type: ClaimType;
  confidence: number;
  status: ClaimStatus;
  requires_evidence: boolean;
  evidence_status: EvidenceStatus;
  parent_claim_id?: string;
  rejection_reason?: string;
  scores?: ClaimScores;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export type ClaimType =
  | "general"
  | "architecture_decision"
  | "technical_approach"
  | "risk_assessment"
  | "tradeoff_analysis"
  | "recommendation"
  | "factual"
  | "opinion";

export type ClaimStatus =
  | "proposed"
  | "evidence_requested"
  | "supported"
  | "challenged"
  | "revision_required"
  | "revised"
  | "accepted"
  | "rejected"
  | "uncertain";

export type EvidenceStatus = "unsupported" | "partial" | "supported" | "over-supported";

export interface ClaimScores {
  logic: number;
  evidence: number;
  feasibility: number;
  critic_resistance: number;
  risk_adjusted: number;
  final: number;
}
```

### 1.5 Python Pydantic Models

Generate or hand-write Pydantic v2 models that mirror the TypeScript types exactly:

```python
# services/reasoning-engine/src/mctagents/core/protocol/claim.py
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
from typing import Optional


class ClaimType(str, Enum):
    GENERAL = "general"
    ARCHITECTURE_DECISION = "architecture_decision"
    TECHNICAL_APPROACH = "technical_approach"
    RISK_ASSESSMENT = "risk_assessment"
    TRADEOFF_ANALYSIS = "tradeoff_analysis"
    RECOMMENDATION = "recommendation"
    FACTUAL = "factual"
    OPINION = "opinion"


class ClaimStatus(str, Enum):
    PROPOSED = "proposed"
    EVIDENCE_REQUESTED = "evidence_requested"
    SUPPORTED = "supported"
    CHALLENGED = "challenged"
    REVISION_REQUIRED = "revision_required"
    REVISED = "revised"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    UNCERTAIN = "uncertain"


class EvidenceStatus(str, Enum):
    UNSUPPORTED = "unsupported"
    PARTIAL = "partial"
    SUPPORTED = "supported"
    OVER_SUPPORTED = "over-supported"


class ClaimScores(BaseModel):
    logic: float = Field(ge=0.0, le=1.0)
    evidence: float = Field(ge=0.0, le=1.0)
    feasibility: float = Field(ge=0.0, le=1.0)
    critic_resistance: float = Field(ge=0.0, le=1.0)
    risk_adjusted: float = Field(ge=0.0, le=1.0)
    final: float = Field(ge=0.0, le=1.0)


class Claim(BaseModel):
    id: str = Field(pattern=r"^claim_[0-9a-f-]+$")
    run_id: str = Field(pattern=r"^run_[0-9a-f-]+$")
    author_agent_id: str = Field(min_length=1, max_length=64)
    text: str = Field(min_length=1, max_length=10000)
    claim_type: ClaimType = ClaimType.GENERAL
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)
    status: ClaimStatus = ClaimStatus.PROPOSED
    requires_evidence: bool = False
    evidence_status: EvidenceStatus = EvidenceStatus.UNSUPPORTED
    parent_claim_id: Optional[str] = None
    rejection_reason: Optional[str] = None
    scores: Optional[ClaimScores] = None
    metadata: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

### 1.6 Required Invariants (Enforced in Validation)

```typescript
// packages/core-protocol/src/validation/validator.ts
export interface InvariantCheck {
  name: string;
  description: string;
  check: (context: RunContext) => InvariantResult;
}

interface InvariantResult {
  passed: boolean;
  violations: string[];
}

export const REQUIRED_INVARIANTS: InvariantCheck[] = [
  {
    name: "final_answer_references_accepted_claims",
    description: "Final answers must reference accepted claims",
    check: (ctx) => {
      const violations: string[] = [];
      for (const fa of ctx.finalAnswers) {
        for (const claimId of fa.accepted_claim_ids) {
          const claim = ctx.claims.find(c => c.id === claimId);
          if (!claim || claim.status !== "accepted") {
            violations.push(`Final answer ${fa.id} references non-accepted claim ${claimId}`);
          }
        }
      }
      return { passed: violations.length === 0, violations };
    }
  },
  {
    name: "high_confidence_needs_evidence",
    description: "High-confidence claims need evidence or explicit uncertainty",
    check: (ctx) => {
      const violations: string[] = [];
      for (const claim of ctx.claims) {
        if (claim.confidence >= 0.7 && claim.requires_evidence && claim.evidence_status === "unsupported") {
          violations.push(`Claim ${claim.id} has confidence ${claim.confidence} but no evidence`);
        }
      }
      return { passed: violations.length === 0, violations };
    }
  },
  {
    name: "rejected_claims_need_reason",
    description: "Every rejected claim needs a rejection reason",
    check: (ctx) => {
      const violations: string[] = [];
      for (const claim of ctx.claims) {
        if (claim.status === "rejected" && !claim.rejection_reason) {
          violations.push(`Claim ${claim.id} is rejected but has no rejection reason`);
        }
      }
      return { passed: violations.length === 0, violations };
    }
  },
  {
    name: "revision_links_old_and_new",
    description: "Every revision must link old claim and new claim",
    check: (ctx) => {
      const violations: string[] = [];
      for (const rev of ctx.revisions) {
        if (!rev.old_claim_id || !rev.new_claim_id) {
          violations.push(`Revision ${rev.id} missing old or new claim link`);
        }
      }
      return { passed: violations.length === 0, violations };
    }
  },
  {
    name: "tool_results_traceable",
    description: "Every tool result must be traceable to a tool call",
    check: (ctx) => {
      return { passed: true, violations: [] };
    }
  },
  {
    name: "final_answer_declares_risks",
    description: "Every final answer must declare remaining risks",
    check: (ctx) => {
      const violations: string[] = [];
      for (const fa of ctx.finalAnswers) {
        if (!fa.risks || fa.risks.length === 0) {
          violations.push(`Final answer ${fa.id} has no declared risks`);
        }
      }
      return { passed: violations.length === 0, violations };
    }
  }
];
```

### 1.7 Testing Strategy

- **Unit tests for every schema:** Valid objects pass, invalid objects rejected with specific error messages
- **Invariant tests:** Each of the 6 invariants tested with positive and negative cases
- **Cross-language consistency:** TypeScript validation matches Python validation on identical payloads
- **Edge cases:** Empty strings, maximum-length strings, boundary confidence values, missing optional fields

### 1.8 Success Criteria

- [ ] All 11 JSON schemas defined and validated
- [ ] TypeScript types compile with strict mode
- [ ] Pydantic models pass all validation tests
- [ ] All 6 required invariants enforced
- [ ] 100% test coverage on validation logic
- [ ] Schema validation test suite passes

---

## STEP 2: Model Gateway

**Estimated Complexity:** 3/5  
**Dependencies:** STEP 0  
**Timeline:** Days 5–10 (parallel with STEP 1)

### 2.1 What to Build

The Model Gateway isolates the reasoning engine from model providers. It enables local-first deployment with Ollama while supporting cloud providers when needed.

#### Files to Create

```
services/model-gateway/
├── go.mod
├── go.sum
├── main.go
├── internal/
│   ├── server/
│   │   ├── server.go
│   │   ├── handlers.go
│   │   └── middleware.go
│   ├── provider/
│   │   ├── provider.go
│   │   ├── ollama.go
│   │   ├── openai_compatible.go
│   │   ├── vllm.go
│   │   ├── lmstudio.go
│   │   ├── openrouter.go
│   │   └── mock.go
│   ├── router/
│   │   ├── router.go
│   │   └── presets.go
│   ├── registry/
│   │   ├── registry.go
│   │   └── models.go
│   └── config/
│       └── config.go
├── tests/
│   ├── provider_test.go
│   ├── router_test.go
│   └── integration_test.go
└── config/
    └── presets.yaml
```

### 2.2 Technology Choices and Why

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Go | Performance, concurrency, type safety, aligns with architecture decision ADR-003 |
| HTTP framework | `net/http` + chi router | Standard library, lightweight, no heavy dependencies |
| Ollama client | Native HTTP | Ollama exposes simple REST API; no SDK needed |
| OpenAI compatibility | HTTP client | OpenAI API is well-documented REST |
| Configuration | YAML + env vars | Human-readable config, 12-factor compliant |

### 2.3 ModelProvider Interface

```go
// services/model-gateway/internal/provider/provider.go
package provider

import (
    "context"
)

type ModelProvider interface {
    Chat(ctx context.Context, req ChatRequest) (*ChatResponse, error)
    Stream(ctx context.Context, req ChatRequest) (<-chan ChatChunk, error)
    Embed(ctx context.Context, req EmbedRequest) (*EmbedResponse, error)
    Health(ctx context.Context) (*ProviderHealth, error)
    Name() string
}

type ChatRequest struct {
    Model       string            `json:"model"`
    Messages    []Message         `json:"messages"`
    Temperature float64           `json:"temperature,omitempty"`
    MaxTokens   int               `json:"max_tokens,omitempty"`
    JSONMode    bool              `json:"json_mode,omitempty"`
    Stop        []string          `json:"stop,omitempty"`
}

type Message struct {
    Role    string `json:"role"`
    Content string `json:"content"`
}

type ChatResponse struct {
    Content      string `json:"content"`
    Model        string `json:"model"`
    TokensIn     int    `json:"tokens_in"`
    TokensOut    int    `json:"tokens_out"`
    FinishReason string `json:"finish_reason"`
    DurationMs   int64  `json:"duration_ms"`
}

type ChatChunk struct {
    Content  string `json:"content"`
    Done     bool   `json:"done"`
    Model    string `json:"model"`
    TokensIn int    `json:"tokens_in,omitempty"`
}

type EmbedRequest struct {
    Model  string   `json:"model"`
    Input  []string `json:"input"`
}

type EmbedResponse struct {
    Embeddings [][]float64 `json:"embeddings"`
    Model      string      `json:"model"`
    Tokens     int         `json:"tokens"`
}

type ProviderHealth struct {
    Status    string   `json:"status"`
    Models    []string `json:"models"`
    LatencyMs int64    `json:"latency_ms"`
}
```

### 2.4 Ollama Integration

```go
// services/model-gateway/internal/provider/ollama.go
package provider

import (
    "bytes"
    "context"
    "encoding/json"
    "fmt"
    "net/http"
    "time"
)

type OllamaProvider struct {
    baseURL    string
    httpClient *http.Client
}

func NewOllamaProvider(baseURL string) *OllamaProvider {
    return &OllamaProvider{
        baseURL:    baseURL,
        httpClient: &http.Client{Timeout: 120 * time.Second},
    }
}

func (o *OllamaProvider) Name() string { return "ollama" }

func (o *OllamaProvider) Chat(ctx context.Context, req ChatRequest) (*ChatResponse, error) {
    ollamaReq := map[string]interface{}{
        "model":    req.Model,
        "messages": req.Messages,
        "stream":   false,
        "options":  map[string]interface{}{},
    }

    if req.Temperature > 0 {
        ollamaReq["options"].(map[string]interface{})["temperature"] = req.Temperature
    }
    if req.MaxTokens > 0 {
        ollamaReq["options"].(map[string]interface{})["num_predict"] = req.MaxTokens
    }
    if req.JSONMode {
        ollamaReq["format"] = "json"
    }

    body, _ := json.Marshal(ollamaReq)
    start := time.Now()

    resp, err := o.httpClient.Post(o.baseURL+"/api/chat", "application/json", bytes.NewReader(body))
    if err != nil {
        return nil, fmt.Errorf("ollama chat failed: %w", err)
    }
    defer resp.Body.Close()

    var ollamaResp struct {
        Message struct {
            Content string `json:"content"`
        } `json:"message"`
        Done              bool  `json:"done"`
        EvalCount         int   `json:"eval_count"`
        PromptEvalCount   int   `json:"prompt_eval_count"`
        TotalDurationMs   int64 `json:"total_duration"`
    }

    if err := json.NewDecoder(resp.Body).Decode(&ollamaResp); err != nil {
        return nil, fmt.Errorf("decode ollama response: %w", err)
    }

    return &ChatResponse{
        Content:      ollamaResp.Message.Content,
        Model:        req.Model,
        TokensIn:     ollamaResp.PromptEvalCount,
        TokensOut:    ollamaResp.EvalCount,
        FinishReason: "stop",
        DurationMs:   time.Since(start).Milliseconds(),
    }, nil
}

func (o *OllamaProvider) Stream(ctx context.Context, req ChatRequest) (<-chan ChatChunk, error) {
    ch := make(chan ChatChunk, 64)

    ollamaReq := map[string]interface{}{
        "model":    req.Model,
        "messages": req.Messages,
        "stream":   true,
    }

    body, _ := json.Marshal(ollamaReq)
    httpReq, err := http.NewRequestWithContext(ctx, "POST", o.baseURL+"/api/chat", bytes.NewReader(body))
    if err != nil {
        close(ch)
        return nil, err
    }
    httpReq.Header.Set("Content-Type", "application/json")

    resp, err := o.httpClient.Do(httpReq)
    if err != nil {
        close(ch)
        return nil, err
    }

    go func() {
        defer close(ch)
        defer resp.Body.Close()
        decoder := json.NewDecoder(resp.Body)
        for {
            var chunk struct {
                Message struct {
                    Content string `json:"content"`
                } `json:"message"`
                Done bool `json:"done"`
            }
            if err := decoder.Decode(&chunk); err != nil {
                return
            }
            ch <- ChatChunk{Content: chunk.Message.Content, Done: chunk.Done, Model: req.Model}
            if chunk.Done {
                return
            }
        }
    }()

    return ch, nil
}

func (o *OllamaProvider) Embed(ctx context.Context, req EmbedRequest) (*EmbedResponse, error) {
    ollamaReq := map[string]interface{}{"model": req.Model, "input": req.Input}
    body, _ := json.Marshal(ollamaReq)
    resp, err := o.httpClient.Post(o.baseURL+"/api/embed", "application/json", bytes.NewReader(body))
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()
    var ollamaResp struct {
        Embeddings [][]float64 `json:"embeddings"`
    }
    json.NewDecoder(resp.Body).Decode(&ollamaResp)
    return &EmbedResponse{Embeddings: ollamaResp.Embeddings, Model: req.Model}, nil
}

func (o *OllamaProvider) Health(ctx context.Context) (*ProviderHealth, error) {
    resp, err := o.httpClient.Get(o.baseURL + "/api/tags")
    if err != nil {
        return &ProviderHealth{Status: "unreachable"}, nil
    }
    defer resp.Body.Close()
    var tags struct {
        Models []struct{ Name string `json:"name"` } `json:"models"`
    }
    json.NewDecoder(resp.Body).Decode(&tags)
    models := make([]string, len(tags.Models))
    for i, m := range tags.Models {
        models[i] = m.Name
    }
    return &ProviderHealth{Status: "healthy", Models: models}, nil
}
```

### 2.5 Model Routing Strategy

```go
// services/model-gateway/internal/router/router.go
package router

import "mctagents/model-gateway/internal/provider"

type ModelPreset struct {
    ChatModel      string `yaml:"chat_model"`
    ReasoningModel string `yaml:"reasoning_model"`
    EmbeddingModel string `yaml:"embedding_model"`
}

var DefaultPresets = map[string]ModelPreset{
    "local_tiny": {
        ChatModel:      "qwen2.5:3b",
        ReasoningModel: "deepseek-r1:1.5b",
        EmbeddingModel: "nomic-embed-text",
    },
    "local_balanced": {
        ChatModel:      "qwen2.5:7b",
        ReasoningModel: "deepseek-r1:7b",
        EmbeddingModel: "bge-m3",
    },
    "local_strong": {
        ChatModel:      "qwen2.5:14b",
        ReasoningModel: "deepseek-r1:14b",
        EmbeddingModel: "bge-m3",
    },
}

var TaskRouting = map[string]string{
    "framer":      "local_balanced",
    "architect":   "local_balanced",
    "evidence":    "local_balanced",
    "critic":      "local_balanced",
    "judge":       "local_strong",
    "synthesizer": "local_strong",
}

type ModelRouter struct {
    providers map[string]provider.ModelProvider
    presets   map[string]ModelPreset
}

func (r *ModelRouter) SelectModel(taskType string) (provider.ModelProvider, string) {
    presetName, ok := TaskRouting[taskType]
    if !ok {
        presetName = "local_balanced"
    }
    preset := r.presets[presetName]

    for name, p := range r.providers {
        health, err := p.Health(nil)
        if err == nil && health.Status == "healthy" {
            if taskType == "judge" || taskType == "synthesizer" {
                return p, preset.ReasoningModel
            }
            return p, preset.ChatModel
        }
    }
    return nil, ""
}
```

### 2.6 Cost and Latency Controls

```yaml
# config/presets.yaml
budgets:
  default:
    max_total_tokens: 12000
    max_model_calls: 16
    max_debate_rounds: 2
    prefer_local: true
    fallback_provider: openai_compatible
  deep:
    max_total_tokens: 40000
    max_model_calls: 32
    max_debate_rounds: 4
    max_runtime_seconds: 600

reliability:
  retry_attempts: 3
  retry_backoff_ms: [500, 1000, 2000]
  provider_timeout_seconds: 60
  circuit_breaker_threshold: 5
  circuit_breaker_reset_seconds: 30
```

### 2.7 Testing Strategy

- **Unit tests for each provider:** Mock HTTP responses, test error handling
- **Router tests:** Verify correct model selection for each task type
- **Streaming tests:** Verify SSE chunks are delivered correctly
- **Integration tests:** Test against real Ollama instance (if available)
- **Circuit breaker tests:** Verify provider failure triggers fallback

### 2.8 Success Criteria

- [ ] Ollama provider handles Chat, Stream, Embed, Health
- [ ] OpenAI-compatible provider works with vLLM/LM Studio/OpenRouter
- [ ] Router selects correct model per task type
- [ ] Streaming delivers chunks without dropping
- [ ] Provider fallback works when primary fails
- [ ] Circuit breaker trips and resets correctly

---

## STEP 3: Reasoning Engine (Python)

**Estimated Complexity:** 5/5  
**Dependencies:** STEPs 0, 1, 2  
**Timeline:** Days 8–20

### 3.1 What to Build

The Reasoning Engine is the core of mCTAgents. It implements the CCSR workflow, agent society, debate mechanism, and consensus engine.

#### Files to Create

```
services/reasoning-engine/
├── pyproject.toml
├── alembic.ini
├── alembic/
│   └── versions/
├── src/
│   └── mctagents/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── protocol/
│       │   │   ├── __init__.py
│       │   │   ├── problem_frame.py
│       │   │   ├── claim.py
│       │   │   ├── evidence.py
│       │   │   ├── objection.py
│       │   │   ├── revision.py
│       │   │   ├── decision.py
│       │   │   ├── final_answer.py
│       │   │   ├── event.py
│       │   │   └── debate_policy.py
│       │   ├── invariants.py
│       │   └── validators.py
│       ├── agents/
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── problem_framer.py
│       │   ├── society_planner.py
│       │   ├── architect.py
│       │   ├── evidence_agent.py
│       │   ├── critic.py
│       │   ├── security_agent.py
│       │   ├── judge.py
│       │   ├── synthesizer.py
│       │   └── prompts/
│       │       ├── framer.txt
│       │       ├── planner.txt
│       │       ├── architect.txt
│       │       ├── evidence.txt
│       │       ├── critic.txt
│       │       ├── security.txt
│       │       ├── judge.txt
│       │       └── synthesizer.txt
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── reasoning_engine.py
│       │   ├── state_machine.py
│       │   ├── debate_controller.py
│       │   ├── consensus.py
│       │   └── drift_detector.py
│       ├── services/
│       │   ├── __init__.py
│       │   ├── event_service.py
│       │   ├── storage_service.py
│       │   ├── model_service.py
│       │   └── evidence_service.py
│       └── api/
│           ├── __init__.py
│           ├── routes.py
│           ├── schemas.py
│           └── deps.py
├── tests/
│   ├── unit/
│   │   ├── test_agents.py
│   │   ├── test_state_machine.py
│   │   ├── test_debate.py
│   │   ├── test_consensus.py
│   │   ├── test_invariants.py
│   │   └── test_protocol.py
│   ├── integration/
│   │   ├── test_engine.py
│   │   ├── test_event_stream.py
│   │   └── test_api.py
│   └── fixtures/
│       ├── sample_problems.json
│       ├── sample_claims.json
│       └── sample_runs.json
└── prompts/
    ├── system_base.txt
    └── templates/
```

### 3.2 Technology Choices and Why

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Language | Python 3.11+ | Best ecosystem for AI/ML, Pydantic for validation |
| Web framework | FastAPI | Async support, auto-docs, Pydantic integration |
| Database | SQLAlchemy 2.0 + asyncpg | Async PostgreSQL access, Alembic migrations |
| Model client | httpx | Async HTTP client for model gateway |
| Event streaming | SSE via `sse-starlette` | Native SSE support in FastAPI |
| Workflow | Custom state machine + optional LangGraph adapter | Control over CCSR logic, extensible |

### 3.3 Agent Society Implementation

#### Base Agent Protocol

```python
# services/reasoning-engine/src/mctagents/agents/base.py
from abc import ABC, abstractmethod
from pydantic import BaseModel
from mctagents.core.protocol.claim import Claim
from mctagents.core.protocol.evidence import Evidence
from mctagents.core.protocol.objection import Objection
from mctagents.core.protocol.problem_frame import ProblemFrame


class AgentContext(BaseModel):
    run_id: str
    problem_frame: ProblemFrame
    claims: list[Claim]
    evidence: list[Evidence]
    objections: list[Objection]
    debate_round: int
    budget_remaining: dict


class AgentResult(BaseModel):
    agent_id: str
    claims: list[Claim] = []
    evidence: list[Evidence] = []
    objections: list[Objection] = []
    revisions: list[dict] = []
    metadata: dict = {}


class BaseAgent(ABC):
    @property
    @abstractmethod
    def agent_id(self) -> str: ...

    @property
    @abstractmethod
    def capabilities(self) -> list[str]: ...

    @abstractmethod
    async def act(self, context: AgentContext) -> AgentResult: ...

    def budget_config(self) -> dict:
        return {"max_tokens": 1200, "max_tool_calls": 3}
```

#### Problem Framer Agent

```python
# services/reasoning-engine/src/mctagents/agents/problem_framer.py
from uuid import uuid4
from mctagents.agents.base import BaseAgent, AgentContext, AgentResult
from mctagents.core.protocol.problem_frame import ProblemFrame
from mctagents.services.model_service import ModelService

FRAMER_SYSTEM_PROMPT = """You are a Problem Framer agent in a social reasoning system.
Your job is to analyze user input and create a structured ProblemFrame.
Return valid JSON matching the schema provided."""

class ProblemFramer(BaseAgent):
    agent_id = "problem_framer"
    capabilities = ["normalize_problem", "detect_domain", "set_risk_level"]

    def __init__(self, model_service: ModelService):
        self.model = model_service

    async def act(self, context: AgentContext) -> AgentResult:
        original_input = context.problem_frame.original_input if context.problem_frame else ""
        prompt = f"""Analyze the following user input and create a structured ProblemFrame.

User input: {original_input}

Return JSON with these fields:
- original_input: the raw user input
- normalized_problem: a clear, structured problem statement
- constraints: array of explicit constraints
- success_criteria: array of what constitutes a good answer
- risk_level: low|medium|high|critical
- domain: software|research|legal|product|general
- requires_business_decision: boolean
- requires_research: boolean
- requires_code: boolean"""

        response = await self.model.chat(
            task_type="framer",
            messages=[
                {"role": "system", "content": FRAMER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            json_mode=True,
        )

        frame_data = self._parse_response(response)
        frame = ProblemFrame(
            id=f"pf_{uuid4()}",
            run_id=context.run_id,
            original_input=frame_data["original_input"],
            normalized_problem=frame_data["normalized_problem"],
            constraints=frame_data.get("constraints", []),
            success_criteria=frame_data.get("success_criteria", []),
            risk_level=frame_data.get("risk_level", "medium"),
            domain=frame_data.get("domain"),
            requires_business_decision=frame_data.get("requires_business_decision", False),
            requires_research=frame_data.get("requires_research", False),
            requires_code=frame_data.get("requires_code", False),
        )

        return AgentResult(
            agent_id=self.agent_id,
            metadata={"problem_frame": frame.model_dump()},
        )

    def _parse_response(self, response: str) -> dict:
        import json
        return json.loads(response)
```

#### Architect Agent

```python
# services/reasoning-engine/src/mctagents/agents/architect.py
import json
from uuid import uuid4
from mctagents.agents.base import BaseAgent, AgentContext, AgentResult
from mctagents.core.protocol.claim import Claim, ClaimType, ClaimStatus
from mctagents.services.model_service import ModelService

ARCHITECT_SYSTEM_PROMPT = """You are an Architect agent in a social reasoning system.
Your job is to propose clear, structured claims that address the problem.
Each claim should be specific, actionable, and include a confidence score."""

class ArchitectAgent(BaseAgent):
    agent_id = "architect_agent"
    capabilities = ["propose_claims", "revise_claims", "compare_alternatives"]

    def __init__(self, model_service: ModelService):
        self.model = model_service

    async def act(self, context: AgentContext) -> AgentResult:
        if context.claims:
            return await self._revise_claims(context)
        return await self._propose_claims(context)

    async def _propose_claims(self, context: AgentContext) -> AgentResult:
        prompt = f"""Analyze this problem and propose structured claims.

Problem: {context.problem_frame.normalized_problem}
Domain: {context.problem_frame.domain}
Constraints: {json.dumps(context.problem_frame.constraints)}
Success criteria: {json.dumps(context.problem_frame.success_criteria)}

Propose 3-5 claims. Each claim must have:
- text: clear proposition statement
- claim_type: one of [architecture_decision, technical_approach, risk_assessment, tradeoff_analysis, recommendation]
- confidence: 0.0-1.0
- requires_evidence: boolean

Return JSON array of claims."""

        response = await self.model.chat(
            task_type="architect",
            messages=[
                {"role": "system", "content": ARCHITECT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            json_mode=True,
        )

        claims_data = self._parse_response(response)
        claims = []
        for c in claims_data:
            claims.append(Claim(
                id=f"claim_{uuid4()}",
                run_id=context.run_id,
                author_agent_id=self.agent_id,
                text=c["text"],
                claim_type=ClaimType(c.get("claim_type", "general")),
                confidence=float(c.get("confidence", 0.5)),
                status=ClaimStatus.PROPOSED,
                requires_evidence=c.get("requires_evidence", False),
            ))

        return AgentResult(agent_id=self.agent_id, claims=claims)

    async def _revise_claims(self, context: AgentContext) -> AgentResult:
        challenged = [c for c in context.claims if c.status in ("challenged", "revision_required")]
        relevant_objections = [
            o for o in context.objections
            if o.target_claim_id in {c.id for c in challenged}
        ]

        prompt = f"""Revise the following challenged claims based on objections.

Challenged claims:
{json.dumps([{'id': c.id, 'text': c.text, 'confidence': c.confidence} for c in challenged])}

Objections:
{json.dumps([{'target_claim_id': o.target_claim_id, 'reason': o.reason, 'severity': o.severity, 'requested_fix': o.requested_fix} for o in relevant_objections])}

For each challenged claim, produce a revised version. Return JSON array with:
- old_claim_id: the claim being revised
- text: revised proposition
- confidence: revised confidence
- reason: why this revision addresses the objections"""

        response = await self.model.chat(
            task_type="architect",
            messages=[
                {"role": "system", "content": ARCHITECT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            json_mode=True,
        )

        revisions_data = self._parse_response(response)
        new_claims = []
        revisions = []
        for rev in revisions_data:
            new_claim = Claim(
                id=f"claim_{uuid4()}",
                run_id=context.run_id,
                author_agent_id=self.agent_id,
                text=rev["text"],
                claim_type=next(
                    (c.claim_type for c in challenged if c.id == rev["old_claim_id"]),
                    ClaimType.GENERAL,
                ),
                confidence=float(rev.get("confidence", 0.5)),
                status=ClaimStatus.REVISED,
                parent_claim_id=rev["old_claim_id"],
            )
            new_claims.append(new_claim)
            revisions.append({
                "old_claim_id": rev["old_claim_id"],
                "new_claim_id": new_claim.id,
                "reason": rev["reason"],
            })

        return AgentResult(agent_id=self.agent_id, claims=new_claims, revisions=revisions)

    def _parse_response(self, response: str) -> list[dict]:
        import json
        return json.loads(response)
```

#### Evidence Agent

```python
# services/reasoning-engine/src/mctagents/agents/evidence_agent.py
import json
from uuid import uuid4
from mctagents.agents.base import BaseAgent, AgentContext, AgentResult
from mctagents.core.protocol.evidence import Evidence, SourceType
from mctagents.core.protocol.claim import EvidenceStatus
from mctagents.services.model_service import ModelService
from mctagents.services.evidence_service import EvidenceService

EVIDENCE_SYSTEM_PROMPT = """You are an Evidence agent in a social reasoning system.
Your job is to find, evaluate, and attach evidence to claims.
Always cite your sources and score reliability."""

class EvidenceAgent(BaseAgent):
    agent_id = "evidence_agent"
    capabilities = ["retrieve_evidence", "score_reliability", "label_unsupported"]

    def __init__(self, model_service: ModelService, evidence_service: EvidenceService):
        self.model = model_service
        self.evidence_svc = evidence_service

    async def act(self, context: AgentContext) -> AgentResult:
        unsupported = [c for c in context.claims if c.requires_evidence and c.evidence_status == "unsupported"]
        all_evidence = []

        for claim in unsupported:
            evidence_items = await self._find_evidence(claim, context)
            all_evidence.extend(evidence_items)

        updated_claims = []
        for claim in context.claims:
            supporting = [e for e in all_evidence if claim.id in e.get("supports_claim_ids", [])]
            if supporting and claim.requires_evidence:
                claim.evidence_status = EvidenceStatus.SUPPORTED
                updated_claims.append(claim)

        return AgentResult(
            agent_id=self.agent_id,
            evidence=[Evidence(
                id=f"ev_{uuid4()}",
                run_id=context.run_id,
                source_type=e.get("source_type", SourceType.INTERNAL_MEMORY),
                source_ref=e.get("source_ref"),
                summary=e["summary"],
                reliability_score=e.get("reliability_score", 0.5),
                supports_claim_ids=e.get("supports_claim_ids", []),
                attacks_claim_ids=e.get("attacks_claim_ids", []),
            ) for e in all_evidence],
            claims=updated_claims,
        )

    async def _find_evidence(self, claim, context) -> list[dict]:
        results = await self.evidence_svc.search(query=claim.text, run_id=context.run_id, top_k=5)
        prompt = f"""Evaluate these search results for the claim: "{claim.text}"

Search results:
{json.dumps([{'content': r['content'][:500], 'source': r['source']} for r in results])}

For each relevant result, return:
- summary: concise evidence statement
- supports_claim: true/false
- reliability_score: 0.0-1.0
- source_type: uploaded_document|official_documentation|web_source|academic_paper|github_repository
- source_ref: source identifier"""

        response = await self.model.chat(
            task_type="evidence",
            messages=[
                {"role": "system", "content": EVIDENCE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            json_mode=True,
        )

        evidence_data = self._parse_response(response)
        return [{
            "summary": e["summary"],
            "source_type": e.get("source_type", "internal_memory"),
            "source_ref": e.get("source_ref"),
            "reliability_score": e.get("reliability_score", 0.5),
            "supports_claim_ids": [claim.id] if e.get("supports_claim") else [],
            "attacks_claim_ids": [] if e.get("supports_claim") else [claim.id],
        } for e in evidence_data]

    def _parse_response(self, response: str) -> list[dict]:
        return json.loads(response)
```

#### Critic Agent

```python
# services/reasoning-engine/src/mctagents/agents/critic.py
import json
from uuid import uuid4
from mctagents.agents.base import BaseAgent, AgentContext, AgentResult
from mctagents.core.protocol.objection import Objection, ObjectionSeverity
from mctagents.services.model_service import ModelService

CRITIC_SYSTEM_PROMPT = """You are a Critic agent in a social reasoning system.
Your job is to rigorously challenge weak claims, detect contradictions, and identify gaps.
Be fair but thorough. Only raise genuine concerns."""

class CriticAgent(BaseAgent):
    agent_id = "critic_agent"
    capabilities = ["challenge_claims", "detect_contradictions", "identify_gaps"]

    def __init__(self, model_service: ModelService):
        self.model = model_service

    async def act(self, context: AgentContext) -> AgentResult:
        claims_to_challenge = [
            c for c in context.claims
            if c.status in ("proposed", "supported", "revised")
        ]
        if not claims_to_challenge:
            return AgentResult(agent_id=self.agent_id)

        prompt = f"""Challenge the following claims. Be rigorous but fair.

Problem: {context.problem_frame.normalized_problem}

Claims:
{json.dumps([{'id': c.id, 'text': c.text, 'confidence': c.confidence, 'evidence_status': c.evidence_status} for c in claims_to_challenge])}

Evidence available:
{json.dumps([{'summary': e.summary, 'reliability': e.reliability_score} for e in context.evidence[:10]])}

For each claim that deserves challenge, return:
- target_claim_id: which claim to challenge
- reason: specific logical, evidence, or feasibility concern
- severity: low|medium|high|critical
- requested_fix: suggested improvement

Only challenge claims with real weaknesses. Do not manufacture objections."""

        response = await self.model.chat(
            task_type="critic",
            messages=[
                {"role": "system", "content": CRITIC_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            json_mode=True,
        )

        objections_data = json.loads(response)
        objections = []
        for o in objections_data:
            objections.append(Objection(
                id=f"obj_{uuid4()}",
                run_id=context.run_id,
                target_claim_id=o["target_claim_id"],
                author_agent_id=self.agent_id,
                reason=o["reason"],
                severity=ObjectionSeverity(o.get("severity", "medium")),
                requested_fix=o.get("requested_fix"),
            ))

        return AgentResult(agent_id=self.agent_id, objections=objections)
```

#### Judge Agent

```python
# services/reasoning-engine/src/mctagents/agents/judge.py
import json
from uuid import uuid4
from mctagents.agents.base import BaseAgent, AgentContext, AgentResult
from mctagents.core.protocol.decision import Decision
from mctagents.core.protocol.claim import ClaimStatus, ClaimScores
from mctagents.services.model_service import ModelService

JUDGE_SYSTEM_PROMPT = """You are a Judge agent in a social reasoning system.
Your job is to evaluate all claims, score them, and make accept/reject decisions.
Be objective, evidence-based, and consistent."""

class JudgeAgent(BaseAgent):
    agent_id = "judge_agent"
    capabilities = ["score_claims", "accept_reject", "determine_consensus"]

    def __init__(self, model_service: ModelService):
        self.model = model_service

    async def act(self, context: AgentContext) -> AgentResult:
        prompt = f"""Evaluate all claims and make a decision.

Problem: {context.problem_frame.normalized_problem}
Debate round: {context.debate_round}

Claims:
{json.dumps([{'id': c.id, 'text': c.text, 'confidence': c.confidence, 'status': c.status, 'evidence_status': c.evidence_status} for c in context.claims])}

Objections:
{json.dumps([{'target_claim_id': o.target_claim_id, 'reason': o.reason, 'severity': o.severity, 'resolved': o.resolved} for o in context.objections])}

Evaluate each claim on these dimensions (0.0-1.0):
- logic: logical consistency and soundness
- evidence: evidence support quality
- feasibility: practical implementability
- critic_resistance: how well it survived objection
- risk_adjusted: adjusted for identified risks

Return JSON with:
- accepted: object mapping claim_id to scores
- rejected: object mapping claim_id to rejection reason
- uncertain: array of claim IDs needing more debate
- needs_more_debate: boolean
- debate_reason: if more debate needed, why
- overall_confidence: 0.0-1.0"""

        response = await self.model.chat(
            task_type="judge",
            messages=[
                {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            json_mode=True,
        )

        decision_data = json.loads(response)
        updated_claims = []
        for c in context.claims:
            if c.id in decision_data.get("accepted", {}):
                c.status = ClaimStatus.ACCEPTED
                scores = decision_data["accepted"][c.id]
                c.scores = ClaimScores(**scores)
                updated_claims.append(c)
            elif c.id in decision_data.get("rejected", {}):
                c.status = ClaimStatus.REJECTED
                c.rejection_reason = decision_data["rejected"][c.id].get("reason", "")
                updated_claims.append(c)
            elif c.id in decision_data.get("uncertain", []):
                c.status = ClaimStatus.UNCERTAIN
                updated_claims.append(c)

        decision = Decision(
            id=f"dec_{uuid4()}",
            run_id=context.run_id,
            accepted_claim_ids=list(decision_data.get("accepted", {}).keys()),
            rejected_claim_ids=list(decision_data.get("rejected", {}).keys()),
            uncertain_claim_ids=decision_data.get("uncertain", []),
            score_breakdown=decision_data.get("accepted", {}),
            confidence=decision_data.get("overall_confidence", 0.5),
            needs_more_debate=decision_data.get("needs_more_debate", False),
            extra_debate_reason=decision_data.get("debate_reason"),
        )

        return AgentResult(
            agent_id=self.agent_id,
            claims=updated_claims,
            metadata={"decision": decision.model_dump()},
        )
```

#### Synthesizer Agent

```python
# services/reasoning-engine/src/mctagents/agents/synthesizer.py
import json
from uuid import uuid4
from mctagents.agents.base import BaseAgent, AgentContext, AgentResult
from mctagents.core.protocol.final_answer import FinalAnswer, RiskItem, RejectedAlternative
from mctagents.services.model_service import ModelService

SYNTHESIZER_SYSTEM_PROMPT = """You are a Synthesizer agent in a social reasoning system.
Your job is to create a clear, structured final answer from accepted claims.
Include risks, next steps, and rejected alternatives."""

class SynthesizerAgent(BaseAgent):
    agent_id = "synthesizer_agent"
    capabilities = ["create_final_answer", "summarize_reasoning"]

    def __init__(self, model_service: ModelService):
        self.model = model_service

    async def act(self, context: AgentContext) -> AgentResult:
        accepted = [c for c in context.claims if c.status == "accepted"]
        rejected = [c for c in context.claims if c.status == "rejected"]

        prompt = f"""Create a clear, structured final answer from the accepted claims.

Problem: {context.problem_frame.normalized_problem}

Accepted claims:
{json.dumps([{'text': c.text, 'scores': c.scores.model_dump() if c.scores else None} for c in accepted])}

Rejected claims (include as alternatives):
{json.dumps([{'text': c.text, 'reason': c.rejection_reason} for c in rejected])}

Create a final answer with:
- answer_text: clear, actionable answer synthesizing accepted claims
- risks: remaining risks or uncertainties
- next_steps: suggested follow-up actions
- rejected_alternatives: why these were rejected
- confidence: 0.0-1.0"""

        response = await self.model.chat(
            task_type="synthesizer",
            messages=[
                {"role": "system", "content": SYNTHESIZER_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            json_mode=False,
        )

        try:
            answer_data = json.loads(response)
        except json.JSONDecodeError:
            answer_data = {"answer_text": response}

        final_answer = FinalAnswer(
            id=f"fa_{uuid4()}",
            run_id=context.run_id,
            answer_text=answer_data.get("answer_text", response),
            accepted_claim_ids=[c.id for c in accepted],
            rejected_alternatives=[
                RejectedAlternative(claim_id=c.id, reason=c.rejection_reason or "")
                for c in rejected
            ],
            risks=[
                RiskItem(
                    description=r.get("description", ""),
                    severity=r.get("severity", "low"),
                    mitigation=r.get("mitigation"),
                )
                for r in answer_data.get("risks", [])
            ],
            next_steps=answer_data.get("next_steps", []),
            confidence=answer_data.get("confidence", 0.7),
        )

        return AgentResult(
            agent_id=self.agent_id,
            metadata={"final_answer": final_answer.model_dump()},
        )
```

### 3.4 CCSR Workflow State Machine

```python
# services/reasoning-engine/src/mctagents/engine/state_machine.py
from enum import Enum

class RunPhase(str, Enum):
    QUEUED = "queued"
    FRAMING = "framing"
    SOCIETY_PLANNING = "society_planning"
    CLAIM_PROPOSAL = "claim_proposal"
    EVIDENCE_ATTACHMENT = "evidence_attachment"
    CRITICISM = "criticism"
    REVISION = "revision"
    JUDGING = "judging"
    ESCALATION = "escalation"
    SYNTHESIS = "synthesis"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class StateMachine:
    VALID_TRANSITIONS = {
        ("queued", "start"): "framing",
        ("framing", "problem_framed"): "society_planning",
        ("society_planning", "society_selected"): "claim_proposal",
        ("claim_proposal", "claims_proposed"): "evidence_attachment",
        ("evidence_attachment", "evidence_attached"): "criticism",
        ("criticism", "criticism_complete"): "revision",
        ("revision", "revision_complete"): "judging",
        ("judging", "judge_accepted"): "synthesis",
        ("judging", "needs_more_debate"): "escalation",
        ("escalation", "escalation_resolved"): "claim_proposal",
        ("synthesis", "synthesis_complete"): "completed",
    }

    ERROR_TRANSITIONS = {phase: "failed" for phase in RunPhase
                         if phase not in (RunPhase.COMPLETED, RunPhase.FAILED, RunPhase.CANCELLED)}

    def __init__(self, max_rounds: int = 2):
        self.current_phase = RunPhase.QUEUED
        self.max_rounds = max_rounds
        self.debate_round = 0
        self.transition_log = []

    def can_transition(self, event: str) -> bool:
        return (
            (self.current_phase.value, event) in self.VALID_TRANSITIONS
            or (self.current_phase.value, event) in self.ERROR_TRANSITIONS
            or event == "cancel"
        )

    def transition(self, event: str) -> RunPhase:
        if event == "cancel":
            self.transition_log.append({"from": self.current_phase.value, "to": "cancelled", "event": event})
            self.current_phase = RunPhase.CANCELLED
            return self.current_phase

        key = (self.current_phase.value, event)
        if key in self.VALID_TRANSITIONS:
            target = self.VALID_TRANSITIONS[key]
            self.transition_log.append({"from": self.current_phase.value, "to": target, "event": event})
            self.current_phase = RunPhase(target)
            if self.current_phase == RunPhase.CLAIM_PROPOSAL:
                self.debate_round += 1
            return self.current_phase

        if key in self.ERROR_TRANSITIONS:
            target = self.ERROR_TRANSITIONS[key]
            self.transition_log.append({"from": self.current_phase.value, "to": target, "event": event})
            self.current_phase = RunPhase(target)
            return self.current_phase

        raise ValueError(f"Invalid transition: {self.current_phase.value} + {event}")

    def should_escalate(self, judge_confidence: float, escalation_threshold: float) -> bool:
        if self.debate_round >= self.max_rounds:
            return False
        return judge_confidence < escalation_threshold
```

### 3.5 Debate/Consensus Mechanism

```python
# services/reasoning-engine/src/mctagents/engine/debate_controller.py
from mctagents.engine.state_machine import StateMachine, RunPhase

class DebateController:
    def __init__(self, state_machine: StateMachine, policy: dict):
        self.state = state_machine
        self.policy = policy
        self.round_history = []

    async def should_continue(self, context: dict) -> bool:
        if self.state.debate_round >= self.policy.get("max_rounds", 2):
            return False

        decision = context.get("decision")
        if decision:
            if decision.confidence >= self.policy.get("judge_confidence_threshold", 0.85):
                return False
            if not decision.needs_more_debate:
                return False
            if self.state.should_escalate(
                decision.confidence,
                self.policy.get("escalation_threshold", 0.6),
            ):
                return True

        if self._has_low_marginal_value():
            return False

        return True

    def _has_low_marginal_value(self) -> bool:
        if len(self.round_history) < 2:
            return False
        last_round = self.round_history[-1]
        prev_round = self.round_history[-2]
        return (
            last_round.get("new_claims", 0) == 0
            and last_round.get("revisions", 0) == 0
        )
```

### 3.6 Reasoning Engine Orchestrator

```python
# services/reasoning-engine/src/mctagents/engine/reasoning_engine.py
from mctagents.engine.state_machine import StateMachine, RunPhase
from mctagents.engine.debate_controller import DebateController
from mctagents.agents.problem_framer import ProblemFramer
from mctagents.agents.architect import ArchitectAgent
from mctagents.agents.evidence_agent import EvidenceAgent
from mctagents.agents.critic import CriticAgent
from mctagents.agents.judge import JudgeAgent
from mctagents.agents.synthesizer import SynthesizerAgent
from mctagents.services.event_service import EventService
from mctagents.services.storage_service import StorageService
from mctagents.services.model_service import ModelService
from mctagents.services.evidence_service import EvidenceService

class ReasoningEngine:
    def __init__(
        self,
        model_service: ModelService,
        evidence_service: EvidenceService,
        event_service: EventService,
        storage_service: StorageService,
    ):
        self.model = model_service
        self.evidence_svc = evidence_service
        self.events = event_service
        self.storage = storage_service

        self.framer = ProblemFramer(model_service)
        self.architect = ArchitectAgent(model_service)
        self.evidence_agent = EvidenceAgent(model_service, evidence_service)
        self.critic = CriticAgent(model_service)
        self.judge = JudgeAgent(model_service)
        self.synthesizer = SynthesizerAgent(model_service)

    async def run(self, run_id: str, problem: str, policy: dict) -> dict:
        state = StateMachine(max_rounds=policy.get("max_rounds", 2))
        debate = DebateController(state, policy)

        claims = []
        evidence = []
        objections = []
        revisions = []
        problem_frame = None

        # Phase 1: Problem Framing
        state.transition("start")
        await self.events.emit(run_id, "run_started", {"problem": problem})

        ctx = self._make_context(run_id, problem_frame, claims, evidence, objections, state.debate_round)
        framer_result = await self.framer.act(ctx)
        problem_frame = framer_result.metadata.get("problem_frame")
        await self.events.emit(run_id, "problem_framed", problem_frame)
        state.transition("problem_framed")

        # Phase 2: Claim Proposal
        state.transition("society_selected")
        ctx = self._make_context(run_id, problem_frame, claims, evidence, objections, state.debate_round)
        architect_result = await self.architect.act(ctx)
        claims.extend(architect_result.claims)
        for claim in architect_result.claims:
            await self.events.emit(run_id, "claim_created", claim.model_dump())
        state.transition("claims_proposed")

        # Phase 3: Evidence Attachment
        ctx = self._make_context(run_id, problem_frame, claims, evidence, objections, state.debate_round)
        evidence_result = await self.evidence_agent.act(ctx)
        evidence.extend(evidence_result.evidence)
        for ev in evidence_result.evidence:
            await self.events.emit(run_id, "evidence_attached", ev.model_dump())
        state.transition("evidence_attached")

        # Phase 4: Criticism
        ctx = self._make_context(run_id, problem_frame, claims, evidence, objections, state.debate_round)
        critic_result = await self.critic.act(ctx)
        objections.extend(critic_result.objections)
        for obj in critic_result.objections:
            await self.events.emit(run_id, "objection_created", obj.model_dump())
        state.transition("criticism_complete")

        # Phase 5: Revision
        ctx = self._make_context(run_id, problem_frame, claims, evidence, objections, state.debate_round)
        revision_result = await self.architect.act(ctx)
        claims.extend(revision_result.claims)
        revisions.extend(revision_result.revisions)
        for rev in revision_result.revisions:
            await self.events.emit(run_id, "claim_revised", rev)
        state.transition("revision_complete")

        # Phase 6: Judging
        ctx = self._make_context(run_id, problem_frame, claims, evidence, objections, state.debate_round)
        judge_result = await self.judge.act(ctx)
        claims.extend(judge_result.claims)
        decision = judge_result.metadata.get("decision")
        await self.events.emit(run_id, "judge_scored", decision)

        if debate.should_continue({"decision": decision}):
            state.transition("needs_more_debate")
            # Additional rounds handled by escalation loop
        else:
            state.transition("judge_accepted")

        # Phase 7: Synthesis
        ctx = self._make_context(run_id, problem_frame, claims, evidence, objections, state.debate_round)
        synth_result = await self.synthesizer.act(ctx)
        final_answer = synth_result.metadata.get("final_answer")
        await self.events.emit(run_id, "final_answer_created", final_answer)

        state.transition("synthesis_complete")
        await self.events.emit(run_id, "run_completed", {"run_id": run_id})

        # Store all objects
        await self.storage.save_run(run_id, problem_frame, claims, evidence, objections, revisions, decision, final_answer)

        return final_answer

    def _make_context(self, run_id, problem_frame, claims, evidence, objections, debate_round):
        from mctagents.agents.base import AgentContext
        from mctagents.core.protocol.problem_frame import ProblemFrame as PF
        return AgentContext(
            run_id=run_id,
            problem_frame=PF(**problem_frame) if problem_frame else PF(id="pf_empty", run_id=run_id, original_input="", normalized_problem=""),
            claims=claims,
            evidence=evidence,
            objections=objections,
            debate_round=debate_round,
            budget_remaining={"max_tokens": 12000},
        )
```

### 3.7 Prompt Engineering

Each agent role has carefully crafted prompts stored in `prompts/` as separate text files. Key principles:

1. **System prompts** define the role, expected output format, and constraints
2. **JSON mode** is used for structured extraction tasks
3. **Few-shot examples** are included for complex tasks
4. **Output schema** is explicitly described in each prompt
5. **Anti-hallucination instructions** are embedded: "If you lack information, say so"

### 3.8 Testing Strategy

- **Unit tests for each agent:** Mock model service, verify correct prompt construction and response parsing
- **State machine tests:** Verify all valid and invalid transitions
- **Debate controller tests:** Verify stop/escalate/drift logic
- **Consensus tests:** Verify scoring and acceptance logic
- **Integration tests:** Run full workflow with mock model responses
- **Invariant tests:** Verify 6 required invariants are enforced

### 3.9 Success Criteria

- [ ] All 5 core agents (Framer, Architect, Evidence, Critic, Judge, Synthesizer) implemented
- [ ] State machine handles all valid transitions
- [ ] Debate controller stops at correct conditions
- [ ] All claims, evidence, objections stored in PostgreSQL
- [ ] Events emitted at every state transition
- [ ] Unit test coverage >80%

---

## STEP 4: API Gateway (Go)

**Estimated Complexity:** 3/5  
**Dependencies:** STEPs 0, 1  
**Timeline:** Days 10–18

### 4.1 What to Build

The Go API Gateway handles HTTP routing, authentication, rate limiting, and SSE event streaming. It proxies requests to the Python reasoning engine and other services.

#### Files to Create

```
services/api-gateway/
├── go.mod
├── go.sum
├── main.go
├── internal/
│   ├── server/
│   │   ├── server.go
│   │   ├── routes.go
│   │   └── middleware/
│   │       ├── auth.go
│   │       ├── ratelimit.go
│   │       ├── cors.go
│   │       ├── logging.go
│   │       └── recovery.go
│   ├── handlers/
│   │   ├── runs.go
│   │   ├── events.go
│   │   ├── claims.go
│   │   ├── evidence.go
│   │   └── health.go
│   ├── streaming/
│   │   ├── sse.go
│   │   └── websocket.go
│   ├── storage/
│   │   ├── postgres.go
│   │   └── queries.go
│   └── config/
│       └── config.go
├── migrations/
│   └── 001_initial.sql
├── tests/
│   ├── handlers_test.go
│   ├── middleware_test.go
│   └── integration_test.go
└── Dockerfile
```

### 4.2 REST API Endpoints

```go
// services/api-gateway/internal/server/routes.go
func SetupRoutes(mux *chi.Mux, deps *Dependencies) {
    mux.Use(middleware.Recovery)
    mux.Use(middleware.Logging)
    mux.Use(middleware.CORS)
    mux.Use(middleware.RateLimit(deps.Config.RateLimit))

    mux.Get("/health", handlers.Health)

    mux.Route("/v1", func(r chi.Router) {
        r.Use(middleware.Auth(deps.Config.Auth))

        // Runs
        r.Post("/runs", handlers.CreateRun(deps))
        r.Get("/runs/{run_id}", handlers.GetRun(deps))
        r.Get("/runs/{run_id}/events", handlers.StreamEvents(deps))
        r.Post("/runs/{run_id}/cancel", handlers.CancelRun(deps))
        r.Get("/runs/{run_id}/claim-graph", handlers.GetClaimGraph(deps))
        r.Get("/runs/{run_id}/evaluation", handlers.GetEvaluation(deps))

        // Claims
        r.Get("/runs/{run_id}/claims", handlers.ListClaims(deps))
        r.Get("/claims/{claim_id}", handlers.GetClaim(deps))
        r.Get("/claims/{claim_id}/lineage", handlers.GetClaimLineage(deps))

        // Evidence
        r.Get("/runs/{run_id}/evidence", handlers.ListEvidence(deps))
        r.Post("/documents", handlers.UploadDocument(deps))
    })
}
```

### 4.3 SSE Event Streaming

```go
// services/api-gateway/internal/streaming/sse.go
package streaming

import (
    "encoding/json"
    "fmt"
    "net/http"
    "sync"
)

type Event struct {
    EventID string          `json:"event_id"`
    RunID   string          `json:"run_id"`
    Type    string          `json:"type"`
    Payload json.RawMessage `json:"payload"`
}

type SSEClient struct {
    RunID string
    Chan  chan Event
    Done  chan struct{}
}

type SSEHub struct {
    clients map[string][]*SSEClient
    mu      sync.RWMutex
}

func NewSSEHub() *SSEHub {
    return &SSEHub{clients: make(map[string][]*SSEClient)}
}

func (h *SSEHub) Subscribe(runID string) *SSEClient {
    client := &SSEClient{RunID: runID, Chan: make(chan Event, 64), Done: make(chan struct{})}
    h.mu.Lock()
    h.clients[runID] = append(h.clients[runID], client)
    h.mu.Unlock()
    return client
}

func (h *SSEHub) Publish(runID string, event Event) {
    h.mu.RLock()
    defer h.mu.RUnlock()
    for _, client := range h.clients[runID] {
        select {
        case client.Chan <- event:
        default:
        }
    }
}

func (h *SSEHub) Unsubscribe(client *SSEClient) {
    h.mu.Lock()
    defer h.mu.Unlock()
    clients := h.clients[client.RunID]
    for i, c := range clients {
        if c == client {
            h.clients[client.RunID] = append(clients[:i], clients[i+1:]...)
            break
        }
    }
    close(client.Done)
}

func HandleSSE(hub *SSEHub) http.HandlerFunc {
    return func(w http.ResponseWriter, r *http.Request) {
        runID := chi.URLParam(r, "run_id")
        client := hub.Subscribe(runID)
        defer hub.Unsubscribe(client)

        w.Header().Set("Content-Type", "text/event-stream")
        w.Header().Set("Cache-Control", "no-cache")
        w.Header().Set("Connection", "keep-alive")

        flusher, ok := w.(http.Flusher)
        if !ok {
            http.Error(w, "streaming unsupported", http.StatusInternalServerError)
            return
        }

        ctx := r.Context()
        for {
            select {
            case <-ctx.Done():
                return
            case <-client.Done:
                return
            case event := <-client.Chan:
                data, _ := json.Marshal(event)
                fmt.Fprintf(w, "event: %s\n", event.Type)
                fmt.Fprintf(w, "data: %s\n\n", data)
                flusher.Flush()
            }
        }
    }
}
```

### 4.4 Authentication

```go
// services/api-gateway/internal/server/middleware/auth.go
func Auth(config *AuthConfig) func(http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            apiKey := r.Header.Get("X-API-Key")
            if apiKey != "" {
                if !validateAPIKey(apiKey, config) {
                    http.Error(w, "invalid api key", http.StatusUnauthorized)
                    return
                }
                ctx := context.WithValue(r.Context(), "tenant_id", getTenantFromKey(apiKey))
                next.ServeHTTP(w, r.WithContext(ctx))
                return
            }

            authHeader := r.Header.Get("Authorization")
            if strings.HasPrefix(authHeader, "Bearer ") {
                token := strings.TrimPrefix(authHeader, "Bearer ")
                if !validateToken(token, config) {
                    http.Error(w, "invalid token", http.StatusUnauthorized)
                    return
                }
                ctx := context.WithValue(r.Context(), "tenant_id", getTenantFromToken(token))
                next.ServeHTTP(w, r.WithContext(ctx))
                return
            }

            if r.URL.Path == "/health" {
                next.ServeHTTP(w, r)
                return
            }

            http.Error(w, "authentication required", http.StatusUnauthorized)
        })
    }
}
```

### 4.5 Testing Strategy

- **Handler tests:** Mock storage and service dependencies, verify response codes and payloads
- **Middleware tests:** Verify auth, rate limiting, CORS behavior
- **SSE tests:** Verify event delivery, client disconnect handling
- **Integration tests:** Full request flow from HTTP to PostgreSQL

### 4.6 Success Criteria

- [ ] All REST endpoints implemented and returning correct responses
- [ ] SSE streaming delivers events in real-time
- [ ] Authentication blocks unauthorized requests
- [ ] Rate limiting prevents abuse
- [ ] All handlers validate input against protocol schemas
- [ ] Graceful shutdown handles in-flight requests

---

## STEP 5: Evidence Service

**Estimated Complexity:** 4/5  
**Dependencies:** STEPs 0, 1  
**Timeline:** Days 12–22

### 5.1 What to Build

The Evidence Service handles document ingestion, chunking, embedding, vector search, and evidence scoring.

#### Files to Create

```
services/evidence-service/
├── pyproject.toml
├── src/
│   └── mctagents/
│       ├── __init__.py
│       ├── ingestion/
│       │   ├── __init__.py
│       │   ├── parser.py
│       │   ├── chunker.py
│       │   └── pipeline.py
│       ├── retrieval/
│       │   ├── __init__.py
│       │   ├── vector_store.py
│       │   ├── hybrid_search.py
│       │   └── reranker.py
│       ├── scoring/
│       │   ├── __init__.py
│       │   ├── reliability.py
│       │   └── relevance.py
│       └── api/
│           ├── __init__.py
│           ├── routes.py
│           └── schemas.py
├── tests/
│   ├── unit/
│   │   ├── test_parser.py
│   │   ├── test_chunker.py
│   │   ├── test_vector_store.py
│   │   └── test_scoring.py
│   └── integration/
│       └── test_pipeline.py
```

### 5.2 Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Vector store | Qdrant | Open-source, easy Docker deployment, filtering support |
| Embedding model | nomic-embed-text (via Ollama) | Local-first, good quality, small footprint |
| Document parsing | PyMuPDF + python-docx + markdown | Cover PDF, Word, Markdown |
| Chunking | Custom recursive splitter | Preserve document structure |

### 5.3 Document Ingestion Pipeline

```python
# services/evidence-service/src/mctagents/ingestion/pipeline.py
from pathlib import Path
from mctagents.ingestion.parser import DocumentParser
from mctagents.ingestion.chunker import DocumentChunker
from mctagents.retrieval.vector_store import VectorStore

class IngestionPipeline:
    def __init__(self, vector_store: VectorStore, embedding_service):
        self.parser = DocumentParser()
        self.chunker = DocumentChunker(chunk_size_tokens=600, overlap_tokens=80, preserve_headings=True)
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    async def ingest(self, document_id: str, file_path: Path) -> dict:
        content = self.parser.parse(file_path)
        chunks = self.chunker.chunk(content)
        texts = [chunk.text for chunk in chunks]
        embeddings = await self.embedding_service.embed(texts)

        chunk_ids = await self.vector_store.upsert(
            collection="documents",
            ids=[f"{document_id}_chunk_{i}" for i in range(len(chunks))],
            vectors=embeddings,
            payloads=[{
                "document_id": document_id,
                "chunk_index": i,
                "content": chunk.text,
                "heading": chunk.heading,
                "page": chunk.page,
                "token_count": chunk.token_count,
            } for i, chunk in enumerate(chunks)],
        )

        return {"document_id": document_id, "chunk_count": len(chunks), "chunk_ids": chunk_ids}
```

### 5.4 Vector Search with Qdrant

```python
# services/evidence-service/src/mctagents/retrieval/vector_store.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

class VectorStore:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)

    async def ensure_collection(self, name: str, vector_size: int = 768):
        collections = self.client.get_collections().collections
        if not any(c.name == name for c in collections):
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )

    async def search(self, collection: str, query_vector: list[float], top_k: int = 10) -> list[dict]:
        results = self.client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=top_k,
        )
        return [{"id": hit.id, "score": hit.score, "payload": hit.payload} for hit in results]

    async def upsert(self, collection: str, ids: list[str], vectors: list[list[float]], payloads: list[dict]) -> list[str]:
        points = [PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i]) for i in range(len(ids))]
        self.client.upsert(collection_name=collection, points=points)
        return ids
```

### 5.5 Evidence Reliability Scoring

```python
# services/evidence-service/src/mctagents/scoring/reliability.py
class EvidenceReliabilityScorer:
    AUTHORITY_MAP = {
        "official_documentation": 0.9,
        "academic_paper": 0.85,
        "github_repository": 0.8,
        "uploaded_document": 0.7,
        "web_source": 0.6,
        "internal_memory": 0.5,
    }

    def score(self, evidence_item: dict) -> float:
        scores = {
            "source_authority": self.AUTHORITY_MAP.get(evidence_item.get("source_type", ""), 0.5),
            "recency": evidence_item.get("recency", 0.7),
            "specificity": evidence_item.get("specificity", 0.7),
            "independence": evidence_item.get("independence", 0.7),
            "retrieval_confidence": evidence_item.get("retrieval_score", 0.5),
        }
        weights = {"source_authority": 0.25, "recency": 0.15, "specificity": 0.25, "independence": 0.15, "retrieval_confidence": 0.20}
        overall = sum(scores[k] * weights[k] for k in scores)
        return round(min(1.0, max(0.0, overall)), 3)
```

### 5.6 Document Chunking Strategy

```python
# services/evidence-service/src/mctagents/ingestion/chunker.py
from dataclasses import dataclass

@dataclass
class DocumentChunk:
    text: str
    heading: str | None
    page: int | None
    section: str | None
    token_count: int
    index: int

class DocumentChunker:
    def __init__(self, chunk_size_tokens: int = 600, overlap_tokens: int = 80, preserve_headings: bool = True):
        self.chunk_size = chunk_size_tokens
        self.overlap = overlap_tokens
        self.preserve_headings = preserve_headings

    def chunk(self, content: list[dict]) -> list[DocumentChunk]:
        chunks = []
        current_chunk = []
        current_tokens = 0
        current_heading = None
        current_page = None

        for block in content:
            block_tokens = len(block["text"].split())
            if block.get("type") == "heading":
                if current_chunk and current_tokens > 0:
                    chunks.append(self._make_chunk(" ".join(current_chunk), current_heading, current_page, len(chunks)))
                    current_chunk = []
                    current_tokens = 0
                current_heading = block["text"]
            if current_tokens + block_tokens > self.chunk_size:
                if current_chunk:
                    chunks.append(self._make_chunk(" ".join(current_chunk), current_heading, current_page, len(chunks)))
                    current_chunk = []
                    current_tokens = 0
            current_chunk.append(block["text"])
            current_tokens += block_tokens
            current_page = block.get("page", current_page)

        if current_chunk:
            chunks.append(self._make_chunk(" ".join(current_chunk), current_heading, current_page, len(chunks)))
        return chunks

    def _make_chunk(self, text, heading, page, index) -> DocumentChunk:
        return DocumentChunk(text=text, heading=heading, page=page, section=heading, token_count=len(text.split()), index=index)
```

### 5.7 Testing Strategy

- **Unit tests for parser:** PDF, DOCX, Markdown parsing
- **Unit tests for chunker:** Verify chunk sizes, overlap, heading preservation
- **Unit tests for vector store:** Mock Qdrant client
- **Unit tests for scorer:** Verify reliability scoring logic
- **Integration tests:** Full pipeline with test documents

### 5.8 Success Criteria

- [ ] Documents ingested and chunked correctly
- [ ] Vector embeddings stored in Qdrant
- [ ] Search returns relevant results
- [ ] Reliability scoring produces reasonable scores
- [ ] API endpoints for upload and search work

---

## STEP 6: Frontend (Next.js)

**Estimated Complexity:** 4/5  
**Dependencies:** STEPs 0, 1, 4  
**Timeline:** Days 15–30

### 6.1 What to Build

The Studio UI makes users feel like they're watching a society of agents think together. It shows structured claims, evidence, objections, and decisions — never raw chain-of-thought.

#### Files to Create

```
apps/studio/
├── package.json
├── tsconfig.json
├── next.config.ts
├── tailwind.config.ts
├── src/
│   ├── app/
│   │   ├── layout.tsx
│   │   ├── page.tsx
│   │   └── runs/
│   │       ├── page.tsx
│   │       └── [runId]/
│   │           └── page.tsx
│   ├── components/
│   │   ├── studio/
│   │   │   ├── AgentSocietyBar.tsx
│   │   │   ├── ClaimNode.tsx
│   │   │   ├── ClaimGraph.tsx
│   │   │   ├── EvidenceCard.tsx
│   │   │   ├── EvidenceBoard.tsx
│   │   │   ├── ObjectionCard.tsx
│   │   │   ├── RevisionDiff.tsx
│   │   │   ├── JudgeScorePanel.tsx
│   │   │   ├── DebateTimeline.tsx
│   │   │   ├── RunReplayControls.tsx
│   │   │   ├── FinalAnswerPanel.tsx
│   │   │   └── NewSessionForm.tsx
│   │   └── dev/
│   │       ├── EventInspector.tsx
│   │       └── TraceViewer.tsx
│   ├── hooks/
│   │   ├── useSSE.ts
│   │   ├── useRun.ts
│   │   └── useClaimGraph.ts
│   ├── lib/
│   │   ├── api.ts
│   │   ├── sse.ts
│   │   └── types.ts
│   └── styles/
│       └── globals.css
└── tests/
    └── components/
        ├── DebateTimeline.test.tsx
        └── ClaimGraph.test.tsx
```

### 6.2 Technology Choices

| Component | Choice | Rationale |
|-----------|--------|-----------|
| Framework | Next.js 14+ (App Router) | React Server Components, SSR |
| Styling | Tailwind CSS + shadcn/ui | Rapid development, consistent design |
| State | React hooks + Context | Simple state management for MVP |
| Real-time | Custom SSE hook | Direct integration with Go gateway |
| Graph | React Flow | Claim graph visualization |
| Validation | Zod | Runtime type validation |

### 6.3 SSE Hook

```typescript
// apps/studio/src/hooks/useSSE.ts
import { useEffect, useRef, useCallback, useState } from "react";

interface SSEEvent {
  event_id: string;
  run_id: string;
  type: string;
  sequence: number;
  agent_id?: string;
  payload: Record<string, unknown>;
  created_at: string;
}

export function useSSE(runId: string | null) {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [connected, setConnected] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (!runId) return;
    const es = new EventSource(`/api/v1/runs/${runId}/events`);
    esRef.current = es;
    es.onopen = () => setConnected(true);
    es.onerror = () => setConnected(false);

    const types = [
      "run_started", "problem_framed", "claim_created", "evidence_attached",
      "objection_created", "claim_revised", "judge_scored", "final_answer_created", "run_completed",
    ];
    types.forEach((type) => {
      es.addEventListener(type, (e) => {
        setEvents((prev) => [...prev, JSON.parse(e.data)]);
      });
    });
  }, [runId]);

  useEffect(() => {
    connect();
    return () => { esRef.current?.close(); };
  }, [connect]);

  return { events, connected };
}
```

### 6.4 Claim Graph Component

```typescript
// apps/studio/src/components/studio/ClaimGraph.tsx
"use client";
import ReactFlow, { Node, Edge, Background, Controls } from "reactflow";
import { useMemo } from "react";

export function ClaimGraph({ claims, evidence, objections, revisions }) {
  const { nodes, edges } = useMemo(() => {
    const nodes: Node[] = claims.map((claim, i) => ({
      id: claim.id,
      position: { x: (i % 3) * 300, y: Math.floor(i / 3) * 200 },
      data: { label: claim.text },
    }));

    const edges: Edge[] = [];
    revisions.forEach((rev) => {
      edges.push({ id: `rev_${rev.id}`, source: rev.old_claim_id, target: rev.new_claim_id, label: "revised", animated: true });
    });
    evidence.forEach((ev) => {
      ev.supports_claim_ids?.forEach((claimId) => {
        edges.push({ id: `ev_${ev.id}_${claimId}`, source: ev.id, target: claimId, label: "supports", style: { stroke: "#22c55e" } });
      });
    });
    objections.forEach((obj) => {
      edges.push({ id: `obj_${obj.id}`, source: obj.id, target: obj.target_claim_id, label: "attacks", style: { stroke: "#ef4444" } });
    });

    return { nodes, edges };
  }, [claims, evidence, objections, revisions]);

  return (
    <div className="h-[600px] border rounded-lg">
      <ReactFlow nodes={nodes} edges={edges}>
        <Background />
        <Controls />
      </ReactFlow>
    </div>
  );
}
```

### 6.5 Testing Strategy

- **Component tests:** Render each component with mock data, verify output
- **Hook tests:** Mock EventSource, verify state updates
- **Integration tests:** Full page render with mock API responses

### 6.6 Success Criteria

- [ ] New session form creates a run
- [ ] SSE connection established and events displayed
- [ ] Claim graph renders with zoom/pan
- [ ] Evidence board shows supporting/attacking evidence
- [ ] Debate timeline shows chronological events
- [ ] Final answer panel displays synthesized answer
- [ ] All components responsive

---

## STEP 7: SDK Packages

**Estimated Complexity:** 3/5  
**Dependencies:** STEPs 1, 4  
**Timeline:** Days 20–28

### 7.1 What to Build

SDKs let developers integrate mCTAgents into their own products without adopting the full Studio UI.

#### TypeScript SDK

```typescript
// packages/ts-sdk/src/index.ts
export class MCTAgentsClient {
  private baseUrl: string;
  private apiKey?: string;

  constructor(config: { baseUrl: string; apiKey?: string }) {
    this.baseUrl = config.baseUrl;
    this.apiKey = config.apiKey;
  }

  get runs() {
    return {
      create: async (params: { problem: string; mode?: string; evidence_policy?: string; budget?: Record<string, number> }) => {
        const resp = await fetch(`${this.baseUrl}/v1/runs`, {
          method: "POST",
          headers: this.headers(),
          body: JSON.stringify(params),
        });
        return resp.json();
      },
      get: async (runId: string) => {
        const resp = await fetch(`${this.baseUrl}/v1/runs/${runId}`, { headers: this.headers() });
        return resp.json();
      },
      stream: async function* (runId: string): AsyncGenerator<ReasoningEvent> {
        const es = new EventSource(`${this.baseUrl}/v1/runs/${runId}/events`);
        const queue: ReasoningEvent[] = [];
        let resolve: (() => void) | null = null;
        const types = ["run_started", "problem_framed", "claim_created", "evidence_attached", "objection_created", "claim_revised", "judge_scored", "final_answer_created", "run_completed"];
        types.forEach((type) => {
          es.addEventListener(type, (e) => { queue.push(JSON.parse(e.data)); resolve?.(); });
        });
        try {
          while (true) {
            if (queue.length === 0) await new Promise<void>((r) => (resolve = r));
            yield queue.shift()!;
          }
        } finally { es.close(); }
      },
      cancel: async (runId: string) => {
        await fetch(`${this.baseUrl}/v1/runs/${runId}/cancel`, { method: "POST", headers: this.headers() });
      },
    };
  }

  private headers(): Record<string, string> {
    const h: Record<string, string> = { "Content-Type": "application/json" };
    if (this.apiKey) h["X-API-Key"] = this.apiKey;
    return h;
  }
}

interface ReasoningEvent { event_id: string; run_id: string; type: string; sequence: number; payload: Record<string, unknown>; created_at: string; }
```

#### Python SDK

```python
# packages/py-sdk/src/mctagents_sdk/__init__.py
import httpx
import json
from typing import Generator
from dataclasses import dataclass

@dataclass
class Run:
    run_id: str
    status: str
    events_url: str

@dataclass
class ReasoningEvent:
    event_id: str
    run_id: str
    type: str
    sequence: int
    payload: dict
    created_at: str

class MCTAgentsClient:
    def __init__(self, base_url: str, api_key: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.Client(timeout=60.0)

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        return headers

    def create_run(self, problem: str, **kwargs) -> Run:
        resp = self.client.post(f"{self.base_url}/v1/runs", json={"problem": problem, **kwargs}, headers=self._headers())
        resp.raise_for_status()
        return Run(**resp.json())

    def stream_events(self, run_id: str) -> Generator[ReasoningEvent, None, None]:
        with self.client.stream("GET", f"{self.base_url}/v1/runs/{run_id}/events", headers=self._headers()) as resp:
            event_type = None
            data_lines = []
            for line in resp.iter_lines():
                if line.startswith("event: "):
                    event_type = line[7:]
                elif line.startswith("data: "):
                    data_lines.append(line[6:])
                elif line == "" and data_lines:
                    payload = json.loads("\n".join(data_lines))
                    yield ReasoningEvent(event_id=payload["event_id"], run_id=payload["run_id"], type=event_type or payload["type"], sequence=payload["sequence"], payload=payload["payload"], created_at=payload["created_at"])
                    event_type = None
                    data_lines = []

    def cancel_run(self, run_id: str) -> None:
        self.client.post(f"{self.base_url}/v1/runs/{run_id}/cancel", headers=self._headers()).raise_for_status()
```

### 7.2 Testing Strategy

- **Unit tests for SDK clients:** Mock HTTP responses, verify request/response handling
- **Streaming tests:** Verify SSE parsing in both TS and Python
- **Type tests:** TypeScript strict mode compilation

### 7.3 Success Criteria

- [ ] TypeScript SDK compiles and all exports work
- [ ] Python SDK passes type checking
- [ ] Both SDKs can create runs and stream events
- [ ] Plugin contract is defined and documented

---

## STEP 8: Evaluation & Benchmarks

**Estimated Complexity:** 4/5  
**Dependencies:** STEPs 1, 3  
**Timeline:** Days 25–35

### 8.1 What to Build

The benchmark suite proves that social reasoning improves answer quality compared to single-agent baselines.

#### Files to Create

```
benchmarks/
├── pyproject.toml
├── src/
│   └── benchmarks/
│       ├── __init__.py
│       ├── runner.py
│       ├── scorers/
│       │   ├── correctness.py
│       │   ├── completeness.py
│       │   ├── consistency.py
│       │   ├── evidence_quality.py
│       │   ├── debate_quality.py
│       │   └── llm_judge.py
│       ├── datasets/
│       │   ├── software_architecture.yaml
│       │   ├── research_debate.yaml
│       │   ├── security_review.yaml
│       │   └── product_decision.yaml
│       ├── baselines/
│       │   └── single_agent.py
│       └── leaderboard.py
├── tasks/
│   └── software_architecture_001.yaml
├── results/
│   └── .gitkeep
└── tests/
    └── test_scorers.py
```

### 8.2 Benchmark Dataset Structure

```yaml
# benchmarks/tasks/software_architecture_001.yaml
id: software_architecture_001
problem: "Design a scalable private document QA system for a 500-person company."
expected_dimensions:
  - architecture
  - retrieval
  - security
  - observability
  - deployment
rubric:
  correctness: 0.25
  completeness: 0.25
  feasibility: 0.20
  evidence: 0.15
  risk_awareness: 0.15
agents:
  - problem_framer
  - solution_architect
  - evidence_agent
  - security_agent
  - critic
  - judge
  - synthesizer
policy: deep_social_reasoning
```

### 8.3 Scoring Pipeline

```python
# benchmarks/src/benchmarks/runner.py
class BenchmarkRunner:
    def __init__(self, mctagents_client, single_agent_client):
        self.mct_client = mctagents_client
        self.single_client = single_agent_client
        self.scorers = [
            CorrectnessScorer(),
            CompletenessScorer(),
            ConsistencyScorer(),
            EvidenceQualityScorer(),
            DebateQualityScorer(),
        ]

    async def run_benchmark(self, task: dict) -> dict:
        single_result = await self.single_client.run(task["problem"])
        mct_run = self.mct_client.create_run(problem=task["problem"], mode=task.get("policy", "balanced_reasoning"))
        mct_events = list(self.mct_client.stream_events(mct_run.run_id))

        single_scores = self._score(single_result, task["rubric"])
        mct_scores = self._score(mct_events, task["rubric"])

        return {
            "task_id": task["id"],
            "single_agent": single_scores,
            "mctagents": mct_scores,
            "improvement": {k: mct_scores[k] - single_scores[k] for k in single_scores},
        }

    def _score(self, result, rubric) -> dict:
        return {scorer.name: scorer.score(result) for scorer in self.scorers}
```

### 8.4 Leaderboard

```python
# benchmarks/src/benchmarks/leaderboard.py
from dataclasses import dataclass
from pathlib import Path

@dataclass
class LeaderboardEntry:
    runtime: str
    model: str
    policy: str
    score: float
    latency: float
    tokens: int
    cost: float
    unsupported_claim_rate: float
    drift_score: float

class Leaderboard:
    def __init__(self, results_dir: str):
        self.results_dir = Path(results_dir)

    def get_top(self, n: int = 10) -> list[LeaderboardEntry]:
        return []

    def export_markdown(self) -> str:
        entries = self.get_top(20)
        lines = [
            "| Rank | Runtime | Model | Policy | Score | Latency | Tokens | Unsupported Rate |",
            "|------|---------|-------|--------|-------|---------|--------|------------------|",
        ]
        for i, e in enumerate(entries, 1):
            lines.append(f"| {i} | {e.runtime} | {e.model} | {e.policy} | {e.score:.3f} | {e.latency:.1f}s | {e.tokens} | {e.unsupported_claim_rate:.3f} |")
        return "\n".join(lines)
```

### 8.5 Evaluation Tracks

**Track A: Single-agent vs Social-agent**
- correctness, completeness, logical consistency, actionability, risk awareness, clarity

**Track B: Evidence grounding**
- unsupported claim rate, evidence relevance, citation precision, source diversity, source reliability

**Track C: Debate quality**
- useful objection rate, claim revision improvement, repeated argument rate, problem drift score, consensus quality

**Track D: Production efficiency**
- latency, tokens, model calls, tool calls, retry count, failure rate, cost per useful answer

### 8.6 Testing Strategy

- **Scorer unit tests:** Verify scoring logic with known inputs
- **Benchmark runner tests:** Mock model responses, verify scoring pipeline
- **Leaderboard tests:** Verify sorting and export

### 8.7 Success Criteria

- [ ] At least 5 benchmark tasks defined
- [ ] Single-agent baseline implemented
- [ ] All scorers produce reasonable scores
- [ ] Leaderboard generates correctly
- [ ] Benchmark run completes end-to-end

---

## STEP 9: Production Readiness

**Estimated Complexity:** 4/5  
**Dependencies:** STEPs 0–6  
**Timeline:** Days 30–40

### 9.1 What to Build

Production hardening: Docker deployment, Kubernetes manifests, observability, security, and documentation.

#### Files to Create

```
deployments/
├── docker-compose/
│   ├── docker-compose.prod.yml
│   └── .env.production
├── k8s/
│   ├── namespace.yaml
│   ├── api-gateway/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── hpa.yaml
│   ├── reasoning-engine/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── model-gateway/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── evidence-service/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   ├── postgres/
│   │   ├── statefulset.yaml
│   │   └── service.yaml
│   └── redis/
│       ├── deployment.yaml
│       └── service.yaml
├── helm/
│   └── mctagents/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
└── observability/
    ├── otel-config.yaml
    ├── grafana/
    │   └── dashboards/
    │       ├── mctagents-overview.json
    │       └── model-provider.json
    └── alerting/
        └── rules.yaml
```

### 9.2 Docker Compose Production

```yaml
# deployments/docker-compose/docker-compose.prod.yml
services:
  api-gateway:
    build:
      context: ../../services/api-gateway
      dockerfile: Dockerfile
      target: production
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgres://mctagents:${POSTGRES_PASSWORD}@postgres:5432/mctagents
      - REDIS_URL=redis://redis:6379
      - MODEL_GATEWAY_URL=http://model-gateway:8090
      - REASONING_ENGINE_URL=http://reasoning-engine:8000
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M

  reasoning-engine:
    build:
      context: ../../services/reasoning-engine
      dockerfile: Dockerfile
      target: production
    environment:
      - DATABASE_URL=postgres://mctagents:${POSTGRES_PASSWORD}@postgres:5432/mctagents
      - MODEL_GATEWAY_URL=http://model-gateway:8090
      - EVIDENCE_SERVICE_URL=http://evidence-service:8001
    depends_on:
      postgres:
        condition: service_healthy
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G

  model-gateway:
    build:
      context: ../../services/model-gateway
      dockerfile: Dockerfile
      target: production
    ports:
      - "8090:8090"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      ollama:
        condition: service_healthy
    restart: unless-stopped

  evidence-service:
    build:
      context: ../../services/evidence-service
      dockerfile: Dockerfile
      target: production
    ports:
      - "8001:8001"
    environment:
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
    depends_on:
      qdrant:
        condition: service_healthy
    restart: unless-stopped
```

### 9.3 Kubernetes Manifests

```yaml
# deployments/k8s/api-gateway/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-gateway
  namespace: mctagents
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-gateway
  template:
    metadata:
      labels:
        app: api-gateway
    spec:
      containers:
        - name: api-gateway
          image: mctagents/api-gateway:latest
          ports:
            - containerPort: 8080
          env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: mctagents-secrets
                  key: database-url
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 10
            periodSeconds: 15
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: api-gateway
  namespace: mctagents
spec:
  selector:
    app: api-gateway
  ports:
    - port: 80
      targetPort: 8080
---
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

### 9.4 Observability (OpenTelemetry)

```python
# services/reasoning-engine/src/mctagents/telemetry.py
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource

def init_telemetry(service_name: str):
    resource = Resource(attributes={SERVICE_NAME: service_name})
    provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    return trace.get_tracer(service_name)

tracer = init_telemetry("reasoning-engine")
```

### 9.5 Security Hardening

Key security measures:

1. **Tool permission model:** Every tool call goes through a gateway with policy checks
2. **Document safety:** Uploaded documents marked as untrusted, prompt injection detection
3. **Input validation:** All API inputs validated against protocol schemas
4. **Secrets management:** No secrets in code, use environment variables
5. **CORS:** Restrictive CORS policy for production
6. **Rate limiting:** Per-tenant rate limiting on all endpoints
7. **Audit logging:** Immutable audit trail for all sensitive actions
8. **SQL injection prevention:** Parameterized queries only
9. **Dependency scanning:** Regular dependency vulnerability scans

### 9.6 Documentation

Required documentation files:

```
docs/
├── getting-started.md
├── quickstart.md
├── concepts/
│   ├── ccsr-protocol.md
│   ├── agent-society.md
│   ├── claim-graph.md
│   └── debate-policies.md
├── architecture/
│   ├── overview.md
│   ├── services.md
│   └── data-flow.md
├── api/
│   ├── rest-api.md
│   ├── events.md
│   └── errors.md
├── sdk/
│   ├── typescript.md
│   └── python.md
├── deployment/
│   ├── docker-compose.md
│   ├── kubernetes.md
│   └── configuration.md
├── contributing/
│   ├── guide.md
│   ├── code-style.md
│   └── testing.md
├── security/
│   ├── policy.md
│   └── threat-model.md
└── benchmarks/
    ├── overview.md
    └── running-benchmarks.md
```

### 9.7 Testing Strategy

- **Docker Compose smoke test:** `docker compose -f prod.yml up` starts successfully
- **Kubernetes deployment test:** `kubectl apply -f` creates all resources
- **Health check tests:** All services report healthy
- **Load test:** Run concurrent requests, verify no crashes
- **Security scan:** Run `trivy` or similar on Docker images

### 9.8 Success Criteria

- [ ] Docker Compose production config works
- [ ] Kubernetes manifests deploy successfully
- [ ] OpenTelemetry traces visible in Jaeger/Grafana
- [ ] Grafana dashboards show key metrics
- [ ] All security measures implemented
- [ ] Documentation complete and accurate

---

## STEP 10: Community & Ecosystem

**Estimated Complexity:** 2/5  
**Dependencies:** STEPs 0–9  
**Timeline:** Days 35–45

### 10.1 What to Build

Community infrastructure for open-source adoption: contributing guidelines, examples, integration guides, and community forums.

#### Files to Create

```
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── LICENSE
├── examples/
│   ├── notebooklm-style/
│   │   ├── README.md
│   │   └── main.py
│   ├── software-architecture-review/
│   │   ├── README.md
│   │   └── main.py
│   ├── research-debate/
│   │   ├── README.md
│   │   └── main.py
│   ├── security-review/
│   │   ├── README.md
│   │   └── main.py
│   └── product-decision/
│       ├── README.md
│       └── main.py
├── integrations/
│   ├── langchain/
│   │   └── README.md
│   ├── llamaindex/
│   │   └── README.md
│   └── openai/
│       └── README.md
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md
│   │   ├── feature_request.md
│   │   └── question.md
│   ├── PULL_REQUEST_TEMPLATE.md
│   └── workflows/
│       ├── ci.yml
│       ├── benchmark.yml
│       └── release.yml
└── docs/
    └── index.md
```

### 10.2 Contributing Guidelines

```markdown
# Contributing to mCTAgents

## Getting Started

1. Fork the repository
2. Clone your fork
3. Run `make setup-dev` to install dependencies
4. Run `make docker-up` to start services
5. Run `make seed-demo` to populate demo data
6. Run `make test` to verify everything works

## Development Workflow

1. Create a branch: `git checkout -b feat/my-feature`
2. Make changes following code style guidelines
3. Run `make lint` and `make test`
4. Commit with conventional commits: `feat: add new feature`
5. Push and create a pull request

## Code Style

- Python: Ruff + mypy (see AGENTS.md)
- TypeScript: Prettier + ESLint + strict mode
- Go: gofmt + golangci-lint
- All code must have tests

## Reporting Issues

- Use GitHub issue templates
- Include reproduction steps
- Include environment details
```

### 10.3 Example Verticals

Each example includes a README with setup instructions, the problem statement, expected agent society, and sample output.

```python
# examples/software-architecture-review/main.py
from mctagents_sdk import MCTAgentsClient

client = MCTAgentsClient(base_url="http://localhost:8080")

run = client.create_run(
    problem="Should we migrate our monolith to microservices?",
    mode="deep_social_reasoning",
    evidence_policy="required_for_major_claims",
)

for event in client.stream_events(run.run_id):
    print(f"[{event.type}] {event.payload}")
```

### 10.4 Integration Guides

- **LangChain:** How to use mCTAgents as a tool in LangChain
- **LlamaIndex:** How to connect mCTAgents to LlamaIndex pipelines
- **OpenAI:** How to use mCTAgents alongside OpenAI function calling

### 10.5 CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  schema-validation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - run: cd packages/core-protocol && pnpm install && pnpm test

  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: cd services/reasoning-engine && pip install -e ".[dev]" && pytest

  go-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: "1.22"
      - run: cd services/api-gateway && go test ./...

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v2
      - run: cd apps/studio && pnpm install && pnpm build

  docker-smoke:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: make docker-up && sleep 30 && make test
```

### 10.6 Testing Strategy

- **Contributing guide review:** Ensure all commands work
- **Example verification:** Run each example end-to-end
- **CI pipeline:** All jobs pass on clean checkout

### 10.7 Success Criteria

- [ ] CONTRIBUTING.md complete and accurate
- [ ] At least 3 example verticals working
- [ ] CI pipeline runs all checks
- [ ] Issue and PR templates created
- [ ] Integration guides written
- [ ] LICENSE file added (MIT or Apache 2.0)

---

## Summary: Implementation Timeline

| Step | Phase | Days | Complexity | Key Deliverable |
|------|-------|------|------------|-----------------|
| STEP 0 | Foundation | 1–5 | 3/5 | Monorepo + DB schema + Docker Compose |
| STEP 1 | Protocol | 3–8 | 3/5 | CCSR schemas + types + invariants |
| STEP 2 | Model Gateway | 5–10 | 3/5 | Ollama + OpenAI-compatible provider |
| STEP 3 | Reasoning Engine | 8–20 | 5/5 | 5 agents + state machine + debate |
| STEP 4 | API Gateway | 10–18 | 3/5 | REST + SSE + auth |
| STEP 5 | Evidence Service | 12–22 | 4/5 | RAG + Qdrant + scoring |
| STEP 6 | Frontend | 15–30 | 4/5 | Studio UI + claim graph + timeline |
| STEP 7 | SDKs | 20–28 | 3/5 | TS + Python SDKs |
| STEP 8 | Benchmarks | 25–35 | 4/5 | Benchmark suite + leaderboard |
| STEP 9 | Production | 30–40 | 4/5 | K8s + observability + security |
| STEP 10 | Community | 35–45 | 2/5 | Docs + examples + CI |

## Dependencies Graph

```
STEP 0 ──┬──> STEP 1 ──┬──> STEP 3 ──┬──> STEP 6
          │              │              │
          ├──> STEP 2    ├──> STEP 4 ──┤
          │              │              │
          └──> STEP 5    ├──> STEP 7 ──┤
                         │              │
                         └──> STEP 8 ──┤
                                        │
                              STEP 9 ──┘
                                        │
                              STEP 10 ──┘
```

## Release Gates

| Version | Milestone | Steps Completed |
|---------|-----------|-----------------|
| v0.1 | Vertical Slice | STEPs 0–4 + partial 6 |
| v0.2 | Claim Graph + Evidence | STEPs 0–5 + 6 |
| v0.3 | SDKs | STEPs 0–7 |
| v0.4 | Benchmarks | STEPs 0–8 |
| v0.5 | Production | STEPs 0–9 |
| v1.0 | Open Source Launch | All STEPs |

## Anti-Patterns to Avoid

1. **Agent chatroom:** Agents talk but no structured claims exist. Fix: Use claim-centered state.
2. **Always deep mode:** Every question triggers many agents. Fix: Use adaptive debate and early stopping.
3. **Framework identity:** Project becomes "LangGraph app." Fix: Own protocol; implement LangGraph as adapter.
4. **RAG as prompt stuffing:** Retrieved chunks dumped without provenance. Fix: Use evidence objects with support/attack links.
5. **Hidden quality:** No one knows whether multi-agent reasoning helped. Fix: Benchmark single-agent vs social-agent.
6. **Over-engineered microservices too early:** Start with modular services, split when boundaries stabilize.
7. **Complex UI before core reasoning works:** Build reasoning engine first, UI second.

## Architecture Decisions

| ADR | Decision | Rationale |
|-----|----------|-----------|
| ADR-001 | Protocol-first architecture | Core schemas are source of truth |
| ADR-002 | Claim-centered state | Argument graph > message logs |
| ADR-003 | Go API Gateway + Python first runtime | Performance + AI ecosystem |
| ADR-004 | Ollama/local-first model gateway | Low barrier to entry |
| ADR-005 | SSE first, WebSocket later | Simpler for MVP |
| ADR-006 | Postgres-first graph storage | Avoid premature graph DB |
| ADR-007 | MCP only through Tool Gateway | Security boundary |
| ADR-008 | Benchmark suite required before v1.0 | Trust and quality proof |

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Too many agents causing latency | Adaptive debate, early stopping, budget limits |
| Debate drift | Drift detection, problem frame anchoring |
| Weak evidence causing hallucinated authority | Evidence reliability scoring, source diversity |
| Framework lock-in | Runtime adapter pattern, protocol-first |
| Over-engineered microservices | Start with 4 services, split when needed |
| Complex UI before core reasoning | Build reasoning engine first |
| No benchmark proof | Benchmark suite required before v1.0 |
