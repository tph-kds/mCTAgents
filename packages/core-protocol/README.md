# Core Protocol

JSON schemas and TypeScript types defining the mCTAgents protocol.

## Overview

This package is the **source of truth** for all protocol objects used across the system. Every service and client validates against these schemas.

## Protocol Objects

| Object | Description |
|--------|-------------|
| `ProblemFrame` | Normalized problem description |
| `Claim` | Structured assertion with confidence |
| `Evidence` | Supporting/attacking information |
| `Objection` | Challenge to a claim |
| `Revision` | Revised version of a claim |
| `Decision` | Judge's acceptance/rejection |
| `FinalAnswer` | Synthesized answer |
| `Event` | Runtime event for streaming |
| `RunState` | Run lifecycle state |
| `DebatePolicy` | Debate configuration |

## Usage

```typescript
import { Claim, Evidence, EventType } from '@mctagents/core-protocol';

const claim: Claim = {
  id: 'c1',
  run_id: 'r1',
  author_agent_id: 'architect',
  text: 'We should adopt microservices',
  confidence: 0.8,
  status: 'proposed',
};
```

## Development

```bash
npm install
npm run build
npm test
```
