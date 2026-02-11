"""Chat request models for API endpoints."""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class AnswerMode(str, Enum):
    """Answering mode for the chatbot."""

    BOOK_ONLY = "book_only"
    SELECTED_TEXT = "selected_text"
    GENERAL_KNOWLEDGE = "general_knowledge"


class QueryContext(BaseModel):
    """Context for the user query."""

    selected_text: Optional[str] = Field(
        None,
        max_length=5000,
        description="User-selected text for Selected-Text mode",
    )
    chapter_filter: Optional[str] = Field(
        None,
        description="Restrict search to specific chapter (e.g., 'Chapter 3')",
    )
    session_id: Optional[str] = Field(
        None, description="Session identifier for analytics tracking"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "selected_text": None,
                "chapter_filter": None,
                "session_id": "sess_abc123",
            }
        }
    }


class QueryOptions(BaseModel):
    """Configuration options for retrieval."""

    top_k: int = Field(
        default=10,
        ge=5,
        le=20,
        description="Number of chunks to retrieve before reranking",
    )
    similarity_threshold: float = Field(
        default=0.7,
        ge=0.5,
        le=1.0,
        description="Minimum cosine similarity for chunk inclusion",
    )
    include_citations: bool = Field(
        default=True, description="Include citation metadata in response"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "top_k": 10,
                "similarity_threshold": 0.7,
                "include_citations": True,
            }
        }
    }


class ChatRequest(BaseModel):
    """Request for chat endpoint."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="User question (max 500 characters)",
    )
    mode: AnswerMode = Field(
        default=AnswerMode.BOOK_ONLY,
        description="Answering mode (default: book_only)",
    )
    context: Optional[QueryContext] = Field(
        default=None, description="Additional query context"
    )
    options: Optional[QueryOptions] = Field(
        default=None, description="Retrieval configuration options"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "What is backpropagation?",
                "mode": "book_only",
                "context": {
                    "selected_text": None,
                    "chapter_filter": None,
                    "session_id": "sess_abc123",
                },
                "options": {
                    "top_k": 10,
                    "similarity_threshold": 0.7,
                    "include_citations": True,
                },
            }
        }
    }
