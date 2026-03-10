"""
Chat API Endpoint
Handles chat requests for the RAG chatbot.
"""

import os
import sys

# Ensure api/src/ is on the path so sibling packages (services, db) resolve.
_API_SRC_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _API_SRC_DIR not in sys.path:
    sys.path.insert(0, _API_SRC_DIR)

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, AsyncGenerator
from datetime import datetime
import logging
import json
import asyncio

from services.rag.orchestrator import get_rag_orchestrator
from services.modes import enforce_mode_boundary, VALID_MODES, ModeBoundaryError
from services.prompts.tone_modifiers import DEFAULT_TONE, is_valid_tone

logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/v1", tags=["chat"])


# Request/Response Models
class ChatMessage(BaseModel):
    """Chat message model."""

    role: str = Field(..., description="Message role (user or assistant)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default=None, description="Message timestamp")


class Citation(BaseModel):
    """Citation model."""

    id: str = Field(..., description="Citation ID")
    number: int = Field(..., description="Citation number")
    chunk_id: str = Field(..., description="Source chunk ID")
    text: str = Field(..., description="Cited text")
    score: float = Field(..., description="Relevance score")
    source: Dict[str, Any] = Field(..., description="Source metadata")
    preview: str = Field(..., description="Preview snippet")


class ChatRequest(BaseModel):
    """Chat request model."""

    message: str = Field(
        ..., min_length=1, max_length=500, description="User message (max 500 chars)"
    )
    mode: Optional[str] = Field(
        default="book_only",
        description="Chat mode (book_only, selected_text, general_knowledge)",
    )
    # T086 [US4] — Tone parameter. Affects language style only; never alters citations.
    tone: Optional[str] = Field(
        default=None,
        description=(
            "Response tone (neutral, academic, beginner_friendly, concise, detailed). "
            "Affects language style only — citations and accuracy are unchanged."
        ),
    )
    selection_context: Optional[Dict[str, Any]] = Field(
        default=None,
        description=(
            "Required when mode='selected_text'. "
            "Dict with 'selected_text' (str) and optional 'source_hint' (dict)."
        ),
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None, description="Optional metadata filters"
    )
    conversation_id: Optional[str] = Field(
        default=None, description="Conversation ID for context"
    )


class ChatResponse(BaseModel):
    """Chat response model."""

    message: str = Field(..., description="Assistant response")
    citations: List[Dict[str, Any]] = Field(
        default=[], description="Source citations"
    )
    refused: bool = Field(default=False, description="Whether request was refused")
    metadata: Dict[str, Any] = Field(default={}, description="Response metadata")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Response timestamp"
    )


class ErrorResponse(BaseModel):
    """Error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Error details")
    status_code: int = Field(..., description="HTTP status code")


# API Endpoints
@router.post(
    "/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    summary="Send a chat message",
    description="Send a question to the RAG chatbot and receive an answer with citations",
)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat message and return a response with citations.

    Args:
        request: Chat request with message and options

    Returns:
        ChatResponse with answer and citations

    Raises:
        HTTPException: If request validation fails or processing errors occur
    """
    try:
        logger.info(f"Received chat request: {request.message[:100]}...")

        # T072 [US3] — Validate mode via boundary enforcement
        try:
            validated_mode = enforce_mode_boundary(request.mode or "book_only")
        except ModeBoundaryError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

        # T086 [US4] — Resolve and validate tone parameter
        raw_tone = request.tone or DEFAULT_TONE.value
        if not is_valid_tone(raw_tone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tone '{raw_tone}'. "
                       f"Valid values: neutral, academic, beginner_friendly, concise, detailed.",
            )
        validated_tone = raw_tone

        # Get orchestrator for the validated mode
        orchestrator = get_rag_orchestrator(mode=validated_mode)

        # Process query
        result = await orchestrator.process_query(
            query=request.message,
            mode=validated_mode,
            filters=request.filters,
            metadata={
                "conversation_id": request.conversation_id,
                "timestamp": datetime.utcnow().isoformat(),
                "tone": validated_tone,
            },
            selection_context=request.selection_context,
        )

        # Build response
        response = ChatResponse(
            message=result.get("message", ""),
            citations=result.get("citations", []),
            refused=result.get("refused", False),
            metadata=result.get("metadata", {}),
            timestamp=datetime.utcnow(),
        )

        logger.info(
            f"Chat request processed successfully "
            f"(refused={response.refused}, citations={len(response.citations)})"
        )

        return response

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}",
        )


def _get_vector_size(vectors: Any) -> Any:
    """Extract vector size from single VectorParams or Dict[str, VectorParams]."""
    if hasattr(vectors, "size"):
        return vectors.size
    if isinstance(vectors, dict) and vectors:
        first = next(iter(vectors.values()))
        return first.size if hasattr(first, "size") else "unknown"
    return "unknown"


@router.get(
    "/debug/qdrant",
    summary="Debug Qdrant retrieval",
    description="Test Qdrant connection, collection info, and a sample retrieval",
)
async def debug_qdrant(query: str = "What is ROS2?") -> Dict[str, Any]:
    """Debug endpoint: shows collection stats and retrieval results for a test query."""
    from db.qdrant_client import qdrant_client
    from services.rag.embedding import get_query_embedding_service

    result: Dict[str, Any] = {}

    # 1. Collection info
    try:
        client = qdrant_client.get_client()
        collection_name = qdrant_client.get_collection_name()
        info = client.get_collection(collection_name)
        result["collection"] = {
            "name": collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "vector_size": _get_vector_size(info.config.params.vectors),
            "status": str(info.status),
        }
    except Exception as e:
        result["collection"] = {"error": str(e)}

    # 2. Embed query
    try:
        embedding_service = get_query_embedding_service()
        embedding = await embedding_service.embed_query(query)
        result["embedding"] = {
            "query": query,
            "dimensions": len(embedding),
            "sample": embedding[:5],
        }
    except Exception as e:
        result["embedding"] = {"error": str(e)}

    # 3. Raw Qdrant search (low threshold)
    try:
        chunks = await qdrant_client.search(
            query_vector=embedding,
            top_k=5,
            score_threshold=0.1,
        )
        result["retrieval"] = {
            "chunks_found": len(chunks),
            "chunks": [
                {
                    "chunk_id": c.get("chunk_id"),
                    "score": round(c.get("score", 0), 4),
                    "text_preview": (c.get("text") or "")[:120],
                    "metadata": c.get("metadata"),
                }
                for c in chunks
            ],
        }
    except Exception as e:
        result["retrieval"] = {"error": str(e)}

    return result


@router.get(
    "/health",
    summary="Health check",
    description="Check if the chat API is healthy",
)
async def health() -> Dict[str, Any]:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "chat-api",
        "timestamp": datetime.utcnow().isoformat(),
    }


# Streaming Support (T036)
async def stream_chat_response(
    orchestrator,
    query: str,
    mode: str = "book_only",
    filters: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    selection_context: Optional[Dict[str, Any]] = None,
) -> AsyncGenerator[str, None]:
    """
    Stream chat response as Server-Sent Events (SSE).

    Args:
        orchestrator: RAG orchestrator
        query: User query
        filters: Optional metadata filters
        metadata: Optional request metadata

    Yields:
        SSE-formatted response chunks
    """
    try:
        # Send initial event
        yield f"event: start\ndata: {json.dumps({'status': 'processing'})}\n\n"

        # Process query
        result = await orchestrator.process_query(
            query=query,
            mode=mode,
            filters=filters,
            metadata=metadata,
            selection_context=selection_context,
        )

        # Stream the response message (simulate streaming)
        message = result.get("message", "")
        words = message.split()

        for i, word in enumerate(words):
            chunk_data = {
                "type": "message_chunk",
                "content": word + " ",
                "index": i,
            }
            yield f"data: {json.dumps(chunk_data)}\n\n"
            await asyncio.sleep(0.05)  # Simulate streaming delay

        # Send citations
        citations = result.get("citations", [])
        if citations:
            citation_data = {
                "type": "citations",
                "citations": citations,
            }
            yield f"event: citations\ndata: {json.dumps(citation_data)}\n\n"

        # Send metadata — include refused inside the metadata dict so the
        # frontend hook can read it as event.data.metadata.refused
        combined_meta = {
            **result.get("metadata", {}),
            "refused": result.get("refused", False),
        }
        metadata_data = {
            "type": "metadata",
            "metadata": combined_meta,
            "refused": result.get("refused", False),
        }
        yield f"event: metadata\ndata: {json.dumps(metadata_data)}\n\n"

        # Send completion event
        yield f"event: done\ndata: {json.dumps({'status': 'complete'})}\n\n"

    except Exception as e:
        logger.error(f"Error in streaming response: {e}", exc_info=True)
        error_data = {
            "type": "error",
            "error": str(e),
        }
        yield f"event: error\ndata: {json.dumps(error_data)}\n\n"


@router.post(
    "/chat/stream",
    summary="Stream chat response",
    description="Send a question and receive a streaming response with Server-Sent Events (SSE)",
)
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """
    Process a chat message and return a streaming response.

    Args:
        request: Chat request with message and options

    Returns:
        StreamingResponse with SSE events

    Raises:
        HTTPException: If request validation fails
    """
    try:
        logger.info(f"Received streaming chat request: {request.message[:100]}...")

        # T072 [US3] — Validate mode via boundary enforcement
        try:
            validated_mode = enforce_mode_boundary(request.mode or "book_only")
        except ModeBoundaryError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            )

        # T086 [US4] — Resolve and validate tone parameter
        raw_tone = request.tone or DEFAULT_TONE.value
        if not is_valid_tone(raw_tone):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid tone '{raw_tone}'. "
                       f"Valid values: neutral, academic, beginner_friendly, concise, detailed.",
            )

        # Get orchestrator for the validated mode
        orchestrator = get_rag_orchestrator(mode=validated_mode)

        # Return streaming response
        return StreamingResponse(
            stream_chat_response(
                orchestrator=orchestrator,
                query=request.message,
                mode=validated_mode,
                filters=request.filters,
                metadata={
                    "conversation_id": request.conversation_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "tone": raw_tone,
                },
                selection_context=request.selection_context,
            ),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",  # Disable nginx buffering
            },
        )

    except HTTPException:
        raise

    except Exception as e:
        logger.error(f"Error in streaming endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your streaming request: {str(e)}",
        )
