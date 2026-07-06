"""FastAPI application for the mCTAgents Evidence Service."""

from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel, Field

from mctagents.api.config import settings
from mctagents.ingestion.pipeline import EmbeddingResult, IngestionPipeline
from mctagents.retrieval.vector_store import VectorStore
from mctagents.scoring.reliability import EvidenceReliabilityScorer

logger = structlog.get_logger(__name__)

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Initialize connections on startup, clean up on shutdown."""
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    vs = _get_vector_store()
    await vs.ensure_collection("documents", vector_size=settings.embedding_dim)
    logger.info("evidence_service_started", port=settings.port)

    yield

    logger.info("evidence_service_stopped")


app = FastAPI(
    title="mCTAgents Evidence Service",
    version="0.1.0",
    description="Document ingestion, vector search, and evidence scoring.",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Lazy singletons (created on startup)
# ---------------------------------------------------------------------------

_vector_store: VectorStore | None = None
_pipeline: IngestionPipeline | None = None
_scorer: EvidenceReliabilityScorer | None = None


def _get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore(
            host=settings.qdrant_host, port=settings.qdrant_port,
        )
    return _vector_store


def _get_scorer() -> EvidenceReliabilityScorer:
    global _scorer
    if _scorer is None:
        _scorer = EvidenceReliabilityScorer()
    return _scorer


# ---------------------------------------------------------------------------
# Embedding stub (replace with real Ollama call in production)
# ---------------------------------------------------------------------------


class _OllamaEmbeddingService:
    """Embedding service that calls Ollama's /api/embeddings endpoint."""

    def __init__(self, base_url: str, model: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model

    async def embed(self, texts: list[str]) -> EmbeddingResult:
        """Generate embeddings for a list of texts via Ollama.

        Falls back to random vectors when Ollama is unreachable (for local dev).
        """
        import httpx

        embeddings: list[list[float]] = []
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                for text in texts:
                    resp = await client.post(
                        f"{self._base_url}/api/embeddings",
                        json={"model": self._model, "prompt": text},
                    )
                    resp.raise_for_status()
                    embeddings.append(resp.json()["embedding"])
        except Exception:
            logger.warning(
                "ollama_embedding_fallback",
                model=self._model,
                count=len(texts),
            )
            import random

            embeddings = [
                [random.random() for _ in range(settings.embedding_dim)]
                for _ in texts
            ]

        return EmbeddingResult(embeddings=embeddings)


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class SearchRequest(BaseModel):
    """Request body for vector search."""

    query: str = Field(..., min_length=1, description="Search query text.")
    run_id: str | None = Field(
        default=None, description="Optional run ID to scope results.",
    )
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results.")
    source_type: str | None = Field(
        default=None, description="Filter by source type.",
    )


class SearchHit(BaseModel):
    """A single search result."""

    id: str
    score: float
    content: str
    heading: str | None = None
    page: int | None = None
    document_id: str | None = None
    reliability_score: float | None = None


class SearchResponse(BaseModel):
    """Response body for vector search."""

    results: list[SearchHit]
    query: str
    total: int


class IngestResponse(BaseModel):
    """Response body for document ingestion."""

    document_id: str
    chunk_count: int
    filename: str


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    service: str
    version: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="ok", service="evidence-service", version="0.1.0")


@app.post("/v1/search", response_model=SearchResponse)
async def search(request: SearchRequest) -> SearchResponse:
    """Search the vector store for evidence matching a query."""
    vs = _get_vector_store()
    scorer = _get_scorer()

    # Embed the query
    embedding_svc = _OllamaEmbeddingService(
        settings.ollama_base_url, settings.embedding_model,
    )
    query_embedding = await embedding_svc.embed([request.query])
    query_vector = query_embedding.embeddings[0]

    # Search
    hits = await vs.search(
        collection="documents",
        query_vector=query_vector,
        top_k=request.top_k,
    )

    results: list[SearchHit] = []
    for hit in hits:
        payload = hit.get("payload") or {}
        content = payload.get("content", "")
        source_type = payload.get("source_type", "uploaded_document")

        reliability = scorer.score_from_retrieval(
            source_type=source_type,
            retrieval_score=hit["score"],
        )

        results.append(
            SearchHit(
                id=str(hit["id"]),
                score=hit["score"],
                content=content,
                heading=payload.get("heading"),
                page=payload.get("page"),
                document_id=payload.get("document_id"),
                reliability_score=reliability,
            ),
        )

    return SearchResponse(
        results=results, query=request.query, total=len(results),
    )


@app.post("/v1/documents", response_model=IngestResponse)
async def upload_document(file: UploadFile = File(...)) -> IngestResponse:
    """Upload and ingest a document into the vector store."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    # Validate extension
    allowed_extensions = {".pdf", ".docx", ".doc", ".md", ".markdown", ".txt", ".text"}
    ext = Path(file.filename).suffix.lower()
    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(sorted(allowed_extensions))}",
        )

    # Save uploaded file
    document_id = str(uuid.uuid4())
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    file_path = upload_dir / f"{document_id}{ext}"

    try:
        content = await file.read()
        file_path.write_bytes(content)
    except Exception as exc:
        logger.error("file_save_failed", filename=file.filename)
        raise HTTPException(
            status_code=500, detail="Failed to save uploaded file.",
        ) from exc

    # Ingest
    embedding_svc = _OllamaEmbeddingService(
        settings.ollama_base_url, settings.embedding_model,
    )
    pipeline = IngestionPipeline(
        vector_store=_get_vector_store(),
        embedding_service=embedding_svc,
        chunk_size_tokens=settings.chunk_size_tokens,
        overlap_tokens=settings.overlap_tokens,
    )

    try:
        result = await pipeline.ingest(document_id, file_path)
    except Exception as exc:
        logger.error("ingestion_failed", document_id=document_id)
        raise HTTPException(
            status_code=500, detail="Document ingestion failed.",
        ) from exc

    return IngestResponse(
        document_id=result["document_id"],
        chunk_count=result["chunk_count"],
        filename=file.filename,
    )


@app.get("/v1/documents/{document_id}")
async def get_document_info(document_id: str) -> dict:
    """Get information about an ingested document."""
    vs = _get_vector_store()

    try:
        info = await vs.get_collection_info("documents")
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Failed to query collection.",
        ) from exc

    return {
        "document_id": document_id,
        "collection_info": info,
    }


@app.delete("/v1/documents/{document_id}")
async def delete_document(document_id: str) -> dict:
    """Delete a document's chunks from the vector store."""
    vs = _get_vector_store()

    try:
        from qdrant_client.models import FieldCondition, Filter, MatchValue
        vs.client.delete(
            collection_name="documents",
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    ),
                ],
            ),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500, detail="Failed to delete document.",
        ) from exc

    return {"document_id": document_id, "status": "deleted"}


@app.post("/v1/score", response_model=dict)
async def score_evidence(evidence_item: dict) -> dict:
    """Score an evidence item's reliability."""
    scorer = _get_scorer()
    reliability = scorer.score(evidence_item)
    return {"reliability_score": reliability, "evidence_item": evidence_item}
