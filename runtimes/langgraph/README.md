# mCTAgents Runtime for LangGraph

## Installation

```bash
npm install @mctagents/runtime-langgraph
```

## Usage

### mCTAgents as a LangGraph Node

```typescript
import { StateGraph } from "@langchain/langgraph";
import { createMCTAgentsNode } from "@mctagents/runtime-langgraph";

const mctNode = createMCTAgentsNode({
  apiUrl: "http://localhost:8080",
});

const graph = new StateGraph({
  // ... your state schema
})
  .addNode("reason", mctNode)
  .addEdge("__start__", "reason")
  .addEdge("reason", "__end__");

const result = await graph.invoke({
  problem: "Should we adopt microservices?",
});

console.log(result.mctagents_claims);
```

### Configuration

```typescript
const mctNode = createMCTAgentsNode({
  apiUrl: "http://localhost:8080",
  apiKey: "optional-api-key",
  mode: "deep_deliberation",
});
```

## How It Works

1. The node receives a `problem` field from the LangGraph state
2. Creates an mCTAgents run via the API
3. Streams all events until completion
4. Returns the run ID, events, claims, and status back to the graph state
