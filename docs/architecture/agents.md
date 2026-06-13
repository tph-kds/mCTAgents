# Agent Society Design

## Overview

mCTAgents uses a society of 6 specialized agents, each with a distinct role in the reasoning process. This mimics how human expert panels work: different perspectives lead to more robust conclusions.

## Agent Roles

### ProblemFramer

**Role**: Problem Analyst  
**Input**: Raw problem statement  
**Output**: Normalized `ProblemFrame`

Responsibilities:
- Parse and normalize the input problem
- Identify domain, constraints, and success criteria
- Assess risk level (low/medium/high/critical)
- Determine if business decisions, research, or code are needed

### Architect

**Role**: Claim Proposer  
**Input**: `ProblemFrame` + context  
**Output**: Structured `Claim` objects

Responsibilities:
- Propose clear, testable claims
- Assign confidence scores (0.0-1.0)
- Mark claims that require evidence
- Revise claims when objections are raised

### EvidenceAgent

**Role**: Researcher  
**Input**: Claims requiring evidence  
**Output**: `Evidence` objects linked to claims

Responsibilities:
- Search document store for supporting evidence
- Score evidence reliability (0.0-1.0)
- Identify evidence that supports or attacks claims
- Request additional evidence when confidence is low

### Critic

**Role**: Adversarial Reviewer  
**Input**: Claims + Evidence  
**Output**: `Objection` objects

Responsibilities:
- Challenge weak reasoning
- Identify logical fallacies
- Point out missing evidence
- Request specific improvements

### Judge

**Role**: Arbiter  
**Input**: All claims, evidence, objections  
**Output**: `Decision` (accept/reject/uncertain)

Responsibilities:
- Evaluate claim strength
- Weigh evidence quality
- Consider objections
- Make final accept/reject decisions
- Trigger more debate if confidence is low

### Synthesizer

**Role**: Answer Compiler  
**Input**: Accepted claims + rejected alternatives  
**Output**: `FinalAnswer`

Responsibilities:
- Combine accepted claims into coherent answer
- Document rejected alternatives
- List remaining risks
- Suggest next steps

## Workflow Phases

```
QUEUED → FRAMING → SOCIETY_PLANNING → CLAIM_PROPOSAL → EVIDENCE_ATTACHMENT
    → CRITICISM → REVISION → JUDGING → [ESCALATION or SYNTHESIS] → COMPLETED
```

Each phase is managed by the state machine and can loop back for additional debate rounds.

## Debate Controller

The debate controller decides whether to continue or stop based on:

1. **Max rounds** - Hard limit on debate iterations
2. **Confidence threshold** - Stop when claims are confident enough
3. **Marginal value** - Stop when new rounds add little value
4. **Objection activity** - Continue if objections are still being raised
