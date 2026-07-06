import logging

import httpx

logger = logging.getLogger(__name__)


class EvidenceServiceError(Exception):
    """Raised when the evidence-service returns an error."""


class EvidenceService:
    """Client for the evidence-service HTTP API."""

    def __init__(self, base_url: str = "http://localhost:8001") -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self._client.aclose()

    async def search(
        self,
        query: str,
        run_id: str | None = None,
        top_k: int = 5,
    ) -> list[dict]:
        """Search for evidence related to a query."""
        try:
            resp = await self._client.post(
                f"{self.base_url}/v1/search",
                json={"query": query, "run_id": run_id, "top_k": top_k},
            )
            resp.raise_for_status()
            return resp.json().get("results", [])
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Evidence search failed: %s %s", exc.response.status_code, exc.response.text,
            )
            raise EvidenceServiceError(
                f"Search returned {exc.response.status_code}",
            ) from exc
        except httpx.RequestError as exc:
            logger.error("Evidence search connection error: %s", exc)
            raise EvidenceServiceError(
                f"Could not reach evidence-service at {self.base_url}",
            ) from exc

    async def upload_document(
        self, filename: str, content: bytes, content_type: str,
    ) -> dict:
        """Upload a document for indexing."""
        try:
            resp = await self._client.post(
                f"{self.base_url}/v1/documents",
                files={"file": (filename, content, content_type)},
            )
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            logger.error(
                "Document upload failed: %s %s",
                exc.response.status_code,
                exc.response.text,
            )
            raise EvidenceServiceError(
                f"Upload returned {exc.response.status_code}",
            ) from exc
        except httpx.RequestError as exc:
            logger.error("Document upload connection error: %s", exc)
            raise EvidenceServiceError(
                f"Could not reach evidence-service at {self.base_url}",
            ) from exc

    async def health(self) -> dict:
        """Check evidence-service health."""
        try:
            resp = await self._client.get(f"{self.base_url}/health")
            resp.raise_for_status()
            return resp.json()
        except httpx.RequestError as exc:
            logger.error("Evidence health check failed: %s", exc)
            return {"status": "unreachable", "error": str(exc)}
