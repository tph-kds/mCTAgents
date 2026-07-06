# Local Model Guide

This guide helps you choose and configure local models for mCTAgents on systems with limited VRAM.

## Model Options for <4GB VRAM

| Model | Size | VRAM | Quality | Speed |
|-------|------|------|---------|-------|
| Qwen3-0.5B-Q4_K_M | 0.4GB | <1GB | Basic | Fast |
| Qwen3-1.7B-Q4_K_M | 1.3GB | <2GB | Good | Medium |
| Qwen3-4B-Q4_K_M | 2.5GB | <3GB | Better | Slower |

## Recommended Configuration

For 4GB VRAM systems:

- **Primary model:** Qwen3-1.7B-Q4_K_M
- **Embedding:** nomic-embed-text (274MB)
- **Total VRAM:** ~2GB (safe margin for context)

For 2GB VRAM systems:

- **Primary model:** Qwen3-0.5B-Q4_K_M
- **Embedding:** nomic-embed-text (274MB)
- **Total VRAM:** ~1GB

## Quick Setup

```bash
# Copy environment config
cp .env.example .env

# Edit .env with your settings (see below)
```

## Environment Variables

Set these in your `.env` file:

```bash
# SGLang Configuration
SGLANG_BASE_URL=http://localhost:30000
SGLANG_MODEL=Qwen/Qwen3-1.7B
SGLANG_PORT=30000

# Model Configuration
DEFAULT_CHAT_MODEL=Qwen/Qwen3-1.7B
DEFAULT_REASONING_MODEL=Qwen/Qwen3-1.7B
DEFAULT_EMBEDDING_MODEL=nomic-embed-text

# Budget Limits (reduce for smaller models)
MAX_TOTAL_TOKENS=8000
MAX_MODEL_CALLS=8
MAX_DEBATE_ROUNDS=1
```

## Launching with Optimized Settings

### Docker (Recommended)

```bash
docker compose --profile sglang up -d
```

### Manual

```bash
# For 4GB VRAM
python -m sglang.launch_server \
  --model Qwen/Qwen3-1.7B \
  --reasoning-parser qwen3 \
  --host 0.0.0.0 \
  --port 30000 \
  --context-length 2048 \
  --mem-fraction-static 0.5

# For 2GB VRAM
python -m sglang.launch_server \
  --model Qwen/Qwen3-0.5B \
  --reasoning-parser qwen3 \
  --host 0.0.0.0 \
  --port 30000 \
  --context-length 1024 \
  --mem-fraction-static 0.4
```

## Switching to Ollama (No GPU)

If you don't have an NVIDIA GPU, use Ollama instead:

```bash
# Start Ollama
ollama serve

# Pull a model
ollama pull qwen2.5:3b

# Update .env
DEFAULT_CHAT_MODEL=qwen2.5:3b
DEFAULT_REASONING_MODEL=qwen2.5:3b
DEFAULT_EMBEDDING_MODEL=nomic-embed-text
```

The reasoning engine automatically falls back to Ollama when SGLang is unavailable.

## Performance Tips

1. **Use quantized models** — Q4_K_M variants reduce VRAM usage by ~75%
2. **Reduce context length** — Smaller context = less memory per request
3. **Lower mem-fraction-static** — Leaves room for KV cache growth
4. **Batch requests** — SGLang handles batching automatically
5. **Monitor with nvidia-smi** — Watch VRAM usage during inference
