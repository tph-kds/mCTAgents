# ADR-004: Ollama/Local-First Model Gateway

## Status
Accepted

## Context
We want zero barrier to entry and no API costs for development.

## Decision
Ollama is the default model provider. Cloud providers (OpenAI, OpenRouter) are fallback options.

## Consequences
- No API keys needed for development
- Complete privacy for local inference
- Lower quality than frontier models
- GPU requirements for good performance
