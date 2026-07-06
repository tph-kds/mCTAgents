from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from .enums import DocumentStatus


class Document(BaseModel):
    id: str = Field(..., description="Unique identifier (UUID)")
    tenant_id: str = Field(
        default="00000000-0000-0000-0000-000000000000",
        description="Tenant UUID",
    )
    filename: str = Field(..., description="Original filename")
    content_type: str | None = Field(default=None, max_length=128)
    size_bytes: int | None = Field(default=None, ge=0)
    status: DocumentStatus = DocumentStatus.UPLOADED
    chunk_count: int = Field(default=0, ge=0)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)


class DocumentChunk(BaseModel):
    id: str = Field(..., description="Unique identifier (UUID)")
    document_id: str = Field(..., description="Reference to parent document (UUID)")
    chunk_index: int = Field(..., ge=0, description="Position within the document")
    content: str = Field(..., description="Text content of the chunk")
    heading: str | None = None
    page: int | None = Field(default=None, ge=1)
    section: str | None = None
    token_count: int | None = Field(default=None, ge=0)
    embedding_id: str | None = Field(
        default=None, max_length=128, description="Reference to vector embedding",
    )
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
