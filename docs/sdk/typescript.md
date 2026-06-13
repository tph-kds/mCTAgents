# TypeScript SDK

## Installation

```bash
npm install @mctagents/ts-sdk
```

## Quick Start

```typescript
import { MCTAgentsClient } from '@mctagents/ts-sdk';

const client = new MCTAgentsClient({
  baseUrl: 'http://localhost:8080',
  apiKey: 'optional-api-key',
});

// Create a reasoning run
const run = await client.runs.create({
  problem: 'Should we adopt microservices?',
  mode: 'balanced_reasoning',
});

console.log(`Run created: ${run.run_id}`);

// Stream events
for await (const event of client.runs.stream(run.run_id)) {
  console.log(`[${event.type}] ${event.agent_id || 'system'}`);

  if (event.type === 'run_completed') {
    break;
  }
}

// Get final claims
const runDetail = await client.runs.get(run.run_id);
console.log('Status:', runDetail.status);
```

## Configuration

```typescript
const client = new MCTAgentsClient({
  baseUrl: 'http://localhost:8080',  // Required
  apiKey: 'your-api-key',            // Optional
});
```

## API Methods

### `client.runs.create(params)`

Create a new reasoning run.

**Parameters:**
- `problem` (string, required): The problem statement
- `mode` (string, optional): Reasoning mode (`balanced_reasoning`, `fast_consensus`, `deep_deliberation`)
- `evidence_policy` (string, optional): Evidence requirements
- `budget` (object, optional): Resource limits

### `client.runs.get(runId)`

Get run details and status.

### `client.runs.stream(runId)`

Async generator that yields SSE events.

### `client.runs.cancel(runId)`

Cancel a running session.

## Error Handling

```typescript
try {
  const run = await client.runs.create({ problem: '...' });
} catch (error) {
  console.error('Failed to create run:', error.message);
}
```
