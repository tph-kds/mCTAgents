FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies for PyMuPDF
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy source first (needed for editable install)
COPY src/ src/
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]"

# Development target
FROM base AS development
CMD ["uvicorn", "mctagents.api.app:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]

# Production target
FROM base AS production
RUN pip install --no-cache-dir -e .
CMD ["uvicorn", "mctagents.api.app:app", "--host", "0.0.0.0", "--port", "8001"]
