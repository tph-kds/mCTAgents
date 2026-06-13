# TypeScript SDK

Client library for the mCTAgents API.

## Installation

```bash
npm install @mctagents/ts-sdk
```

## Usage

```typescript
import { MCTAgentsClient } from '@mctagents/ts-sdk';

const client = new MCTAgentsClient({ baseUrl: 'http://localhost:8080' });

// Create a run
const run = await client.runs.create({
  problem: 'Should we adopt microservices?',
});

// Stream events
for await (const event of client.runs.stream(run.run_id)) {
  console.log(`[${event.type}]`, event.payload);
  if (event.type === 'run_completed') break;
}

// Get claims
const claims = await client.runs.getClaims(run.run_id);
```

## Development

```bash
npm install
npm run build
```
