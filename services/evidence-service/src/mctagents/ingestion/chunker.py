"""Document chunker that splits parsed content into embeddable chunks."""

from __future__ import annotations

from dataclasses import dataclass

import structlog

from mctagents.ingestion.parser import ContentBlock

logger = structlog.get_logger(__name__)


@dataclass
class DocumentChunk:
    """A chunk of text ready for embedding and storage."""

    text: str
    heading: str | None
    page: int | None
    section: str | None
    token_count: int
    index: int


class DocumentChunker:
    """Splits parsed content blocks into overlapping chunks for embedding.

    Args:
        chunk_size_tokens: Maximum tokens per chunk.
        overlap_tokens: Number of tokens to overlap between chunks.
    """

    def __init__(
        self, chunk_size_tokens: int = 600, overlap_tokens: int = 80,
    ) -> None:
        self.chunk_size = chunk_size_tokens
        self.overlap = overlap_tokens

    def chunk(self, blocks: list[ContentBlock]) -> list[DocumentChunk]:
        """Split content blocks into overlapping chunks.

        Headings always start a new chunk. When the token limit is reached,
        the current chunk is finalized and the last few blocks are kept as
        overlap for the next chunk.

        Args:
            blocks: List of parsed content blocks.

        Returns:
            List of DocumentChunk objects.
        """
        if not blocks:
            return []

        chunks: list[DocumentChunk] = []
        current_texts: list[str] = []
        current_tokens = 0
        current_heading: str | None = None
        current_page: int | None = None

        for block in blocks:
            block_tokens = self._count_tokens(block.text)

            # Headings always force a new chunk
            if block.type == "heading":
                if current_texts:
                    chunks.append(
                        self._make_chunk(
                            " ".join(current_texts),
                            current_heading,
                            current_page,
                            len(chunks),
                        ),
                    )
                    current_texts = []
                    current_tokens = 0
                current_heading = block.text

            # Check if adding this block would exceed the chunk size
            if current_tokens + block_tokens > self.chunk_size:
                if current_texts:
                    chunks.append(
                        self._make_chunk(
                            " ".join(current_texts),
                            current_heading,
                            current_page,
                            len(chunks),
                        ),
                    )
                    # Keep overlap from the end of the current chunk
                    overlap_text = (
                        " ".join(current_texts[-2:])
                        if len(current_texts) > 1
                        else ""
                    )
                    current_texts = [overlap_text] if overlap_text else []
                    current_tokens = self._count_tokens(overlap_text)

            current_texts.append(block.text)
            current_tokens += block_tokens
            if block.page is not None:
                current_page = block.page

        # Finalize remaining text
        if current_texts:
            chunks.append(
                self._make_chunk(
                    " ".join(current_texts),
                    current_heading,
                    current_page,
                    len(chunks),
                ),
            )

        logger.info("document_chunked", total_chunks=len(chunks))
        return chunks

    @staticmethod
    def _count_tokens(text: str) -> int:
        """Estimate token count using whitespace splitting."""
        return len(text.split())

    @staticmethod
    def _make_chunk(
        text: str,
        heading: str | None,
        page: int | None,
        index: int,
    ) -> DocumentChunk:
        """Create a DocumentChunk from accumulated text."""
        return DocumentChunk(
            text=text,
            heading=heading,
            page=page,
            section=heading,
            token_count=len(text.split()),
            index=index,
        )
