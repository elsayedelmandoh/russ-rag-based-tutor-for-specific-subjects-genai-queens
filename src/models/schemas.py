from __future__ import annotations

from enum import Enum
from typing import List, Optional
from uuid import uuid4

from pydantic import BaseModel, Field, validator


class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


class Citation(BaseModel):
    source_document: str
    page_number: Optional[int]
    text_snippet: str
    relevance_score: Optional[float]


class Chunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: f"chunk-{uuid4().hex[:8]}")
    text: str
    source_document: str
    page_number: Optional[int]
    section_heading: Optional[str]
    chunk_index: int = 0
    collection_name: Optional[str]

    @validator("chunk_index")
    def index_non_negative(cls, v):
        if v is None:
            return 0
        if v < 0:
            raise ValueError("chunk_index must be >= 0")
        return v


class Document(BaseModel):
    document_id: str = Field(default_factory=lambda: f"doc-{uuid4().hex[:8]}")
    file_name: str
    collection_name: Optional[str] = None
    total_pages: Optional[int] = None
    status: DocumentStatus = DocumentStatus.PENDING
    error_message: Optional[str] = None
    subject: Optional[str] = None


class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    citations: Optional[List[Citation]] = None
    safety_status: Optional[str] = None


class ConversationSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"sess-{uuid4().hex[:8]}")
    subject: Optional[str] = None
    messages: List[ChatMessage] = Field(default_factory=list)


class Subject(BaseModel):
    name: str
    collection_names: List[str] = Field(default_factory=list)


class RetrievalResult(BaseModel):
    chunk: Chunk
    score: float


class SafetyCheckResult(BaseModel):
    is_safe: bool
    violated_categories: List[str] = Field(default_factory=list)
    raw_response: Optional[str]
