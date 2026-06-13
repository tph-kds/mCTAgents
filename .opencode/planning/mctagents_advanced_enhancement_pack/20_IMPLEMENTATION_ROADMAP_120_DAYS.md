# Implementation Roadmap: 120 Days

## Phase 1: Days 1-14 — Vertical Slice

Goal: one complete social reasoning run.

Build:

```text
core protocol schemas
reasoning-engine with 5 agents
Go API Gateway
Ollama model gateway
SSE event stream
Next.js live timeline
Postgres storage
```

Success demo:

```text
User submits problem -> agents propose/evidence/criticize/revise -> judge -> final answer -> UI timeline
```

## Phase 2: Days 15-30 — Claim Graph and Evidence Board

Build:

```text
claim graph storage
argument edges
evidence service
Qdrant document retrieval
claim graph UI
evidence board UI
```

## Phase 3: Days 31-45 — SDK and Integration

Build:

```text
TypeScript SDK
Python SDK
public REST docs
embeddable React components
example integration apps
```

## Phase 4: Days 46-60 — Evaluation and Benchmarks

Build:

```text
single-agent baseline
mCTAgents benchmark suite
rubric-based scoring
unsupported claim detector
benchmark dashboard
```

## Phase 5: Days 61-75 — Tool Gateway and MCP

Build:

```text
tool gateway
MCP client adapter
permission policies
tool audit logs
safe tool output handling
```

## Phase 6: Days 76-90 — Reliability

Build:

```text
idempotency keys
retry policies
outbox/inbox pattern
dead-letter events
circuit breakers
partial run recovery
```

## Phase 7: Days 91-105 — Advanced Runtime Adapters

Build:

```text
Pydantic AI adapter
OpenAI Agents SDK adapter
Mastra proof-of-concept adapter
runtime capability matrix
```

## Phase 8: Days 106-120 — Open-Source Launch Quality

Build:

```text
README polish
docs site
contribution guide
security policy
example videos/GIFs
benchmark report
GitHub issue templates
plugin templates
```

## Release gates

```text
v0.1: vertical slice
v0.2: claim graph + evidence
v0.3: SDKs
v0.4: benchmarks
v0.5: MCP/tool gateway
v1.0: stable protocol + production deployment guide
```
