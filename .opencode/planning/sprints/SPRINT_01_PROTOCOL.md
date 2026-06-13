# Sprint 01: Core Protocol

**Duration:** Days 3-8 | **Goal:** CCSR schemas, TypeScript types, Pydantic models, invariants

## Tasks

### Day 3-4: JSON Schemas
- [ ] Create `problem-frame.json` schema
- [ ] Create `claim.json` schema (with all statuses, types)
- [ ] Create `evidence.json` schema (with source types)
- [ ] Create `objection.json` schema (with severity levels)
- [ ] Create `revision.json` schema (with revision types)
- [ ] Create `decision.json` schema (with score breakdown)
- [ ] Create `final-answer.json` schema (with risks)
- [ ] Create `event.json` schema (with all event types)
- [ ] Create `run-state.json` schema
- [ ] Create `debate-policy.json` schema
- [ ] Create `agent-contract.json` schema
- [ ] Validate all schemas against JSON Schema Draft 2020-12

### Day 5-6: TypeScript Types
- [ ] Create `src/types/problem-frame.ts`
- [ ] Create `src/types/claim.ts` (with ClaimType, ClaimStatus, ClaimScores)
- [ ] Create `src/types/evidence.ts` (with SourceType)
- [ ] Create `src/types/objection.ts` (with ObjectionSeverity)
- [ ] Create `src/types/revision.ts` (with RevisionType)
- [ ] Create `src/types/decision.ts`
- [ ] Create `src/types/final-answer.ts` (with RiskItem, RejectedAlternative)
- [ ] Create `src/types/event.ts` (with EventType)
- [ ] Create `src/types/index.ts` barrel export
- [ ] Create `src/constants/` with enums
- [ ] Verify TypeScript strict mode compilation

### Day 6-7: Python Pydantic Models
- [ ] Create `core/protocol/problem_frame.py`
- [ ] Create `core/protocol/claim.py` (with all enums)
- [ ] Create `core/protocol/evidence.py`
- [ ] Create `core/protocol/objection.py`
- [ ] Create `core/protocol/revision.py`
- [ ] Create `core/protocol/decision.py`
- [ ] Create `core/protocol/final_answer.py`
- [ ] Create `core/protocol/event.py`
- [ ] Create `core/protocol/debate_policy.py`
- [ ] Create `core/protocol/__init__.py` barrel export
- [ ] Verify Pydantic v2 validation works

### Day 7-8: Invariants + Validation
- [ ] Implement `final_answer_references_accepted_claims` check
- [ ] Implement `high_confidence_needs_evidence` check
- [ ] Implement `rejected_claims_need_reason` check
- [ ] Implement `revision_links_old_and_new` check
- [ ] Implement `tool_results_traceable` check
- [ ] Implement `final_answer_declares_risks` check
- [ ] Create validator.ts for TypeScript
- [ ] Create validators.py for Python
- [ ] Write test suite for all 6 invariants
- [ ] Ensure cross-language consistency (TS ↔ Python)

## Definition of Done
- [ ] All 11 JSON schemas defined and valid
- [ ] TypeScript types compile with strict mode
- [ ] Pydantic models pass all validation tests
- [ ] All 6 required invariants enforced
- [ ] 100% test coverage on validation logic
- [ ] Schema validation test suite passes

## Risks
- **Schema versioning:** Use `$id` URIs for version tracking
- **Cross-language drift:** Automated consistency tests

## Retro Notes
- _To be filled after sprint completion_
