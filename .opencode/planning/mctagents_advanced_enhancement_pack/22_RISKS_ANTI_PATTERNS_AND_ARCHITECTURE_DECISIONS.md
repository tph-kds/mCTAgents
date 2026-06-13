# Risks, Anti-Patterns, and Architecture Decisions

## 1. Major risks

```text
Too many agents causing latency without better quality
Debate drift away from the original problem
Weak evidence causing hallucinated authority
Framework lock-in
Over-engineered microservices too early
Complex UI before core reasoning works
Uncontrolled tool execution
No benchmark proof
```

## 2. Anti-patterns

### Anti-pattern: Agent chatroom

Agents talk, but no structured claims, evidence, or decisions exist.

Fix:

```text
Use claim-centered state.
```

### Anti-pattern: Always deep mode

Every question triggers many agents.

Fix:

```text
Use adaptive debate and early stopping.
```

### Anti-pattern: Framework identity

Project becomes “LangGraph app.”

Fix:

```text
Own protocol; implement LangGraph as adapter.
```

### Anti-pattern: RAG as prompt stuffing

Retrieved chunks are dumped into prompts without provenance.

Fix:

```text
Use evidence objects with support/attack links.
```

### Anti-pattern: Hidden quality

No one knows whether multi-agent reasoning helped.

Fix:

```text
Benchmark single-agent vs social-agent.
```

## 3. Architecture decisions

```text
ADR-001: protocol-first architecture
ADR-002: claim-centered state instead of message-only logs
ADR-003: Go API Gateway + Python first runtime
ADR-004: Ollama/local-first model gateway
ADR-005: SSE first, WebSocket later
ADR-006: Postgres-first graph storage, graph DB later only if needed
ADR-007: MCP only through Tool Gateway
ADR-008: benchmark suite required before v1.0
```
