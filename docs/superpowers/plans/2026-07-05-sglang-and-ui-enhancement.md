# SGLang Integration + UI/UX Subagent Enhancement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace Ollama with SGLang for <4GB VRAM local inference, add agent thinking traces panel and agent detail popover to Studio UI, and write running guidelines documentation.

**Architecture:** SGLang serves Qwen3-1.7B-Q4_K_M (1.28GB) via OpenAI-compatible API. The reasoning engine's existing `OpenAICompatibleProvider` connects to it. Studio gains two new HUD components: `ThinkingTracesPanel` (live reasoning steps) and `AgentPopover` (click-to-inspect agent details). Documentation covers SGLang setup and local model optimization.

**Tech Stack:** Python (FastAPI, SGLang, Pydantic), Go (API gateway), TypeScript (Next.js 14, React Three Fiber, Tailwind CSS), Docker Compose

## Global Constraints

- Python >=3.11, TypeScript >=5.3, Go >=1.22
- Ruff for Python linting (line-length=88), ESLint + Prettier for TypeScript
- Pydantic v2 for all Python data models
- React Three Fiber for 3D visualization
- SSE for real-time event streaming
- Docker Compose for local development
- Qwen3-1.7B-Q4_K_M (1.28GB) as primary model
- <4GB VRAM budget total

---

## File Structure

### New Files
| File | Responsibility |
|------|---------------|
| `services/reasoning-engine/src/mctagents/services/model_gateway/sglang.py` | SGLang-specific provider (thin wrapper or config) |
| `apps/studio/src/components/hud/ThinkingTracesPanel.tsx` | Live thinking traces visualization |
| `apps/studio/src/components/three/AgentPopover.tsx` | Agent detail popover on avatar click |
| `docs/getting-started/sglang-setup.md` | SGLang installation and configuration guide |
| `docs/getting-started/local-model-guide.md` | Local model optimization for <4GB VRAM |
| `services/reasoning-engine/tests/unit/test_sglang_provider.py` | Tests for SGLang provider |
| `apps/studio/src/components/hud/__tests__/ThinkingTracesPanel.test.tsx` | Tests for thinking traces |
| `apps/studio/src/components/three/__tests__/AgentPopover.test.tsx` | Tests for agent popover |

### Modified Files
| File | Change |
|------|--------|
| `docker-compose.yml` | Add SGLang service |
| `docker-compose.override.yml` | Add SGLang dev overrides |
| `.env.example` | Add SGLang env vars |
| `services/reasoning-engine/src/mctagents/services/model_gateway/config.py` | SGLang config support |
| `services/reasoning-engine/src/mctagents/api/app.py` | Initialize SGLang provider |
| `services/reasoning-engine/src/mctagents/agents/base.py` | Add ThinkingStep model |
| `services/reasoning-engine/src/mctagents/agents/architect.py` | Emit thinking steps |
| `services/reasoning-engine/src/mctagents/agents/critic.py` | Emit thinking steps |
| `services/reasoning-engine/src/mctagents/agents/judge.py` | Emit thinking steps |
| `services/reasoning-engine/src/mctagents/agents/evidence_agent.py` | Emit thinking steps |
| `services/reasoning-engine/src/mctagents/agents/problem_framer.py` | Emit thinking steps |
| `services/reasoning-engine/src/mctagents/agents/synthesizer.py` | Emit thinking steps |
| `apps/studio/src/app/runs/[runId]/page.tsx` | Integrate new panels |
| `apps/studio/src/components/three/AgentAvatar.tsx` | Add onClick handler |
| `apps/studio/src/components/three/Workspace.tsx` | Manage selected agent state |
| `apps/studio/src/hooks/useSSE.ts` | Parse thinking step events |
| `apps/studio/src/lib/types.ts` | Add ThinkingStep type |
| `README.md` | Update with SGLang instructions |

---

## Phase 1: SGLang Integration

### Task 1: Add SGLang Provider Configuration

**Files:**
- Modify: `services/reasoning-engine/src/mctagents/services/model_gateway/config.py`
- Create: `services/reasoning-engine/tests/unit/test_sglang_provider.py`

**Interfaces:**
- Consumes: `ModelGatewayConfig` from config.py
- Produces: `SGLangConfig` dataclass with `base_url`, `model`, `context_length`

- [ ] **Step 1: Write the failing test**

```python
# services/reasoning-engine/tests/unit/test_sglang_provider.py
import pytest
from mctagents.services.model_gateway.config import SGLangConfig


def test_sglang_config_defaults():
    config = SGLangConfig()
    assert config.base_url == "http://localhost:30000"
    assert config.model == "Qwen/Qwen3-1.7B"
    assert config.context_length == 4096


def test_sglang_config_from_env(monkeypatch):
    monkeypatch.setenv("SGLANG_BASE_URL", "http://custom:9999")
    monkeypatch.setenv("SGLANG_MODEL", "custom-model")
    config = SGLangConfig.from_env()
    assert config.base_url == "http://custom:9999"
    assert config.model == "custom-model"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd services/reasoning-engine && python -m pytest tests/unit/test_sglang_provider.py -v`
Expected: FAIL with `ImportError: cannot import name 'SGLangConfig'`

- [ ] **Step 3: Write minimal implementation**

```python
# services/reasoning-engine/src/mctagents/services/model_gateway/config.py
# Add after existing ModelGatewayConfig:

import os
from dataclasses import dataclass, field


@dataclass
class SGLangConfig:
    """Configuration for SGLang model provider."""
    base_url: str = field(default_factory=lambda: os.getenv("SGLANG_BASE_URL", "http://localhost:30000"))
    model: str = field(default_factory=lambda: os.getenv("SGLANG_MODEL", "Qwen/Qwen3-1.7B"))
    context_length: int = field(default_factory=lambda: int(os.getenv("SGLANG_CONTEXT_LENGTH", "4096")))
    api_key: str = field(default_factory=lambda: os.getenv("SGLANG_API_KEY", ""))

    @classmethod
    def from_env(cls) -> "SGLangConfig":
        return cls()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd services/reasoning-engine && python -m pytest tests/unit/test_sglang_provider.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/reasoning-engine/src/mctagents/services/model_gateway/config.py services/reasoning-engine/tests/unit/test_sglang_provider.py
git commit -m "feat: add SGLangConfig for SGLang provider integration"
```

---

### Task 2: Wire SGLang into Reasoning Engine App

**Files:**
- Modify: `services/reasoning-engine/src/mctagents/api/app.py`
- Modify: `services/reasoning-engine/src/mctagents/services/model_gateway/__init__.py`

**Interfaces:**
- Consumes: `SGLangConfig` from Task 1
- Produces: SGLang provider instance used by `ReasoningEngine`

- [ ] **Step 1: Write the failing test**

```python
# Add to existing test_models.py or create test_sglang_init.py
import pytest
from unittest.mock import patch, MagicMock


def test_sglang_provider_initialization():
    with patch.dict("os.environ", {"SGLANG_BASE_URL": "http://test:30000"}):
        from mctagents.services.model_gateway.config import SGLangConfig
        config = SGLangConfig.from_env()
        assert config.base_url == "http://test:30000"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd services/reasoning-engine && python -m pytest tests/unit/test_models.py -v -k sglang`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# services/reasoning-engine/src/mctagents/services/model_gateway/__init__.py
# Add to existing exports:

from .config import SGLangConfig

__all__ = [
    "ModelProvider",
    "ChatMessage",
    "ChatResponse",
    "EmbeddingResponse",
    "ModelRouter",
    "ModelPreset",
    "TaskType",
    "SGLangConfig",
]
```

Update `services/reasoning-engine/src/mctagents/api/app.py` lifespan to support SGLang:

```python
# In the lifespan function, after existing provider setup:

# Try SGLang first, fall back to Ollama
sglang_config = SGLangConfig.from_env()
try:
    # Test SGLang connectivity
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{sglang_config.base_url}/v1/models", timeout=5.0)
        if resp.status_code == 200:
            model_provider = OpenAICompatibleProvider(
                base_url=sglang_config.base_url,
                api_key=sglang_config.api_key or "not-needed",
                default_model=sglang_config.model,
            )
            logger.info("Using SGLang provider", base_url=sglang_config.base_url)
        else:
            raise ConnectionError("SGLang not available")
except Exception:
    logger.warning("SGLang not available, falling back to Ollama")
    model_provider = OllamaProvider(base_url=ollama_url)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd services/reasoning-engine && python -m pytest tests/unit/test_models.py -v -k sglang`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/reasoning-engine/src/mctagents/services/model_gateway/__init__.py services/reasoning-engine/src/mctagents/api/app.py
git commit -m "feat: wire SGLang provider into reasoning engine with Ollama fallback"
```

---

### Task 3: Add SGLang Service to Docker Compose

**Files:**
- Modify: `docker-compose.yml`
- Modify: `docker-compose.override.yml`
- Modify: `.env.example`

**Interfaces:**
- Consumes: SGLang Docker image, GPU passthrough
- Produces: Running SGLang server on port 30000

- [ ] **Step 1: Write the failing test**

No unit test needed for Docker Compose. Manual verification step.

- [ ] **Step 2: Add SGLang service to docker-compose.yml**

Add after the `ollama` service definition:

```yaml
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
      start_period: 60s
    networks:
      - mctagents
    profiles:
      - sglang
```

Add volume:
```yaml
  sglang_data:
    driver: local
```

- [ ] **Step 3: Add SGLang dev overrides to docker-compose.override.yml**

```yaml
  sglang:
    command: >
      --model Qwen/Qwen3-1.7B
      --reasoning-parser qwen3
      --host 0.0.0.0
      --port 30000
      --context-length 4096
      --mem-fraction-static 0.7
```

- [ ] **Step 4: Update .env.example**

Add after existing model variables:

```bash
# SGLang Configuration
SGLANG_PORT=30000
SGLANG_BASE_URL=http://sglang:30000
SGLANG_MODEL=Qwen/Qwen3-1.7B
SGLANG_CONTEXT_LENGTH=4096
SGLANG_API_KEY=
HF_TOKEN=
```

- [ ] **Step 5: Add sglang_data volume to volumes section**

Already added in Step 2.

- [ ] **Step 6: Commit**

```bash
git add docker-compose.yml docker-compose.override.yml .env.example
git commit -m "feat: add SGLang service to Docker Compose with GPU passthrough"
```

---

### Task 4: Update Reasoning Engine Defaults

**Files:**
- Modify: `services/reasoning-engine/src/mctagents/api/app.py`
- Modify: `.env.example`

**Interfaces:**
- Consumes: `SGLangConfig` from Task 1
- Produces: Updated default model names

- [ ] **Step 1: Update model defaults in app.py**

In the lifespan function, change the default model resolution:

```python
# Before:
chat_model = os.getenv("DEFAULT_CHAT_MODEL", "qwen2.5:7b")
reasoning_model = os.getenv("DEFAULT_REASONING_MODEL", "deepseek-r1:7b")

# After:
chat_model = os.getenv("DEFAULT_CHAT_MODEL", "Qwen/Qwen3-1.7B")
reasoning_model = os.getenv("DEFAULT_REASONING_MODEL", "Qwen/Qwen3-1.7B")
```

- [ ] **Step 2: Update .env.example**

```bash
# Before:
DEFAULT_CHAT_MODEL=qwen2.5:7b
DEFAULT_REASONING_MODEL=deepseek-r1:7b

# After:
DEFAULT_CHAT_MODEL=Qwen/Qwen3-1.7B
DEFAULT_REASONING_MODEL=Qwen/Qwen3-1.7B
```

- [ ] **Step 3: Commit**

```bash
git add services/reasoning-engine/src/mctagents/api/app.py .env.example
git commit -m "feat: update default models to Qwen3-1.7B for SGLang"
```

---

## Phase 2: Thinking Traces Panel

### Task 5: Add ThinkingStep Model to Protocol

**Files:**
- Modify: `services/reasoning-engine/src/mctagents/core/protocol/__init__.py`
- Create: `services/reasoning-engine/src/mctagents/core/protocol/thinking_step.py`

**Interfaces:**
- Consumes: Pydantic BaseModel
- Produces: `ThinkingStep` model, `AgentResult.thinking_steps` field

- [ ] **Step 1: Write the failing test**

```python
# services/reasoning-engine/tests/unit/test_thinking_step.py
import pytest
from mctagents.core.protocol.thinking_step import ThinkingStep


def test_thinking_step_creation():
    step = ThinkingStep(
        step_type="reasoning",
        content="Analyzing the claim structure...",
        agent_id="architect_agent",
    )
    assert step.step_type == "reasoning"
    assert step.content == "Analyzing the claim structure..."
    assert step.agent_id == "architect_agent"
    assert step.tool_name is None
    assert step.tool_args is None
    assert step.duration_ms is None


def test_thinking_step_tool_call():
    step = ThinkingStep(
        step_type="tool_call",
        content="Searching for evidence...",
        agent_id="evidence_agent",
        tool_name="vector_search",
        tool_args={"query": "microservices security", "top_k": 5},
    )
    assert step.tool_name == "vector_search"
    assert step.tool_args == {"query": "microservices security", "top_k": 5}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd services/reasoning-engine && python -m pytest tests/unit/test_thinking_step.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [ ] **Step 3: Write minimal implementation**

```python
# services/reasoning-engine/src/mctagents/core/protocol/thinking_step.py
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ThinkingStep(BaseModel):
    """A single reasoning step within an agent's thinking process."""

    step_type: str = Field(
        ...,
        description="Type of step: reasoning, tool_call, tool_result, observation",
    )
    content: str = Field(
        ...,
        description="Text content of this thinking step",
    )
    agent_id: str = Field(
        ...,
        description="Identifier of the agent performing this step",
    )
    tool_name: str | None = Field(
        default=None,
        description="Name of the tool being called, if step_type is tool_call",
    )
    tool_args: dict[str, Any] | None = Field(
        default=None,
        description="Arguments passed to the tool, if step_type is tool_call",
    )
    duration_ms: int | None = Field(
        default=None,
        description="Duration of this step in milliseconds, if measurable",
    )
    sequence: int = Field(
        default=0,
        description="Sequence number within the agent's thinking process",
    )
```

Update `services/reasoning-engine/src/mctagents/core/protocol/__init__.py`:

```python
from .thinking_step import ThinkingStep

__all__ = [
    # ... existing exports ...
    "ThinkingStep",
]
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd services/reasoning-engine && python -m pytest tests/unit/test_thinking_step.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/reasoning-engine/src/mctagents/core/protocol/thinking_step.py services/reasoning-engine/src/mctagents/core/protocol/__init__.py services/reasoning-engine/tests/unit/test_thinking_step.py
git commit -m "feat: add ThinkingStep model to protocol for agent reasoning traces"
```

---

### Task 6: Add ThinkingSteps to AgentResult

**Files:**
- Modify: `services/reasoning-engine/src/mctagents/agents/base.py`

**Interfaces:**
- Consumes: `ThinkingStep` from Task 5
- Produces: `AgentResult.thinking_steps` field

- [ ] **Step 1: Write the failing test**

```python
# Add to existing test_models.py
def test_agent_result_has_thinking_steps():
    from mctagents.agents.base import AgentResult
    from mctagents.core.protocol.thinking_step import ThinkingStep

    result = AgentResult(
        agent_id="test_agent",
        thinking_steps=[
            ThinkingStep(step_type="reasoning", content="thinking...", agent_id="test_agent"),
        ],
    )
    assert len(result.thinking_steps) == 1
    assert result.thinking_steps[0].content == "thinking..."
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd services/reasoning-engine && python -m pytest tests/unit/test_models.py -v -k thinking`
Expected: FAIL with `TypeError: unexpected keyword argument 'thinking_steps'`

- [ ] **Step 3: Write minimal implementation**

```python
# services/reasoning-engine/src/mctagents/agents/base.py
# Add import at top:
from mctagents.core.protocol.thinking_step import ThinkingStep

# Modify AgentResult class:
@dataclass
class AgentResult:
    """Result returned by an agent's act() method."""
    agent_id: str
    claims: list = field(default_factory=list)
    evidence: list = field(default_factory=list)
    objections: list = field(default_factory=list)
    revisions: list = field(default_factory=list)
    events: list = field(default_factory=list)
    thinking_steps: list[ThinkingStep] = field(default_factory=list)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd services/reasoning-engine && python -m pytest tests/unit/test_models.py -v -k thinking`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/reasoning-engine/src/mctagents/agents/base.py
git commit -m "feat: add thinking_steps field to AgentResult"
```

---

### Task 7: Emit Thinking Steps from Architect Agent

**Files:**
- Modify: `services/reasoning-engine/src/mctagents/agents/architect.py`

**Interfaces:**
- Consumes: `ThinkingStep`, `AgentResult`
- Produces: Thinking steps appended during `act()` method

- [ ] **Step 1: Write the failing test**

```python
# services/reasoning-engine/tests/unit/test_architect_thinking.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from mctagents.agents.architect import ArchitectAgent
from mctagents.agents.base import AgentContext


@pytest.mark.asyncio
async def test_architect_emits_thinking_steps():
    mock_provider = AsyncMock()
    mock_provider.chat = AsyncMock(return_value=MagicMock(
        content='{"claims": [], "reasoning": "No claims to revise"}'
    ))

    agent = ArchitectAgent(model_provider=mock_provider)
    context = AgentContext(
        run_id="test-run",
        problem_frame=MagicMock(original_input="Test problem"),
        claims=[],
        evidence=[],
        objections=[],
    )

    result = await agent.act(context)
    assert len(result.thinking_steps) > 0
    assert any(s.step_type == "reasoning" for s in result.thinking_steps)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd services/reasoning-engine && python -m pytest tests/unit/test_architect_thinking.py -v`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```python
# services/reasoning-engine/src/mctagents/agents/architect.py
# Add import at top:
from mctagents.core.protocol.thinking_step import ThinkingStep

# Modify act() method to emit thinking steps:

async def act(self, context: AgentContext) -> AgentResult:
    thinking_steps: list[ThinkingStep] = []
    step_seq = 0

    # Initial reasoning step
    thinking_steps.append(ThinkingStep(
        step_type="reasoning",
        content=f"Analyzing problem: {context.problem_frame.original_input[:100]}...",
        agent_id=self.agent_id,
        sequence=step_seq,
    ))
    step_seq += 1

    if not context.claims:
        # Propose mode
        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content="No existing claims. Entering propose mode to generate initial claims.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))
        step_seq += 1

        # ... existing propose logic ...

        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content=f"Proposed {len(new_claims)} claims covering the problem space.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))
    else:
        # Revise mode
        thinking_steps.append(ThinkingStep(
            step_type="reasoning",
            content=f"Found {len(context.claims)} existing claims. Entering revise mode.",
            agent_id=self.agent_id,
            sequence=step_seq,
        ))
        step_seq += 1

        # ... existing revise logic ...

    return AgentResult(
        agent_id=self.agent_id,
        claims=new_claims,
        thinking_steps=thinking_steps,
        # ... other fields ...
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd services/reasoning-engine && python -m pytest tests/unit/test_architect_thinking.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add services/reasoning-engine/src/mctagents/agents/architect.py services/reasoning-engine/tests/unit/test_architect_thinking.py
git commit -m "feat: emit thinking steps from ArchitectAgent"
```

---

### Task 8: Emit Thinking Steps from All Agents

**Files:**
- Modify: `services/reasoning-engine/src/mctagents/agents/critic.py`
- Modify: `services/reasoning-engine/src/mctagents/agents/judge.py`
- Modify: `services/reasoning-engine/src/mctagents/agents/evidence_agent.py`
- Modify: `services/reasoning-engine/src/mctagents/agents/problem_framer.py`
- Modify: `services/reasoning-engine/src/mctagents/agents/synthesizer.py`

**Interfaces:**
- Consumes: `ThinkingStep` from Task 5
- Produces: Thinking steps in each agent's `act()` method

- [ ] **Step 1: Add thinking steps to CriticAgent**

```python
# services/reasoning-engine/src/mctagents/agents/critic.py
# Add at top:
from mctagents.core.protocol.thinking_step import ThinkingStep

# In act() method, add:
thinking_steps = []
step_seq = 0

thinking_steps.append(ThinkingStep(
    step_type="reasoning",
    content=f"Examining {len(context.claims)} active claims for potential objections.",
    agent_id=self.agent_id,
    sequence=step_seq,
))
step_seq += 1

# After analyzing each claim:
thinking_steps.append(ThinkingStep(
    step_type="reasoning",
    content=f"Found {len(new_objections)} genuine objections across all claims.",
    agent_id=self.agent_id,
    sequence=step_seq,
))

# Include in return AgentResult(..., thinking_steps=thinking_steps, ...)
```

- [ ] **Step 2: Add thinking steps to JudgeAgent**

```python
# services/reasoning-engine/src/mctagents/agents/judge.py
# Similar pattern:
thinking_steps = []
step_seq = 0

thinking_steps.append(ThinkingStep(
    step_type="reasoning",
    content=f"Scoring {len(context.claims)} claims across 5 dimensions.",
    agent_id=self.agent_id,
    sequence=step_seq,
))

# After scoring each claim:
thinking_steps.append(ThinkingStep(
    step_type="reasoning",
    content=f"Verdict: {len(accepted)} accepted, {len(rejected)} rejected, {len(uncertain)} uncertain.",
    agent_id=self.agent_id,
    sequence=step_seq,
))
```

- [ ] **Step 3: Add thinking steps to EvidenceAgent**

```python
# services/reasoning-engine/src/mctagents/agents/evidence_agent.py
thinking_steps = []
step_seq = 0

thinking_steps.append(ThinkingStep(
    step_type="reasoning",
    content=f"Evaluating evidence requirements for {len([c for c in context.claims if c.requires_evidence])} claims.",
    agent_id=self.agent_id,
    sequence=step_seq,
))

# When calling evidence service:
thinking_steps.append(ThinkingStep(
    step_type="tool_call",
    content="Searching vector store for relevant evidence...",
    agent_id=self.agent_id,
    tool_name="vector_search",
    tool_args={"query": claim.text[:100]},
    sequence=step_seq,
))
```

- [ ] **Step 4: Add thinking steps to ProblemFramer**

```python
# services/reasoning-engine/src/mctagents/agents/problem_framer.py
thinking_steps = []
step_seq = 0

thinking_steps.append(ThinkingStep(
    step_type="reasoning",
    content="Normalizing user input into structured problem frame.",
    agent_id=self.agent_id,
    sequence=step_seq,
))
```

- [ ] **Step 5: Add thinking steps to SynthesizerAgent**

```python
# services/reasoning-engine/src/mctagents/agents/synthesizer.py
thinking_steps = []
step_seq = 0

thinking_steps.append(ThinkingStep(
    step_type="reasoning",
    content=f"Synthesizing final answer from {len(accepted_claims)} accepted claims.",
    agent_id=self.agent_id,
    sequence=step_seq,
))
```

- [ ] **Step 6: Run all agent tests**

Run: `cd services/reasoning-engine && python -m pytest tests/unit/ -v`
Expected: All tests PASS

- [ ] **Step 7: Commit**

```bash
git add services/reasoning-engine/src/mctagents/agents/*.py
git commit -m "feat: emit thinking steps from all agent implementations"
```

---

### Task 9: Create ThinkingTracesPanel Component

**Files:**
- Create: `apps/studio/src/components/hud/ThinkingTracesPanel.tsx`

**Interfaces:**
- Consumes: `ThinkingStep[]` from SSE events
- Produces: Rendered panel with auto-scrolling trace list

- [ ] **Step 1: Write the failing test**

```tsx
// apps/studio/src/components/hud/__tests__/ThinkingTracesPanel.test.tsx
import { render, screen } from "@testing-library/react";
import { ThinkingTracesPanel } from "../ThinkingTracesPanel";

const mockSteps = [
  {
    step_type: "reasoning",
    content: "Analyzing the claim structure...",
    agent_id: "architect_agent",
    sequence: 0,
  },
  {
    step_type: "tool_call",
    content: "Searching for evidence...",
    agent_id: "evidence_agent",
    tool_name: "vector_search",
    sequence: 1,
  },
];

describe("ThinkingTracesPanel", () => {
  it("renders thinking steps", () => {
    render(<ThinkingTracesPanel steps={mockSteps} />);
    expect(screen.getByText("Analyzing the claim structure...")).toBeInTheDocument();
    expect(screen.getByText("Searching for evidence...")).toBeInTheDocument();
  });

  it("shows agent names", () => {
    render(<ThinkingTracesPanel steps={mockSteps} />);
    expect(screen.getByText("architect")).toBeInTheDocument();
    expect(screen.getByText("evidence")).toBeInTheDocument();
  });

  it("renders empty state when no steps", () => {
    render(<ThinkingTracesPanel steps={[]} />);
    expect(screen.getByText("Waiting for agent activity...")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/studio && npm test -- --testPathPattern=ThinkingTracesPanel`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```tsx
// apps/studio/src/components/hud/ThinkingTracesPanel.tsx
"use client";

import { useEffect, useRef } from "react";

interface ThinkingStep {
  step_type: string;
  content: string;
  agent_id: string;
  tool_name?: string;
  tool_args?: Record<string, unknown>;
  duration_ms?: number;
  sequence: number;
}

const AGENT_COLORS: Record<string, string> = {
  problem_framer: "text-blue-400 border-blue-400",
  architect_agent: "text-cyan-400 border-cyan-400",
  evidence_agent: "text-green-400 border-green-400",
  critic_agent: "text-orange-400 border-orange-400",
  judge_agent: "text-purple-400 border-purple-400",
  synthesizer_agent: "text-emerald-400 border-emerald-400",
};

const STEP_TYPE_LABELS: Record<string, string> = {
  reasoning: "THINKING",
  tool_call: "ACTION",
  tool_result: "RESULT",
  observation: "OBSERVE",
};

function formatAgentName(agentId: string): string {
  return agentId.replace("_agent", "").replace("_", " ");
}

interface ThinkingTracesPanelProps {
  steps: ThinkingStep[];
}

export function ThinkingTracesPanel({ steps }: ThinkingTracesPanelProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [steps]);

  return (
    <div className="glass-panel flex flex-col h-64">
      <div className="flex items-center justify-between px-3 py-2 border-b border-white/5">
        <span className="text-[10px] uppercase tracking-widest text-white/50">
          Thinking Traces
        </span>
        <span className="text-[10px] text-white/30 bg-white/5 px-1.5 py-0.5 rounded">
          {steps.length}
        </span>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 py-2 space-y-2">
        {steps.length === 0 ? (
          <div className="text-[10px] text-white/30 text-center py-4">
            Waiting for agent activity...
          </div>
        ) : (
          steps.map((step, i) => (
            <div
              key={i}
              className={`border-l-2 pl-2 py-1 ${AGENT_COLORS[step.agent_id] || "text-white/50 border-white/20"}`}
            >
              <div className="flex items-center gap-2 mb-0.5">
                <span className="text-[9px] font-mono uppercase opacity-60">
                  {formatAgentName(step.agent_id)}
                </span>
                <span className="text-[8px] px-1 py-0 rounded bg-white/5 text-white/40">
                  {STEP_TYPE_LABELS[step.step_type] || step.step_type}
                </span>
              </div>
              <p className="text-[10px] text-white/70 leading-relaxed line-clamp-3">
                {step.content}
              </p>
              {step.tool_name && (
                <span className="text-[8px] text-white/30 font-mono">
                  {step.tool_name}
                </span>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/studio && npm test -- --testPathPattern=ThinkingTracesPanel`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/studio/src/components/hud/ThinkingTracesPanel.tsx apps/studio/src/components/hud/__tests__/ThinkingTracesPanel.test.tsx
git commit -m "feat: add ThinkingTracesPanel component for live agent reasoning visualization"
```

---

### Task 10: Parse Thinking Steps in SSE Hook

**Files:**
- Modify: `apps/studio/src/hooks/useSSE.ts`
- Modify: `apps/studio/src/lib/types.ts`

**Interfaces:**
- Consumes: SSE events from API
- Produces: `ThinkingStep[]` array in hook state

- [ ] **Step 1: Add ThinkingStep type to types.ts**

```typescript
// apps/studio/src/lib/types.ts
// Add after existing types:

export interface ThinkingStep {
  step_type: string;
  content: string;
  agent_id: string;
  tool_name?: string;
  tool_args?: Record<string, unknown>;
  duration_ms?: number;
  sequence: number;
}
```

- [ ] **Step 2: Update useSSE hook to extract thinking steps**

```typescript
// apps/studio/src/hooks/useSSE.ts
// Add to the hook's state:

const [thinkingSteps, setThinkingSteps] = useState<ThinkingStep[]>([]);

// In the event handler, add:
if (parsed.type === "agent_started" || parsed.type === "tool_called" || parsed.type === "tool_result") {
  const payload = parsed.payload as Record<string, unknown>;
  if (payload.thinking_steps && Array.isArray(payload.thinking_steps)) {
    setThinkingSteps(prev => [...prev, ...payload.thinking_steps as ThinkingStep[]]);
  }
}

// Return thinkingSteps from the hook:
return { events, connected, thinkingSteps };
```

- [ ] **Step 3: Commit**

```bash
git add apps/studio/src/hooks/useSSE.ts apps/studio/src/lib/types.ts
git commit -m "feat: parse thinking steps from SSE events in useSSE hook"
```

---

## Phase 3: Agent Detail Popover

### Task 11: Create AgentPopover Component

**Files:**
- Create: `apps/studio/src/components/three/AgentPopover.tsx`

**Interfaces:**
- Consumes: Agent data, claims, objections, events
- Produces: Floating popover positioned near clicked avatar

- [ ] **Step 1: Write the failing test**

```tsx
// apps/studio/src/components/three/__tests__/AgentPopover.test.tsx
import { render, screen } from "@testing-library/react";
import { AgentPopover } from "../AgentPopover";

const mockAgent = {
  id: "architect_agent",
  name: "Architect",
  description: "Proposes architectural decisions",
  role: "architect",
};

const mockClaims = [
  {
    id: "c1",
    text: "We should adopt microservices",
    status: "accepted",
    confidence: 0.85,
    author_agent_id: "architect_agent",
  },
];

describe("AgentPopover", () => {
  it("renders agent name and description", () => {
    render(
      <AgentPopover
        agent={mockAgent}
        claims={mockClaims}
        objections={[]}
        events={[]}
        onClose={() => {}}
      />
    );
    expect(screen.getByText("Architect")).toBeInTheDocument();
    expect(screen.getByText("Proposes architectural decisions")).toBeInTheDocument();
  });

  it("shows claims count", () => {
    render(
      <AgentPopover
        agent={mockAgent}
        claims={mockClaims}
        objections={[]}
        events={[]}
        onClose={() => {}}
      />
    );
    expect(screen.getByText("1")).toBeInTheDocument();
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/studio && npm test -- --testPathPattern=AgentPopover`
Expected: FAIL

- [ ] **Step 3: Write minimal implementation**

```tsx
// apps/studio/src/components/three/AgentPopover.tsx
"use client";

import { useState } from "react";

interface AgentInfo {
  id: string;
  name: string;
  description: string;
  role: string;
}

interface Claim {
  id: string;
  text: string;
  status: string;
  confidence: number;
  author_agent_id: string;
}

interface Objection {
  id: string;
  target_claim_id: string;
  reason: string;
  severity: string;
  author_agent_id: string;
}

interface AgentPopoverProps {
  agent: AgentInfo;
  claims: Claim[];
  objections: Objection[];
  events: Array<{ type: string; agent_id?: string; created_at: string }>;
  onClose: () => void;
}

type Tab = "claims" | "objections" | "activity";

const STATUS_COLORS: Record<string, string> = {
  accepted: "bg-emerald-500/20 text-emerald-400",
  rejected: "bg-red-500/20 text-red-400",
  proposed: "bg-gray-500/20 text-gray-400",
  challenged: "bg-amber-500/20 text-amber-400",
  supported: "bg-green-500/20 text-green-400",
  uncertain: "bg-yellow-500/20 text-yellow-400",
};

const SEVERITY_COLORS: Record<string, string> = {
  critical: "bg-red-500/20 text-red-400",
  high: "bg-orange-500/20 text-orange-400",
  medium: "bg-yellow-500/20 text-yellow-400",
  low: "bg-gray-500/20 text-gray-400",
};

export function AgentPopover({
  agent,
  claims,
  objections,
  events,
  onClose,
}: AgentPopoverProps) {
  const [activeTab, setActiveTab] = useState<Tab>("claims");

  const agentClaims = claims.filter(c => c.author_agent_id === agent.id);
  const agentObjections = objections.filter(o => o.author_agent_id === agent.id);
  const agentEvents = events.filter(e => e.agent_id === agent.id);

  return (
    <div className="absolute top-4 right-4 w-80 glass-panel z-50 animate-in fade-in">
      <div className="flex items-center justify-between px-4 py-3 border-b border-white/5">
        <div>
          <h3 className="text-sm font-medium text-white">{agent.name}</h3>
          <p className="text-[10px] text-white/50">{agent.description}</p>
        </div>
        <button
          onClick={onClose}
          className="text-white/30 hover:text-white/70 text-xs"
        >
          x
        </button>
      </div>

      <div className="flex border-b border-white/5">
        {(["claims", "objections", "activity"] as Tab[]).map(tab => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`flex-1 py-2 text-[10px] uppercase tracking-wider ${
              activeTab === tab
                ? "text-white border-b-2 border-cyan-400"
                : "text-white/30 hover:text-white/50"
            }`}
          >
            {tab} ({tab === "claims" ? agentClaims.length : tab === "objections" ? agentObjections.length : agentEvents.length})
          </button>
        ))}
      </div>

      <div className="max-h-64 overflow-y-auto p-3">
        {activeTab === "claims" && (
          <div className="space-y-2">
            {agentClaims.length === 0 ? (
              <p className="text-[10px] text-white/30 text-center py-4">No claims yet</p>
            ) : (
              agentClaims.map(claim => (
                <div key={claim.id} className="p-2 rounded bg-white/5">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`text-[8px] px-1 py-0 rounded ${STATUS_COLORS[claim.status] || ""}`}>
                      {claim.status}
                    </span>
                    <span className="text-[9px] text-white/40">
                      {Math.round(claim.confidence * 100)}%
                    </span>
                  </div>
                  <p className="text-[10px] text-white/70 line-clamp-2">{claim.text}</p>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "objections" && (
          <div className="space-y-2">
            {agentObjections.length === 0 ? (
              <p className="text-[10px] text-white/30 text-center py-4">No objections raised</p>
            ) : (
              agentObjections.map(obj => (
                <div key={obj.id} className="p-2 rounded bg-white/5">
                  <span className={`text-[8px] px-1 py-0 rounded ${SEVERITY_COLORS[obj.severity] || ""}`}>
                    {obj.severity}
                  </span>
                  <p className="text-[10px] text-white/70 mt-1 line-clamp-2">{obj.reason}</p>
                </div>
              ))
            )}
          </div>
        )}

        {activeTab === "activity" && (
          <div className="space-y-1">
            {agentEvents.length === 0 ? (
              <p className="text-[10px] text-white/30 text-center py-4">No activity yet</p>
            ) : (
              agentEvents.map((event, i) => (
                <div key={i} className="flex items-center gap-2 py-1">
                  <span className="text-[8px] text-white/30 font-mono">{event.type}</span>
                  <span className="text-[8px] text-white/20">
                    {new Date(event.created_at).toLocaleTimeString()}
                  </span>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/studio && npm test -- --testPathPattern=AgentPopover`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add apps/studio/src/components/three/AgentPopover.tsx apps/studio/src/components/three/__tests__/AgentPopover.test.tsx
git commit -m "feat: add AgentPopover component for agent detail inspection"
```

---

### Task 12: Add Click Handler to AgentAvatar

**Files:**
- Modify: `apps/studio/src/components/three/AgentAvatar.tsx`
- Modify: `apps/studio/src/components/three/Workspace.tsx`

**Interfaces:**
- Consumes: `onClick` callback from Workspace
- Produces: Clickable agent avatars that trigger popover

- [ ] **Step 1: Add onClick prop to AgentAvatar**

```tsx
// apps/studio/src/components/three/AgentAvatar.tsx
// Modify interface:

interface AgentAvatarProps {
  position: [number, number, number];
  agentId: string;
  agentName: string;
  role: string;
  isActive: boolean;
  isSpeaking: boolean;
  onClick?: (agentId: string) => void;
}

// In the component, add click handler to the mesh:
<mesh
  onClick={(e) => {
    e.stopPropagation();
    onClick?.(agentId);
  }}
  // ... existing props
>
```

- [ ] **Step 2: Manage selected agent state in Workspace**

```tsx
// apps/studio/src/components/three/Workspace.tsx
// Add state:

const [selectedAgentId, setSelectedAgentId] = useState<string | null>(null);

// Pass to AgentAvatar:
<AgentAvatar
  {...config}
  isActive={agentStates[config.agentId]?.isActive || false}
  isSpeaking={agentStates[config.agentId]?.isSpeaking || false}
  onClick={setSelectedAgentId}
/>

// Render AgentPopover when agent is selected:
{selectedAgentId && (
  <AgentPopover
    agent={agentConfigs.find(a => a.agentId === selectedAgentId)!}
    claims={claims}
    objections={objections}
    events={events}
    onClose={() => setSelectedAgentId(null)}
  />
)}
```

- [ ] **Step 3: Commit**

```bash
git add apps/studio/src/components/three/AgentAvatar.tsx apps/studio/src/components/three/Workspace.tsx
git commit -m "feat: add click-to-inspect interaction on agent avatars"
```

---

## Phase 4: Layout Polish + Documentation

### Task 13: Integrate New Panels into Run Detail Page

**Files:**
- Modify: `apps/studio/src/app/runs/[runId]/page.tsx`

**Interfaces:**
- Consumes: `ThinkingTracesPanel`, `AgentPopover`, thinking steps from SSE
- Produces: Updated layout with all panels integrated

- [ ] **Step 1: Update run detail page layout**

```tsx
// apps/studio/src/app/runs/[runId]/page.tsx
// Add imports:
import { ThinkingTracesPanel } from "@/components/hud/ThinkingTracesPanel";

// In the component, destructure thinkingSteps from useSSE:
const { events, connected, thinkingSteps } = useSSE(runId);

// Update layout to include ThinkingTracesPanel:
<div className="flex h-[calc(100vh-3.5rem)]">
  {/* Left sidebar */}
  <div className="w-72 flex flex-col border-r border-white/5">
    <ControlsPanel phase={phase} round={round} />
    <MiniTimeline events={events} />
    <ThinkingTracesPanel steps={thinkingSteps} />
  </div>

  {/* 3D Workspace */}
  <div className="flex-1 relative">
    <Workspace events={events} phase={phase} round={round} />
  </div>

  {/* Right sidebar */}
  <div className="w-72 border-l border-white/5">
    <ClaimsSidebar claims={claims} />
  </div>
</div>
```

- [ ] **Step 2: Commit**

```bash
git add apps/studio/src/app/runs/[runId]/page.tsx
git commit -m "feat: integrate ThinkingTracesPanel into run detail page layout"
```

---

### Task 14: Write SGLang Setup Documentation

**Files:**
- Create: `docs/getting-started/sglang-setup.md`
- Create: `docs/getting-started/local-model-guide.md`

**Interfaces:**
- Consumes: SGLang configuration from Task 1-4
- Produces: Setup guides for users

- [ ] **Step 1: Create SGLang setup guide**

```markdown
# SGLang Setup Guide

## Prerequisites

- Python >=3.11
- NVIDIA GPU with >=4GB VRAM
- NVIDIA Container Toolkit (for Docker GPU passthrough)

## Quick Start (Docker)

```bash
# Start all services with SGLang
docker compose --profile sglang up -d

# Wait for model download (~1.3GB)
docker logs -f mctagents-sglang

# Open Studio
open http://localhost:3000
```

## Manual Setup

### Install SGLang

```bash
pip install sglang[all]
```

### Download Model

```bash
huggingface-cli download Qwen/Qwen3-1.7B --local-dir ./models/Qwen3-1.7B
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

## VRAM Optimization

| Setting | Default | Low VRAM (<4GB) |
|---------|---------|-----------------|
| `--context-length` | 4096 | 2048 |
| `--mem-fraction-static` | 0.7 | 0.5 |
| `--quantization` | none | awq or gptq |

## Troubleshooting

### GPU out of memory
- Reduce `--context-length` to 2048
- Reduce `--mem-fraction-static` to 0.5
- Use a smaller model (Qwen3-0.5B)

### Slow inference
- Ensure CUDA is properly installed
- Check `nvidia-smi` for GPU utilization
- Reduce context length
```

- [ ] **Step 2: Create local model guide**

```markdown
# Local Model Guide

## Model Options for <4GB VRAM

| Model | Size | VRAM | Quality | Speed |
|-------|------|------|---------|-------|
| Qwen3-0.5B-Q4_K_M | 0.4GB | <1GB | Basic | Fast |
| Qwen3-1.7B-Q4_K_M | 1.3GB | <2GB | Good | Medium |
| Qwen3-4B-Q4_K_M | 2.5GB | <3GB | Better | Slower |

## Recommended Configuration

For 4GB VRAM:
- Primary model: Qwen3-1.7B-Q4_K_M
- Embedding: nomic-embed-text (274MB)
- Total VRAM: ~2GB (safe margin)

## Environment Variables

```bash
SGLANG_BASE_URL=http://localhost:30000
SGLANG_MODEL=Qwen/Qwen3-1.7B
DEFAULT_CHAT_MODEL=Qwen/Qwen3-1.7B
DEFAULT_REASONING_MODEL=Qwen/Qwen3-1.7B
DEFAULT_EMBEDDING_MODEL=nomic-embed-text
```
```

- [ ] **Step 3: Commit**

```bash
git add docs/getting-started/
git commit -m "docs: add SGLang setup and local model optimization guides"
```

---

### Task 15: Update README.md

**Files:**
- Modify: `README.md`

**Interfaces:**
- Consumes: All previous tasks
- Produces: Updated README with SGLang instructions

- [ ] **Step 1: Update README quick start section**

```markdown
## Quick Start

### Prerequisites
- Docker + Docker Compose
- NVIDIA GPU with >=4GB VRAM (optional, CPU fallback available)

### With SGLang (Recommended for <4GB VRAM)

```bash
git clone <repo-url> && cd mCTAgents
cp .env.example .env
docker compose --profile sglang up -d
# Wait for model download, then open http://localhost:3000
```

### With Ollama (Default)

```bash
git clone <repo-url> && cd mCTAgents
cp .env.example .env
make dev
# Pull models: ollama pull qwen2.5:7b ollama pull nomic-embed-text
# Open http://localhost:3000
```
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: update README with SGLang quick start instructions"
```

---

## Phase 5: Testing and Verification

### Task 16: Run Full Test Suite

**Files:**
- None (verification only)

- [ ] **Step 1: Run Python tests**

Run: `cd services/reasoning-engine && python -m pytest tests/unit/ -v`
Expected: All tests PASS

- [ ] **Step 2: Run TypeScript tests**

Run: `cd apps/studio && npm test`
Expected: All tests PASS

- [ ] **Step 3: Run linting**

```bash
cd services/reasoning-engine && ruff check .
cd apps/studio && npm run lint
```
Expected: No errors

- [ ] **Step 4: Run type checking**

```bash
cd services/reasoning-engine && mypy .
cd apps/studio && npm run typecheck
```
Expected: No errors

- [ ] **Step 5: Verify Docker Compose starts**

Run: `docker compose --profile sglang up -d`
Wait 60 seconds for SGLang to download model and start.
Run: `curl http://localhost:30000/v1/models`
Expected: Response with Qwen3-1.7B model listed

- [ ] **Step 6: Verify Studio loads**

Open: `http://localhost:3000`
Expected: Landing page loads without errors

- [ ] **Step 7: Create a test run**

1. Click "Start New Session"
2. Enter: "Should we adopt microservices architecture?"
3. Click "Start Reasoning"
4. Observe: 3D avatars animate, thinking traces appear in left panel
5. Click an agent avatar: popover shows claims/objections/activity
6. Wait for completion: Final answer panel appears at bottom

- [ ] **Step 8: Commit final state**

```bash
git add -A
git commit -m "feat: complete SGLang integration and UI/UX subagent enhancement"
```

---

## Summary

| Phase | Tasks | Estimated Time |
|-------|-------|---------------|
| 1: SGLang Integration | Tasks 1-4 | 2-3 hours |
| 2: Thinking Traces | Tasks 5-10 | 3-4 hours |
| 3: Agent Popover | Tasks 11-12 | 2-3 hours |
| 4: Layout + Docs | Tasks 13-15 | 1-2 hours |
| 5: Testing | Task 16 | 1 hour |
| **Total** | **16 tasks** | **9-13 hours** |
