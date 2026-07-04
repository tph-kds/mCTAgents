# SGLang Setup Guide

SGLang is the default model provider for mCTAgents, offering high-performance LLM inference with OpenAI-compatible API.

## Prerequisites

- Python >=3.11
- NVIDIA GPU with >=4GB VRAM
- NVIDIA Container Toolkit (for Docker GPU passthrough)
- Docker and Docker Compose

## Quick Start (Docker)

The fastest way to get SGLang running is via Docker Compose:

```bash
# Start all services including SGLang
docker compose --profile sglang up -d

# Wait for model download (~1.3GB for Qwen3-1.7B)
docker logs -f mctagents-sglang

# Open Studio UI
open http://localhost:3000
```

To stop SGLang:

```bash
docker compose --profile sglang down
```

## Manual Setup

### Install SGLang

```bash
pip install sglang[all]
```

### Download Model

```bash
pip install huggingface_hub
huggingface-cli download Qwen/Qwen3-1.7B --local-dir ./models/Qwen3-1.7B
```

For gated models, set your HuggingFace token first:

```bash
export HF_TOKEN=your-huggingface-token
huggingface-cli login
```

### Launch Server

```bash
python -m sglang.launch_server \
  --model ./models/Qwen3-1.7B \
  --reasoning-parser qwen3 \
  --host 0.0.0.0 \
  --port 30000 \
  --context-length 4096 \
  --mem-fraction-static 0.7
```

### Verify

```bash
curl http://localhost:30000/v1/models
```

You should see the model listed in the response.

## VRAM Optimization

| Setting | Default | Low VRAM (<4GB) |
|---------|---------|-----------------|
| `--context-length` | 4096 | 2048 |
| `--mem-fraction-static` | 0.7 | 0.5 |
| `--quantization` | none | awq or gptq |

For low VRAM systems, use a quantized model:

```bash
python -m sglang.launch_server \
  --model Qwen/Qwen3-1.7B \
  --reasoning-parser qwen3 \
  --host 0.0.0.0 \
  --port 30000 \
  --context-length 2048 \
  --mem-fraction-static 0.5 \
  --quantization awq
```

## Environment Variables

Configure mCTAgents to use SGLang by setting these in your `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `SGLANG_BASE_URL` | SGLang server URL | `http://sglang:30000` |
| `SGLANG_MODEL` | Model name | `Qwen/Qwen3-1.7B` |
| `SGLANG_CONTEXT_LENGTH` | Max context length | `4096` |
| `SGLANG_PORT` | Exposed port | `30000` |
| `HF_TOKEN` | HuggingFace token for gated models | (empty) |

## Troubleshooting

### GPU out of memory

- Reduce `--context-length` to 2048
- Reduce `--mem-fraction-static` to 0.5
- Use a smaller model (Qwen3-0.5B)
- Use a quantized variant (awq/gptq)

### Slow inference

- Ensure CUDA is properly installed: `nvidia-smi`
- Check GPU utilization during inference
- Reduce context length to decrease memory pressure

### Model download fails

- Check internet connectivity
- Set `HF_TOKEN` if using gated models
- Verify available disk space

### Port 30000 already in use

- Change the port in `.env`: `SGLANG_PORT=30001`
- Or stop the conflicting process: `lsof -i :30000`
