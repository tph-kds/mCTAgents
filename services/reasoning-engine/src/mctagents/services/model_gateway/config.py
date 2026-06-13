from pydantic_settings import BaseSettings


class ModelGatewayConfig(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    default_chat_model: str = "qwen2.5:7b"
    default_reasoning_model: str = "deepseek-r1:7b"
    default_embedding_model: str = "nomic-embed-text"
    provider_timeout: float = 60.0
    max_retries: int = 3

    model_config = {"env_prefix": "MODEL_GATEWAY_"}
