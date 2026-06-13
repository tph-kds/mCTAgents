# ADR-002: Claim-Centered State

## Status
Accepted

## Context
Traditional agent systems store message logs. We need inspectable, replayable reasoning.

## Decision
All reasoning state is stored as structured objects (Claims, Evidence, Objections, Revisions) rather than message strings. The argument graph is the primary data structure.

## Consequences
- Reasoning is transparent and auditable
- Claims can be scored, compared, and tracked
- UI shows structured claims, not chat bubbles
- More complex data model than message logs
