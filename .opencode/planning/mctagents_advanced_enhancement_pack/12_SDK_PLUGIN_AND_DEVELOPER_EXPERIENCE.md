# SDK, Plugin, and Developer Experience Strategy

## 1. SDK-first philosophy

For open-source adoption, mCTAgents must be useful even without the full Studio UI. Developers should be able to integrate the reasoning engine into their own product with a few lines of code.

## 2. TypeScript SDK

```ts
const client = new MCTAgentsClient({
  baseUrl: "http://localhost:8080",
  apiKey: process.env.MCTAGENTS_API_KEY,
});

const run = await client.runs.create({
  problem: "Should we split our monolith into microservices?",
  mode: "deep_social_reasoning",
  requireEvidence: true,
});

for await (const event of client.runs.stream(run.id)) {
  console.log(event.type, event.payload);
}
```

## 3. Python SDK

```python
client = MCTAgentsClient(base_url="http://localhost:8080", api_key=os.getenv("MCTAGENTS_API_KEY"))

run = client.runs.create(
    problem="Design a private NotebookLM-like system.",
    mode="balanced_reasoning",
    require_evidence=True,
)

for event in client.runs.stream(run.id):
    print(event.type, event.payload)
```

## 4. Plugin types

```text
Agent plugin
Debate policy plugin
Evidence provider plugin
Tool provider plugin
Model provider plugin
Evaluation metric plugin
UI component plugin
Runtime adapter plugin
```

## 5. Agent plugin contract

```yaml
id: fintech_risk_agent
name: FinTech Risk Reviewer
version: 0.1.0
inputs:
  - problem_frame
  - claims
  - evidence
outputs:
  - objections
  - risk_claims
permissions:
  tools:
    - web_search
    - document_search
budget:
  max_tokens: 1500
  max_tool_calls: 3
```

## 6. Developer documentation

Required docs:

```text
Quickstart
Concepts
Architecture
Protocol Spec
SDK Reference
Agent Plugin Guide
Debate Policy Guide
MCP Tool Guide
Deployment Guide
Security Guide
Benchmark Guide
Contribution Guide
```

## 7. Open-source contributor path

Make it easy to contribute:

```text
Good first issue labels
example plugins
local dev script
seed demo data
test fixtures
schema validation
benchmark task templates
```
