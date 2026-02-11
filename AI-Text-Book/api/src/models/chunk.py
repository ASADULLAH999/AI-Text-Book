"""Chunk data models for textbook content."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class ChunkMetadata(BaseModel):
    """Metadata for a textbook chunk."""

    chapter: str = Field(
        ..., description="Chapter name (e.g., 'Chapter 3: Neural Networks')"
    )
    section: str = Field(
        ..., description="Section identifier (e.g., '3.2 Backpropagation')"
    )
    page_number: Optional[int] = Field(
        None, description="Page number in textbook (if applicable)"
    )
    heading: str = Field(
        ..., description="Heading hierarchy (e.g., '3.2.1 Gradient Descent')"
    )
    word_count: int = Field(..., ge=0, description="Word count in chunk")
    token_count: int = Field(
        ..., ge=0, le=1024, description="Token count (512-1024 range)"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when chunk was created",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "chapter": "Chapter 3: Neural Networks",
                "section": "3.2 Backpropagation",
                "page_number": 45,
                "heading": "3.2.1 Gradient Descent Algorithm",
                "word_count": 187,
                "token_count": 523,
                "created_at": "2026-02-05T10:30:00Z",
            }
        }
    }


class Chunk(BaseModel):
    """Textbook chunk with embedding and metadata."""

    chunk_id: str = Field(..., description="Unique identifier (e.g., 'chunk_4589')")
    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="Raw chunk text content",
    )
    embedding: List[float] = Field(
        ...,
        min_length=1536,
        max_length=1536,
        description="1536-dim vector from OpenAI text-embedding-3-small",
    )
    metadata: ChunkMetadata = Field(
        ..., description="Chunk metadata for filtering and citation"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "chunk_id": "chunk_4589",
                "text": "Backpropagation is a supervised learning algorithm used to train neural networks. It computes gradients of the loss function with respect to network weights...",
                "embedding": [0.023, -0.142, 0.089],  # Truncated for example
                "metadata": {
                    "chapter": "Chapter 3: Neural Networks",
                    "section": "3.2 Backpropagation",
                    "page_number": 45,
                    "heading": "3.2.1 Gradient Descent Algorithm",
                    "word_count": 187,
                    "token_count": 523,
                    "created_at": "2026-02-05T10:30:00Z",
                },
            }
        }
    }
