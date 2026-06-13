# ADR-005: SSE First, WebSocket Later

## Status
Accepted

## Context
We need real-time event streaming from reasoning engine to UI.

## Decision
Use Server-Sent Events (SSE) for MVP. Consider WebSocket for bidirectional communication later.

## Consequences
- Simpler implementation than WebSocket
- Works through HTTP proxies
- One-directional (server → client) is sufficient for MVP
- Can upgrade to WebSocket later if needed
