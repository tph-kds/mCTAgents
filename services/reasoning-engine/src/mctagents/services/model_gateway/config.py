from pydantic_settings import BaseSettings


class ModelGatewayConfig(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    default_chat_model: str = "qwen2.5:7b"
    default_reasoning_model: str = "deepseek-r1:7b"
    default_embedding_model: str = "nomic-embed-text"
    provider_timeout: float = 60.0
    max_retries: int = 3

    model_config = {"env_prefix": "MODEL_GATEWAY_"}


class SGLangConfig(BaseSettings):
    """Configuration for SGLang model provider."""

    base_url: str = "http://localhost:30000"
    model: str = "Qwen/Qwen3-1.7B"
    context_length: int = 4096

    model_config = {"env_prefix": "SGLANG_"}

    @classmethod
    def from_env(cls) -> "SGLangConfig":
        return cls()
