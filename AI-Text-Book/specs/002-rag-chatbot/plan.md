# Implementation Plan: RAG-Powered Textbook Chatbot

**Branch**: `002-rag-chatbot` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-rag-chatbot/spec.md`

---

## Summary

Build a serverless, production-grade RAG (Retrieval-Augmented Generation) chatbot embedded within the AI textbook platform. The system retrieves relevant content from textbook chapters, generates accurate answers with full citation traceability, and enforces strict mode boundaries (Book-Only, Selected-Text-Only, General Knowledge). Architecture prioritizes grounded accuracy, serverless reliability, and explicit error handling over operational complexity.

**Primary Approach**: Vector database (Qdrant Cloud) + semantic chunking + reranking pipeline + LLM orchestration (OpenAI) deployed as stateless serverless functions.

---

## Technical Context

**Language/Version**:
- Backend: Python 3.11+
- Frontend: TypeScript 5.x / React 18.x
- Infrastructure: Node.js 18+ (Docusaurus build)

**Primary Dependencies**:
- **LLM**: OpenAI API (gpt-4, text-embedding-3-small/large)
- **Vector DB**: Qdrant Cloud Python SDK
- **Database**: Neon Serverless Postgres (psycopg3)
- **API Framework**: FastAPI 0.109+ with Pydantic v2
- **Frontend Integration**: React Query, Docusaurus plugins
- **Embeddings**: sentence-transformers (local reranking fallback)

**Storage**:
- Vector Store: Qdrant Cloud (managed, persistent)
- Metadata: Neon Serverless Postgres (chapter references, chunk mappings, user analytics)
- Static Content: Docusaurus markdown files (existing textbook)
- Caching: Vercel Edge Cache / Upstash Redis (rate limiting only)

**Testing**:
- Unit: pytest with pytest-asyncio, pytest-mock
- Integration: pytest with testcontainers (local Qdrant)
- Contract: Schemathesis (OpenAPI validation)
- E2E: Playwright (mode boundaries, citation links)
- Load: Locust (rate limiting, degradation)

**Target Platform**:
- Serverless functions (Vercel/Fly.io/AWS Lambda)
- Edge-compatible where possible (rate limiting, static serving)
- Browser: Modern evergreen (Chrome, Firefox, Safari, Edge)

**Project Type**: Web application (frontend + backend API)

**Performance Goals**:
- Response latency: p95 < 3s, p99 < 5s
- Time to first token: < 500ms (streaming)
- Vector search: < 200ms (Qdrant)
- Concurrent users: 100+ simultaneous queries
- Throughput: 1000 requests/hour sustained

**Constraints**:
- Serverless cold start: < 1s initialization
- Memory limit: 512MB per function (Vercel)
- Request timeout: 10s (Vercel), 30s (Fly.io)
- Embedding API: 3000 tokens/min (OpenAI free tier)
- Vector DB: 1GB storage, 100 collections (Qdrant free tier)
- Cost: < $50/month operational (excluding OpenAI usage)

**Scale/Scope**:
- Textbook: 4 modules, ~30 chapters, ~200,000 words
- Chunks: ~500-800 semantic chunks (512-1024 tokens each)
- Users: 100-500 concurrent learners
- Queries: 10k-50k queries/month
- Uptime: 99.9% SLA target

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Article I: Core Principles

| Principle | Compliance | Implementation |
|-----------|-----------|----------------|
| 1.1 Grounded Accuracy | ✅ PASS | All answers mapped to chunk IDs; citation validation in pipeline |
| 1.2 Deterministic Behavior | ✅ PASS | Stateless functions; no session state; controlled temperature |
| 1.3 Strict Scope Enforcement | ✅ PASS | Mode enum enforced; validation middleware rejects contamination |
| 1.4 Separation of Concerns | ✅ PASS | Modular: retrieval, validation, generation, citation, routing |
| 1.5 Serverless-First Reliability | ✅ PASS | No background workers; managed services only; edge-compatible |
| 1.6 Explicit Over Implicit | ✅ PASS | Structured logging; explicit errors; OpenAPI contracts |

### ✅ Article II: Technical Architecture

| Requirement | Compliance | Notes |
|------------|-----------|-------|
| Forbidden: Redis session state | ✅ PASS | Using stateless JWT/session tokens |
| Forbidden: Manual servers | ✅ PASS | Vercel serverless functions only |
| Forbidden: Custom vector indexing | ✅ PASS | Qdrant Cloud managed service |
| Required: Managed databases | ✅ PASS | Qdrant Cloud + Neon Postgres |
| Required: Stateless handling | ✅ PASS | No in-memory state; query-scoped context |
| Required: API-first design | ✅ PASS | OpenAPI 3.1 spec; FastAPI auto-generation |

### ✅ Article III: Answering Modes

| Mode | Implementation | Validation |
|------|---------------|-----------|
| Book-Only (default) | Vector retrieval + grounding check | Citation validator middleware |
| Selected-Text-Only | Boundary-preserved selection context | Selection metadata logger |
| General Knowledge | Opt-in flag + disclaimer injection | Mode enum + UI warning banner |

### ✅ Article IV: RAG Pipeline Laws

| Requirement | Implementation |
|------------|----------------|
| Semantic chunking | LangChain RecursiveCharacterTextSplitter with 10% overlap |
| Chunk size: 512-1024 tokens | Configurable via environment variable |
| Metadata preservation | Chapter, section, page, heading stored in Qdrant payload |
| Retrieval order (6 steps) | Orchestrated in `retrieval_service.py` |
| Failure handling | Explicit error messages per scenario (Article IV.3) |

### ✅ Article V: Citation & Attribution Laws

| Requirement | Implementation |
|------------|----------------|
| Citation format | Chapter + section + chunk ID + confidence score |
| Inline citations | Superscript numbers with expandable references |
| Citation validation | Post-generation grounding check validates chunk support |
| User interaction | Click citation → scroll to source with highlight |

### ⚠️ Article VII: API Contract Law

| Requirement | Status | Notes |
|------------|--------|-------|
| OpenAPI 3.0+ spec | ✅ READY | FastAPI auto-generation |
| Versioned endpoints | ✅ READY | `/api/v1/chat` pattern |
| Schema validation | ✅ READY | Pydantic models with strict validation |
| Deprecation policy | ⚠️ TODO | Need to define header strategy for beta → v1 |

### ✅ Articles VIII-XI: Security, Monitoring, Testing

| Article | Compliance | Implementation |
|---------|-----------|----------------|
| VIII: Security | ✅ PASS | Upstash rate limiting; secret env vars; input validation |
| IX: Observability | ✅ PASS | Structured JSON logs; Sentry integration; OpenTelemetry spans |
| X: Success Criteria | ✅ READY | Defined in spec; test suite validates all criteria |
| XI: Testing & QA | ✅ READY | 80%+ coverage mandate; CI/CD pipeline |

**Constitution Compliance Summary**: ✅ **APPROVED** — All constitutional requirements satisfied. No violations requiring justification.

---

## Project Structure

### Documentation (this feature)

```text
specs/002-rag-chatbot/
├── spec.md              # Feature specification (✅ COMPLETE)
├── plan.md              # This file (implementation plan)
├── research.md          # Phase 0 output (technology evaluation)
├── data-model.md        # Phase 1 output (database schemas, chunk structure)
├── api-contracts.md     # Phase 1 output (OpenAPI specs, request/response schemas)
├── tasks.md             # Phase 2 output (dependency-ordered task list)
└── adr/                 # Architecture Decision Records
    ├── 001-vector-db-selection.md
    ├── 002-embedding-model-choice.md
    └── 003-serverless-platform-choice.md
```

### Source Code (repository root)

```text
# Backend API (serverless functions)
api/
├── src/
│   ├── models/
│   │   ├── chat_request.py       # Pydantic request models
│   │   ├── chat_response.py      # Pydantic response models
│   │   ├── chunk.py               # Chunk data model
│   │   └── citation.py            # Citation model
│   ├── services/
│   │   ├── retrieval_service.py   # Vector search + reranking
│   │   ├── generation_service.py  # LLM orchestration
│   │   ├── citation_service.py    # Citation validation
│   │   ├── mode_router.py         # Mode boundary enforcement
│   │   └── embedding_service.py   # Text → embeddings
│   ├── middleware/
│   │   ├── rate_limiter.py        # Upstash rate limiting
│   │   ├── auth_middleware.py     # Optional JWT validation
│   │   └── logger.py              # Structured logging
│   ├── routes/
│   │   ├── chat.py                # POST /api/v1/chat
│   │   ├── health.py              # GET /api/v1/health
│   │   └── chunks.py              # GET /api/v1/chunks (admin)
│   ├── db/
│   │   ├── qdrant_client.py       # Vector DB connection
│   │   ├── postgres_client.py     # Neon Postgres connection
│   │   └── migrations/            # SQL migration scripts
│   └── main.py                    # FastAPI app entrypoint
├── tests/
│   ├── unit/
│   │   ├── test_retrieval.py
│   │   ├── test_generation.py
│   │   └── test_citation.py
│   ├── integration/
│   │   ├── test_rag_pipeline.py
│   │   └── test_mode_enforcement.py
│   └── e2e/
│       └── test_chat_flows.py
├── scripts/
│   ├── ingest_textbook.py         # Chunk + embed + upload to Qdrant
│   ├── seed_database.py           # Initialize Postgres metadata
│   └── validate_chunks.py         # Verify chunk quality
├── requirements.txt
├── pyproject.toml
└── vercel.json                    # Vercel deployment config

# Frontend Integration (Docusaurus plugin)
src/
├── components/
│   ├── ChatWidget/
│   │   ├── index.tsx              # Main chat UI component
│   │   ├── ChatInput.tsx          # Query input with mode selector
│   │   ├── ChatMessage.tsx        # Message bubble with citations
│   │   ├── CitationBadge.tsx      # Clickable citation badges
│   │   ├── ModeSelector.tsx       # Book-Only / Selected-Text / General
│   │   └── styles.module.css
│   └── TextSelection/
│       ├── SelectionCapture.tsx   # Text selection event handler
│       └── SelectionHighlight.tsx # Visual selection indicator
├── hooks/
│   ├── useChat.ts                 # React Query hook for chat API
│   ├── useTextSelection.ts        # Selection state management
│   └── useCitations.ts            # Citation linking and scrolling
├── services/
│   └── chatApi.ts                 # API client with types
└── types/
    ├── chat.ts                    # TypeScript types matching API
    └── citation.ts

# Shared
shared/
└── openapi.yaml                   # OpenAPI 3.1 specification (source of truth)

# Infrastructure
infrastructure/
├── terraform/                     # Qdrant + Neon provisioning (optional)
└── monitoring/
    ├── sentry.config.js
    └── opentelemetry.config.js
```

**Structure Decision**: Web application (frontend + backend) selected because:
1. RAG chatbot requires backend API for vector search and LLM orchestration
2. Frontend integration must embed seamlessly into existing Docusaurus textbook
3. Separation enables independent scaling and testing of API and UI components
4. Serverless backend deployed to Vercel; static frontend served via Vercel Edge

---

## Complexity Tracking

*No constitutional violations requiring justification.*

All complexity is justified by problem domain requirements:
- Vector DB: Required for semantic search (constitutional mandate: managed services)
- Reranking: Required for citation accuracy (constitutional mandate: grounded accuracy)
- Mode router: Required for mode boundary enforcement (constitutional mandate: strict scope)
- Structured logging: Required for observability (constitutional mandate: explicit behavior)

---

## Phase 0: Research & Validation

**Objective**: Validate technology choices and establish baseline architecture.

### Research Areas

#### 0.1 Vector Database Evaluation
- **Options**: Qdrant Cloud, Pinecone, Weaviate, Chroma
- **Criteria**: Free tier limits, latency, metadata filtering, managed service quality
- **Decision**: Qdrant Cloud (1GB free, <200ms queries, Python SDK, metadata filters)
- **ADR**: `adr/001-vector-db-selection.md`

#### 0.2 Embedding Model Selection
- **Options**: OpenAI (text-embedding-3-small/large), sentence-transformers (local), Cohere
- **Criteria**: Accuracy (MTEB benchmark), cost, latency, context window
- **Decision**: OpenAI text-embedding-3-small (1536 dims, $0.02/1M tokens, 8191 context)
- **ADR**: `adr/002-embedding-model-choice.md`

#### 0.3 Reranking Strategy
- **Options**: Cross-encoder (ms-marco), LLM-based reranking, no reranking
- **Criteria**: Latency impact, accuracy improvement, operational cost
- **Decision**: Cross-encoder with local model fallback (sentence-transformers/ms-marco-MiniLM-L-12-v2)
- **Trade-off**: +100-200ms latency for 15-20% relevance improvement

#### 0.4 Serverless Platform Selection
- **Options**: Vercel, Fly.io, AWS Lambda, Cloudflare Workers
- **Criteria**: Cold start time, timeout limits, free tier, Python support
- **Decision**: Vercel (primary) with Fly.io fallback for long-running queries
- **ADR**: `adr/003-serverless-platform-choice.md`

#### 0.5 Chunking Strategy
- **Options**: Fixed-size, semantic (RecursiveCharacterTextSplitter), sentence-based
- **Criteria**: Context preservation, citation granularity, overlap management
- **Decision**: Semantic chunking with 10% overlap (LangChain implementation)
- **Parameters**: 512-1024 tokens, split on paragraphs → sentences → characters

#### 0.6 LLM Selection for Generation
- **Options**: GPT-4 Turbo, GPT-3.5 Turbo, Claude 3, Llama 3
- **Criteria**: Cost, latency, instruction following, citation formatting
- **Decision**: GPT-4 Turbo (gpt-4-1106-preview) for accuracy; GPT-3.5 Turbo fallback
- **Streaming**: Server-Sent Events (SSE) for time-to-first-token optimization

### Validation Experiments

#### Experiment 1: Chunk Size Optimization
- **Hypothesis**: 512-1024 tokens balances context and retrieval precision
- **Method**: Generate chunks at 256, 512, 1024, 2048 tokens; measure retrieval accuracy
- **Metric**: Precision@3 on 50 ground-truth Q&A pairs
- **Expected Result**: 512-1024 tokens achieves >85% precision@3

#### Experiment 2: Reranking Impact
- **Hypothesis**: Cross-encoder improves top-3 relevance by 15%+
- **Method**: A/B test vector search vs. vector + reranking on 100 queries
- **Metric**: NDCG@3 (Normalized Discounted Cumulative Gain)
- **Expected Result**: Reranking increases NDCG@3 from 0.72 → 0.85+

#### Experiment 3: Cold Start Mitigation
- **Hypothesis**: Pre-warming Vercel function reduces cold start to <500ms
- **Method**: Measure P95 latency with/without Vercel warming configuration
- **Metric**: Time to first byte (TTFB)
- **Expected Result**: Pre-warming reduces cold start from 1.2s → <500ms

---

## Phase 1: Design & Architecture

**Objective**: Define data models, API contracts, and system interfaces.

### 1.1 Data Models

**Chunk Model** (`api/src/models/chunk.py`):
```python
class Chunk(BaseModel):
    chunk_id: str
    text: str
    embedding: List[float]  # 1536-dim vector
    metadata: ChunkMetadata

class ChunkMetadata(BaseModel):
    chapter: str
    section: str
    page_number: Optional[int]
    heading: str
    word_count: int
    created_at: datetime
```

**Chat Request Model** (`api/src/models/chat_request.py`):
```python
class ChatRequest(BaseModel):
    query: str = Field(..., max_length=500)
    mode: AnswerMode = AnswerMode.BOOK_ONLY
    context: Optional[QueryContext] = None
    options: Optional[QueryOptions] = None

class AnswerMode(str, Enum):
    BOOK_ONLY = "book_only"
    SELECTED_TEXT = "selected_text"
    GENERAL_KNOWLEDGE = "general_knowledge"

class QueryContext(BaseModel):
    selected_text: Optional[str] = None
    chapter_filter: Optional[str] = None
    session_id: Optional[str] = None

class QueryOptions(BaseModel):
    top_k: int = Field(default=10, ge=5, le=20)
    similarity_threshold: float = Field(default=0.7, ge=0.5, le=1.0)
    include_citations: bool = True
```

**Chat Response Model** (`api/src/models/chat_response.py`):
```python
class ChatResponse(BaseModel):
    answer: str
    mode: AnswerMode
    sources: List[Source]
    metadata: ResponseMetadata

class Source(BaseModel):
    chunk_id: str
    chapter: str
    section: str
    title: str
    confidence: float
    excerpt: str

class ResponseMetadata(BaseModel):
    request_id: str
    latency_ms: int
    chunks_retrieved: int
    chunks_used: int
    model: str
```

**Database Schemas** (documented in `data-model.md`):
- Qdrant: Vector collection schema with metadata fields
- Postgres: Chunk metadata, query logs, analytics tables

### 1.2 API Contracts

**Endpoints** (documented in `api-contracts.md` and `shared/openapi.yaml`):

```yaml
POST /api/v1/chat
  Request: ChatRequest
  Response: ChatResponse | ErrorResponse
  Rate Limit: 10/hour (anonymous), 100/hour (authenticated)

GET /api/v1/health
  Response: { status: "healthy", version: "1.0.0" }

GET /api/v1/chunks?chapter={chapter}&page={page}
  Response: PaginatedChunks
  Auth: Admin only
```

### 1.3 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Docusaurus)                     │
│  ┌──────────────┐  ┌────────────────┐  ┌─────────────────┐ │
│  │ ChatWidget   │  │ TextSelection  │  │ CitationBadge   │ │
│  └──────┬───────┘  └────────┬───────┘  └────────┬────────┘ │
│         │                   │                    │          │
│         └───────────────────┴────────────────────┘          │
│                             │                                │
│                     React Query (SWR)                        │
└─────────────────────────────┼──────────────────────────────┘
                              │ HTTPS (JSON)
┌─────────────────────────────┼──────────────────────────────┐
│              API Gateway (Vercel Edge)                       │
│         Rate Limiting (Upstash) + Auth Middleware           │
└─────────────────────────────┼──────────────────────────────┘
                              │
┌─────────────────────────────┼──────────────────────────────┐
│              Serverless Functions (Python 3.11)              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  /api/v1/chat (FastAPI route)                         │  │
│  │  ┌────────────┐  ┌─────────────┐  ┌───────────────┐  │  │
│  │  │ Mode Router│→ │ Retrieval   │→ │ Generation    │  │  │
│  │  │            │  │ Service     │  │ Service       │  │  │
│  │  └────────────┘  └──────┬──────┘  └───────┬───────┘  │  │
│  │                          │                  │           │  │
│  │                   ┌──────┴──────────────────┴───────┐  │  │
│  │                   │     Citation Service            │  │  │
│  │                   │   (Grounding Validation)        │  │  │
│  │                   └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└───────────────────────┬──────────────┬──────────────────────┘
                        │              │
        ┌───────────────┘              └──────────────┐
        │                                             │
┌───────▼─────────────┐                  ┌────────────▼────────┐
│   Qdrant Cloud      │                  │  OpenAI API         │
│  (Vector Search)    │                  │ (Embeddings + LLM)  │
│  • Semantic chunks  │                  │ • text-embed-3-sm   │
│  • Metadata filters │                  │ • gpt-4-turbo       │
│  • <200ms queries   │                  │ • Streaming SSE     │
└─────────────────────┘                  └─────────────────────┘
        │
        │ Metadata sync
        │
┌───────▼────────────────┐
│  Neon Serverless PG    │
│  • Chunk metadata      │
│  • Query logs          │
│  • Analytics           │
└────────────────────────┘
```

### 1.4 RAG Pipeline Flow

```
1. Query Received
   ↓
2. Mode Validation (mode_router.py)
   ├─ Book-Only → proceed
   ├─ Selected-Text → extract selection boundaries
   └─ General Knowledge → set flag + inject disclaimer
   ↓
3. Query Embedding (embedding_service.py)
   → OpenAI text-embedding-3-small (1536-dim)
   ↓
4. Vector Search (retrieval_service.py)
   → Qdrant similarity search (top_k=10-20)
   → Metadata filtering (if chapter_filter set)
   ↓
5. Reranking (retrieval_service.py)
   → Cross-encoder scores top_k candidates
   → Select top_n=3-5 final chunks
   ↓
6. Context Window Enforcement
   → Fit chunks into LLM context (max 8k tokens)
   → Truncate or summarize if overflow
   ↓
7. Prompt Construction (generation_service.py)
   → System: mode instructions + grounding rules
   → User: query
   → Context: retrieved chunks with IDs
   ↓
8. LLM Generation (generation_service.py)
   → OpenAI GPT-4 Turbo (streaming)
   → Temperature=0.3 (low variability)
   ↓
9. Citation Validation (citation_service.py)
   → Parse generated citations
   → Verify chunk IDs exist
   → Check chunk content supports claim
   ↓
10. Response Assembly
    → Answer + sources + metadata
    → Confidence scores per source
    ↓
11. Return ChatResponse (JSON)
```

---

## Phase 2: Implementation Roadmap

**Objective**: Break down implementation into testable, dependency-ordered tasks.

### Phase 2.1: Infrastructure Setup
- [ ] Provision Qdrant Cloud collection (1536 dims, cosine similarity)
- [ ] Provision Neon Serverless Postgres database
- [ ] Set up Vercel project with Python runtime
- [ ] Configure environment variables (API keys, DB URLs)
- [ ] Set up Sentry error tracking
- [ ] Configure Upstash Redis for rate limiting

### Phase 2.2: Document Processing Pipeline
- [ ] Script: Extract markdown from Docusaurus docs/
- [ ] Script: Semantic chunking with RecursiveCharacterTextSplitter
- [ ] Script: Generate embeddings for all chunks (OpenAI API)
- [ ] Script: Upload chunks + embeddings to Qdrant
- [ ] Script: Sync chunk metadata to Postgres
- [ ] Validation: Verify chunk quality (coverage, overlap, metadata)

### Phase 2.3: Backend API - Core Services
- [ ] `embedding_service.py`: Text → embeddings (with caching)
- [ ] `retrieval_service.py`: Vector search + reranking
- [ ] `generation_service.py`: LLM orchestration with streaming
- [ ] `citation_service.py`: Citation validation + grounding check
- [ ] `mode_router.py`: Mode boundary enforcement

### Phase 2.4: Backend API - Routes & Middleware
- [ ] `routes/chat.py`: POST /api/v1/chat endpoint
- [ ] `routes/health.py`: Health check endpoint
- [ ] `middleware/rate_limiter.py`: Upstash integration
- [ ] `middleware/logger.py`: Structured JSON logging
- [ ] `middleware/auth_middleware.py`: Optional JWT validation

### Phase 2.5: API Contracts & Validation
- [ ] Define OpenAPI 3.1 spec (`shared/openapi.yaml`)
- [ ] Pydantic models for all request/response types
- [ ] Schema validation middleware
- [ ] Contract tests with Schemathesis

### Phase 2.6: Frontend Integration
- [ ] `ChatWidget` component (React)
- [ ] `ModeSelector` component (Book-Only / Selected-Text / General)
- [ ] `CitationBadge` component (clickable, scrolls to source)
- [ ] `useChat` React Query hook
- [ ] `useTextSelection` hook for selection capture
- [ ] API client with TypeScript types

### Phase 2.7: Testing & QA
- [ ] Unit tests (80%+ coverage): services, models, utilities
- [ ] Integration tests: RAG pipeline end-to-end
- [ ] Contract tests: API schema validation
- [ ] E2E tests (Playwright): mode boundaries, citation links
- [ ] Load tests (Locust): rate limiting, degradation

### Phase 2.8: Deployment & Monitoring
- [ ] Vercel deployment configuration (`vercel.json`)
- [ ] CI/CD pipeline (GitHub Actions): test → build → deploy
- [ ] OpenTelemetry instrumentation (trace spans)
- [ ] Sentry integration (error tracking)
- [ ] Monitoring dashboards (Vercel Analytics + custom metrics)

### Phase 2.9: Documentation & Runbooks
- [ ] API documentation (OpenAPI UI: Swagger/ReDoc)
- [ ] Runbook: Common incidents and resolutions
- [ ] Quickstart guide for local development
- [ ] ADRs for key decisions (vector DB, embedding model, platform)

**Detailed task breakdown**: See `tasks.md` (generated by `/sp.tasks` command in Phase 2).

---

## Risk Analysis

### High-Priority Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| OpenAI API rate limits exceeded | Medium | High | Implement exponential backoff; queue system; fallback to GPT-3.5 |
| Qdrant Cloud free tier exhausted (1GB) | Medium | Medium | Monitor storage usage; implement chunk archival; upgrade plan if needed |
| Cold start latency >3s (poor UX) | Medium | Medium | Vercel function warming; pre-load embeddings; optimize imports |
| Hallucination despite grounding | Low | Critical | Strict citation validation; confidence thresholds; manual QA sampling |
| Mode contamination (e.g., general knowledge in Book-Only) | Low | High | Automated tests for mode boundaries; enum enforcement; middleware validation |

### Medium-Priority Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|-----------|
| Embedding cost exceeds budget | Low | Medium | Cache embeddings; batch API calls; monitor usage |
| Reranking latency degrades UX | Medium | Low | Profile bottleneck; consider lighter model; make reranking optional |
| Citation links break (chunk ID mismatches) | Low | Medium | Automated tests; chunk ID integrity checks; migration scripts |

---

## Success Metrics

### Technical Metrics (Phase 2 completion)
- [ ] API latency: p95 < 3s, p99 < 5s
- [ ] Citation accuracy: >95% (manual sampling of 100 responses)
- [ ] Hallucination rate: <5% (grounding check violations)
- [ ] Test coverage: >80% (unit + integration)
- [ ] Uptime: >99.5% over 30 days
- [ ] Mode boundary violations: 0 (automated tests)

### User Experience Metrics (post-launch)
- [ ] User satisfaction: >4.0/5.0 (feedback survey)
- [ ] Query success rate: >90% (relevant answer returned)
- [ ] Citation click-through rate: >30% (users verify sources)
- [ ] Time to first token: <500ms (p95)

### Operational Metrics
- [ ] One-command deployment (Vercel CLI)
- [ ] Zero-downtime updates (blue-green deployment)
- [ ] Self-service troubleshooting (runbook completeness)
- [ ] Cost per query: <$0.05 (OpenAI + infrastructure)

---

## Dependencies & Blockers

### External Dependencies
- OpenAI API availability (99.9% SLA per OpenAI)
- Qdrant Cloud uptime (99.9% SLA per Qdrant)
- Neon Postgres availability (99.95% SLA per Neon)
- Vercel platform stability

### Internal Dependencies
- Existing textbook content (Docusaurus markdown files)
- Authentication system (if gating chatbot access)
- Analytics tracking infrastructure

### Potential Blockers
- OpenAI API key approval/budget allocation
- Qdrant Cloud account provisioning
- Neon Postgres free tier limits (10GB storage)
- Vercel free tier limits (100GB bandwidth/month)

---

## Next Steps

1. **Review & Approve Plan**: Stakeholder sign-off on architecture and roadmap
2. **Phase 0 Research**: Execute validation experiments (chunking, reranking, cold start)
3. **Phase 1 Design**: Complete `data-model.md` and `api-contracts.md`
4. **Generate Tasks**: Run `/sp.tasks` to create `tasks.md` with dependency-ordered implementation tasks
5. **Kick off Phase 2**: Begin infrastructure setup and document processing pipeline

---

**Plan Status**: ✅ **COMPLETE** — Ready for review and Phase 0 execution

**Next Command**: `/sp.tasks` (generate detailed, dependency-ordered task list)

**Estimated Timeline**:
- Phase 0 (Research): 3-5 days
- Phase 1 (Design): 5-7 days
- Phase 2 (Implementation): 15-20 days
- **Total**: 23-32 days (4-6 weeks)
