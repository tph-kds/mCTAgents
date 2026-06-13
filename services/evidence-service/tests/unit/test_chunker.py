"""Tests for the document chunker."""

import pytest
from mctagents.ingestion.chunker import DocumentChunker
from mctagents.ingestion.parser import ContentBlock


@pytest.fixture
def chunker():
    return DocumentChunker(chunk_size_tokens=20, overlap_tokens=5)


def _make_block(text: str, block_type: str = "paragraph", page: int | None = None) -> ContentBlock:
    return ContentBlock(text=text, type=block_type, page=page)


class TestDocumentChunker:
    def test_empty_input(self, chunker):
        assert chunker.chunk([]) == []

    def test_single_block(self, chunker):
        blocks = [_make_block("Hello world")]
        chunks = chunker.chunk(blocks)
        assert len(chunks) == 1
        assert chunks[0].text == "Hello world"

    def test_heading_starts_new_chunk(self, chunker):
        blocks = [
            _make_block("Content before heading", "paragraph"),
            _make_block("New Section", "heading"),
            _make_block("Content after heading", "paragraph"),
        ]
        chunks = chunker.chunk(blocks)
        assert len(chunks) >= 2
        assert chunks[0].heading is None or chunks[0].heading != "New Section"

    def test_chunk_respects_size_limit(self):
        small_chunker = DocumentChunker(chunk_size_tokens=5, overlap_tokens=2)
        blocks = [
            _make_block("word1 word2 word3"),
            _make_block("word4 word5 word6"),
            _make_block("word7 word8 word9"),
        ]
        chunks = small_chunker.chunk(blocks)
        for chunk in chunks:
            assert chunk.token_count <= 7  # some tolerance for overlap

    def test_chunks_have_indices(self, chunker):
        blocks = [_make_block("A"), _make_block("B"), _make_block("C")]
        chunks = chunker.chunk(blocks)
        for i, chunk in enumerate(chunks):
            assert chunk.index == i

    def test_page_tracking(self, chunker):
        blocks = [
            _make_block("Page 1 content", page=1),
            _make_block("Page 2 content", page=2),
        ]
        chunks = chunker.chunk(blocks)
        assert len(chunks) > 0
