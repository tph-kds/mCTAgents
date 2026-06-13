# Runtime Adapter Strategy

## 1. Why adapter strategy

mCTAgents should not force all users into one agent framework. The social reasoning protocol should be stable; runtimes should be replaceable.

## 2. Core interface

```ts
interface RuntimeAdapter {
  run(input: SocialReasoningRunRequest): AsyncIterable<ReasoningEvent>;
  validatePolicy(policy: DebatePolicy): ValidationResult;
  listCapabilities(): RuntimeCapabilities;
}
```

## 3. First runtime: custom Python + LangGraph

Use LangGraph for the first production-like runtime because it maps naturally to stateful graph execution.

```text
ProblemFramerNode
  -> SocietyPlannerNode
  -> ClaimProposalNode
  -> EvidenceNode
  -> CriticNode
  -> RevisionNode
  -> JudgeNode
  -> SynthesizerNode
```

## 4. Pydantic AI runtime

Use for type-safe agent outputs, validators, dependency injection, testing, and evals. This is especially useful for protocol schemas and JSON reliability.

## 5. OpenAI Agents runtime

Use for teams that want hosted model features, handoffs, guardrails, tool approvals, and structured outputs.

## 6. Mastra runtime

Use for TypeScript teams and product apps that want a native Node/Next.js integration path.

## 7. Custom Go runtime

Long-term option. Build after the protocol stabilizes.

Best use cases:

```text
- low-latency simple workflows
- embedded enterprise deployments
- strict typed service boundaries
- high-throughput event processing
```

## 8. Runtime capability matrix

| Capability | LangGraph | Pydantic AI | OpenAI Agents | Mastra | Custom Go |
|---|---:|---:|---:|---:|---:|
| Graph workflow | Strong | Medium | Medium | Medium | Custom |
| Type safety | Medium | Strong | Medium | Strong TS | Strong |
| Handoffs | Strong | Custom | Strong | Medium | Custom |
| Durable workflow | External | Temporal support path | External | External | External |
| Local-first | Strong | Strong | Medium | Strong | Strong |
| MVP speed | Strong | Strong | Medium | Medium | Low |

## 9. Rule

Do not expose runtime-specific concepts to end users. Users should configure mCTAgents policies, not LangGraph internals.
