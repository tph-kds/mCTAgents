import os
from dataclasses import dataclass, field

from pydantic_settings import BaseSettings


class ModelGatewayConfig(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    default_chat_model: str = "qwen2.5:7b"
    default_reasoning_model: str = "deepseek-r1:7b"
    default_embedding_model: str = "nomic-embed-text"
    provider_timeout: float = 60.0
    max_retries: int = 3

    model_config = {"env_prefix": "MODEL_GATEWAY_"}


@dataclass
class SGLangConfig:
    """Configuration for SGLang model provider."""

    base_url: str = field(
        default_factory=lambda: os.getenv(
            "SGLANG_BASE_URL", "http://localhost:30000",
        ),
    )
    model: str = field(
        default_factory=lambda: os.getenv(
            "SGLANG_MODEL", "Qwen/Qwen3-1.7B",
        ),
    )
    context_length: int = field(
        default_factory=lambda: int(
            os.getenv("SGLANG_CONTEXT_LENGTH", "4096"),
        ),
    )
    api_key: str = field(
        default_factory=lambda: os.getenv("SGLANG_API_KEY", ""),
    )

    @classmethod
    def from_env(cls) -> "SGLangConfig":
        return cls()
