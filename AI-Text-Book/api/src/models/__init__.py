"""Data models for RAG chatbot API."""

from .chunk import Chunk, ChunkMetadata
from .chat_request import ChatRequest, AnswerMode, QueryContext, QueryOptions
from .chat_response import ChatResponse, Source, ResponseMetadata, ConfidenceLevel
from .citation import Citation
from .errors import ErrorResponse, ErrorDetail, ErrorCode

__all__ = [
    # Chunk models
    "Chunk",
    "ChunkMetadata",
    # Request models
    "ChatRequest",
    "AnswerMode",
    "QueryContext",
    "QueryOptions",
    # Response models
    "ChatResponse",
    "Source",
    "ResponseMetadata",
    "ConfidenceLevel",
    # Citation models
    "Citation",
    # Error models
    "ErrorResponse",
    "ErrorDetail",
    "ErrorCode",
]
