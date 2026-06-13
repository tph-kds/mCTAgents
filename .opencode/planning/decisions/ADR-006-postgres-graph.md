# ADR-006: Postgres-First Graph Storage

## Status
Accepted

## Context
We need to store claims, evidence, objections, and their relationships.

## Decision
Use PostgreSQL with JSONB for flexible fields and `argument_edges` table for relationships. Avoid premature graph database adoption.

## Consequences
- Proven, reliable storage
- JSONB provides schema flexibility
- SQL queries for complex reasoning
- Can migrate to graph DB later if needed
