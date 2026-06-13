# Sprint 02: Model Gateway

**Duration:** Days 5-10 | **Goal:** Ollama provider, OpenAI-compatible provider, model router

## Tasks

### Day 5-6: Provider Interface + Ollama
- [ ] Define `ModelProvider` interface (Chat, Stream, Embed, Health)
- [ ] Define request/response types (ChatRequest, ChatResponse, etc.)
- [ ] Implement `OllamaProvider.Chat()` with JSON mode
- [ ] Implement `OllamaProvider.Stream()` with chunked response
- [ ] Implement `OllamaProvider.Embed()` for embeddings
- [ ] Implement `OllamaProvider.Health()` with model listing
- [ ] Write unit tests with mock HTTP responses

### Day 7-8: OpenAI-Compatible Provider
- [ ] Implement `OpenAICompatibleProvider.Chat()`
- [ ] Implement `OpenAICompatibleProvider.Stream()` with SSE parsing
- [ ] Implement `OpenAICompatibleProvider.Embed()`
- [ ] Implement `OpenAICompatibleProvider.Health()`
- [ ] Test with vLLM, LM Studio, OpenRouter endpoints
- [ ] Write unit tests

### Day 8-9: Model Router
- [ ] Define `ModelPreset` (chat, reasoning, embedding models)
- [ ] Define `TaskRouting` map (framer→balanced, judge→strong, etc.)
- [ ] Implement `ModelRouter.SelectModel()` by task type
- [ ] Implement health-based provider selection
- [ ] Implement fallback logic (primary → secondary)
- [ ] Configure budget presets (default, deep)
- [ ] Write router tests

### Day 9-10: Reliability + Config
- [ ] Implement retry with exponential backoff (3 attempts)
- [ ] Implement circuit breaker (5 failures → open, 30s reset)
- [ ] Add provider timeout (60s)
- [ ] Create `config/presets.yaml` with budget configs
- [ ] Add latency/usage metrics collection
- [ ] Write integration tests

## Definition of Done
- [ ] Ollama provider handles Chat, Stream, Embed, Health
- [ ] OpenAI-compatible provider works with vLLM/LM Studio
- [ ] Router selects correct model per task type
- [ ] Streaming delivers chunks without dropping
- [ ] Provider fallback works when primary fails
- [ ] Circuit breaker trips and resets correctly

## Risks
- **Ollama not running:** Graceful error with helpful message
- **Model not available:** Auto-download or skip with warning

## Retro Notes
- _To be filled after sprint completion_
