# STEP 1: Core Protocol Layer

**Timeline:** Days 3-8 | **Complexity:** 3/5 | **Dependencies:** STEP 0

## Goal

Define the CCSR (Claim-Centered Social Reasoning) protocol as the source of truth that all services implement against.

## Protocol Objects

### ProblemFrame
Defines what agents are solving. Fields: `original_input`, `normalized_problem`, `constraints`, `success_criteria`, `risk_level`, `domain`.

### Claim
A proposition that can be supported, attacked, revised, accepted, or rejected. Has `claim_type`, `confidence` (0-1), `status` (9 states), `evidence_status`, and optional `scores`.

### Evidence
Source-backed support or attack item. Has `source_type`, `reliability_score`, and links to claims it supports/attacks.

### Objection
A challenge against a claim. Has `severity` (low/critical), `requested_fix`, and resolution tracking.

### Revision
Links old claim to new claim after improvement. Has `revision_type` (objection_driven, evidence_driven, judge_feedback, self_improvement).

### Decision
Judge output with `accepted_claim_ids`, `rejected_claim_ids`, `uncertain_claim_ids`, and `score_breakdown`.

### FinalAnswer
Synthesized answer referencing accepted claims. Must include `risks`, `rejected_alternatives`, and `next_steps`.

## 6 Required Invariants

1. **Final answers reference accepted claims** - No referencing non-accepted claims
2. **High-confidence claims need evidence** - Or explicit uncertainty
3. **Rejected claims need reasons** - Every rejection documented
4. **Revisions link old and new** - Traceability maintained
5. **Tool results traceable** - Every result has a tool call
6. **Final answers declare risks** - No risk-free answers

## Files
```
packages/core-protocol/
├── schemas/          # 11 JSON Schema files
├── src/types/        # TypeScript interfaces
├── src/validation/   # Invariant checks
├── src/constants/    # Status enums, event types
└── tests/            # Validation test suite
```

## Success Criteria
- [ ] All 11 JSON schemas defined
- [ ] TypeScript types compile with strict mode
- [ ] Pydantic models pass validation
- [ ] All 6 invariants enforced
- [ ] 100% test coverage on validation
