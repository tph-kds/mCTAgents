from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import uuid
import httpx
import logging

logger = logging.getLogger(__name__)

from mctagents.engine.reasoning_engine import ReasoningEngine
from mctagents.services.event_service import EventService
from mctagents.services.storage_service import StorageService
from mctagents.services.model_gateway.router import ModelRouter, ModelPreset, TaskType
from mctagents.services.model_gateway.ollama import OllamaProvider
from mctagents.services.model_gateway.openai_compatible import OpenAICompatibleProvider
from mctagents.services.model_gateway.config import SGLangConfig

_reasoning_engine: ReasoningEngine | None = None
_event_service: EventService | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _reasoning_engine, _event_service
    import os

    ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    db_url = os.getenv("DATABASE_URL", "postgres://mctagents:devpassword@localhost:5432/mctagents")

    sglang_config = SGLangConfig.from_env()
    model_provider = None
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{sglang_config.base_url}/v1/models", timeout=5.0)
            if resp.status_code == 200:
                model_provider = OpenAICompatibleProvider(
                    base_url=sglang_config.base_url,
                    api_key="not-needed",
                )
                logger.info("Using SGLang provider", extra={"base_url": sglang_config.base_url})
    except Exception:
        pass

    if model_provider is None:
        logger.warning("SGLang not available, falling back to Ollama")
        model_provider = OllamaProvider(base_url=ollama_url)

    router = ModelRouter(
        providers={"default": model_provider},
        preset=ModelPreset(
            chat_model=os.getenv("DEFAULT_CHAT_MODEL", "qwen2.5:7b"),
            reasoning_model=os.getenv("DEFAULT_REASONING_MODEL", "deepseek-r1:7b"),
            embedding_model=os.getenv("DEFAULT_EMBEDDING_MODEL", "nomic-embed-text"),
        ),
    )

    _event_service = EventService()
    storage = StorageService(db_url)
    await storage.connect()

    _reasoning_engine = ReasoningEngine(
        model_router=router,
        event_service=_event_service,
        storage_service=storage,
    )

    yield

    await storage.close()


app = FastAPI(title="mCTAgents Reasoning Engine", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CreateRunRequest(BaseModel):
    problem: str
    mode: str = "balanced_reasoning"
    evidence_policy: str = "required_for_major_claims"
    budget: dict | None = None


class RunResponse(BaseModel):
    run_id: str
    status: str
    events_url: str


@app.get("/health")
async def health():
    return {"status": "ok", "service": "reasoning-engine"}


@app.post("/v1/runs", response_model=RunResponse)
async def create_run(request: CreateRunRequest):
    run_id = f"run_{uuid.uuid4().hex[:12]}"

    await _reasoning_engine._storage.save_run(run_id, "queued", request.mode)

    policy = request.budget or {"max_rounds": 2, "max_tokens": 12000, "max_model_calls": 16}
    asyncio.create_task(_run_reasoning(run_id, request.problem, policy))

    return RunResponse(run_id=run_id, status="queued", events_url=f"/v1/runs/{run_id}/events")


async def _run_reasoning(run_id: str, problem: str, policy: dict):
    try:
        await _reasoning_engine.run(run_id, problem, policy)
    except Exception as e:
        await _event_service.emit(run_id, "run_failed", {"error": str(e)})
        await _reasoning_engine._storage.update_run_status(run_id, "failed")


@app.get("/v1/runs/{run_id}")
async def get_run(run_id: str):
    run = await _reasoning_engine._storage.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@app.get("/v1/runs/{run_id}/events")
async def stream_events(run_id: str):
    from fastapi.responses import StreamingResponse
    import json

    queue = _event_service.subscribe(run_id)

    async def event_generator():
        try:
            for event in _event_service.get_events(run_id):
                data = json.dumps({
                    "event_id": event.event_id, "run_id": event.run_id,
                    "type": event.type, "sequence": event.sequence,
                    "agent_id": event.agent_id, "payload": event.payload,
                    "created_at": event.created_at.isoformat(),
                })
                yield f"event: {event.type}\ndata: {data}\n\n"

            while True:
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    data = json.dumps({
                        "event_id": event.event_id, "run_id": event.run_id,
                        "type": event.type, "sequence": event.sequence,
                        "agent_id": event.agent_id, "payload": event.payload,
                        "created_at": event.created_at.isoformat(),
                    })
                    yield f"event: {event.type}\ndata: {data}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            _event_service.unsubscribe(run_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive", "X-Accel-Buffering": "no"},
    )


@app.post("/v1/runs/{run_id}/cancel")
async def cancel_run(run_id: str):
    await _reasoning_engine._storage.update_run_status(run_id, "cancelled")
    await _event_service.emit(run_id, "run_cancelled", {})
    return {"status": "cancelled"}


@app.get("/v1/runs/{run_id}/claims")
async def list_claims(run_id: str):
    claims = await _reasoning_engine._storage.get_claims(run_id)
    return {"claims": claims}


@app.get("/v1/runs/{run_id}/evidence")
async def list_evidence(run_id: str):
    evidence = await _reasoning_engine._storage.get_evidence(run_id)
    return {"evidence": evidence}
