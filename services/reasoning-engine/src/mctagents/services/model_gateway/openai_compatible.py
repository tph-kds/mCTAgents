import json
from collections.abc import AsyncIterator

import httpx

from mctagents.services.model_gateway.base import (
    ChatMessage,
    ChatResponse,
    EmbeddingResponse,
    ModelProvider,
)


class OpenAICompatibleProvider(ModelProvider):
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 60.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=timeout)

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

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
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": False,
        }
        if model:
            payload["model"] = model
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        resp = await self.client.post(
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            headers=self._headers(),
        )
        resp.raise_for_status()
        data = resp.json()

        choice = data["choices"][0]
        usage = data.get("usage", {})

        return ChatResponse(
            content=choice["message"]["content"],
            model=data.get("model", model or "unknown"),
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            total_tokens=usage.get("total_tokens", 0),
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
            payload["response_format"] = {"type": "json_object"}

        async with self.client.stream(
            "POST",
            f"{self.base_url}/v1/chat/completions",
            json=payload,
            headers=self._headers(),
        ) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload_str = line[len("data: "):]
                if payload_str.strip() == "[DONE]":
                    break
                chunk = json.loads(payload_str)
                delta = chunk["choices"][0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    yield content

    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> EmbeddingResponse:
        payload: dict = {
            "input": texts,
        }
        if model:
            payload["model"] = model

        resp = await self.client.post(
            f"{self.base_url}/v1/embeddings",
            json=payload,
            headers=self._headers(),
        )
        resp.raise_for_status()
        data = resp.json()

        embeddings = [item["embedding"] for item in data["data"]]
        used_model = data.get("model", model or "unknown")

        return EmbeddingResponse(embeddings=embeddings, model=used_model)

    async def health(self) -> dict:
        try:
            resp = await self.client.get(
                f"{self.base_url}/v1/models",
                headers=self._headers(),
            )
            resp.raise_for_status()
            return {"status": "healthy", "provider": "openai-compatible", "models": resp.json()}
        except httpx.HTTPError as e:
            return {"status": "unhealthy", "provider": "openai-compatible", "error": str(e)}

    async def available_models(self) -> list[str]:
        resp = await self.client.get(
            f"{self.base_url}/v1/models",
            headers=self._headers(),
        )
        resp.raise_for_status()
        data = resp.json()
        return [m["id"] for m in data.get("data", [])]
