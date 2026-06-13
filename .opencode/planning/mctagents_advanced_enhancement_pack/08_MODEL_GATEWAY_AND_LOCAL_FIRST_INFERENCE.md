# Model Gateway and Local-First Inference

## 1. Model gateway purpose

The model gateway isolates the reasoning engine from model providers. It enables local-first deployment while still allowing cloud providers when needed.

## 2. Required providers

```text
Ollama
OpenAI-compatible API
vLLM
LM Studio
OpenRouter
Mock provider for tests
```

## 3. Model interface

```go
type ModelProvider interface {
    Chat(ctx context.Context, req ChatRequest) (*ChatResponse, error)
    Stream(ctx context.Context, req ChatRequest) (<-chan ChatChunk, error)
    Embed(ctx context.Context, req EmbedRequest) (*EmbedResponse, error)
    Health(ctx context.Context) (*ProviderHealth, error)
}
```

## 4. Local-first model presets

For low VRAM development:

```yaml
presets:
  local_tiny:
    chat_model: qwen2.5:3b
    reasoning_model: deepseek-r1:1.5b
    embedding_model: nomic-embed-text
  local_balanced:
    chat_model: qwen2.5:7b
    reasoning_model: deepseek-r1:7b
    embedding_model: bge-m3
  cloud_hybrid:
    fast_model: local_small
    deep_model: openai_compatible_large
```

## 5. Routing strategy

```text
Simple task -> small local model
Structured extraction -> reliable JSON-capable model
Evidence summary -> cheap local/cloud model
Judge decision -> stronger model
Final synthesis -> stronger model if quality matters
```

## 6. Cost and latency controls

```yaml
budget:
  max_total_tokens: 12000
  max_model_calls: 16
  max_debate_rounds: 2
  prefer_local: true
  fallback_provider: openai_compatible
```

## 7. Capability registry

Each model should have metadata:

```json
{
  "name": "qwen2.5:3b",
  "provider": "ollama",
  "supports_json": true,
  "supports_tools": false,
  "context_window": 32768,
  "cost_per_1k_tokens": 0,
  "latency_class": "low",
  "recommended_roles": ["framer", "critic", "summarizer"]
}
```

## 8. Reliability features

```text
- retries with backoff
- provider fallback
- structured output validation
- timeout per role
- token budget enforcement
- response schema repair
- streaming cancellation
```
