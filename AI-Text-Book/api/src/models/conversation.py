"""
Conversation data model for RAG-Powered Textbook Chatbot.

Represents a conversation session between a user and the chatbot,
tracking context, mode, and metadata across multiple messages.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Conversation(BaseModel):
    """
    Conversation model for session persistence.

    Maps to conversations table in Postgres database.
    Tracks user sessions, mode selections, and conversation metadata.
    """

    id: str = Field(..., description="UUID primary key")
    user_id: Optional[str] = Field(None, description="User identifier (optional for anonymous)")
    book_id: str = Field(..., description="Textbook identifier")
    chapter_id: Optional[int] = Field(None, description="Current chapter context")
    mode: str = Field(..., description="Active answering mode: book_only | selected_text | general_knowledge")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Conversation creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    status: str = Field(default="active", description="Conversation status: active | completed | abandoned")
    metadata: Optional[dict] = Field(default=None, description="Additional conversation metadata (JSONB)")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "user_12345",
                "book_id": "bio101",
                "chapter_id": 3,
                "mode": "book_only",
                "created_at": "2026-02-14T10:30:00Z",
                "updated_at": "2026-02-14T10:35:00Z",
                "status": "active",
                "metadata": {
                    "session_source": "web",
                    "last_chapter_viewed": 3
                }
            }
        }


class ConversationCreate(BaseModel):
    """Request model for creating a new conversation."""

    user_id: Optional[str] = Field(None, description="User identifier")
    book_id: str = Field(..., description="Textbook identifier")
    chapter_id: Optional[int] = Field(None, description="Starting chapter")
    mode: str = Field(default="book_only", description="Initial answering mode")
    metadata: Optional[dict] = Field(default=None, description="Initial metadata")


class ConversationUpdate(BaseModel):
    """Request model for updating an existing conversation."""

    chapter_id: Optional[int] = Field(None, description="Updated chapter context")
    mode: Optional[str] = Field(None, description="Updated answering mode")
    status: Optional[str] = Field(None, description="Updated status")
    metadata: Optional[dict] = Field(None, description="Updated metadata (merged)")
