"""Tests for the document parser."""

import pytest
from pathlib import Path
from mctagents.ingestion.parser import DocumentParser, ContentBlock


@pytest.fixture
def parser():
    return DocumentParser()


class TestDocumentParser:
    def test_parse_markdown(self, parser, tmp_path):
        md_file = tmp_path / "test.md"
        md_file.write_text("# Heading 1\n\nSome content here.\n\n## Heading 2\n\nMore content.\n")
        blocks = parser.parse(md_file)
        assert len(blocks) > 0
        assert any(b.type == "heading" for b in blocks)
        assert any(b.text == "Heading 1" for b in blocks)

    def test_parse_empty_markdown(self, parser, tmp_path):
        md_file = tmp_path / "empty.md"
        md_file.write_text("")
        blocks = parser.parse(md_file)
        assert blocks == []

    def test_parse_plain_text(self, parser, tmp_path):
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("Line one.\nLine two.\nLine three.\n")
        blocks = parser.parse(txt_file)
        assert len(blocks) > 0

    def test_parse_unsupported_format(self, parser, tmp_path):
        xyz_file = tmp_path / "test.xyz"
        xyz_file.write_text("content")
        with pytest.raises(ValueError, match="Unsupported"):
            parser.parse(xyz_file)
