import json
from typing import AsyncIterator

import httpx

from mctagents.services.model_gateway.base import (
    ChatMessage,
    ChatResponse,
    EmbeddingResponse,
    ModelProvider,
)


class OllamaProvider(ModelProvider):
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(timeout=timeout)

    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        json_mode: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> ChatResponse:
        payload: dict = {
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        if model:
            payload["model"] = model
        if json_mode:
            payload["format"] = "json"

        resp = await self.client.post(f"{self.base_url}/api/chat", json=payload)
        resp.raise_for_status()
        data = resp.json()

        return ChatResponse(
            content=data["message"]["content"],
            model=data.get("model", model or "unknown"),
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get("eval_count", 0),
            total_tokens=data.get("prompt_eval_count", 0) + data.get("eval_count", 0),
        )

    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        json_mode: bool = False,
    ) -> AsyncIterator[str]:
        payload: dict = {
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": True,
        }
        if model:
            payload["model"] = model
        if json_mode:
            payload["format"] = "json"

        async with self.client.stream(
            "POST", f"{self.base_url}/api/chat", json=payload
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.strip():
                    continue
                chunk = json.loads(line)
                if "message" in chunk:
                    content = chunk["message"].get("content", "")
                    if content:
                        yield content
                if chunk.get("done", False):
                    break

    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> EmbeddingResponse:
        all_embeddings: list[list[float]] = []
        used_model = model or "nomic-embed-text"

        for text in texts:
            payload: dict = {
                "model": used_model,
                "input": text,
            }
            resp = await self.client.post(f"{self.base_url}/api/embed", json=payload)
            resp.raise_for_status()
            data = resp.json()
            embeddings = data.get("embeddings", [])
            if embeddings:
                all_embeddings.extend(embeddings)

        return EmbeddingResponse(embeddings=all_embeddings, model=used_model)

    async def health(self) -> dict:
        try:
            resp = await self.client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            return {"status": "healthy", "provider": "ollama", "models": resp.json()}
        except httpx.HTTPError as e:
            return {"status": "unhealthy", "provider": "ollama", "error": str(e)}

    async def available_models(self) -> list[str]:
        resp = await self.client.get(f"{self.base_url}/api/tags")
        resp.raise_for_status()
        data = resp.json()
        return [m["name"] for m in data.get("models", [])]
