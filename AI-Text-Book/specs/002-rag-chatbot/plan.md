# Implementation Plan: RAG-Powered Textbook Chatbot

**Branch**: `002-rag-chatbot` | **Date**: 2026-02-14 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-rag-chatbot/spec.md`

## Summary

Implement a production-grade RAG (Retrieval-Augmented Generation) chatbot system embedded within an interactive textbook platform. The chatbot enables students to ask questions about textbook content with three distinct answering modes: Book-Only (strict grounding), Selected-Text-Only (focused context), and General Knowledge (exploratory learning). All book-grounded responses must include verifiable citations with confidence scores, chunk identifiers, and source references. The system operates on serverless infrastructure with managed vector and relational databases, ensuring 99.9% uptime, < 3s response times (p95), and < 5% hallucination rates.

## Technical Context

**Language/Version**: Python 3.11+ (backend API), TypeScript 5.x (frontend)
**Primary Dependencies**:
- Backend: FastAPI (serverless), LangChain, Qdrant Python Client, Neon Postgres Client, OpenAI SDK
- Frontend: React 18.x, Docusaurus 3.x, CSS Modules

**Storage**:
- Vector Database: Qdrant Cloud (managed, free tier minimum)
- Relational Database: Neon Serverless Postgres (conversations, messages, feedback, analytics)
- Object Storage: CDN for static textbook content

**Testing**:
- Backend: pytest (unit, integration), pytest-cov (coverage)
- Frontend: Jest (unit), Playwright (E2E)
- Contract: OpenAPI schema validation

**Target Platform**:
- API: Vercel Serverless Functions (primary) or AWS Lambda
- Frontend: Vercel (static hosting + edge functions)
- Databases: Qdrant Cloud + Neon (managed services)

**Project Type**: Web application (frontend + backend)

**Performance Goals**:
- Query response time: < 3s (p95), < 2s (p50)
- Time to first token: < 500ms (streaming responses)
- Concurrent users: 100+ without degradation
- Throughput: 100 requests/second sustained
- Uptime: 99.9% (< 43 minutes downtime/month)

**Constraints**:
- Serverless-only (no manual background processes)
- Per-query cost: < $0.10 (LLM + vector search + DB)
- Citation accuracy: > 95%
- Hallucination rate: < 5%
- Grounding rate: > 90%
- Mobile responsive: down to 320px screen width

**Scale/Scope**:
- Target users: 1,000 concurrent students
- Textbook size: 10-20 chapters (~200-500 pages)
- Vector index: ~10,000-50,000 chunks
- Query volume: ~10,000 queries/day expected
- Conversation retention: 90 days

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Article I: Core Principles

✅ **Grounded Accuracy (1.1)**
- Implementation: Book-Only mode enforces strict citation requirements
- Validation: Every factual claim maps to chunk ID with confidence scores
- Compliance: Refusal messages when content insufficient

✅ **Deterministic Behavior (1.2)**
- Implementation: Retrieval pipeline follows fixed order: embed → search → filter → rerank → validate
- Validation: Same query + context produces consistent results (temperature = 0 for core logic)
- Compliance: No hidden state transitions; mode persists within session only

✅ **Strict Scope Enforcement (1.3)**
- Implementation: Three hard-coded modes with explicit boundary checks
- Validation: Mode cannot be bypassed; cross-mode contamination triggers errors
- Compliance: Mode indicator always visible to user

✅ **Separation of Concerns (1.4)**
- Implementation: Isolated components - retrieval, validation, generation, citation, UI
- Validation: Each component has clear input/output contracts
- Compliance: No silent scope expansion

✅ **Serverless-First Reliability (1.5)**
- Implementation: Vercel Functions (API), Qdrant Cloud, Neon Postgres
- Validation: Zero manual processes; auto-scaling enabled
- Compliance: Stateless request handling

✅ **Explicit Over Implicit (1.6)**
- Implementation: Clear error messages with recovery actions
- Validation: All mode switches logged; visible state indicators
- Compliance: Structured logging with request IDs

### Article II: Technical Architecture

✅ **Forbidden Technologies Check (2.1)**
- No Redis for session state ✅
- No client-side FastAPI ✅
- No manual background servers ✅
- No stateful in-memory storage ✅
- No unmanaged databases ✅
- No synchronous blocking in request paths ✅

✅ **Mandatory Characteristics (2.2)**
- Serverless execution (Vercel Functions) ✅
- Managed databases (Qdrant Cloud, Neon) ✅
- Stateless requests ✅
- Explicit failure handling ✅
- Idempotent operations (where applicable) ✅
- Graceful degradation patterns ✅
- Observable logging (structured JSON) ✅
- API-first design with versioning ✅

✅ **Approved Technology Stack (2.3)**
- LLM: OpenAI GPT-4 / GPT-3.5-turbo ✅
- Vector DB: Qdrant Cloud ✅
- Relational DB: Neon Serverless Postgres ✅
- Embeddings: OpenAI text-embedding-3-large ✅
- API Framework: FastAPI (serverless deployment) ✅
- Frontend: Docusaurus 3.x + React 18.x ✅
- Hosting: Vercel (frontend + serverless functions) ✅

### Article III: RAG Chatbot Answering Modes

✅ **Book-Only Mode (3.1)**
- Implementation: Default mode; strict textbook-only responses
- Validation: Every sentence maps to chunk ID; no general knowledge
- Compliance: Refusal message template enforced

✅ **Selected-Text-Only Mode (3.2)**
- Implementation: Zero vector retrieval; uses selection boundaries only
- Validation: Selection metadata logged; size limits enforced (50-4000 tokens)
- Compliance: Refusal template for insufficient context

✅ **General Knowledge Mode (3.3)**
- Implementation: Opt-in only; clear visual indicator (amber badge + banner)
- Validation: Disclaimer shown on first use; can be disabled anytime
- Compliance: Separated from book-grounded responses with visual distinction

✅ **Mode Enforcement (3.4)**
- Implementation: Hard-coded boundary checks; no silent switching
- Validation: Mode state tracked per conversation; logged in analytics
- Compliance: Violations trigger system errors

### Article IV: RAG Pipeline Laws

✅ **Document Processing (4.1)**
- Chunking: Semantic with 10-15% overlap, 512-1024 tokens
- Metadata: Chapter, section, page, heading hierarchy preserved
- Deduplication: Identical chunks merged with provenance

✅ **Retrieval Process (4.2)**
- Pipeline order: Query embedding → Vector search (top-k=20) → Metadata filter → Rerank (top-n=5) → Context window validation
- Parameters: similarity_threshold=0.7, context_limit=8000 tokens
- Compliance: Non-negotiable order enforced

✅ **Failure Handling (4.3)**
- No relevant chunks → Clear refusal message
- Partial relevance → Explicit partial answer with missing aspects noted
- Ambiguous query → Clarification request with options
- Context overflow → Focus suggestion

✅ **Quality Assurance (4.4)**
- Relevance scoring for every chunk
- Cross-validation between query and answer
- Citation integrity verification
- Hallucination detection via grounding check

### Article V: Citation & Attribution Laws

✅ **Citation Requirements (5.1)**
- Format: Chapter + section + chunk ID + confidence (Low/Medium/High)
- Visual: 📚 icon, formatted source list
- Compliance: Every book-grounded answer includes citations

✅ **Inline Citation Format (5.2)**
- Approved patterns: Superscript numbers, bracketed references, inline badges
- Validation: Citations link to retrievable chunks
- Compliance: Chunk content must support cited claim

### Article VII: API Contract Law

✅ **Schema Requirements (7.1)**
- OpenAPI 3.0+ specification
- JSON Schema validation for all requests/responses
- Required field enforcement

✅ **Versioning Policy (7.2)**
- URL path versioning: `/api/v1/chat`
- Deprecation notice: 90 days minimum

✅ **Error Response Standard (7.3)**
- Required format: code, message, details, timestamp, request_id
- User-facing errors must be actionable

### Article VIII: Security & Reliability

✅ **Secrets Management (8.1)**
- Environment variables for API keys
- No client-side credentials
- Least-privilege access

✅ **Rate Limiting (8.2)**
- Tiers: Anonymous (10/hr), Authenticated (100/hr), Premium (1000/hr)
- Implementation: Upstash Redis (edge KV)
- Burst allowance: 2x base rate for 10s

✅ **Graceful Degradation (8.4)**
- Vector DB down → Keyword search fallback (BM25)
- LLM API down → Queue + retry with backoff
- Postgres down → Cached responses

### Article IX: Observability & Monitoring

✅ **Logging Requirements (9.1)**
- Structured JSON logs with request_id, user_id, mode, chunks_retrieved, response_time_ms
- Levels: ERROR, WARN, INFO, DEBUG

✅ **Metrics & Alerting (9.2)**
- Metrics: Latency (p50/p95/p99), error rate, retrieval success, citation accuracy, user satisfaction
- Alerts: Error rate > 5%, latency p95 > 5s, vector DB unavailable

✅ **Tracing (9.3)**
- End-to-end tracing: Query processing → Embedding → Vector search → Reranking → LLM generation → Citation resolution

### Article X: Success Criteria

✅ **Technical Validation (10.1)**
- Zero runtime conflicts ✅
- No manual processes ✅
- All answers traceable via audit logs ✅
- 99.9% uptime target ✅
- < 1% error rate target ✅

✅ **Quality Validation (10.2)**
- 95%+ citation accuracy target ✅
- < 5% hallucination rate target ✅
- User satisfaction > 4.0/5.0 target ✅
- Mode boundaries enforced ✅

✅ **Operational Validation (10.3)**
- One-command deployment ✅
- Automated rollback ✅
- Zero-downtime updates ✅

### Constitution Check Summary

**Status**: ✅ **PASSED** - All constitutional requirements satisfied

**No Violations** - All architecture decisions align with constitutional principles

## Project Structure

### Documentation (this feature)

```text
specs/002-rag-chatbot/
├── spec.md             # Feature specification (already created)
├── plan.md             # This file
├── research.md         # Phase 0 output (to be created)
├── data-model.md       # Phase 1 output (to be created)
├── quickstart.md       # Phase 1 output (to be created)
├── contracts/          # Phase 1 output (to be created)
│   ├── openapi.yaml
│   └── schemas/
└── tasks.md            # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
# Web Application Structure (Frontend + Backend)

api/
├── src/
│   ├── main.py                      # FastAPI app entry point
│   ├── config.py                    # Environment configuration
│   ├── models/                      # Data models
│   │   ├── conversation.py
│   │   ├── message.py
│   │   ├── citation.py
│   │   └── feedback.py
│   ├── services/                    # Business logic
│   │   ├── rag/
│   │   │   ├── retrieval.py         # Vector search + reranking
│   │   │   ├── embedding.py         # OpenAI embedding generation
│   │   │   ├── grounding.py         # Validation + hallucination detection
│   │   │   └── chunking.py          # Document processing
│   │   ├── modes/
│   │   │   ├── book_only.py
│   │   │   ├── selected_text.py
│   │   │   └── general_knowledge.py
│   │   ├── citation_service.py      # Citation generation + validation
│   │   └── conversation_service.py  # Session management
│   ├── db/                          # Database clients
│   │   ├── qdrant_client.py
│   │   ├── postgres_client.py
│   │   └── migrations/
│   ├── middleware/                  # Request processing
│   │   ├── rate_limiter.py
│   │   ├── logger.py
│   │   └── error_handler.py
│   └── api/                         # API routes
│       └── v1/
│           ├── chat.py              # /api/v1/chat endpoints
│           ├── feedback.py          # /api/v1/feedback endpoints
│           └── health.py            # /api/v1/health endpoints
├── tests/
│   ├── unit/                        # Unit tests
│   │   ├── test_retrieval.py
│   │   ├── test_modes.py
│   │   └── test_grounding.py
│   ├── integration/                 # Integration tests
│   │   ├── test_rag_pipeline.py
│   │   └── test_api_contracts.py
│   └── fixtures/                    # Test data
│       └── sample_chunks.json
├── scripts/                         # Utility scripts
│   ├── chunk_textbook.py            # Document processing
│   ├── upload_to_qdrant.py          # Vector DB population
│   └── run_migrations.py            # Database setup
└── requirements.txt

src/                                  # Frontend (Docusaurus + React)
├── components/
│   ├── ChatPanel/                   # Main chat interface
│   │   ├── index.tsx
│   │   ├── ChatInput.tsx
│   │   ├── MessageList.tsx
│   │   ├── ModeSelector.tsx
│   │   └── styles.module.css
│   ├── Citation/                    # Citation components
│   │   ├── CitationPreview.tsx
│   │   ├── CitationCard.tsx
│   │   └── styles.module.css
│   ├── TextSelection/               # Selection handling
│   │   ├── SelectionMenu.tsx
│   │   └── styles.module.css
│   └── KeyTerm/                     # Glossary tooltips
│       ├── TermHighlight.tsx
│       └── TermTooltip.tsx
├── services/
│   ├── chatApi.ts                   # API client
│   ├── feedbackApi.ts
│   └── sessionManager.ts            # Local state management
├── hooks/
│   ├── useChat.ts                   # Chat state + mutations
│   ├── useTextSelection.ts
│   └── useCitations.ts
├── types/
│   ├── chat.ts                      # TypeScript interfaces
│   ├── citation.ts
│   └── mode.ts
└── theme/                           # Docusaurus theme overrides
    ├── DocPage.tsx                  # Integrated chat panel
    └── Root.tsx                     # Global providers

docs/                                 # Textbook markdown content
├── chapter-01/
├── chapter-02/
└── chapter-03/

tests/e2e/                           # End-to-end tests
├── chat.spec.ts                     # User journeys
├── modes.spec.ts                    # Mode switching
└── citations.spec.ts                # Citation interactions
```

**Structure Decision**:
- **Backend (api/)**: FastAPI serverless functions with modular RAG services
- **Frontend (src/)**: Docusaurus with React components for chat interface
- **Docs (docs/)**: Textbook markdown content processed into chunks
- **Tests**: Separated by type (unit, integration, E2E) with appropriate tools

This structure supports:
- Independent backend/frontend deployment
- Clear separation of RAG logic, modes, and API
- Docusaurus integration via theme overrides
- Comprehensive testing at all levels

## Complexity Tracking

**Status**: No violations - all architectural decisions align with constitutional principles.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

## Next Steps

1. **Phase 0: Research** - Generate `research.md` to resolve technology choices and best practices
2. **Phase 1: Design** - Generate `data-model.md`, `contracts/`, and `quickstart.md`
3. **Phase 2: Tasks** - Use `/sp.tasks` command to generate implementation tasks
4. **Phase 3: Implementation** - Execute tasks using TDD approach
