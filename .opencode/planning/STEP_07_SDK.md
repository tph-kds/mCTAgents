# STEP 7: SDK Packages

**Timeline:** Days 20-28 | **Complexity:** 3/5 | **Dependencies:** STEPs 1, 4

## Goal

Let developers integrate mCTAgents into their products without adopting the full Studio UI.

## TypeScript SDK

```typescript
const client = new MCTAgentsClient({ baseUrl: "http://localhost:8080" });
const run = await client.runs.create({ problem: "..." });
for await (const event of client.runs.stream(run.run_id)) {
  console.log(event.type, event.payload);
}
```

## Python SDK

```python
client = MCTAgentsClient(base_url="http://localhost:8080")
run = client.create_run(problem="...")
for event in client.stream_events(run.run_id):
    print(event.type, event.payload)
```

## Features
- Create, get, cancel runs
- Stream events via SSE (async generator in TS, generator in Python)
- Type-safe with full IntelliSense support
- Automatic reconnection on stream disconnect

## Plugin Contract
```typescript
interface MCTPlugin {
  name: string;
  version: string;
  onEvent?: (event: ReasoningEvent) => void;
  onClaim?: (claim: Claim) => void;
  tools?: ToolDefinition[];
}
```

## Files
```
packages/ts-sdk/       # TypeScript SDK
packages/py-sdk/       # Python SDK
```

## Success Criteria
- [ ] TypeScript SDK compiles
- [ ] Python SDK passes type checking
- [ ] Both SDKs can create runs and stream events
- [ ] Plugin contract defined
