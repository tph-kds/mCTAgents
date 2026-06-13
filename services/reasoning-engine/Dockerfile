FROM python:3.11-slim AS base
WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]" 2>/dev/null || pip install --no-cache-dir fastapi uvicorn pydantic pydantic-settings sqlalchemy asyncpg alembic httpx redis sse-starlette python-dotenv structlog opentelemetry-api opentelemetry-sdk

FROM base AS development
COPY . .
CMD ["uvicorn", "mctagents.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS production
COPY . .
CMD ["uvicorn", "mctagents.api.app:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
