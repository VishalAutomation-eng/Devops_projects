"""Pydantic schemas for API IO."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    """User registration payload."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
    """User login payload."""

    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT response."""

    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    """User response."""

    id: int
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentRead(BaseModel):
    """Uploaded document response."""

    id: int
    filename: str
    chunk_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class QuestionRequest(BaseModel):
    """Question payload for RAG."""

    question: str = Field(min_length=3, max_length=2000)
    top_k: int | None = Field(default=None, ge=1, le=10)


class SourceChunk(BaseModel):
    """Retrieved source chunk metadata."""

    document_id: int
    filename: str
    page: int
    score: float
    text: str


class AnswerResponse(BaseModel):
    """RAG answer response."""

    answer: str
    sources: list[SourceChunk]
    token_usage: dict[str, int]
