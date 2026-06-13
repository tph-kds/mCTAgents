# CCSR Protocol

## Overview

The Claim-Centered Social Reasoning (CCSR) protocol defines how agents communicate through structured objects. Every interaction produces typed, validated objects that can be stored, queried, and replayed.

## Protocol Objects

### ProblemFrame

Represents a normalized problem statement.

```json
{
  "id": "uuid",
  "run_id": "uuid",
  "original_input": "Should we adopt microservices?",
  "normalized_problem": "Evaluate whether migrating to microservices architecture is beneficial...",
  "constraints": ["budget < $50k", "6 month timeline"],
  "success_criteria": ["99.9% uptime", "10x scale"],
  "risk_level": "high",
  "domain": "architecture",
  "requires_business_decision": true,
  "requires_research": true,
  "requires_code": false
}
```

### Claim

A structured assertion with confidence and status.

```json
{
  "id": "uuid",
  "run_id": "uuid",
  "author_agent_id": "architect",
  "text": "Microservices will improve deployment frequency by 3x",
  "claim_type": "architecture_decision",
  "confidence": 0.75,
  "status": "proposed",
  "requires_evidence": true,
  "evidence_status": "unsupported",
  "scores": {
    "logic": 0.8,
    "evidence": 0.0,
    "feasibility": 0.7,
    "critic_resistance": 0.5,
    "risk_adjusted": 0.6,
    "final": 0.52
  }
}
```

### Claim Status Lifecycle

```
proposed → evidence_requested → supported → challenged → revision_required
    ↓                                              ↓
    └──────────────────────────────────────────────┘
                        ↓
              accepted / rejected / uncertain
```

### Evidence

Supporting or attacking information for claims.

```json
{
  "id": "uuid",
  "run_id": "uuid",
  "source_type": "uploaded_document",
  "source_ref": "netflix-tech-blog.pdf",
  "summary": "Netflix reported 100x deployment frequency after microservices adoption",
  "reliability_score": 0.85,
  "supports_claim_ids": ["claim-uuid-1"],
  "attacks_claim_ids": []
}
```

### Objection

A challenge to a claim's reasoning.

```json
{
  "id": "uuid",
  "run_id": "uuid",
  "target_claim_id": "claim-uuid-1",
  "author_agent_id": "critic",
  "reason": "The Netflix example may not apply to smaller organizations",
  "severity": "medium",
  "requested_fix": "Provide evidence from similar-scale companies"
}
```

### Revision

A revised version of a claim.

```json
{
  "id": "uuid",
  "run_id": "uuid",
  "old_claim_id": "claim-uuid-1",
  "new_claim_id": "claim-uuid-2",
  "reason": "Added evidence from mid-size companies",
  "revision_type": "objection_driven",
  "improvement_score": 0.2
}
```

### Decision

The judge's accept/reject decision.

```json
{
  "id": "uuid",
  "run_id": "uuid",
  "accepted_claim_ids": ["claim-uuid-2"],
  "rejected_claim_ids": ["claim-uuid-3"],
  "uncertain_claim_ids": [],
  "score_breakdown": {},
  "confidence": 0.82,
  "needs_more_debate": false,
  "extra_debate_reason": null
}
```

### FinalAnswer

The synthesized final answer.

```json
{
  "id": "uuid",
  "run_id": "uuid",
  "answer_text": "Based on the evidence, microservices adoption is recommended...",
  "accepted_claim_ids": ["claim-uuid-2"],
  "rejected_alternatives": [{"text": "Keep monolith", "reason": "Insufficient evidence"}],
  "risks": [
    {"description": "Increased operational complexity", "severity": "high", "mitigation": "Start with 2-3 services"}
  ],
  "next_steps": ["Conduct team readiness assessment", "Pilot with billing service"],
  "confidence": 0.82
}
```

## Required Invariants

1. **Final answers must reference accepted claims** - No orphaned references
2. **High-confidence claims need evidence** - Claims ≥0.7 confidence with `requires_evidence=true` must have `evidence_status=supported`
3. **Rejected claims need reasons** - Every rejected claim must have a `rejection_reason`
4. **Revisions link claims** - Every revision must have distinct `old_claim_id` and `new_claim_id`
5. **Unique claim IDs** - No duplicate claim identifiers in a run
6. **Final answers declare risks** - Every final answer must have at least one risk item
