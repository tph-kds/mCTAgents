# Adaptive Debate and Consensus Engine

## 1. Why adaptive debate

Fixed debate is expensive and can reduce quality when agents repeat each other or drift away from the problem. mCTAgents should use **adaptive debate**, where the system decides how much social reasoning is needed.

## 2. Debate stages

```text
Round 0: Problem framing
Round 1: Claim proposal
Round 2: Evidence attachment
Round 3: Criticism/refutation
Round 4: Revision
Round 5: Judge scoring
Optional escalation: extra agents or extra evidence
```

## 3. Debate policies

### Fast policy

```yaml
policy: fast_social_check
agents: [problem_framer, critic_agent, synthesizer]
max_rounds: 0
require_evidence: false
use_case: simple questions
```

### Balanced policy

```yaml
policy: balanced_reasoning
agents: [problem_framer, architect, evidence_agent, critic, judge]
max_rounds: 1
require_evidence: true_for_major_claims
use_case: medium-complexity implementation questions
```

### Deep policy

```yaml
policy: deep_social_reasoning
agents: [problem_framer, society_planner, architect, evidence_agent, critic, risk_agent, judge, synthesizer]
max_rounds: 2
require_evidence: true
judge_confidence_threshold: 0.85
use_case: architecture, research, high-impact decisions
```

### Courtroom policy

```yaml
policy: courtroom_verification
agents: [claimant, opponent, evidence_agent, cross_examiner, judge_panel, synthesizer]
max_rounds: 3
require_evidence: strict
use_case: claim verification, controversial questions, research review
```

## 4. Stop conditions

```text
Stop when:
- judge confidence >= threshold
- no high-severity objections remain
- claims are sufficiently supported
- additional debate has low marginal value
- latency or cost budget is exceeded
```

## 5. Escalation conditions

```text
Escalate when:
- judge confidence < threshold
- claims conflict
- source reliability is low
- critic finds high-severity objection
- answer would be high impact
- user requests deep analysis
```

## 6. Consensus scoring

Each accepted claim should receive:

```json
{
  "logic_score": 0.91,
  "evidence_score": 0.82,
  "critic_resistance_score": 0.87,
  "feasibility_score": 0.9,
  "risk_adjusted_score": 0.84,
  "final_score": 0.87
}
```

## 7. Drift prevention

The judge or supervisor should check every round:

```text
- Are agents still addressing the original problem?
- Are they repeating previous arguments?
- Are they inventing unrelated constraints?
- Is there real improvement in claims?
```

If drift appears, return to the problem frame and prune irrelevant claims.
