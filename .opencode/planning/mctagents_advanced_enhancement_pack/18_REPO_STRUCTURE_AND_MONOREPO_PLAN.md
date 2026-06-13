# Repository Structure and Monorepo Plan

## 1. Recommended monorepo

```text
mctagents/
├── apps/
│   ├── studio/                 # Next.js UI
│   └── playground/             # simple integration demo
├── services/
│   ├── api-gateway/            # Go
│   ├── reasoning-engine/       # Python
│   ├── model-gateway/          # Go or Python
│   ├── evidence-service/       # Python
│   ├── tool-gateway/           # Go
│   ├── evaluation-service/     # Python
│   └── trace-service/          # optional wrapper
├── packages/
│   ├── core-protocol/          # schemas/types
│   ├── ts-sdk/
│   ├── py-sdk/
│   ├── ui-components/
│   ├── agent-registry/
│   ├── policy-registry/
│   └── prompt-registry/
├── runtimes/
│   ├── langgraph-adapter/
│   ├── pydantic-ai-adapter/
│   ├── openai-agents-adapter/
│   ├── mastra-adapter/
│   └── custom-runtime/
├── examples/
│   ├── notebooklm-style/
│   ├── software-architecture-review/
│   ├── research-debate/
│   ├── security-review/
│   └── product-decision/
├── benchmarks/
├── docs/
├── deployments/
│   ├── docker-compose/
│   ├── k8s/
│   └── helm/
└── scripts/
```

## 2. Package ownership

```text
core-protocol: stable contracts
reasoning-engine: implementation
runtime adapters: optional compatibility
sdk: integration
studio: visualization
benchmarks: trust and quality proof
```

## 3. Development commands

```bash
make dev
make test
make lint
make benchmark-smoke
make docker-up
make docker-down
make seed-demo
```

## 4. Versioning

```text
Protocol version: semver, strict compatibility
Service version: independent
SDK version: tied to public API
Plugin version: independent with compatibility metadata
```

## 5. CI pipeline

```text
schema validation
unit tests
integration tests
frontend build
docker compose smoke test
benchmark subset
security scan
license check
```
