# STEP 2: Model Gateway

**Timeline:** Days 5-10 | **Complexity:** 3/5 | **Dependencies:** STEP 0

## Goal

Isolate the reasoning engine from model providers. Enable local-first deployment with Ollama while supporting cloud providers.

## Providers

| Provider | Use Case |
|----------|----------|
| Ollama | Default, local-first, zero cost |
| OpenAI-compatible | vLLM, LM Studio, OpenRouter |
| vLLM | High-throughput serving |
| LM Studio | Desktop local inference |
| OpenRouter | Multi-model cloud gateway |

## Model Router

Routes by task type:
- `framer` → balanced model
- `architect` → balanced model
- `evidence` → balanced model
- `critic` → balanced model
- `judge` → strong/reasoning model
- `synthesizer` → strong/reasoning model

## Budget Controls
```yaml
budgets:
  default:
    max_total_tokens: 12000
    max_model_calls: 16
    max_debate_rounds: 2
  deep:
    max_total_tokens: 40000
    max_model_calls: 32
    max_debate_rounds: 4
```

## Reliability
- Retry with exponential backoff (3 attempts)
- Circuit breaker (5 failures → open, 30s reset)
- Provider timeout (60s)
- Automatic fallback to next provider

## Files
```
services/model-gateway/
├── internal/provider/    # Ollama, OpenAI, mock providers
├── internal/router/      # Task-based model selection
├── internal/registry/    # Available models
└── config/presets.yaml   # Budget and reliability config
```

## Success Criteria
- [ ] Ollama provider: Chat, Stream, Embed, Health
- [ ] OpenAI-compatible provider works
- [ ] Router selects correct model per task
- [ ] Streaming delivers chunks correctly
- [ ] Provider fallback works
- [ ] Circuit breaker trips and resets
