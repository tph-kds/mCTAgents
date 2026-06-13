# Sprint 03: Reasoning Engine

**Duration:** Days 8-20 | **Goal:** 6 agents, state machine, debate controller, consensus engine

## Tasks

### Day 8-10: Agent Base + Framer + Architect
- [ ] Create `AgentContext` and `AgentResult` models
- [ ] Create `BaseAgent` abstract class
- [ ] Implement `ProblemFramer` agent
- [ ] Write framer system prompt
- [ ] Implement `ArchitectAgent.propose_claims()`
- [ ] Write architect system prompt
- [ ] Unit tests for framer and architect

### Day 11-13: Evidence + Critic
- [ ] Implement `EvidenceAgent` with search integration
- [ ] Implement evidence finding with model evaluation
- [ ] Implement reliability scoring
- [ ] Write evidence system prompt
- [ ] Implement `CriticAgent.challenge_claims()`
- [ ] Implement contradiction detection
- [ ] Write critic system prompt
- [ ] Unit tests for evidence and critic

### Day 14-16: Judge + Synthesizer
- [ ] Implement `JudgeAgent.score_claims()`
- [ ] Implement accept/reject/uncertain logic
- [ ] Implement score breakdown (logic, evidence, feasibility, etc.)
- [ ] Write judge system prompt
- [ ] Implement `SynthesizerAgent.create_final_answer()`
- [ ] Implement risk declaration
- [ ] Write synthesizer system prompt
- [ ] Unit tests for judge and synthesizer

### Day 17-18: State Machine + Debate Controller
- [ ] Implement `StateMachine` with 13 phases
- [ ] Implement valid transition map
- [ ] Implement error transitions
- [ ] Implement `DebateController.should_continue()`
- [ ] Implement drift detection
- [ ] Implement marginal value check
- [ ] Unit tests for state machine and debate

### Day 19-20: Reasoning Engine Orchestrator
- [ ] Implement `ReasoningEngine.run()` orchestrator
- [ ] Integrate all 6 agents
- [ ] Integrate state machine and debate controller
- [ ] Integrate event emission at every transition
- [ ] Integrate storage service for persistence
- [ ] Run end-to-end integration test
- [ ] Verify all invariants are enforced

## Definition of Done
- [ ] All 6 agents implemented and tested
- [ ] State machine handles all valid transitions
- [ ] Debate controller stops at correct conditions
- [ ] Events emitted at every state transition
- [ ] All claims, evidence, objections stored in PostgreSQL
- [ ] Unit test coverage >80%

## Risks
- **Model quality varies:** Use strong models for judge/synthesizer
- **Debate loops:** Implement max rounds and marginal value check
- **Prompt engineering:** Iterate on prompts based on test results

## Retro Notes
- _To be filled after sprint completion_
