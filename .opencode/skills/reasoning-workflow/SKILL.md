# Reasoning Workflow Skill

## Purpose

Implement the CCSR (Claim-Centered Social Reasoning) workflow.

## When to Use

- Building the reasoning engine
- Adding new agent roles
- Modifying the debate flow
- Implementing consensus mechanisms

## Workflow Steps

1. **Problem Framing** - Parse user input into ProblemFrame
2. **Claim Generation** - Architect proposes initial claims
3. **Evidence Attachment** - Evidence agent finds supporting/contradicting info
4. **Objection Creation** - Critic challenges weak claims
5. **Claim Revision** - Architect improves claims based on feedback
6. **Decision Making** - Judge scores and accepts/rejects claims
7. **Synthesis** - Final answer references accepted claims

## Agent Roles

| Role | Responsibility |
|------|----------------|
| Architect | Proposes and revises claims |
| Evidence | Attaches sources to claims |
| Critic | Creates objections |
| Judge | Scores and decides |
| Synthesizer | Creates final answer |

## State Machine

```
proposed -> evidence_requested -> supported -> challenged
    -> revision_required -> revised -> accepted | rejected | uncertain
```

## Event Types

```python
EVENTS = [
    "run_started",
    "problem_framed",
    "claim_created",
    "evidence_attached",
    "objection_created",
    "claim_revised",
    "judge_scored",
    "final_answer_created",
    "run_completed",
]
```

## Implementation Pattern

```python
class ReasoningEngine:
    async def run(self, problem: str) -> FinalAnswer:
        frame = await self.frame_problem(problem)
        claims = await self.architect.propose(frame)
        
        for claim in claims:
            evidence = await self.evidence.find(claim)
            objections = await self.critic.challenge(claim, evidence)
            claim = await self.architect.revise(claim, objections)
        
        decision = await self.judge.decide(claims)
        return await self.synthesizer.create(decision)
```
