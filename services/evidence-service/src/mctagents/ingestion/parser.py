"""Document parser supporting PDF, DOCX, Markdown, and plain text."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ContentBlock:
    """A parsed block of content from a document."""

    text: str
    type: str  # "text", "heading"
    page: int | None = None


class DocumentParser:
    """Parses various document formats into structured content blocks."""

    def parse(self, file_path: Path) -> list[ContentBlock]:
        """Parse a document file into a list of content blocks.

        Args:
            file_path: Path to the document file.

        Returns:
            List of ContentBlock objects.

        Raises:
            ValueError: If the file type is not supported.
            FileNotFoundError: If the file does not exist.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"Document not found: {file_path}")

        ext = file_path.suffix.lower()
        logger.info("parsing_document", path=str(file_path), extension=ext)

        if ext == ".pdf":
            return self._parse_pdf(file_path)
        if ext in (".docx", ".doc"):
            return self._parse_docx(file_path)
        if ext in (".md", ".markdown"):
            return self._parse_markdown(file_path)
        if ext in (".txt", ".text"):
            return self._parse_text(file_path)
        raise ValueError(f"Unsupported file type: {ext}")

    def _parse_pdf(self, path: Path) -> list[ContentBlock]:
        """Parse a PDF file using PyMuPDF (fitz)."""
        try:
            import fitz
        except ImportError:
            logger.error("pymupdf_not_installed")
            raise RuntimeError(
                "PyMuPDF is required for PDF parsing. Install with: pip install pymupdf",
            ) from None

        blocks: list[ContentBlock] = []
        doc = fitz.open(str(path))
        try:
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text()
                for line in text.split("\n"):
                    line = line.strip()
                    if line:
                        blocks.append(
                            ContentBlock(text=line, type="text", page=page_num + 1),
                        )
        finally:
            doc.close()

        logger.info("pdf_parsed", path=str(path), blocks=len(blocks))
        return blocks

    def _parse_docx(self, path: Path) -> list[ContentBlock]:
        """Parse a DOCX file using python-docx."""
        try:
            from docx import Document
        except ImportError:
            logger.error("python_docx_not_installed")
            raise RuntimeError(
                "python-docx is required for DOCX parsing. "
                "Install with: pip install python-docx",
            ) from None

        doc = Document(str(path))
        blocks: list[ContentBlock] = []
        for para in doc.paragraphs:
            if para.text.strip():
                block_type = (
                    "heading" if para.style.name.startswith("Heading") else "text"
                )
                blocks.append(ContentBlock(text=para.text.strip(), type=block_type))

        logger.info("docx_parsed", path=str(path), blocks=len(blocks))
        return blocks

    def _parse_markdown(self, path: Path) -> list[ContentBlock]:
        """Parse a Markdown file with simple heading detection."""
        content = path.read_text(encoding="utf-8")
        blocks: list[ContentBlock] = []
        for line in content.split("\n"):
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                blocks.append(
                    ContentBlock(text=line.lstrip("#").strip(), type="heading"),
                )
            else:
                blocks.append(ContentBlock(text=line, type="text"))

        logger.info("markdown_parsed", path=str(path), blocks=len(blocks))
        return blocks

    def _parse_text(self, path: Path) -> list[ContentBlock]:
        """Parse a plain text file."""
        content = path.read_text(encoding="utf-8")
        blocks = [
            ContentBlock(text=line.strip(), type="text")
            for line in content.split("\n")
            if line.strip()
        ]

        logger.info("text_parsed", path=str(path), blocks=len(blocks))
        return blocks
