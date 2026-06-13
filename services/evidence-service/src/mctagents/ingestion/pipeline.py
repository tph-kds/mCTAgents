"""Full ingestion pipeline: parse -> chunk -> embed -> store."""

from __future__ import annotations

from pathlib import Path

import structlog

from mctagents.ingestion.chunker import DocumentChunker
from mctagents.ingestion.parser import DocumentParser
from mctagents.retrieval.vector_store import VectorStore

logger = structlog.get_logger(__name__)


class EmbeddingResult:
    """Result from an embedding service call."""

    def __init__(self, embeddings: list[list[float]]) -> None:
        self.embeddings = embeddings


class IngestionPipeline:
    """Orchestrates document ingestion from file to vector store.

    Args:
        vector_store: VectorStore instance for storing embeddings.
        embedding_service: Service that produces embeddings from text.
        chunk_size_tokens: Maximum tokens per chunk.
        overlap_tokens: Number of tokens to overlap between chunks.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_service: object,
        chunk_size_tokens: int = 600,
        overlap_tokens: int = 80,
    ) -> None:
        self.parser = DocumentParser()
        self.chunker = DocumentChunker(
            chunk_size_tokens=chunk_size_tokens,
            overlap_tokens=overlap_tokens,
        )
        self.vector_store = vector_store
        self.embedding_service = embedding_service

    async def ingest(self, document_id: str, file_path: Path) -> dict:
        """Ingest a document into the vector store.

        Steps:
            1. Parse the document into content blocks.
            2. Chunk the blocks into overlapping segments.
            3. Generate embeddings for all chunks.
            4. Upsert chunks and embeddings into the vector store.

        Args:
            document_id: Unique identifier for this document.
            file_path: Path to the document file.

        Returns:
            Dict with document_id and chunk_count.
        """
        logger.info(
            "ingestion_started",
            document_id=document_id,
            file_path=str(file_path),
        )

        # Step 1: Parse
        blocks = self.parser.parse(file_path)
        if not blocks:
            logger.warning("empty_document", document_id=document_id)
            return {"document_id": document_id, "chunk_count": 0}

        # Step 2: Chunk
        chunks = self.chunker.chunk(blocks)
        if not chunks:
            logger.warning("no_chunks_produced", document_id=document_id)
            return {"document_id": document_id, "chunk_count": 0}

        # Step 3: Embed
        texts = [c.text for c in chunks]
        embedding_result = await self.embedding_service.embed(texts)

        if len(embedding_result.embeddings) != len(chunks):
            logger.error(
                "embedding_count_mismatch",
                expected=len(chunks),
                received=len(embedding_result.embeddings),
            )
            raise RuntimeError(
                f"Embedding count mismatch: expected {len(chunks)}, "
                f"got {len(embedding_result.embeddings)}",
            )

        # Step 4: Store
        ids = [f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        payloads = [
            {
                "document_id": document_id,
                "chunk_index": i,
                "content": c.text,
                "heading": c.heading,
                "page": c.page,
                "section": c.section,
                "token_count": c.token_count,
            }
            for i, c in enumerate(chunks)
        ]

        await self.vector_store.upsert(
            collection="documents",
            ids=ids,
            vectors=embedding_result.embeddings,
            payloads=payloads,
        )

        logger.info(
            "ingestion_completed",
            document_id=document_id,
            chunk_count=len(chunks),
        )

        return {"document_id": document_id, "chunk_count": len(chunks)}
