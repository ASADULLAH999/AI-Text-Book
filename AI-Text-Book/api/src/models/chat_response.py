"""Chat response models for API endpoints."""

from pydantic import BaseModel, Field
from typing import List
from enum import Enum
from .chat_request import AnswerMode


class ConfidenceLevel(str, Enum):
    """Confidence level for citation."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Source(BaseModel):
    """Citation source with metadata."""

    chunk_id: str = Field(..., description="Unique chunk identifier")
    chapter: str = Field(..., description="Source chapter")
    section: str = Field(..., description="Source section")
    title: str = Field(..., description="Heading title")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)"
    )
    confidence_level: ConfidenceLevel = Field(
        ..., description="Human-readable confidence level"
    )
    excerpt: str = Field(
        ..., max_length=500, description="Text excerpt from chunk (max 500 chars)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "chunk_id": "chunk_4589",
                "chapter": "Chapter 3",
                "section": "Section 2.1",
                "title": "Neural Network Training",
                "confidence": 0.92,
                "confidence_level": "high",
                "excerpt": "Backpropagation computes gradients by applying the chain rule...",
            }
        }
    }


class ResponseMetadata(BaseModel):
    """Metadata about the response generation."""

    request_id: str = Field(
        ..., description="Unique request identifier for tracing"
    )
    latency_ms: int = Field(
        ..., ge=0, description="Total response time in milliseconds"
    )
    chunks_retrieved: int = Field(
        ..., ge=0, description="Number of chunks retrieved from vector search"
    )
    chunks_used: int = Field(
        ..., ge=0, description="Number of chunks used in final answer generation"
    )
    model: str = Field(
        default="gpt-4-turbo", description="LLM model used for generation"
    )
    embeddings_model: str = Field(
        default="text-embedding-3-small", description="Embedding model used"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "request_id": "req_xyz789",
                "latency_ms": 1234,
                "chunks_retrieved": 5,
                "chunks_used": 2,
                "model": "gpt-4-turbo",
                "embeddings_model": "text-embedding-3-small",
            }
        }
    }


class ChatResponse(BaseModel):
    """Response from chat endpoint."""

    answer: str = Field(..., min_length=1, description="Generated answer text")
    mode: AnswerMode = Field(..., description="Mode used to generate answer")
    sources: List[Source] = Field(
        default=[],
        description="Citation sources (empty if mode=general_knowledge)",
    )
    metadata: ResponseMetadata = Field(
        ..., description="Response metadata for monitoring"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "answer": "Backpropagation is a supervised learning algorithm used to train neural networks by computing gradients of the loss function with respect to network weights. The algorithm propagates errors backward through the network layers, allowing efficient optimization of weights using gradient descent.",
                "mode": "book_only",
                "sources": [
                    {
                        "chunk_id": "chunk_4589",
                        "chapter": "Chapter 3",
                        "section": "Section 2.1",
                        "title": "Neural Network Training",
                        "confidence": 0.92,
                        "confidence_level": "high",
                        "excerpt": "Backpropagation computes gradients by applying the chain rule to propagate errors backward through network layers...",
                    },
                    {
                        "chunk_id": "chunk_4612",
                        "chapter": "Chapter 3",
                        "section": "Section 2.3",
                        "title": "Gradient Descent Optimization",
                        "confidence": 0.78,
                        "confidence_level": "medium",
                        "excerpt": "Gradient descent uses backpropagation gradients to iteratively update weights in the direction that minimizes loss...",
                    },
                ],
                "metadata": {
                    "request_id": "req_xyz789",
                    "latency_ms": 1234,
                    "chunks_retrieved": 5,
                    "chunks_used": 2,
                    "model": "gpt-4-turbo",
                    "embeddings_model": "text-embedding-3-small",
                },
            }
        }
    }
