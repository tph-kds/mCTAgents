# ADR-001: Protocol-First Architecture

## Status
Accepted

## Context
We need to ensure all services (Go API, Python engine, TypeScript frontend) can interoperate without tight coupling.

## Decision
Core protocol schemas (JSON Schema + TypeScript types + Pydantic models) are the source of truth. All services implement against these schemas.

## Consequences
- Services can evolve independently
- Cross-language validation is consistent
- New services can be added without modifying existing ones
- Schema changes require coordinated updates
