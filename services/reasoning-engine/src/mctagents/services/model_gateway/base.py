from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import AsyncIterator


@dataclass
class ChatMessage:
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class ChatResponse:
    content: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class EmbeddingResponse:
    embeddings: list[list[float]] = field(default_factory=list)
    model: str = ""


class ModelProvider(ABC):
    @abstractmethod
    async def chat(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        json_mode: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> ChatResponse: ...

    @abstractmethod
    async def chat_stream(
        self,
        messages: list[ChatMessage],
        model: str | None = None,
        json_mode: bool = False,
    ) -> AsyncIterator[str]: ...

    @abstractmethod
    async def embed(
        self,
        texts: list[str],
        model: str | None = None,
    ) -> EmbeddingResponse: ...

    @abstractmethod
    async def health(self) -> dict: ...

    @abstractmethod
    async def available_models(self) -> list[str]: ...
