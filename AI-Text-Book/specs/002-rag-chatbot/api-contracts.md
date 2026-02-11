# API Contracts & Endpoints

**Feature ID:** 002-rag-chatbot
**Phase:** 1 (Design & Architecture)
**Created:** 2026-02-05
**Status:** Complete

---

## Overview

This document defines all API endpoints, request/response schemas, error codes, and rate limiting for the RAG-powered textbook chatbot backend.

**Base URL**: `/api/v1`
**Protocol**: HTTPS only
**Content-Type**: `application/json`
**Authentication**: Optional (JWT bearer token if enabled)

---

## Endpoints

### 1. POST /api/v1/chat

Main endpoint for submitting questions and receiving answers.

**Purpose**: Execute RAG pipeline (embed query → retrieve chunks → generate answer → validate citations)

**Rate Limits**:
- Anonymous: 10 requests/hour
- Authenticated: 100 requests/hour
- Premium: 1000 requests/hour
- Burst allowance: 2x base rate for 10 seconds

**Request Schema**:
```json
{
  "query": "What is backpropagation?",
  "mode": "book_only",
  "context": {
    "selected_text": null,
    "chapter_filter": null,
    "session_id": "sess_abc123"
  },
  "options": {
    "top_k": 10,
    "similarity_threshold": 0.7,
    "include_citations": true
  }
}
```

**Request Fields**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `query` | string | Yes | 1-500 chars | User question |
| `mode` | enum | No | book_only, selected_text, general_knowledge | Answering mode (default: book_only) |
| `context.selected_text` | string | No | Max 5000 chars | Selected text for Selected-Text mode |
| `context.chapter_filter` | string | No | - | Restrict search to chapter |
| `context.session_id` | string | No | - | Session ID for analytics |
| `options.top_k` | integer | No | 5-20 | Chunks to retrieve (default: 10) |
| `options.similarity_threshold` | float | No | 0.5-1.0 | Min similarity (default: 0.7) |
| `options.include_citations` | boolean | No | - | Include citations (default: true) |

**Success Response (200 OK)**:
```json
{
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
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| `answer` | string | Generated answer text (never empty) |
| `mode` | enum | Mode used (echoed for UI visual distinction) |
| `sources` | array | Citation sources (empty if mode=general_knowledge) |
| `sources[].chunk_id` | string | Unique chunk identifier |
| `sources[].chapter` | string | Source chapter |
| `sources[].section` | string | Source section |
| `sources[].title` | string | Heading title |
| `sources[].confidence` | float | Confidence score (0.0-1.0) |
| `sources[].confidence_level` | enum | high, medium, low |
| `sources[].excerpt` | string | Text excerpt (max 500 chars) |
| `metadata.request_id` | string | Request ID for tracing |
| `metadata.latency_ms` | integer | Total response time |
| `metadata.chunks_retrieved` | integer | Chunks retrieved from vector DB |
| `metadata.chunks_used` | integer | Chunks used in answer |
| `metadata.model` | string | LLM model used |
| `metadata.embeddings_model` | string | Embedding model used |

**Error Responses**:

**400 Bad Request** - Validation error:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Query exceeds maximum length",
    "details": "Query length: 523 characters (max: 500)",
    "timestamp": "2026-02-05T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

**404 Not Found** - No relevant content:
```json
{
  "error": {
    "code": "RETRIEVAL_FAILED",
    "message": "No relevant textbook content found",
    "details": "Query: 'quantum mechanics basics'. No chunks exceeded similarity threshold (0.7).",
    "timestamp": "2026-02-05T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

**429 Too Many Requests** - Rate limit exceeded:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded for anonymous users",
    "details": "Limit: 10 requests/hour. Retry after 3420 seconds.",
    "timestamp": "2026-02-05T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

**500 Internal Server Error** - Service failure:
```json
{
  "error": {
    "code": "GENERATION_FAILED",
    "message": "Failed to generate answer",
    "details": "OpenAI API error: Rate limit exceeded",
    "timestamp": "2026-02-05T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

**504 Gateway Timeout** - Request timeout:
```json
{
  "error": {
    "code": "TIMEOUT_ERROR",
    "message": "Request exceeded timeout limit",
    "details": "RAG pipeline exceeded 10s timeout. Query routed to fallback service.",
    "timestamp": "2026-02-05T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

---

### 2. GET /api/v1/health

Health check endpoint for monitoring.

**Purpose**: Verify API service availability and dependency health

**Rate Limits**: Unlimited (used for monitoring)

**Request**: No body required

**Success Response (200 OK)**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-02-05T10:30:00Z",
  "dependencies": {
    "qdrant": "connected",
    "postgres": "connected",
    "openai": "available"
  },
  "uptime_seconds": 86400
}
```

**Degraded Response (200 OK with warnings)**:
```json
{
  "status": "degraded",
  "version": "1.0.0",
  "timestamp": "2026-02-05T10:30:00Z",
  "dependencies": {
    "qdrant": "connected",
    "postgres": "disconnected",
    "openai": "available"
  },
  "warnings": [
    "Postgres connection failed - query logging unavailable"
  ],
  "uptime_seconds": 86400
}
```

**Error Response (503 Service Unavailable)**:
```json
{
  "status": "unhealthy",
  "version": "1.0.0",
  "timestamp": "2026-02-05T10:30:00Z",
  "dependencies": {
    "qdrant": "disconnected",
    "postgres": "disconnected",
    "openai": "unavailable"
  },
  "errors": [
    "Qdrant connection failed",
    "OpenAI API unreachable"
  ]
}
```

---

### 3. GET /api/v1/chunks

Admin endpoint for chunk inspection and debugging.

**Purpose**: Retrieve chunks with metadata for validation and debugging

**Authentication**: Required (admin role)

**Rate Limits**: 100 requests/hour

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `chapter` | string | No | Filter by chapter |
| `page` | integer | No | Pagination page (default: 1) |
| `per_page` | integer | No | Results per page (default: 20, max: 100) |

**Request Example**:
```
GET /api/v1/chunks?chapter=Chapter%203&page=1&per_page=20
```

**Success Response (200 OK)**:
```json
{
  "chunks": [
    {
      "chunk_id": "chunk_4589",
      "text": "Backpropagation is a supervised learning algorithm...",
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
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total_chunks": 648,
    "total_pages": 33
  }
}
```

**Error Response (401 Unauthorized)**:
```json
{
  "error": {
    "code": "AUTHENTICATION_REQUIRED",
    "message": "Authentication required for admin endpoint",
    "details": "Provide JWT token in Authorization header",
    "timestamp": "2026-02-05T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

---

## Error Codes Reference

| Code | HTTP Status | Description | User-Facing Message |
|------|-------------|-------------|---------------------|
| `RETRIEVAL_FAILED` | 404 | No relevant chunks found | "I couldn't find relevant information in the textbook to answer your question." |
| `GENERATION_FAILED` | 500 | LLM generation error | "I encountered an error generating the answer. Please try again." |
| `INVALID_MODE` | 400 | Invalid mode specified | "Invalid answering mode. Use 'book_only', 'selected_text', or 'general_knowledge'." |
| `RATE_LIMIT_EXCEEDED` | 429 | Rate limit hit | "You've exceeded the rate limit. Please wait before trying again." |
| `VALIDATION_ERROR` | 400 | Request validation failed | "Your request contains invalid data. Please check and try again." |
| `INSUFFICIENT_CONTEXT` | 400 | Selected text too short | "The selected text doesn't contain enough information to answer this question." |
| `AMBIGUOUS_QUERY` | 400 | Query unclear | "Your question could refer to multiple topics. Can you be more specific?" |
| `TIMEOUT_ERROR` | 504 | Request timeout | "The request took too long. Please try a simpler question or try again later." |
| `SERVICE_UNAVAILABLE` | 503 | Dependency failure | "The service is temporarily unavailable. Please try again later." |

---

## Authentication (Optional)

**Header**: `Authorization: Bearer <jwt_token>`

**JWT Claims**:
```json
{
  "sub": "user_xyz789",
  "role": "authenticated",
  "tier": "premium",
  "exp": 1706860800
}
```

**Rate Limit Tiers**:
- **Anonymous** (no token): 10 requests/hour
- **Authenticated** (role=authenticated): 100 requests/hour
- **Premium** (tier=premium): 1000 requests/hour
- **Admin** (role=admin): Unlimited + access to /chunks endpoint

---

## CORS Configuration

**Allowed Origins**:
- Development: `http://localhost:3000`
- Production: `https://textbook.example.com`

**Allowed Methods**: `GET, POST, OPTIONS`

**Allowed Headers**: `Content-Type, Authorization`

**Credentials**: Allowed (for authenticated requests)

---

## Rate Limiting Details

**Implementation**: Upstash Redis (edge KV store)

**Headers**:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1706860800
Retry-After: 3420
```

**Burst Allowance**:
- First 10 seconds: 2x base rate allowed
- After burst: Base rate enforced
- Cooldown: 5 minutes after burst

**Error Response**:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": "Limit: 100 requests/hour. 87 remaining. Resets at 2026-02-05T12:00:00Z",
    "timestamp": "2026-02-05T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

---

## Performance SLAs

**Target Latencies** (95th percentile):
- POST /api/v1/chat: < 3000ms
- GET /api/v1/health: < 100ms
- GET /api/v1/chunks: < 500ms

**Availability**: 99.9% uptime (43.2 minutes downtime/month)

**Error Budget**: < 1% error rate under normal load

---

## Monitoring & Observability

**Request ID**: Every request receives a unique `request_id` (format: `req_<uuid>`)

**Structured Logging**:
```json
{
  "timestamp": "2026-02-05T10:30:00Z",
  "level": "INFO",
  "request_id": "req_abc123",
  "user_id": "user_xyz789",
  "mode": "book_only",
  "query": "What is backpropagation?",
  "chunks_retrieved": 5,
  "chunks_used": 2,
  "response_time_ms": 1234,
  "status": "success"
}
```

**OpenTelemetry Traces**:
- Span 1: Query processing
- Span 2: Embedding generation
- Span 3: Vector search
- Span 4: Reranking
- Span 5: LLM generation
- Span 6: Citation resolution

**Metrics**:
- Request rate (requests/second)
- Latency percentiles (p50, p95, p99)
- Error rate by error code
- Cache hit rate
- Dependency health (Qdrant, Postgres, OpenAI)

---

## Security

**Input Validation**:
- Query length: Max 500 characters
- Selected text: Max 5000 characters
- Top-k: Range 5-20
- Similarity threshold: Range 0.5-1.0

**Abuse Protection**:
- Profanity detection (reject offensive queries)
- SQL/JS injection detection (sanitize inputs)
- CAPTCHA trigger: 5+ failed requests in 1 minute
- IP-based blocks: 10+ rate limit violations → 1 hour block

**Secrets Management**:
- No API keys in client-side code
- Environment variable injection only
- Secret rotation capability via Vercel dashboard

---

## Deprecation Policy

**Version Header**: `X-API-Version: 1.0`

**Deprecation Notice** (6 months before removal):
```json
{
  "warning": "This endpoint version will be deprecated on 2026-08-05. Migrate to /api/v2/chat",
  "deprecation_date": "2026-08-05",
  "migration_guide": "https://docs.example.com/migration-v1-to-v2"
}
```

**Beta Endpoints**: `/api/beta/*` (no SLA guarantees)

---

## OpenAPI Specification

Full OpenAPI 3.1 specification available at: `shared/openapi.yaml`

**Interactive Documentation**:
- Swagger UI: `/api/docs`
- ReDoc: `/api/redoc`

---

**Document Status**: ✅ **COMPLETE**
**Last Updated**: 2026-02-05
