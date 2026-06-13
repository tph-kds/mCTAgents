"""Configuration for the Evidence Service loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with defaults suitable for local Docker Compose dev."""

    model_config = {"env_prefix": "", "env_file": ".env", "extra": "ignore"}

    # Server
    host: str = "0.0.0.0"
    port: int = 8001
    log_level: str = "debug"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Embedding model (via Ollama)
    ollama_base_url: str = "http://localhost:11434"
    embedding_model: str = "nomic-embed-text"
    embedding_dim: int = 768

    # Ingestion
    chunk_size_tokens: int = 600
    overlap_tokens: int = 80

    # Search
    default_top_k: int = 5
    max_top_k: int = 50

    # Storage
    upload_dir: str = "/tmp/evidence-service/uploads"


settings = Settings()
