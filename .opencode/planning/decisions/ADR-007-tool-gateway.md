# ADR-007: MCP Only Through Tool Gateway

## Status
Accepted

## Context
We need to support MCP (Model Context Protocol) for tool integration while maintaining security.

## Decision
All MCP tool calls go through a Tool Gateway with policy checks. No direct tool access from agents.

## Consequences
- Security boundary for tool execution
- Policy enforcement (permissions, rate limits)
- Audit trail for all tool calls
- Additional latency for tool calls
