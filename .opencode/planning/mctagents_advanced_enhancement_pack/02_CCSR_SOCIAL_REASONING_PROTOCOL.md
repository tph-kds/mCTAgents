# CCSR: Claim-Centered Social Reasoning Protocol

## 1. Protocol purpose

CCSR means **Claim-Centered Social Reasoning**. It is the central methodology of mCTAgents.

Instead of storing only agent messages, the system stores reasoning objects:

```text
ProblemFrame -> Claim -> Evidence -> Objection -> Revision -> Vote -> Decision -> FinalAnswer
```

This makes the reasoning process inspectable, replayable, and evaluable.

## 2. Core entities

### ProblemFrame
Defines what the agents are solving.

```json
{
  "id": "pf_001",
  "run_id": "run_001",
  "original_input": "How should I build mCTAgents?",
  "normalized_problem": "Design an open-source social reasoning engine for AI-native products.",
  "constraints": ["open-source", "local-first", "evidence-backed", "SDK-first"],
  "success_criteria": ["useful answers", "transparent reasoning", "easy integration"],
  "risk_level": "medium"
}
```

### Claim
A proposition that can be supported, attacked, revised, accepted, or rejected.

```json
{
  "id": "claim_001",
  "run_id": "run_001",
  "author_agent_id": "architect_agent",
  "text": "mCTAgents should be protocol-first and framework-agnostic.",
  "claim_type": "architecture_decision",
  "confidence": 0.88,
  "status": "proposed",
  "requires_evidence": true
}
```

### Evidence
A source-backed support or attack item.

```json
{
  "id": "ev_001",
  "run_id": "run_001",
  "source_type": "official_docs",
  "source_ref": "MCP GitHub",
  "summary": "MCP standardizes integration between LLM apps and tools/data.",
  "supports_claim_ids": ["claim_001"],
  "reliability_score": 0.86
}
```

### Objection
A challenge against a claim.

```json
{
  "id": "obj_001",
  "target_claim_id": "claim_001",
  "author_agent_id": "critic_agent",
  "reason": "Protocol-first design may slow MVP delivery.",
  "severity": "medium",
  "requested_fix": "Define a minimal protocol subset for v0.1."
}
```

### Revision
A claim improvement caused by objections or new evidence.

```json
{
  "id": "rev_001",
  "old_claim_id": "claim_001",
  "new_claim_id": "claim_002",
  "reason": "Reduced scope to minimal protocol for MVP while preserving architecture direction."
}
```

### Decision
Judge output selecting accepted/rejected claims.

```json
{
  "id": "decision_001",
  "accepted_claim_ids": ["claim_002"],
  "rejected_claim_ids": ["claim_003"],
  "score_breakdown": {
    "logic": 0.91,
    "evidence": 0.84,
    "feasibility": 0.89,
    "open_source_value": 0.93
  },
  "confidence": 0.89
}
```

## 3. Protocol state machine

```text
proposed
  -> evidence_requested
  -> supported
  -> challenged
  -> revision_required
  -> revised
  -> accepted | rejected | uncertain
```

## 4. Required invariants

1. A final answer must reference accepted claims.
2. High-confidence claims need evidence or explicit uncertainty.
3. Every rejected claim needs a rejection reason.
4. Every revision must link old claim and new claim.
5. Every tool result must be traceable to a tool call.
6. Every final answer must declare remaining risks.

## 5. Why this protocol matters

A message-only agent system produces conversation logs. A claim-centered system produces an argument graph. That is the core quality upgrade.
