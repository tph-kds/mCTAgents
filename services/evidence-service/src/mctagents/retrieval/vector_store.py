"""Qdrant vector store integration for document embeddings."""

from __future__ import annotations

import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams

logger = structlog.get_logger(__name__)

# Default embedding dimension for nomic-embed-text via Ollama
DEFAULT_VECTOR_SIZE = 768


class VectorStore:
    """Qdrant-backed vector store for document embeddings.

    Args:
        host: Qdrant server host.
        port: Qdrant server port.
    """

    def __init__(self, host: str = "localhost", port: int = 6333) -> None:
        self._host = host
        self._port = port
        self.client = QdrantClient(host=host, port=port)
        logger.info("vector_store_initialized", host=host, port=port)

    async def ensure_collection(
        self, name: str, vector_size: int = DEFAULT_VECTOR_SIZE,
    ) -> None:
        """Create the collection if it does not already exist.

        Args:
            name: Collection name.
            vector_size: Dimension of embedding vectors.
        """
        collections = self.client.get_collections().collections
        if not any(c.name == name for c in collections):
            self.client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
            )
            logger.info(
                "collection_created",
                name=name,
                vector_size=vector_size,
            )
        else:
            logger.debug("collection_exists", name=name)

    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 10,
        score_threshold: float | None = None,
        query_filter: object | None = None,
    ) -> list[dict]:
        """Search for similar vectors in the collection.

        Args:
            collection: Collection name.
            query_vector: The query embedding vector.
            top_k: Maximum number of results.
            score_threshold: Minimum similarity score.
            query_filter: Optional Qdrant filter.

        Returns:
            List of result dicts with id, score, and payload.
        """
        search_kwargs: dict = {
            "collection_name": collection,
            "query_vector": query_vector,
            "limit": top_k,
        }
        if score_threshold is not None:
            search_kwargs["score_threshold"] = score_threshold
        if query_filter is not None:
            search_kwargs["query_filter"] = query_filter

        results = self.client.search(**search_kwargs)
        hits = [
            {"id": hit.id, "score": hit.score, "payload": hit.payload}
            for hit in results
        ]

        logger.info(
            "vector_search_completed",
            collection=collection,
            top_k=top_k,
            results_count=len(hits),
        )
        return hits

    async def upsert(
        self,
        collection: str,
        ids: list[str],
        vectors: list[list[float]],
        payloads: list[dict],
    ) -> list[str]:
        """Insert or update vectors in the collection.

        Args:
            collection: Collection name.
            ids: Point IDs.
            vectors: Embedding vectors.
            payloads: Metadata payloads for each point.

        Returns:
            The list of upserted IDs.
        """
        if not ids:
            return []

        points = [
            PointStruct(id=ids[i], vector=vectors[i], payload=payloads[i])
            for i in range(len(ids))
        ]
        self.client.upsert(collection_name=collection, points=points)

        logger.info(
            "vectors_upserted",
            collection=collection,
            count=len(ids),
        )
        return ids

    async def delete(self, collection: str, ids: list[str]) -> None:
        """Delete points from the collection.

        Args:
            collection: Collection name.
            ids: Point IDs to delete.
        """
        if not ids:
            return

        self.client.delete(
            collection_name=collection,
            points_selector=ids,
        )
        logger.info("vectors_deleted", collection=collection, count=len(ids))

    async def get_collection_info(self, collection: str) -> dict:
        """Get metadata about a collection.

        Args:
            collection: Collection name.

        Returns:
            Dict with points_count and other collection info.
        """
        info = self.client.get_collection(collection)
        return {
            "name": collection,
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "status": str(info.status),
        }
