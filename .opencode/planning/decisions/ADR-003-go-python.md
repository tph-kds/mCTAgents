# ADR-003: Go API Gateway + Python Runtime

## Status
Accepted

## Context
We need high-performance HTTP handling and best-in-class AI/ML ecosystem.

## Decision
- Go for API gateway (chi router, SSE, concurrency)
- Python for reasoning engine (Pydantic, async, AI libraries)

## Consequences
- Go provides excellent performance for HTTP routing
- Python provides best AI/ML ecosystem
- Two language runtimes to maintain
- Clear service boundaries
