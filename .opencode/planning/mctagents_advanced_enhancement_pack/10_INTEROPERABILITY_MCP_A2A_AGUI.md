# Interoperability with MCP, A2A, and AG-UI

## 1. Purpose

mCTAgents should become easy to integrate into any AI-native product. Interoperability protocols help adoption.

## 2. MCP strategy

MCP is the best fit for tool and data integration.

Architecture:

```text
Reasoning Engine
  -> Tool Gateway
  -> MCP Client
  -> MCP Server
  -> GitHub / Files / DB / Search / Internal APIs
```

mCTAgents must add security around MCP:

```text
- allowlist tools
- classify risk level
- require approval for dangerous operations
- log every tool call
- sanitize retrieved context
- prevent prompt injection from tool output
```

## 3. A2A strategy

A2A is for agent-to-agent interoperability. Add later after MVP.

Use cases:

```text
- ask an external coding agent to inspect a repo
- ask an external research agent to gather sources
- invite another organization's agent into a debate
- delegate specialized tasks to remote agents
```

mCTAgents should expose an Agent Card:

```json
{
  "name": "mCTAgents Social Reasoning Engine",
  "capabilities": ["claim_debate", "evidence_verification", "decision_synthesis"],
  "input_modes": ["text", "documents", "claim_graph"],
  "output_modes": ["final_answer", "claim_graph", "debate_timeline"]
}
```

## 4. AG-UI strategy

AG-UI inspires frontend event design.

mCTAgents event stream:

```text
run_started
agent_selected
problem_framed
claim_created
evidence_requested
evidence_attached
objection_created
claim_revised
judge_scored
final_answer_created
run_completed
```

## 5. Unified event schema

```json
{
  "event_id": "evt_001",
  "run_id": "run_001",
  "type": "claim_created",
  "agent_id": "architect_agent",
  "payload": {
    "claim_id": "claim_001",
    "text": "Use protocol-first architecture."
  },
  "timestamp": "2026-06-13T00:00:00Z"
}
```

## 6. Integration maturity path

```text
v0.1 REST + SSE
v0.2 TypeScript SDK + Python SDK
v0.3 MCP client adapter
v0.4 embeddable UI components
v0.5 A2A compatibility
v0.6 external agent society federation
```
