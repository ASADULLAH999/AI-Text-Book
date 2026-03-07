"""
Message data model for RAG-Powered Textbook Chatbot.

Represents individual messages within a conversation, tracking user queries,
assistant responses, citations, and response metadata.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class Message(BaseModel):
    """
    Message model for conversation persistence.

    Maps to messages table in Postgres database.
    Stores both user queries and assistant responses with full metadata.
    """

    id: str = Field(..., description="UUID primary key")
    conversation_id: str = Field(..., description="Foreign key to conversations table")
    role: str = Field(..., description="Message role: user | assistant")
    content: str = Field(..., description="Message text content")
    mode: str = Field(..., description="Answering mode when message was created")
    tone: Optional[str] = Field(None, description="Response tone: academic | beginner | concise | detailed | neutral")
    action: Optional[str] = Field(None, description="Text action: explain | summarize | examples | elaborate | simplify")
    citations: Optional[List[dict]] = Field(default=None, description="Citations metadata (JSONB array)")
    confidence_score: Optional[float] = Field(None, description="Response confidence score (0.0-1.0)")
    tokens_used: Optional[int] = Field(None, description="Total tokens used for generation")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")
    metadata: Optional[dict] = Field(default=None, description="Additional message metadata (JSONB)")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "660e8400-e29b-41d4-a716-446655440001",
                "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
                "role": "assistant",
                "content": "Photosynthesis is the process by which plants convert light energy into chemical energy...",
                "mode": "book_only",
                "tone": "beginner",
                "action": "explain",
                "citations": [
                    {
                        "chunk_id": "ch3_s21_p2",
                        "chapter": 3,
                        "section": "2.1",
                        "title": "Plant Biology Fundamentals",
                        "confidence": "high",
                        "text_preview": "Photosynthesis occurs in chloroplasts..."
                    }
                ],
                "confidence_score": 0.92,
                "tokens_used": 245,
                "created_at": "2026-02-14T10:35:12Z",
                "metadata": {
                    "retrieval_time_ms": 87,
                    "generation_time_ms": 1423,
                    "chunks_retrieved": 5
                }
            }
        }


class MessageCreate(BaseModel):
    """Request model for creating a new message."""

    conversation_id: str = Field(..., description="Parent conversation ID")
    role: str = Field(..., description="Message role: user | assistant")
    content: str = Field(..., description="Message content")
    mode: str = Field(..., description="Active answering mode")
    tone: Optional[str] = Field(None, description="Response tone")
    action: Optional[str] = Field(None, description="Text action applied")
    citations: Optional[List[dict]] = Field(default=None, description="Citations array")
    confidence_score: Optional[float] = Field(None, description="Confidence score")
    tokens_used: Optional[int] = Field(None, description="Tokens consumed")
    metadata: Optional[dict] = Field(default=None, description="Additional metadata")


class MessageResponse(BaseModel):
    """Response model for message retrieval."""

    id: str
    conversation_id: str
    role: str
    content: str
    mode: str
    tone: Optional[str] = None
    action: Optional[str] = None
    citations: Optional[List[dict]] = None
    confidence_score: Optional[float] = None
    tokens_used: Optional[int] = None
    created_at: datetime
    metadata: Optional[dict] = None
