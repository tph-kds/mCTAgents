# Evidence Service

Python service for document ingestion, vector search, and evidence scoring.

## Overview

The evidence service handles document processing, embedding generation, vector storage (Qdrant), and evidence reliability scoring.

## Architecture

```
src/mctagents/
├── api/             FastAPI REST API
├── ingestion/       Document parser, chunker, pipeline
├── retrieval/       Qdrant vector store integration
└── scoring/         Evidence reliability scorer
```

## Supported Formats

- PDF (via PyMuPDF)
- DOCX (via python-docx)
- Markdown
- Plain text

## Development

```bash
pip install -e ".[dev]"
pytest tests/ -v
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/v1/search` | Vector search for evidence |
| `POST` | `/v1/documents` | Upload and ingest a document |
| `GET` | `/v1/documents/{id}` | Get document info |
| `DELETE` | `/v1/documents/{id}` | Delete a document |
| `POST` | `/v1/score` | Score evidence reliability |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_HOST` | `localhost` | Qdrant server host |
| `QDRANT_PORT` | `6333` | Qdrant server port |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama for embeddings |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model name |
| `EMBEDDING_DIM` | `768` | Embedding dimension |
| `CHUNK_SIZE_TOKENS` | `600` | Max tokens per chunk |
| `OVERLAP_TOKENS` | `80` | Token overlap between chunks |
