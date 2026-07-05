# Design Spec: SGLang Integration + UI/UX Subagent Visualization

**Date**: 2026-07-05
**Status**: Draft
**Author**: opencode (mimo-v2.5-free)

---

## 1. Overview

This design covers three interconnected workstreams for the mCTAgents project:

1. **SGLang Integration** -- Replace Ollama with SGLang as the default local inference engine, optimized for <4GB VRAM using Qwen3-1.7B-Q4_K_M.
2. **Subagent UI/UX Enhancement** -- Add thinking traces panels and agent detail popovers to the Studio frontend, making each agent's internal reasoning visible.
3. **Running Guidelines** -- Documentation for setting up and running the entire system locally.

---

## 2. Current State

### What Exists
- **Ollama** is the default model provider (`services/model-gateway/` proxies Ollama's API)
- **Studio** (`apps/studio/`) has a 3D workspace with 6 agent avatars, HUD panels, and SSE streaming
- **Reasoning Engine** (`services/reasoning-engine/`) has an `OpenAICompatibleProvider` that talks to any OpenAI-compatible API
- Default models: `qwen2.5:7b` (chat), `deepseek-r1:7b` (reasoning), `nomic-embed-text` (embedding)
- Docker Compose runs 8 services including Ollama

### What's Missing
- No SGLang support in the model gateway or reasoning engine
- No agent thinking traces visualization (events show in timeline but not step-by-step reasoning)
- No agent detail popover (clicking 3D avatars does nothing)
- `FinalAnswerPanel`, `EvidenceBoard`, `DebateTimeline` components exist but are unused
- No documentation for SGLang setup

---

## 3. Workstream 1: SGLang Integration

### 3.1 Model Selection

| Role | Model | Size | VRAM | Purpose |
|------|-------|------|------|---------|
| Chat (framer/architect/evidence/critic) | Qwen3-1.7B-Q4_K_M | 1.28GB | <2GB | General reasoning |
| Reasoning (judge/synthesizer) | Qwen3-1.7B-Q4_K_M | 1.28GB | <2GB | With `--reasoning-parser qwen3` |
| Embedding | nomic-embed-text | 274MB | <1GB | Vector embeddings |

Total VRAM: ~2.5GB (fits comfortably in 4GB).

### 3.2 SGLang Server Configuration

```bash
# Launch SGLang server
python -m sglang.launch_server \
  --model Qwen/Qwen3-1.7B \
  --reasoning-parser qwen3 \
  --host 0.0.0.0 \
  --port 30000 \
  --context-length 4096 \
  --mem-fraction-static 0.7
```

SGLang exposes an OpenAI-compatible API at `/v1/chat/completions` and `/v1/models`.

### 3.3 Provider Integration

**Option A (Recommended): Use OpenAICompatibleProvider directly**

The reasoning engine already has `OpenAICompatibleProvider` (`services/reasoning-engine/src/mctagents/services/model_gateway/openai_compatible.py`). We configure it to point at SGLang's OpenAI-compatible endpoint:

- `base_url`: `http://sglang:30000/v1`
- No API key needed for local
- Model name: `Qwen/Qwen3-1.7B`

**Changes needed:**
1. Add `sglang` service to `docker-compose.yml`
2. Update `services/reasoning-engine/src/mctagents/services/model_gateway/config.py` to support SGLang URL
3. Update `services/reasoning-engine/src/mctagents/api/app.py` to use SGLang as default provider
4. Update `.env.example` with SGLang defaults

### 3.4 Docker Compose Changes

```yaml
# New service in docker-compose.yml
sglang:
  image: lmsysorg/sglang:latest
  container_name: mctagents-sglang
  ports:
    - "${SGLANG_PORT:-30000}:30000"
  volumes:
    - sglang_data:/root/.cache/huggingface
  environment:
    - HUGGING_FACE_HUB_TOKEN=${HF_TOKEN:-}
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:30000/health"]
    interval: 30s
    timeout: 10s
    retries: 5
  networks:
    - mctagents
```

### 3.5 Environment Variable Updates

```bash
# .env.example additions
SGLANG_PORT=30000
SGLANG_BASE_URL=http://sglang:30000
DEFAULT_CHAT_MODEL=Qwen/Qwen3-1.7B
DEFAULT_REASONING_MODEL=Qwen/Qwen3-1.7B
DEFAULT_EMBEDDING_MODEL=nomic-embed-text
```

### 3.6 Embedding Fallback

For embeddings, SGLang also serves embedding models. If SGLang doesn't support the embedding model, we keep the Ollama provider as a fallback just for embeddings, or use a standalone embedding server.

---

## 4. Workstream 2: Subagent UI/UX Enhancement

### 4.1 Agent Thinking Traces Panel

**File**: `apps/studio/src/components/hud/ThinkingTracesPanel.tsx`

**Purpose**: Show each agent's internal reasoning steps in real-time as SSE events arrive.

**Data Source**: SSE events from the reasoning engine. The following event types contain thinking trace data:
- `agent_started` -- agent begins reasoning (payload contains agent_id, initial context)
- `tool_called` -- agent calls a tool (payload contains tool name, arguments)
- `tool_result` -- tool returns result (payload contains result summary)
- `claim_created` -- agent proposes a claim
- `objection_created` -- critic raises an objection
- `claim_revised` -- architect revises a claim
- `judge_scored` -- judge scores a claim

**Component Structure**:
```
ThinkingTracesPanel
├── Header: "THINKING TRACES" + event count badge
├── Filter bar: checkboxes per agent role (All, Framer, Architect, Evidence, Critic, Judge, Synthesizer)
└── Scrollable list (auto-scroll to bottom, pause on manual scroll)
    └── TraceEntry (per event)
        ├── Agent avatar icon (small, colored by role)
        ├── Agent name + role badge
        ├── Timestamp (relative: "2s ago")
        ├── Step type label (THINKING, ACTION, RESULT, CLAIM, OBJECTION)
        └── Content (truncated to 3 lines, expandable on click)
```

**Visual Design**:
- Glass morphism card matching existing HUD style
- Agent role colors: framer=blue, architect=cyan, evidence=green, critic=orange, judge=purple, synthesizer=emerald
- Monospace font for tool call arguments
- Subtle left-border accent color matching agent role
- Maximum 200 entries visible (older entries virtualized or removed)

**Integration**:
- Add to left sidebar below `MiniTimeline`
- Pass `events` array from parent page
- Filter events by type before rendering

### 4.2 Agent Detail Popover

**File**: `apps/studio/src/components/three/AgentPopover.tsx`

**Purpose**: Show detailed information about an agent when its 3D avatar is clicked.

**Trigger**: Click handler on `AgentAvatar` component in the 3D scene.

**Component Structure**:
```
AgentPopover (positioned in 3D space via @react-three/drei Html)
├── Header
│   ├── Agent role icon (large)
│   ├── Agent name
│   └── Role description
├── Tabs: [Claims | Objections | Activity]
│   ├── Claims tab
│   │   └── List of claims authored by this agent
│   │       ├── Status badge (accepted/rejected/proposed/challenged)
│   │       ├── Claim text (truncated)
│   │       └── Confidence score
│   ├── Objections tab
│   │   └── List of objections raised by this agent
│   │       ├── Target claim reference
│   │       ├── Severity badge
│   │       └── Reason text
│   └── Activity tab
│       └── Timeline of this agent's events
│           ├── Event type
│           ├── Timestamp
│           └── Payload summary
├── Stats
│   ├── Claims proposed: N
│   ├── Claims accepted: N
│   ├── Objections raised: N
│   └── Average confidence: X%
└── Close button (X)
```

**Visual Design**:
- Glass morphism card with backdrop blur
- Positioned relative to the clicked avatar using `Html` from drei
- Fades in/out with CSS transitions
- Semi-transparent dark background (`rgba(0,0,0,0.85)`)
- Neon border glow matching agent role color
- Click outside or press Escape to dismiss

**Integration**:
- Modify `AgentAvatar.tsx` to accept `onClick` callback
- Modify `Workspace.tsx` to manage selected agent state
- Pass claims and events data to the popover

### 4.3 Layout Refinement

**Current layout** (run detail page):
```
┌─────────────────────────────────────────┐
│ StatusBar                               │
├──────────┬──────────────────┬───────────┤
│ Controls │  3D WORKSPACE    │ Claims    │
│ Panel    │                  │ Sidebar   │
│ Mini     │                  │           │
│ Timeline │                  │           │
├──────────┴──────────────────┴───────────┤
```

**Proposed layout**:
```
┌─────────────────────────────────────────────────┐
│ StatusBar                                       │
├──────────┬──────────────────┬───────────────────┤
│ Controls │                  │ Claims Sidebar     │
│ Panel    │  3D WORKSPACE    │                   │
│ Mini     │  (with popover)  │                   │
│ Timeline │                  │                   │
│ Thinking │                  │                   │
│ Traces   │                  │                   │
├──────────┴──────────────────┴───────────────────┤
│ EvidenceBoard (if evidence exists)              │
├─────────────────────────────────────────────────┤
│ FinalAnswerPanel (when completed)               │
└─────────────────────────────────────────────────┘
```

**Changes**:
1. Add `ThinkingTracesPanel` below `MiniTimeline` in left sidebar
2. Add `EvidenceBoard` component below the 3D workspace (conditionally rendered)
3. Add `FinalAnswerPanel` at bottom (conditionally rendered when run completes)
4. Make `ControlsPanel` collapsible to save space
5. Improve mobile responsive behavior (stack sidebar panels vertically on small screens)

### 4.4 SSE Event Enhancement

The thinking traces need richer event data. Add to the reasoning engine:

**New event payload fields**:
```python
# In agents/base.py, AgentResult should include:
thinking_steps: list[ThinkingStep] = []

class ThinkingStep(BaseModel):
    step_type: str  # "reasoning", "tool_call", "tool_result", "observation"
    content: str
    tool_name: str | None = None
    tool_args: dict | None = None
    duration_ms: int | None = None
```

Each agent's `act()` method should append thinking steps to the result. This gives the frontend detailed reasoning traces.

---

## 5. Workstream 3: Running Guidelines

### 5.1 Prerequisites
- Docker + Docker Compose
- NVIDIA GPU with >= 4GB VRAM
- NVIDIA Container Toolkit (for GPU passthrough in Docker)
- ~5GB disk space (models + containers)

### 5.2 Setup Steps

```bash
# 1. Clone and enter the repo
git clone <repo-url> && cd mCTAgents

# 2. Copy environment file
cp .env.example .env

# 3. Start all services (SGLang + infrastructure + apps)
make dev

# 4. Wait for SGLang to download model (~1.3GB)
# Check: docker logs mctagents-sglang

# 5. Open Studio
open http://localhost:3000

# 6. Create a new reasoning session
# Enter a problem statement and click "Start Session"
```

### 5.3 Manual SGLang Setup (without Docker)

```bash
# Install SGLang
pip install sglang[all]

# Download model
huggingface-cli download Qwen/Qwen3-1.7B --local-dir ./models/Qwen3-1.7B

# Launch server
python -m sglang.launch_server \
  --model ./models/Qwen3-1.7B \
  --reasoning-parser qwen3 \
  --host 0.0.0.0 \
  --port 30000 \
  --context-length 4096

# Verify
curl http://localhost:30000/v1/models
```

### 5.4 VRAM Optimization Tips

- Use `--context-length 2048` to reduce memory if needed
- Use `--mem-fraction-static 0.6` to leave room for KV cache
- Qwen3-1.7B-Q4_K_M uses ~1.3GB for weights + ~500MB for KV cache = ~1.8GB total
- Safe for 4GB VRAM GPUs (RTX 3060, RTX 4060, etc.)

---

## 6. Implementation Order

### Phase 1: SGLang Integration (Estimated: 2-3 hours)
1. Create `SGLangProvider` or configure `OpenAICompatibleProvider` for SGLang
2. Add SGLang service to `docker-compose.yml`
3. Update `.env.example` and `docker-compose.override.yml`
4. Update reasoning engine app.py to use SGLang defaults
5. Test with `make dev` and verify inference works

### Phase 2: Thinking Traces Panel (Estimated: 3-4 hours)
1. Add `ThinkingStep` model to reasoning engine protocol
2. Update agent `act()` methods to emit thinking steps
3. Create `ThinkingTracesPanel.tsx` component
4. Integrate into run detail page layout
5. Test with live SSE events

### Phase 3: Agent Detail Popover (Estimated: 2-3 hours)
1. Create `AgentPopover.tsx` component
2. Modify `AgentAvatar.tsx` to support click events
3. Modify `Workspace.tsx` to manage selected agent state
4. Wire up claims/events data to popover
5. Test click interaction in 3D scene

### Phase 4: Layout Polish + Documentation (Estimated: 1-2 hours)
1. Add EvidenceBoard and FinalAnswerPanel to run detail page
2. Make ControlsPanel collapsible
3. Write running guidelines documentation
4. Update README.md with SGLang instructions

**Total estimated effort: 8-12 hours**

---

## 7. Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| SGLang GPU memory exceeds 4GB | High | Use smaller context length, reduce mem-fraction |
| Qwen3-1.7B quality insufficient for reasoning | Medium | Can swap to Qwen3-0.5B for speed or Qwen3-4B if VRAM allows |
| SSE events don't contain thinking step data | Medium | Add thinking step emission to agent base class |
| 3D popover performance with many events | Low | Virtualize event list, limit visible entries |
| SGLang Docker image compatibility | Low | Fallback to pip install in a custom container |

---

## 8. Testing Strategy

### SGLang Integration
- Unit test: `OpenAICompatibleProvider` with mock SGLang responses
- Integration test: Start SGLang with Qwen3-1.7B, create a run, verify events flow
- VRAM test: Monitor GPU memory during inference

### UI Components
- Unit test: `ThinkingTracesPanel` renders events correctly
- Unit test: `AgentPopover` shows claims/objections for selected agent
- E2E test: Create a run, verify thinking traces appear, click agent avatar, verify popover

### Documentation
- Verify all setup commands work on a fresh machine
- Test Docker Compose start-to-finish flow

---

## 9. Files to Create/Modify

### New Files
- `apps/studio/src/components/hud/ThinkingTracesPanel.tsx`
- `apps/studio/src/components/three/AgentPopover.tsx`
- `docs/getting-started/sglang-setup.md`
- `docs/getting-started/local-model-guide.md`

### Modified Files
- `docker-compose.yml` -- Add SGLang service
- `docker-compose.override.yml` -- Add SGLang dev overrides
- `.env.example` -- Add SGLang env vars
- `services/reasoning-engine/src/mctagents/services/model_gateway/config.py` -- SGLang config
- `services/reasoning-engine/src/mctagents/api/app.py` -- SGLang provider init
- `services/reasoning-engine/src/mctagents/agents/base.py` -- Add ThinkingStep
- `services/reasoning-engine/src/mctagents/agents/*.py` -- Emit thinking steps
- `apps/studio/src/app/runs/[runId]/page.tsx` -- Integrate new panels
- `apps/studio/src/components/three/AgentAvatar.tsx` -- Add click handler
- `apps/studio/src/components/three/Workspace.tsx` -- Manage selected agent state
- `apps/studio/src/hooks/useSSE.ts` -- Parse thinking step events
- `README.md` -- Update with SGLang instructions
