# Open-Source Ecosystem Synchronization

## 1. Why ecosystem synchronization matters

mCTAgents should not reinvent every primitive. The strongest open-source products usually win by composing existing ecosystems while owning a unique abstraction. For mCTAgents, the unique abstraction is not model calling, RAG, or workflow scheduling. It is **social reasoning state**.

## 2. Ecosystem layers

| Layer | Representative ecosystem | mCTAgents position |
|---|---|---|
| Agent orchestration | LangGraph, OpenAI Agents SDK, Pydantic AI, Mastra | Runtime adapters |
| Tool integration | MCP, native function calling, API gateways | Tool/evidence connectors |
| Agent interoperability | A2A, ACP-style ideas | Future external agent bridge |
| Frontend event protocol | AG-UI-style event streams | Studio event schema inspiration |
| Reliable workflows | Temporal, Dapr workflows, queues | Deep-run durability layer |
| Observability | OpenTelemetry, Langfuse, Phoenix | Default tracing/eval stack |
| Sandbox execution | OpenHands-style workspace/server pattern | Safe tool/code execution layer |
| RAG/knowledge | LlamaIndex, Qdrant, pgvector, GraphRAG | Evidence retrieval + claim provenance |

## 3. What to adopt

### LangGraph
Use for the first Python runtime adapter because it already handles graph-shaped, stateful workflows. mCTAgents should define the protocol; LangGraph should execute one implementation.

### OpenAI Agents SDK
Use as a future adapter for users who already rely on instructions, tools, handoffs, guardrails, and structured outputs.

### Pydantic AI
Use for typed structured outputs, validators, dependency injection, testing, and eval-friendly Python agent implementation.

### Mastra
Use as inspiration and possibly adapter for TypeScript-heavy AI-native teams.

### MCP
Use for external tools and context. Do not expose MCP servers directly to agents without mCTAgents policy checks.

### A2A
Use later when mCTAgents needs to communicate with external agents from other organizations or frameworks.

### AG-UI
Use its event-based idea to design the Studio stream: claim_created, evidence_attached, objection_created, decision_made.

### Temporal
Use after MVP for long-running, retryable social reasoning workflows.

### OpenTelemetry + Langfuse/Phoenix
Use from the beginning to make the system debuggable.

## 4. What not to do

Avoid making mCTAgents:

```text
- only a LangGraph wrapper
- only a CrewAI-style role YAML runner
- only a chatbot UI
- only an MCP client
- only a prompt library
- only a workflow engine
```

The project must own the claim/evidence/debate/revision/decision graph.

## 5. Adapter-first policy

Every external framework should connect through one of these adapter interfaces:

```text
RuntimeAdapter
ModelProviderAdapter
ToolProviderAdapter
EvidenceProviderAdapter
MemoryProviderAdapter
TraceProviderAdapter
EvaluationProviderAdapter
UIEventAdapter
```

This lets users integrate mCTAgents without abandoning their preferred stack.
