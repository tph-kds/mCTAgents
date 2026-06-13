# mCTAgents Planning

This folder contains the complete implementation plan for mCTAgents - an open-source social reasoning engine where a society of agents debate, challenge, and refine claims to produce transparent, evidence-backed answers.

## Quick Links

| Document | Purpose |
|----------|---------|
| [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) | **Full 4000+ line plan** with code examples, schemas, and detailed specifications |
| [ROADMAP.md](ROADMAP.md) | High-level timeline and milestones |
| [CHEATSHEET.md](CHEATSHEET.md) | Quick reference card for the project |

## Structure

```
.opencode/planning/
├── README.md                              # This file
├── IMPLEMENTATION_PLAN.md                 # Full implementation plan (4000+ lines)
├── ROADMAP.md                             # Timeline and milestones
├── CHEATSHEET.md                          # Quick reference
├── decisions/                             # Architecture Decision Records
│   ├── ADR-001-protocol-first.md
│   ├── ADR-002-claim-centered.md
│   ├── ADR-003-go-python.md
│   ├── ADR-004-local-first.md
│   ├── ADR-005-sse-first.md
│   ├── ADR-006-postgres-graph.md
│   ├── ADR-007-tool-gateway.md
│   └── ADR-008-benchmarks-required.md
├── sprints/                               # Sprint planning
│   ├── README.md
│   ├── SPRINT_00_SETUP.md
│   ├── SPRINT_01_PROTOCOL.md
│   ├── SPRINT_02_GATEWAY.md
│   ├── SPRINT_03_ENGINE.md
│   ├── SPRINT_04_API.md
│   ├── SPRINT_05_EVIDENCE.md
│   ├── SPRINT_06_UI.md
│   ├── SPRINT_07_SDK.md
│   ├── SPRINT_08_BENCH.md
│   ├── SPRINT_09_PROD.md
│   ├── SPRINT_10_LAUNCH.md
│   └── retrospective/
├── STEP_00_FOUNDATION.md                  # Step-by-step breakdowns
├── STEP_01_PROTOCOL.md
├── STEP_02_MODEL_GATEWAY.md
├── STEP_03_REASONING_ENGINE.md
├── STEP_04_API_GATEWAY.md
├── STEP_05_EVIDENCE_SERVICE.md
├── STEP_06_FRONTEND.md
├── STEP_07_SDK.md
├── STEP_08_BENCHMARKS.md
├── STEP_09_PRODUCTION.md
└── STEP_10_COMMUNITY.md
```

## Implementation Steps

| Step | Name | Days | Complexity | Sprint |
|------|------|------|------------|--------|
| 0 | Project Foundation | 1-5 | 3/5 | Sprint 00 |
| 1 | Core Protocol Layer | 3-8 | 3/5 | Sprint 01 |
| 2 | Model Gateway | 5-10 | 3/5 | Sprint 02 |
| 3 | Reasoning Engine | 8-20 | 5/5 | Sprint 03 |
| 4 | API Gateway | 10-18 | 3/5 | Sprint 04 |
| 5 | Evidence Service | 12-22 | 4/5 | Sprint 05 |
| 6 | Frontend | 15-30 | 4/5 | Sprint 06 |
| 7 | SDK Packages | 20-28 | 3/5 | Sprint 07 |
| 8 | Evaluation & Benchmarks | 25-35 | 4/5 | Sprint 08 |
| 9 | Production Readiness | 30-40 | 4/5 | Sprint 09 |
| 10 | Community & Ecosystem | 35-45 | 2/5 | Sprint 10 |

## Architecture Decisions

| ADR | Decision | Status |
|-----|----------|--------|
| ADR-001 | Protocol-first architecture | Accepted |
| ADR-002 | Claim-centered state | Accepted |
| ADR-003 | Go API Gateway + Python runtime | Accepted |
| ADR-004 | Ollama/local-first model gateway | Accepted |
| ADR-005 | SSE first, WebSocket later | Accepted |
| ADR-006 | Postgres-first graph storage | Accepted |
| ADR-007 | MCP only through Tool Gateway | Accepted |
| ADR-008 | Benchmark suite required before v1.0 | Accepted |

## Dependency Graph

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

| Version | Milestone | Steps |
|---------|-----------|-------|
| v0.1 | Vertical Slice | 0-4 + partial 6 |
| v0.2 | Claim Graph + Evidence | 0-5 + 6 |
| v0.3 | SDKs | 0-7 |
| v0.4 | Benchmarks | 0-8 |
| v0.5 | Production | 0-9 |
| v1.0 | Open Source Launch | All |

## How to Use This Plan

1. **Start with IMPLEMENTATION_PLAN.md** - Read the full 4000+ line plan for detailed specifications
2. **Check ROADMAP.md** - Understand the timeline and milestones
3. **Follow sprints** - Each sprint has daily tasks and definition of done
4. **Reference ADRs** - Understand the reasoning behind architecture decisions
5. **Use CHEATSHEET.md** - Quick reference for commands and structures
