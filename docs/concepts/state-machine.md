# State Machine

## Overview

The CCSR workflow is managed by a deterministic state machine that ensures valid transitions between phases.

## States

| State | Description |
|-------|-------------|
| `queued` | Run created, waiting to start |
| `framing` | ProblemFramer analyzing input |
| `society_planning` | Selecting agent configuration |
| `claim_proposal` | Architect proposing claims |
| `evidence_attachment` | EvidenceAgent gathering evidence |
| `criticism` | Critic challenging claims |
| `revision` | Architect revising claims |
| `judging` | Judge evaluating claims |
| `escalation` | Debate needs more rounds |
| `synthesis` | Synthesizer creating final answer |
| `completed` | Run finished successfully |
| `failed` | Run encountered an error |
| `cancelled` | Run was cancelled by user |

## Valid Transitions

```
queued      ──start──▶          framing
framing     ──problem_framed──▶  society_planning
society_planning ──society_selected──▶ claim_proposal
claim_proposal ──claims_proposed──▶ evidence_attachment
evidence_attachment ──evidence_attached──▶ criticism
criticism   ──criticism_complete──▶ revision
revision    ──revision_complete──▶ judging
judging     ──judge_accepted──▶  synthesis
judging     ──needs_more_debate──▶ escalation
escalation  ──escalation_resolved──▶ claim_proposal
synthesis   ──synthesis_complete──▶ completed

Any active state ──cancel──▶ cancelled
```

## Escalation Loop

When the judge determines more debate is needed:

1. State transitions to `escalation`
2. State transitions back to `claim_proposal`
3. The cycle repeats: proposal → evidence → criticism → revision → judging
4. The debate controller tracks rounds and stops at max_rounds

## Configuration

The state machine accepts a `max_rounds` parameter (default: 3) that limits how many times the escalation loop can repeat.
