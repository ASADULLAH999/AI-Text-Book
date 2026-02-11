# Data Models & Database Schemas

**Feature ID:** 002-rag-chatbot
**Phase:** 1 (Design & Architecture)
**Created:** 2026-02-05
**Status:** Complete

---

## Overview

This document defines all data models, schemas, and database structures for the RAG-powered textbook chatbot. Models are organized into three layers:

1. **Application Models**: Pydantic models for API requests/responses
2. **Vector Database Schema**: Qdrant collection configuration and metadata structure
3. **Relational Database Schema**: Postgres tables for metadata, logs, and analytics

---

## 1. Application Models (Pydantic)

### 1.1 Chunk Model (`api/src/models/chunk.py`)

Represents a semantic chunk of textbook content with embeddings and metadata.

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class ChunkMetadata(BaseModel):
    """Metadata for a textbook chunk."""
    chapter: str = Field(..., description="Chapter name (e.g., 'Chapter 3: Neural Networks')")
    section: str = Field(..., description="Section identifier (e.g., '3.2 Backpropagation')")
    page_number: Optional[int] = Field(None, description="Page number in textbook (if applicable)")
    heading: str = Field(..., description="Heading hierarchy (e.g., '3.2.1 Gradient Descent')")
    word_count: int = Field(..., ge=0, description="Word count in chunk")
    token_count: int = Field(..., ge=0, le=1024, description="Token count (512-1024 range)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp when chunk was created")

class Chunk(BaseModel):
    """Textbook chunk with embedding and metadata."""
    chunk_id: str = Field(..., description="Unique identifier (e.g., 'chunk_4589')")
    text: str = Field(..., min_length=1, max_length=10000, description="Raw chunk text content")
    embedding: List[float] = Field(..., min_items=1536, max_items=1536, description="1536-dim vector from OpenAI text-embedding-3-small")
    metadata: ChunkMetadata = Field(..., description="Chunk metadata for filtering and citation")

    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "chunk_4589",
                "text": "Backpropagation is a supervised learning algorithm used to train neural networks. It computes gradients of the loss function with respect to network weights...",
                "embedding": [0.023, -0.142, 0.089, "... (1536 values total)"],
                "metadata": {
                    "chapter": "Chapter 3: Neural Networks",
                    "section": "3.2 Backpropagation",
                    "page_number": 45,
                    "heading": "3.2.1 Gradient Descent Algorithm",
                    "word_count": 187,
                    "token_count": 523,
                    "created_at": "2026-02-05T10:30:00Z"
                }
            }
        }
```

**Usage**:
- Document ingestion: Create chunks from textbook markdown
- Vector upload: Store chunks + embeddings in Qdrant
- Retrieval: Return chunks from vector search results

---

### 1.2 Chat Request Model (`api/src/models/chat_request.py`)

Request schema for POST /api/v1/chat endpoint.

```python
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
    selected_text: Optional[str] = Field(None, max_length=5000, description="User-selected text for Selected-Text mode")
    chapter_filter: Optional[str] = Field(None, description="Restrict search to specific chapter (e.g., 'Chapter 3')")
    session_id: Optional[str] = Field(None, description="Session identifier for analytics tracking")

class QueryOptions(BaseModel):
    """Configuration options for retrieval."""
    top_k: int = Field(default=10, ge=5, le=20, description="Number of chunks to retrieve before reranking")
    similarity_threshold: float = Field(default=0.7, ge=0.5, le=1.0, description="Minimum cosine similarity for chunk inclusion")
    include_citations: bool = Field(default=True, description="Include citation metadata in response")

class ChatRequest(BaseModel):
    """Request for chat endpoint."""
    query: str = Field(..., min_length=1, max_length=500, description="User question (max 500 characters)")
    mode: AnswerMode = Field(default=AnswerMode.BOOK_ONLY, description="Answering mode (default: book_only)")
    context: Optional[QueryContext] = Field(default=None, description="Additional query context")
    options: Optional[QueryOptions] = Field(default=None, description="Retrieval configuration options")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "What is backpropagation?",
                "mode": "book_only",
                "context": {
                    "selected_text": None,
                    "chapter_filter": None,
                    "session_id": "sess_abc123"
                },
                "options": {
                    "top_k": 10,
                    "similarity_threshold": 0.7,
                    "include_citations": True
                }
            }
        }
```

**Validation Rules**:
- `query`: Required, 1-500 characters (prevents abuse)
- `mode`: Enum validation (prevents invalid modes)
- `selected_text`: Optional, max 5000 characters (Selected-Text mode only)
- `top_k`: Range 5-20 (balances accuracy and latency)
- `similarity_threshold`: Range 0.5-1.0 (prevents irrelevant chunks)

---

### 1.3 Chat Response Model (`api/src/models/chat_response.py`)

Response schema for POST /api/v1/chat endpoint.

```python
from pydantic import BaseModel, Field
from typing import List
from enum import Enum

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
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0.0-1.0)")
    confidence_level: ConfidenceLevel = Field(..., description="Human-readable confidence level")
    excerpt: str = Field(..., max_length=500, description="Text excerpt from chunk (max 500 chars)")

class ResponseMetadata(BaseModel):
    """Metadata about the response generation."""
    request_id: str = Field(..., description="Unique request identifier for tracing")
    latency_ms: int = Field(..., ge=0, description="Total response time in milliseconds")
    chunks_retrieved: int = Field(..., ge=0, description="Number of chunks retrieved from vector search")
    chunks_used: int = Field(..., ge=0, description="Number of chunks used in final answer generation")
    model: str = Field(default="gpt-4-turbo", description="LLM model used for generation")
    embeddings_model: str = Field(default="text-embedding-3-small", description="Embedding model used")

class ChatResponse(BaseModel):
    """Response from chat endpoint."""
    answer: str = Field(..., min_length=1, description="Generated answer text")
    mode: AnswerMode = Field(..., description="Mode used to generate answer")
    sources: List[Source] = Field(default=[], description="Citation sources (empty if mode=general_knowledge)")
    metadata: ResponseMetadata = Field(..., description="Response metadata for monitoring")

    class Config:
        json_schema_extra = {
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
                        "excerpt": "Backpropagation computes gradients by applying the chain rule to propagate errors backward through network layers..."
                    },
                    {
                        "chunk_id": "chunk_4612",
                        "chapter": "Chapter 3",
                        "section": "Section 2.3",
                        "title": "Gradient Descent Optimization",
                        "confidence": 0.78,
                        "confidence_level": "medium",
                        "excerpt": "Gradient descent uses backpropagation gradients to iteratively update weights in the direction that minimizes loss..."
                    }
                ],
                "metadata": {
                    "request_id": "req_xyz789",
                    "latency_ms": 1234,
                    "chunks_retrieved": 5,
                    "chunks_used": 2,
                    "model": "gpt-4-turbo",
                    "embeddings_model": "text-embedding-3-small"
                }
            }
        }
```

**Response Structure**:
- `answer`: Generated answer text (never empty)
- `mode`: Echo the mode used (for UI visual distinction)
- `sources`: Empty array for general_knowledge mode, populated otherwise
- `metadata`: Always included for monitoring and debugging

---

### 1.4 Citation Model (`api/src/models/citation.py`)

Citation validation and confidence scoring model.

```python
from pydantic import BaseModel, Field
from typing import Optional

class Citation(BaseModel):
    """Citation extracted from generated answer."""
    chunk_id: str = Field(..., description="Referenced chunk ID")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score from reranking")
    is_valid: bool = Field(default=True, description="Whether citation passed grounding check")
    validation_error: Optional[str] = Field(None, description="Error message if citation failed validation")

    @property
    def confidence_level(self) -> str:
        """Map confidence score to human-readable level."""
        if self.confidence_score >= 0.8:
            return "high"
        elif self.confidence_score >= 0.6:
            return "medium"
        else:
            return "low"

    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "chunk_4589",
                "confidence_score": 0.92,
                "is_valid": True,
                "validation_error": None
            }
        }
```

**Validation Logic**:
- `confidence_score >= 0.8`: High confidence (green badge in UI)
- `0.6 <= confidence_score < 0.8`: Medium confidence (yellow badge)
- `confidence_score < 0.6`: Low confidence (orange badge, warning)
- `is_valid = False`: Citation failed grounding check (rejected)

---

### 1.5 Error Response Model (`api/src/models/errors.py`)

Standardized error response schema.

```python
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class ErrorCode(str, Enum):
    """Error codes for API responses."""
    RETRIEVAL_FAILED = "RETRIEVAL_FAILED"
    GENERATION_FAILED = "GENERATION_FAILED"
    INVALID_MODE = "INVALID_MODE"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INSUFFICIENT_CONTEXT = "INSUFFICIENT_CONTEXT"
    AMBIGUOUS_QUERY = "AMBIGUOUS_QUERY"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"

class ErrorResponse(BaseModel):
    """Standardized error response."""
    error: ErrorDetail = Field(..., description="Error details")

class ErrorDetail(BaseModel):
    """Detailed error information."""
    code: ErrorCode = Field(..., description="Machine-readable error code")
    message: str = Field(..., description="Human-readable error message")
    details: str = Field(..., description="Additional context about the error")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
    request_id: str = Field(..., description="Request ID for tracing")

    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "RETRIEVAL_FAILED",
                    "message": "No relevant textbook content found",
                    "details": "Query: 'quantum mechanics basics'",
                    "timestamp": "2026-02-05T10:30:00Z",
                    "request_id": "req_abc123"
                }
            }
        }
```

---

## 2. Vector Database Schema (Qdrant)

### 2.1 Collection Configuration

```python
from qdrant_client.http.models import Distance, VectorParams

COLLECTION_NAME = "textbook_chunks"

COLLECTION_CONFIG = {
    "collection_name": COLLECTION_NAME,
    "vectors_config": VectorParams(
        size=1536,  # OpenAI text-embedding-3-small dimensions
        distance=Distance.COSINE  # Cosine similarity for semantic search
    ),
    "optimizers_config": {
        "default_segment_number": 2,  # Performance tuning
        "indexing_threshold": 20000  # HNSW index threshold
    },
    "hnsw_config": {
        "m": 16,  # Number of edges per node (balance accuracy/speed)
        "ef_construct": 100,  # Build-time accuracy
        "full_scan_threshold": 10000  # Switch to exact search for small collections
    }
}
```

### 2.2 Metadata Payload Schema

Every chunk in Qdrant includes a payload with metadata for filtering and citation.

```json
{
  "chunk_id": "chunk_4589",
  "chapter": "Chapter 3: Neural Networks",
  "section": "3.2 Backpropagation",
  "page_number": 45,
  "heading": "3.2.1 Gradient Descent Algorithm",
  "word_count": 187,
  "token_count": 523,
  "created_at": "2026-02-05T10:30:00Z",
  "text": "Backpropagation is a supervised learning algorithm..."
}
```

**Indexed Fields** (for filtering):
- `chapter` (keyword index)
- `section` (keyword index)
- `page_number` (integer index)

**Usage Example**:
```python
# Filter by chapter
results = client.search(
    collection_name=COLLECTION_NAME,
    query_vector=embedding,
    limit=10,
    query_filter={
        "must": [
            {"key": "chapter", "match": {"value": "Chapter 3: Neural Networks"}}
        ]
    }
)
```

---

## 3. Relational Database Schema (Postgres)

### 3.1 `chunk_metadata` Table

Stores chunk metadata for audit trail and citation resolution.

```sql
CREATE TABLE chunk_metadata (
    chunk_id VARCHAR(50) PRIMARY KEY,
    chapter VARCHAR(200) NOT NULL,
    section VARCHAR(200) NOT NULL,
    page_number INTEGER,
    heading VARCHAR(500) NOT NULL,
    word_count INTEGER NOT NULL CHECK (word_count >= 0),
    token_count INTEGER NOT NULL CHECK (token_count BETWEEN 512 AND 1024),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes for fast lookup
    INDEX idx_chapter (chapter),
    INDEX idx_section (section),
    INDEX idx_created_at (created_at)
);

-- Trigger to update updated_at timestamp
CREATE TRIGGER update_chunk_metadata_updated_at
    BEFORE UPDATE ON chunk_metadata
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

**Purpose**:
- Audit trail for chunk provenance
- Citation link resolution (chunk_id → chapter/section/page)
- Analytics on chunk usage patterns

---

### 3.2 `query_logs` Table

Logs every user query for analytics and monitoring.

```sql
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(100) UNIQUE NOT NULL,
    query TEXT NOT NULL,
    mode VARCHAR(50) NOT NULL CHECK (mode IN ('book_only', 'selected_text', 'general_knowledge')),
    latency_ms INTEGER NOT NULL CHECK (latency_ms >= 0),
    chunks_retrieved INTEGER NOT NULL CHECK (chunks_retrieved >= 0),
    chunks_used INTEGER NOT NULL CHECK (chunks_used >= 0),
    user_id VARCHAR(100),  -- Optional, if authentication enabled
    session_id VARCHAR(100),
    chapter_filter VARCHAR(200),
    similarity_threshold DECIMAL(3, 2),
    error_code VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes for analytics queries
    INDEX idx_timestamp (timestamp),
    INDEX idx_mode (mode),
    INDEX idx_user_id (user_id),
    INDEX idx_request_id (request_id)
);
```

**Purpose**:
- Query latency monitoring (p50, p95, p99)
- Mode usage analytics (book_only vs general_knowledge)
- Error rate tracking by error_code
- User behavior analysis

**Sample Query**:
```sql
-- Calculate p95 latency by mode
SELECT
    mode,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_latency_ms
FROM query_logs
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY mode;
```

---

### 3.3 `analytics` Table

Aggregated metrics for monitoring dashboards.

```sql
CREATE TABLE analytics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10, 2) NOT NULL,
    dimensions JSONB,  -- Flexible dimensions (e.g., {"mode": "book_only", "chapter": "Chapter 3"})
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Unique constraint to prevent duplicate metrics
    UNIQUE (date, metric_name, dimensions),

    -- Indexes for fast aggregation
    INDEX idx_date (date),
    INDEX idx_metric_name (metric_name),
    INDEX idx_dimensions_gin (dimensions USING gin)  -- GIN index for JSONB queries
);
```

**Example Metrics**:
```sql
-- Daily query count by mode
INSERT INTO analytics (date, metric_name, metric_value, dimensions)
VALUES ('2026-02-05', 'query_count', 1234, '{"mode": "book_only"}');

-- Average latency
INSERT INTO analytics (date, metric_name, metric_value, dimensions)
VALUES ('2026-02-05', 'avg_latency_ms', 1456, '{"mode": "book_only"}');

-- Citation accuracy (manual sampling)
INSERT INTO analytics (date, metric_name, metric_value, dimensions)
VALUES ('2026-02-05', 'citation_accuracy_pct', 96.5, '{"sample_size": 100}');
```

**Query Example**:
```sql
-- Get weekly trends for citation accuracy
SELECT
    date,
    metric_value AS citation_accuracy_pct
FROM analytics
WHERE
    metric_name = 'citation_accuracy_pct'
    AND date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date;
```

---

## 4. Relationship Diagram

```
┌─────────────────────────────────────────────────────┐
│                 Application Layer                    │
│  ┌──────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │ ChatRequest  │  │ChatResponse │  │   Chunk    │ │
│  └──────────────┘  └─────────────┘  └────────────┘ │
└─────────────────────────────────────────────────────┘
                        │
                        │ API Contract
                        │
┌─────────────────────────────────────────────────────┐
│                   Storage Layer                      │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │      Qdrant Vector Database                │    │
│  │  Collection: textbook_chunks               │    │
│  │  - Vectors: 1536-dim embeddings            │    │
│  │  - Payload: chunk metadata                 │    │
│  └────────────────────────────────────────────┘    │
│                        │                             │
│                        │ Sync metadata               │
│                        ↓                             │
│  ┌────────────────────────────────────────────┐    │
│  │      Postgres (Neon Serverless)            │    │
│  │  Tables:                                   │    │
│  │  - chunk_metadata (audit trail)            │    │
│  │  - query_logs (monitoring)                 │    │
│  │  - analytics (aggregated metrics)          │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## 5. Data Flow

### Ingestion Flow (Phase 3)
1. Extract markdown → Parse into chunks
2. Generate embeddings (OpenAI API) → 1536-dim vectors
3. Upload to Qdrant (vectors + metadata payload)
4. Sync metadata to Postgres `chunk_metadata` table
5. Validate chunk coverage and metadata completeness

### Query Flow (Phase 4-5)
1. User submits ChatRequest
2. Generate query embedding (OpenAI API)
3. Vector search in Qdrant (top_k candidates)
4. Rerank candidates (cross-encoder)
5. Generate answer (OpenAI LLM)
6. Validate citations (grounding check)
7. Log to Postgres `query_logs` table
8. Return ChatResponse

### Analytics Flow (Phase 8)
1. Query logs written in real-time to `query_logs` table
2. Nightly aggregation job computes metrics (p95 latency, error rate, etc.)
3. Write aggregated metrics to `analytics` table
4. Monitoring dashboard queries `analytics` for visualization

---

## 6. Validation Rules

### Data Integrity
- **chunk_id**: Unique, never null, format `chunk_####`
- **embeddings**: Exactly 1536 dimensions, all float values
- **token_count**: Range 512-1024 (enforced during chunking)
- **similarity_threshold**: Range 0.5-1.0 (prevents irrelevant results)
- **query length**: Max 500 characters (prevents abuse)

### Constitutional Compliance
- ✅ No session state stored (stateless design)
- ✅ All secrets in environment variables (no hardcoded keys)
- ✅ Structured logging (JSON format, request_id tracing)
- ✅ Explicit error codes (no silent failures)

---

## Next Steps

- [ ] **T014-T017**: Implement Pydantic models in `api/src/models/`
- [ ] **T033-T036**: Create Postgres migrations in `api/src/db/migrations/`
- [ ] **T048-T049**: Implement Qdrant collection setup in `api/src/db/qdrant_client.py`

---

**Document Status**: ✅ **COMPLETE**
**Last Updated**: 2026-02-05
