# Master Enhancement Direction for mCTAgents

## Source grounding

This pack is aligned with the user's original mCTAgents purpose: multi-critical-thinking agents that interact, debate, suggest, refute, negotiate, and produce clearer solutions across many contexts; the user also emphasized Go backend, frontend visualization, local/Ollama-first model deployment, low GPU constraints, and open-source integration.

Ecosystem references used for architectural grounding:
- LangGraph: open-source low-level orchestration for long-running, stateful agents.
- Model Context Protocol (MCP): open protocol for connecting LLM apps to external tools and data.
- Agent2Agent (A2A): open protocol for agent interoperability.
- AG-UI: event-based protocol for connecting agents to user-facing applications.
- OpenAI Agents SDK: agents with tools, handoffs, guardrails, structured outputs.
- Pydantic AI: type-safe agent framework and structured outputs/evals direction.
- Mastra: TypeScript AI application framework with agents, workflows, memory, observability.
- Temporal: durable execution for resilient long-running workflows.
- OpenTelemetry: vendor-neutral traces, metrics, logs collection.
- Langfuse/Phoenix-style LLM observability: trace, prompt, evaluate, debug LLM applications.
- OpenHands Software Agent SDK: sandboxed execution, lifecycle control, REST/WebSocket services, local-to-remote execution portability.


## 1. Final product thesis

mCTAgents should become an **open-source social reasoning infrastructure** rather than a normal multi-agent chatbot. The central value proposition is:

> Build AI-native products where a society of agents can propose claims, attach evidence, challenge assumptions, revise weak reasoning, and converge into a final answer that is transparent, auditable, and benchmarkable.

The strongest direction is not to compete directly with LangGraph, MCP, OpenAI Agents SDK, Mastra, Pydantic AI, OpenHands, or Temporal. Instead, mCTAgents should sit above them as a **reasoning layer**:

```text
User/Product
  -> mCTAgents SDK
  -> Social Reasoning Protocol
  -> Reasoning Engine
  -> Runtime adapters
  -> Tool/model/evidence infrastructure
```

## 2. Core differentiation

Most frameworks answer:

```text
How do I build an agent?
How do I let it call tools?
How do I orchestrate steps?
```

mCTAgents should answer:

```text
How do many agents improve thinking quality?
How do agents disagree productively?
How do we verify claims with evidence?
How do we show users why the final answer was selected?
How do we benchmark whether multi-agent reasoning is better than a single model?
```

## 3. Non-negotiable pillars

1. **Protocol-first**: define Claim, Evidence, Objection, Revision, Vote, Decision, DebatePolicy, RunState.
2. **Runtime-agnostic**: support LangGraph first, then OpenAI Agents SDK, Pydantic AI, Mastra, custom Go/Python runtimes.
3. **Evidence-grounded**: every high-confidence claim needs evidence or an explicit uncertainty label.
4. **Adaptive debate**: avoid always using many agents; escalate only when uncertainty, conflict, or risk requires it.
5. **Observable-by-default**: every model call, tool call, claim mutation, and judge decision is traceable.
6. **SDK-first**: developers should integrate mCTAgents into any product without adopting your full UI.
7. **Local-first**: Ollama, local vector DB, local Postgres, Docker Compose, low-GPU path.
8. **Production-ready evolution**: durable workflows, outbox/inbox, retries, idempotency, audit logs.
9. **Open-source-friendly**: docs, examples, contribution guide, plugin interfaces, benchmark suite.
10. **Benchmark-proven**: show single-agent baseline vs mCTAgents in measurable tasks.

## 4. Recommended architecture summary

```text
AI-native product / Studio UI
        ↓
TypeScript/Python SDK + REST/SSE API
        ↓
Go API Gateway
        ↓
Social Reasoning Engine Core
        ↓
Runtime Adapters: LangGraph / OpenAI Agents / Pydantic AI / Mastra / Custom
        ↓
Evidence Layer + Tool Layer + Memory Layer
        ↓
Model Gateway: Ollama / vLLM / OpenAI-compatible / LM Studio / OpenRouter
        ↓
Observability + Evaluation + Durable Workflow layer
```

## 5. MVP vs phenomenal open-source project

MVP proves the vertical slice:

```text
Problem -> Claim proposals -> Evidence -> Objections -> Revisions -> Judge -> Final answer -> UI replay
```

A phenomenal open-source project proves the ecosystem:

```text
Protocol + SDK + adapters + benchmark + plugin marketplace + visual studio + reliable deployment
```

## 6. Strategic decision

Build only one thing first: **a working claim-centered social reasoning run**. Everything else exists to support that.

If the first demo can show agents improving a weak answer through evidence-backed objection and revision, the project has a strong identity.
