# System Architecture & RAG Pipeline

**Feature ID:** 002-rag-chatbot
**Phase:** 1 (Design & Architecture)
**Created:** 2026-02-05
**Status:** Complete

---

## Overview

This document defines the complete system architecture for the RAG-powered textbook chatbot, including component interactions, data flow, deployment model, and the 11-step RAG pipeline flow.

---

## 1. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         User (Student/Instructor)                        │
│                              Web Browser                                 │
└─────────────────────────┬───────────────────────────────────────────────┘
                          │ HTTPS
                          │
┌─────────────────────────▼───────────────────────────────────────────────┐
│                    Frontend (Docusaurus + React)                         │
│  ┌────────────┐  ┌──────────────┐  ┌────────────┐  ┌────────────────┐  │
│  │ ChatWidget │  │ ModeSelector │  │ TextSelect │  │ CitationBadge  │  │
│  └──────┬─────┘  └──────┬───────┘  └─────┬──────┘  └────────┬───────┘  │
│         │                │                 │                  │          │
│         └────────────────┴─────────────────┴──────────────────┘          │
│                                    │                                     │
│                            React Query (SWR)                             │
│                         chatApi.ts (API Client)                          │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ POST /api/v1/chat
                                     │ (JSON over HTTPS)
┌────────────────────────────────────▼────────────────────────────────────┐
│                     API Gateway (Vercel Edge)                            │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Rate Limiting (Upstash Redis)                                   │  │
│  │  • Anonymous: 10 req/hr                                          │  │
│  │  • Authenticated: 100 req/hr                                     │  │
│  │  • Premium: 1000 req/hr                                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Auth Middleware (Optional JWT Validation)                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
┌────────────────────────────────────▼────────────────────────────────────┐
│              Serverless Functions (Python 3.11 / FastAPI)               │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  POST /api/v1/chat (FastAPI Route)                              │  │
│  │                                                                  │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │  │
│  │  │ Mode Router │→ │  Retrieval   │→ │  Generation Service    │ │  │
│  │  │  (T065-68)  │  │  Service     │  │     (T059-61)          │ │  │
│  │  │             │  │  (T055-58)   │  │                        │ │  │
│  │  └─────────────┘  └──────┬───────┘  └──────────┬─────────────┘ │  │
│  │                           │                      │               │  │
│  │  ┌─────────────────────────┴──────────────────────┴───────────┐ │  │
│  │  │            Citation Service (Grounding Validation)          │ │  │
│  │  │                       (T062-64)                             │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  │                                                                  │  │
│  │  ┌──────────────────────────────────────────────────────────────┐ │  │
│  │  │  Middleware Layer                                            │ │  │
│  │  │  • Rate Limiter (T072)                                       │ │  │
│  │  │  • Structured Logger (T073)                                  │ │  │
│  │  │  • Schema Validator (T075)                                   │ │  │
│  │  │  • Error Handler (T076-77)                                   │ │  │
│  │  └──────────────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  ┌────────────────────────────┐  ┌──────────────────────────────────┐  │
│  │  GET /api/v1/health        │  │  GET /api/v1/chunks (Admin)      │  │
│  │  Health Check (T070)       │  │  Chunk Inspection (T071)         │  │
│  └────────────────────────────┘  └──────────────────────────────────┘  │
└──────────────┬────────────────────────┬──────────────────┬──────────────┘
               │                        │                  │
       ┌───────▼────────┐     ┌─────────▼────────┐  ┌─────▼────────┐
       │  Qdrant Cloud  │     │   OpenAI API     │  │Neon Postgres │
       │  (Vector DB)   │     │  (Embeddings +   │  │  (Metadata)  │
       │                │     │   LLM)           │  │              │
       │ • 1536-dim     │     │ • text-embed-3-  │  │ • Chunk meta │
       │   embeddings   │     │   small          │  │ • Query logs │
       │ • Metadata     │     │ • gpt-4-turbo    │  │ • Analytics  │
       │   filtering    │     │ • Streaming SSE  │  │              │
       │ • <200ms query │     │                  │  │              │
       └────────────────┘     └──────────────────┘  └──────────────┘
               │
               │ Metadata Sync
               │
       ┌───────▼─────────────────┐
       │  Upstash Redis          │
       │  (Rate Limiting)        │
       │  • Edge KV Store        │
       │  • Request counters     │
       │  • Burst tracking       │
       └─────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                        Monitoring & Observability                        │
│  ┌──────────────┐  ┌─────────────┐  ┌───────────────┐  ┌────────────┐  │
│  │   Sentry     │  │ OpenTelemetry│ │ Vercel        │  │  LogTail   │  │
│  │ (Error Track)│  │ (Tracing)    │ │ (Analytics)   │  │ (Logging)  │  │
│  └──────────────┘  └─────────────┘  └───────────────┘  └────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Component Descriptions

### 2.1 Frontend Layer (Docusaurus + React)

**Components**:
- **ChatWidget**: Main chat UI container with message history and input
- **ModeSelector**: Radio buttons/dropdown for mode selection (Book-Only/Selected-Text/General)
- **TextSelection**: Captures user text selection for Selected-Text mode
- **CitationBadge**: Clickable citation badges with confidence indicators

**Responsibilities**:
- Render chat UI embedded in textbook sidebar/floating widget
- Capture user input (query, mode, selected text)
- Display answers with citations and confidence badges
- Handle citation clicks (scroll to source location)
- Manage chat history within reading session

**Technology**: React 18.x, TypeScript 5.x, Docusaurus 3.x

---

### 2.2 API Gateway (Vercel Edge)

**Components**:
- **Rate Limiter**: Upstash Redis-backed rate limiting (tier-based)
- **Auth Middleware**: Optional JWT validation for tier identification
- **CORS Handler**: Cross-origin request validation

**Responsibilities**:
- Enforce rate limits (10/100/1000 req/hr by tier)
- Validate JWT tokens (if authentication enabled)
- Add security headers (HSTS, CSP, X-Frame-Options)
- Route requests to serverless functions

**Technology**: Vercel Edge Functions, Upstash Redis

---

### 2.3 Serverless Functions (Python 3.11 / FastAPI)

**Services**:

#### Mode Router (`api/src/services/mode_router.py`)
- Validate `AnswerMode` enum
- Enforce mode boundaries (prevent silent switching)
- Extract context (selected_text, chapter_filter)
- Generate mode-specific instructions for LLM

#### Retrieval Service (`api/src/services/retrieval_service.py`)
- Generate query embedding (OpenAI API)
- Vector similarity search (Qdrant, top_k=10-20)
- Metadata filtering (if chapter_filter provided)
- Rerank candidates (cross-encoder, select top_n=3-5)
- Context window enforcement (fit chunks in 8k tokens)

#### Generation Service (`api/src/services/generation_service.py`)
- Construct prompt (system instructions + user query + context chunks)
- LLM generation (OpenAI GPT-4 Turbo, streaming SSE)
- Temperature=0.3 (low variability for consistency)
- Stream response tokens to client

#### Citation Service (`api/src/services/citation_service.py`)
- Parse citations from generated answer
- Validate chunk IDs exist in Qdrant
- Grounding check (verify chunk content supports claim)
- Confidence scoring (map similarity score to High/Medium/Low)

#### Embedding Service (`api/src/services/embedding_service.py`)
- Text → embeddings (OpenAI text-embedding-3-small)
- Caching layer (avoid redundant API calls)
- Batch processing for ingestion phase

**Middleware**:
- **Rate Limiter**: Upstash integration, tier-based limits
- **Structured Logger**: JSON logs with request_id, context
- **Schema Validator**: Pydantic model validation
- **Error Handler**: Catch exceptions, return ErrorResponse

**Technology**: Python 3.11, FastAPI 0.109+, Pydantic v2

---

### 2.4 External Services

#### Qdrant Cloud (Vector Database)
- **Purpose**: Semantic search over textbook chunks
- **Schema**: 1536-dim embeddings, cosine similarity
- **Metadata**: Chapter, section, page, heading (for filtering/citations)
- **Performance**: <200ms query latency, 99.9% SLA
- **Cost**: Free tier (1GB storage) → $25/month (4GB)

#### OpenAI API (Embeddings + LLM)
- **Embeddings**: text-embedding-3-small (1536 dims, $0.02/1M tokens)
- **LLM**: gpt-4-turbo (streaming SSE, temperature=0.3)
- **Performance**: ~50ms embedding latency, ~1500ms LLM generation (streaming)
- **Cost**: ~$0.02/month (embeddings) + variable LLM cost

#### Neon Serverless Postgres (Metadata Storage)
- **Purpose**: Chunk metadata, query logs, analytics
- **Schema**: `chunk_metadata`, `query_logs`, `analytics` tables
- **Performance**: <100ms queries, automatic scaling
- **Cost**: Free tier (10GB storage)

#### Upstash Redis (Rate Limiting)
- **Purpose**: Edge-compatible rate limiting
- **Storage**: Request counters per user/IP
- **Performance**: <10ms operations (edge-optimized)
- **Cost**: Free tier (10k commands/day)

---

## 3. RAG Pipeline Flow (11 Steps)

```
User Query: "What is backpropagation?"
    │
    ▼
┌───────────────────────────────────────────────────────────────────┐
│ Step 1: Query Received                                            │
│ • Extract query, mode, context, options from ChatRequest         │
│ • Generate request_id for tracing                                │
│ • Start latency timer                                             │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ Step 2: Mode Validation (mode_router.py)                         │
│ • Validate AnswerMode enum (book_only/selected_text/general)     │
│ • Extract context (selected_text, chapter_filter)                │
│ • Generate mode-specific instructions                            │
│ • Reject if mode contamination detected                          │
│                                                                   │
│ Output: Validated mode + context + instructions                  │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ Step 3: Query Embedding (embedding_service.py)                   │
│ • Call OpenAI API: text-embedding-3-small                        │
│ • Input: query text (max 500 chars)                              │
│ • Output: 1536-dim embedding vector                              │
│ • Latency: ~50ms                                                  │
│                                                                   │
│ Example: [0.023, -0.142, 0.089, ... (1536 values)]              │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ Step 4: Vector Search (retrieval_service.py)                     │
│ • Query Qdrant with embedding vector                             │
│ • top_k=10 (retrieve 10 candidate chunks)                        │
│ • similarity_threshold=0.7 (min cosine similarity)               │
│ • Latency: <200ms                                                 │
│                                                                   │
│ Output: 10 candidate chunks with similarity scores               │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ Step 5: Metadata Filtering (retrieval_service.py)                │
│ • Apply chapter_filter if specified (QueryContext)               │
│ • Filter by page_number range if specified                       │
│ • Filter out duplicates (same chunk_id)                          │
│                                                                   │
│ Output: Filtered candidate chunks (5-10 remaining)               │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ Step 6: Reranking (retrieval_service.py)                         │
│ • Load cross-encoder model (ms-marco-MiniLM-L-12-v2)            │
│ • Rerank candidates with query-chunk relevance scores            │
│ • Select top_n=3-5 final chunks                                  │
│ • Latency: +100-200ms                                             │
│                                                                   │
│ Output: Top 3-5 chunks with reranked scores                      │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ Step 7: Context Window Enforcement (retrieval_service.py)        │
│ • Calculate total tokens in selected chunks                      │
│ • Fit chunks into LLM context window (8k tokens max)            │
│ • Truncate or summarize if overflow                              │
│                                                                   │
│ Output: Context chunks fitting in 8k token budget                │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ Step 8: Prompt Construction (generation_service.py)              │
│ • System prompt: Mode instructions + grounding rules             │
│ • User query: Original question                                  │
│ • Context: Retrieved chunks with chunk_ids                       │
│                                                                   │
│ Example Prompt:                                                   │
│ System: "You are a textbook assistant. Answer using ONLY the     │
│          provided context. Cite chunk_ids in your answer."       │
│ User: "What is backpropagation?"                                  │
│ Context: "[chunk_4589] Backpropagation is a supervised..."       │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ Step 9: LLM Generation (generation_service.py)                   │
│ • Call OpenAI API: gpt-4-turbo (streaming SSE)                  │
│ • Temperature: 0.3 (low variability)                             │
│ • Stream tokens to client in real-time                           │
│ • Latency: ~1500ms (first token <500ms)                          │
│                                                                   │
│ Output: Generated answer text with inline chunk_id citations     │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ Step 10: Citation Validation (citation_service.py)               │
│ • Parse chunk_ids from generated answer                          │
│ • Verify chunk_ids exist in Qdrant                               │
│ • Grounding check: Does chunk content support claim?            │
│ • Confidence scoring: Map similarity score to High/Med/Low       │
│ • Reject answer if grounding check fails                         │
│                                                                   │
│ Output: Validated citations with confidence levels               │
└───────────────────────┬───────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────────────┐
│ Step 11: Response Assembly & Return                              │
│ • Construct ChatResponse with answer + sources + metadata        │
│ • Log query to Postgres (query_logs table)                       │
│ • Stop latency timer, include in metadata                        │
│ • Return JSON response to client                                 │
│                                                                   │
│ Output: ChatResponse (200 OK) or ErrorResponse (4xx/5xx)        │
└───────────────────────────────────────────────────────────────────┘
```

---

## 4. Data Flow

### 4.1 Ingestion Flow (One-Time Setup)

```
Textbook Markdown Files
    │
    ▼
┌────────────────────────────────┐
│ Extract & Parse                │
│ • Read markdown files          │
│ • Parse frontmatter metadata   │
│ • Extract chapter/section info │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Semantic Chunking              │
│ • RecursiveCharacterSplitter   │
│ • 512-1024 tokens per chunk    │
│ • 10% overlap                  │
│ • Preserve metadata            │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Generate Embeddings            │
│ • Batch chunks (100 per call)  │
│ • OpenAI text-embedding-3-small│
│ • 1536-dim vectors             │
│ • Cache embeddings locally     │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Upload to Qdrant               │
│ • Batch upload (1000/batch)    │
│ • Store vectors + metadata     │
│ • Verify upload success        │
└────────┬───────────────────────┘
         │
         ▼
┌────────────────────────────────┐
│ Sync Metadata to Postgres     │
│ • Insert into chunk_metadata   │
│ • Create indexes               │
│ • Validate data integrity      │
└────────────────────────────────┘
```

### 4.2 Query Flow (Real-Time)

```
User Query → Frontend → API Gateway → Serverless Function → External Services → Response
     │           │            │                │                      │              │
     │           │            │                ▼                      │              │
     │           │            │         Mode Validation               │              │
     │           │            │                │                      │              │
     │           │            │                ▼                      │              │
     │           │            │         Query Embedding ──────────────┼──> OpenAI   │
     │           │            │                │                      │              │
     │           │            │                ▼                      │              │
     │           │            │         Vector Search ────────────────┼──> Qdrant   │
     │           │            │                │                      │              │
     │           │            │                ▼                      │              │
     │           │            │            Reranking                  │              │
     │           │            │                │                      │              │
     │           │            │                ▼                      │              │
     │           │            │         LLM Generation ───────────────┼──> OpenAI   │
     │           │            │                │                      │              │
     │           │            │                ▼                      │              │
     │           │            │         Citation Validation           │              │
     │           │            │                │                      │              │
     │           │            │                ▼                      │              │
     │           │            │         Log to Postgres ──────────────┼──> Neon     │
     │           │            │                │                      │              │
     │           │            │                ▼                      │              │
     │           │            └───────── Response Assembly            │              │
     │           │                             │                      │              │
     │           └─────────────────────────────┼──────────────────────┘              │
     │                                         │                                     │
     └─────────────────────────────────────────┼─────────────────────────────────────┘
                                              │
                                        Display Answer + Citations
```

---

## 5. Deployment Model

### 5.1 Vercel Deployment

**Configuration** (`vercel.json`):
```json
{
  "functions": {
    "api/src/main.py": {
      "runtime": "python3.11",
      "memory": 512,
      "maxDuration": 10
    }
  },
  "routes": [
    { "src": "/api/v1/(.*)", "dest": "api/src/main.py" }
  ]
}
```

**Deployment Commands**:
```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod

# Deploy to preview
vercel
```

**Environment Variables** (Vercel Dashboard):
- `QDRANT_URL`
- `QDRANT_API_KEY`
- `OPENAI_API_KEY`
- `NEON_DATABASE_URL`
- `UPSTASH_REDIS_URL`
- `SENTRY_DSN`

### 5.2 Fly.io Fallback (Optional)

**Configuration** (`fly.toml`):
```toml
app = "rag-chatbot-fallback"
primary_region = "iad"

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  min_machines_running = 0
```

**Deployment Commands**:
```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Login to Fly.io
flyctl auth login

# Deploy app
flyctl deploy

# Scale to zero (cost optimization)
flyctl scale count 0
```

---

## 6. Failure Modes & Recovery

| Failure Mode | Detection | Recovery Strategy | SLA Impact |
|--------------|-----------|-------------------|------------|
| Qdrant unavailable | Health check fails | Keyword search fallback | Degraded UX |
| OpenAI API rate limit | 429 error | Queue + exponential backoff | Increased latency |
| Vercel timeout (10s) | asyncio.TimeoutError | Route to Fly.io fallback | Minimal impact |
| Postgres connection lost | Connection error | Continue without logging | No impact on queries |
| Reranker model OOM | Memory error | Disable reranking, use top-k | Slight accuracy drop |

---

## 7. Performance Optimization

### 7.1 Cold Start Mitigation
- Lazy load reranker model (global scope caching)
- Pre-warm functions with health check pings
- Minimize imports (defer heavy libraries)

### 7.2 Caching Strategy
- Query embeddings cached (reduce OpenAI API calls)
- Qdrant client connection pooling
- Postgres prepared statements

### 7.3 Streaming Response
- Server-Sent Events (SSE) for LLM tokens
- Time to first token <500ms
- Progressive UI update

---

**Document Status**: ✅ **COMPLETE**
**Last Updated**: 2026-02-05
