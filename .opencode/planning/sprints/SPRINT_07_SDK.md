# Sprint 07: SDK Packages

**Duration:** Days 20-28 | **Goal:** TypeScript SDK, Python SDK, plugin contract

## Tasks

### Day 20-22: TypeScript SDK
- [ ] Initialize `packages/ts-sdk` with package.json
- [ ] Implement `MCTAgentsClient` class
- [ ] Implement `client.runs.create()` method
- [ ] Implement `client.runs.get()` method
- [ ] Implement `client.runs.stream()` with AsyncGenerator
- [ ] Implement `client.runs.cancel()` method
- [ ] Add authentication headers
- [ ] Add error handling and retries
- [ ] Write unit tests with mock HTTP

### Day 23-25: Python SDK
- [ ] Initialize `packages/py-sdk` with pyproject.toml
- [ ] Implement `MCTAgentsClient` class
- [ ] Implement `client.create_run()` method
- [ ] Implement `client.stream_events()` with Generator
- [ ] Implement `client.cancel_run()` method
- [ ] Add authentication headers
- [ ] Add error handling
- [ ] Write unit tests with mock HTTP

### Day 26-27: Plugin Contract
- [ ] Define `MCTPlugin` interface (TypeScript)
- [ ] Define `MCTPlugin` protocol (Python)
- [ ] Define tool registration API
- [ ] Define event hook API
- [ ] Write plugin documentation

### Day 28: Documentation + Publishing
- [ ] Write SDK README with usage examples
- [ ] Add API reference documentation
- [ ] Configure npm publishing
- [ ] Configure PyPI publishing
- [ ] Test both SDKs against running API

## Definition of Done
- [ ] TypeScript SDK compiles and all exports work
- [ ] Python SDK passes type checking
- [ ] Both SDKs can create runs and stream events
- [ ] Plugin contract is defined and documented
- [ ] SDK README with examples is complete

## Risks
- **API changes:** Pin SDK version to API version
- **Streaming compatibility:** Test with multiple runtimes

## Retro Notes
- _To be filled after sprint completion_
