# STEP 3: Reasoning Engine

**Timeline:** Days 8-20 | **Complexity:** 5/5 | **Dependencies:** STEPs 0, 1, 2

## Goal

The core of mCTAgents. Implement the CCSR workflow, agent society, debate mechanism, and consensus engine.

## Agent Society

| Agent | Role | Capabilities |
|-------|------|-------------|
| ProblemFramer | Analyze input → ProblemFrame | normalize, detect domain, set risk |
| Architect | Propose + revise claims | propose_claims, revise_claims, compare |
| EvidenceAgent | Find + attach evidence | retrieve, score reliability, label |
| Critic | Challenge weak claims | detect contradictions, identify gaps |
| Judge | Score + accept/reject | score_claims, determine_consensus |
| Synthesizer | Create final answer | summarize, structure, declare risks |

## State Machine (13 Phases)

```
queued → framing → society_planning → claim_proposal
→ evidence_attachment → criticism → revision → judging
→ [escalation → claim_proposal] (loop)
→ synthesis → completed
```

## Debate Controller

Decides when to continue debating:
- Max rounds reached? → Stop
- Judge confidence high enough? → Stop
- No new value from debate? → Stop
- Low marginal improvement? → Stop

## Workflow

1. **Problem Framing** - Framer creates ProblemFrame
2. **Claim Proposal** - Architect proposes 3-5 claims
3. **Evidence Attachment** - Evidence agent finds supporting info
4. **Criticism** - Critic challenges weak claims
5. **Revision** - Architect revises challenged claims
6. **Judging** - Judge scores and accepts/rejects
7. **(Loop)** - If more debate needed, repeat from step 3
8. **Synthesis** - Synthesizer creates final answer

## Files
```
services/reasoning-engine/
├── src/mctagents/
│   ├── agents/          # 6 agent implementations
│   ├── engine/          # State machine, debate, consensus
│   ├── services/        # Event, storage, model, evidence
│   ├── core/protocol/   # Pydantic models
│   └── api/             # FastAPI routes
├── prompts/             # Agent system prompts
└── tests/               # Unit + integration tests
```

## Success Criteria
- [ ] All 6 agents implemented
- [ ] State machine handles all transitions
- [ ] Debate controller stops correctly
- [ ] Events emitted at every transition
- [ ] All data stored in PostgreSQL
- [ ] Unit test coverage >80%
