# Tasks: RAG-Powered Textbook Chatbot

**Feature ID:** 002-rag-chatbot
**Input**: Design documents from `/specs/002-rag-chatbot/`
**Prerequisites**: spec.md ✅, plan.md ✅

**Branch**: `002-rag-chatbot`
**Created**: 2026-02-05
**Status**: Ready for Implementation

---

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, etc.)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with:
- **Backend API**: `api/src/` (Python/FastAPI)
- **Frontend**: `src/` (React/TypeScript/Docusaurus)
- **Shared**: `shared/` (OpenAPI specs, types)
- **Tests**: `api/tests/` and `src/__tests__/`

---

## User Stories (Extracted from spec.md)

**US1 (P1)**: As a student, I can ask questions in Book-Only mode and receive accurate, citation-backed answers derived exclusively from textbook content
**US2 (P2)**: As a student, I can select text and ask questions about only that selected content without semantic expansion
**US3 (P2)**: As a student, I can opt into General Knowledge mode to get AI-enhanced answers with clear warnings
**US4 (P1)**: As a student, I can click citations to view source text and scroll to the referenced location in the textbook
**US5 (P3)**: As an administrator, I can monitor chatbot performance, error rates, and usage metrics in real-time
**US6 (P1)**: As a student, I receive explicit error messages when the system cannot answer my question

---

## Phase 0: Research & Validation (3-5 days)

**Purpose**: Validate technology choices and establish baseline architecture

### Research Experiments

- [X] T001 [P] [Phase0] Document vector database evaluation in specs/002-rag-chatbot/research.md - compare Qdrant, Pinecone, Weaviate on latency, metadata filtering, free tier limits
- [X] T002 [P] [Phase0] Document embedding model selection in specs/002-rag-chatbot/research.md - benchmark OpenAI text-embedding-3-small vs 3-large on MTEB, cost, latency
- [X] T003 [P] [Phase0] Document reranking strategy in specs/002-rag-chatbot/research.md - measure cross-encoder impact on relevance (NDCG@3 target: 0.85+)
- [X] T004 [P] [Phase0] Document serverless platform selection in specs/002-rag-chatbot/research.md - compare Vercel, Fly.io, AWS Lambda on cold start, timeout, Python support
- [X] T005 [P] [Phase0] Document chunking strategy in specs/002-rag-chatbot/research.md - validate semantic chunking with 10% overlap achieves >85% precision@3

### Validation Experiments

- [ ] T006 [Phase0] Experiment: Chunk size optimization - generate chunks at 256, 512, 1024, 2048 tokens and measure Precision@3 on 50 ground-truth Q&A pairs
- [ ] T007 [Phase0] Experiment: Reranking impact - A/B test vector search vs. vector+reranking on 100 queries, measure NDCG@3 improvement
- [ ] T008 [Phase0] Experiment: Cold start mitigation - measure Vercel function pre-warming reduces TTFB from 1.2s to <500ms

### Architecture Decision Records

- [X] T009 [P] [Phase0] Create ADR: specs/002-rag-chatbot/adr/001-vector-db-selection.md - document decision, alternatives, rationale
- [X] T010 [P] [Phase0] Create ADR: specs/002-rag-chatbot/adr/002-embedding-model-choice.md - document decision, cost analysis, accuracy trade-offs
- [X] T011 [P] [Phase0] Create ADR: specs/002-rag-chatbot/adr/003-serverless-platform-choice.md - document Vercel primary with Fly.io fallback

**Checkpoint Phase 0**: Research complete, technology stack validated, ADRs documented

---

## Phase 1: Design & Architecture (5-7 days)

**Purpose**: Define data models, API contracts, and system interfaces


### Data Models

- [X] T012 [P] [Phase1] Document data models in specs/002-rag-chatbot/data-model.md - define Chunk, ChunkMetadata, ChatRequest, ChatResponse, Citation schemas
- [X] T013 [P] [Phase1] Document database schemas in specs/002-rag-chatbot/data-model.md - Qdrant collection schema (1536 dims, cosine), Postgres tables (chunk_metadata, query_logs, analytics)
- [X] T014 [P] [Phase1] Create Pydantic models in api/src/models/chunk.py - Chunk and ChunkMetadata classes with validation
- [X] T015 [P] [Phase1] Create Pydantic models in api/src/models/chat_request.py - ChatRequest, AnswerMode enum, QueryContext, QueryOptions with Field validation
- [X] T016 [P] [Phase1] Create Pydantic models in api/src/models/chat_response.py - ChatResponse, Source, ResponseMetadata classes
- [X] T017 [P] [Phase1] Create Pydantic models in api/src/models/citation.py - Citation model with confidence scoring

### API Contracts

- [X] T018 [Phase1] Document API contracts in specs/002-rag-chatbot/api-contracts.md - define all endpoints, request/response schemas, error codes, rate limits
- [X] T019 [Phase1] Create OpenAPI 3.1 spec in shared/openapi.yaml - complete specification with examples, authentication, error responses
- [X] T020 [P] [Phase1] Create TypeScript types in src/types/chat.ts - mirror API contracts for frontend
- [X] T021 [P] [Phase1] Create TypeScript types in src/types/citation.ts - citation and source types

### System Architecture

- [X] T022 [Phase1] Document system architecture in specs/002-rag-chatbot/architecture.md - complete diagram with component interactions, data flow, deployment model
- [X] T023 [Phase1] Document RAG pipeline flow in specs/002-rag-chatbot/architecture.md - 11-step flow from query to response with validation checkpoints

**Checkpoint Phase 1**: All design artifacts complete, ready for implementation

---

## Phase 2: Infrastructure Setup (2-3 days)

**Purpose**: Provision managed services and configure deployment environment

**⚠️ CRITICAL**: No implementation work can begin until this phase is complete

### External Service Provisioning

- [X] T024 [P] [Phase2] Provision Qdrant Cloud collection - 1536 dimensions, cosine similarity, metadata fields (chapter, section, page, heading)
- [X] T025 [P] [Phase2] Provision Neon Serverless Postgres database - create database, note connection URL
- [X] T026 [P] [Phase2] Setup Upstash Redis account - configure for rate limiting (edge KV store)
<!-- - [X] T027 [P] [Phase2] Setup Sentry project - configure for error tracking and alerting -->
- [X] T028 [P] [Phase2] Obtain OpenAI API key - verify quota for embeddings (text-embedding-3-small) and LLM (gpt-4-turbo)

### Project Configuration

<!-- - [ ] T029 [Phase2] Setup Vercel project - link repository, configure Python runtime, set deployment branch to 002-rag-chatbot
- [ ] T030 [Phase2] Configure environment variables in Vercel - QDRANT_URL, QDRANT_API_KEY, NEON_DATABASE_URL, OPENAI_API_KEY, UPSTASH_REDIS_URL, SENTRY_DSN -->
- [ ] T031 [P] [Phase2] Create .env.example file at repository root - document all required environment variables with descriptions
<!-- - [ ] T032 [P] [Phase2] Create vercel.json in api/ - configure serverless function routes, timeout (30s), memory (512MB) -->

### Database Schema Creation

- [ ] T033 [Phase2] Create Postgres migration: api/src/db/migrations/001_create_chunk_metadata.sql - table for chapter, section, chunk_id, word_count, created_at
- [ ] T034 [Phase2] Create Postgres migration: api/src/db/migrations/002_create_query_logs.sql - table for request_id, query, mode, latency_ms, chunks_retrieved, timestamp
- [ ] T035 [Phase2] Create Postgres migration: api/src/db/migrations/003_create_analytics.sql - aggregated metrics table for monitoring
- [ ] T036 [Phase2] Run migrations against Neon database - verify schema creation

### Monitoring & Observability

<!-- - [ ] T037 [P] [Phase2] Configure Sentry SDK in api/src/main.py - integrate with FastAPI, set sample rate, environment tags
- [ ] T038 [P] [Phase2] Setup structured logging in api/src/middleware/logger.py - JSON format with request_id, timestamp, level, context
- [ ] T039 [P] [Phase2] Configure OpenTelemetry in api/src/main.py - trace spans for query processing, embedding, vector search, LLM generation -->

**Checkpoint Phase 2**: Infrastructure provisioned, database schema ready, monitoring configured - implementation can begin

---

## Phase 3: Document Processing Pipeline (3-4 days)

**Purpose**: Ingest textbook content, chunk, embed, and upload to vector database

### Content Extraction

- [ ] T040 [Phase3] Create script: api/scripts/extract_markdown.py - extract all markdown files from TextBook/docs/, preserve directory structure
- [ ] T041 [Phase3] Create script: api/scripts/parse_metadata.py - extract chapter, section, heading hierarchy from frontmatter and headings

### Semantic Chunking

- [ ] T042 [Phase3] Create chunking script: api/scripts/chunk_textbook.py - use LangChain RecursiveCharacterTextSplitter, 512-1024 tokens, 10% overlap
- [ ] T043 [Phase3] Implement metadata preservation in api/scripts/chunk_textbook.py - attach chapter, section, page, heading to each chunk
- [ ] T044 [Phase3] Implement deduplication in api/scripts/chunk_textbook.py - merge identical chunks, track provenance

### Embedding Generation

- [ ] T045 [Phase3] Create embedding service: api/src/services/embedding_service.py - OpenAI text-embedding-3-small client with error handling and retry
- [ ] T046 [Phase3] Create batch embedding script: api/scripts/generate_embeddings.py - process chunks in batches of 100, rate limit 3000 tokens/min
- [ ] T047 [Phase3] Add embedding caching in api/scripts/generate_embeddings.py - cache embeddings locally to avoid re-generation on retry

### Vector Database Upload

- [ ] T048 [Phase3] Create Qdrant client: api/src/db/qdrant_client.py - connection management, collection operations, error handling
- [ ] T049 [Phase3] Create upload script: api/scripts/upload_to_qdrant.py - batch upload chunks + embeddings + metadata to Qdrant collection
- [ ] T050 [Phase3] Create metadata sync script: api/scripts/sync_postgres.py - sync chunk metadata (chunk_id, chapter, section) to Postgres for audit trail

### Validation

- [ ] T051 [Phase3] Create validation script: api/scripts/validate_chunks.py - verify chunk coverage (all chapters), overlap correctness, metadata completeness
- [ ] T052 [Phase3] Run ingestion pipeline end-to-end - extract → chunk → embed → upload → validate
- [ ] T053 [Phase3] Create ingestion runbook in specs/002-rag-chatbot/runbooks/ingestion.md - document process, troubleshooting, re-run procedure

**Checkpoint Phase 3**: Textbook fully ingested, embeddings in Qdrant, metadata in Postgres, validation passed

---

## Phase 4: Backend API - Core Services (5-6 days)

**Purpose**: Implement RAG pipeline services (retrieval, generation, citation, mode routing)

### Embedding Service

- [ ] T054 [US1] [Phase4] Implement embedding service in api/src/services/embedding_service.py - text → embeddings with OpenAI API, caching, error handling, retry with exponential backoff

### Retrieval Service

- [ ] T055 [US1] [Phase4] Implement vector search in api/src/services/retrieval_service.py - query embedding → Qdrant similarity search (top_k=10-20, similarity_threshold=0.7)
- [ ] T056 [US1] [Phase4] Implement metadata filtering in api/src/services/retrieval_service.py - support chapter_filter from QueryContext
- [ ] T057 [US1] [Phase4] Implement reranking in api/src/services/retrieval_service.py - cross-encoder (ms-marco-MiniLM-L-12-v2) rescores top_k, selects top_n=3-5
- [ ] T058 [US1] [Phase4] Implement context window enforcement in api/src/services/retrieval_service.py - fit chunks into 8k token LLM context, truncate or summarize if overflow

### Generation Service

- [ ] T059 [US1] [Phase4] Implement LLM orchestration in api/src/services/generation_service.py - OpenAI GPT-4 Turbo client with streaming (SSE), temperature=0.3
- [ ] T060 [US1] [Phase4] Implement prompt construction in api/src/services/generation_service.py - system prompt (mode instructions + grounding rules), user query, context (chunks with IDs)
- [ ] T061 [US1] [Phase4] Implement streaming response in api/src/services/generation_service.py - Server-Sent Events for time-to-first-token <500ms

### Citation Service

- [ ] T062 [US1,US4] [Phase4] Implement citation parsing in api/src/services/citation_service.py - extract chunk IDs from generated answer
- [ ] T063 [US1,US4] [Phase4] Implement citation validation in api/src/services/citation_service.py - verify chunk IDs exist in Qdrant, check chunk content supports claim (grounding check)
- [ ] T064 [US1,US4] [Phase4] Implement confidence scoring in api/src/services/citation_service.py - Low/Medium/High based on similarity score and cross-encoder rank

### Mode Router

- [ ] T065 [US1,US2,US3] [Phase4] Implement mode validation in api/src/services/mode_router.py - validate AnswerMode enum, enforce mode boundaries (no silent switching)
- [ ] T066 [US2] [Phase4] Implement Selected-Text-Only mode in api/src/services/mode_router.py - extract selection boundaries, use only selected_text as context (no semantic expansion)
- [ ] T067 [US3] [Phase4] Implement General Knowledge mode in api/src/services/mode_router.py - opt-in flag validation, inject disclaimer into response
- [ ] T068 [US6] [Phase4] Implement failure handling in api/src/services/mode_router.py - explicit error messages per scenario (no relevant chunks, partial relevance, ambiguous query, context overflow)

**Checkpoint Phase 4**: All core services implemented and unit tested

---

## Phase 5: Backend API - Routes & Middleware (3-4 days)

**Purpose**: Expose API endpoints, implement rate limiting, logging, authentication

### API Routes

- [ ] T069 [US1] [Phase5] Implement POST /api/v1/chat in api/src/routes/chat.py - integrate mode_router → retrieval → generation → citation services, return ChatResponse
- [ ] T070 [P] [Phase5] Implement GET /api/v1/health in api/src/routes/health.py - return {status: "healthy", version: "1.0.0"}
- [ ] T071 [P] [Phase5] Implement GET /api/v1/chunks in api/src/routes/chunks.py - admin-only endpoint for chunk inspection (pagination support)

### Middleware

- [ ] T072 [US1,US5] [Phase5] Implement rate limiter in api/src/middleware/rate_limiter.py - Upstash Redis integration, 10/hour (anonymous), 100/hour (authenticated), 1000/hour (premium), burst allowance 2x for 10s
- [ ] T073 [P] [US5] [Phase5] Implement structured logger in api/src/middleware/logger.py - JSON format, request_id, user_id, mode, query, chunks_retrieved, response_time_ms
- [ ] T074 [P] [Phase5] [Phase5] Implement auth middleware in api/src/middleware/auth_middleware.py - optional JWT validation, extract user_id for rate limiting tier
- [ ] T075 [Phase5] Implement schema validation middleware in api/src/middleware/validator.py - validate request/response against Pydantic models, return 422 on validation error

### Error Handling

- [ ] T076 [US6] [Phase5] Implement global error handler in api/src/main.py - catch exceptions, return structured error response (code, message, details, timestamp, request_id)
- [ ] T077 [US6] [Phase5] Define error taxonomy in api/src/models/errors.py - RETRIEVAL_FAILED, GENERATION_FAILED, RATE_LIMIT_EXCEEDED, INVALID_MODE, etc.

### Database Clients

- [ ] T078 [P] [Phase5] Implement Qdrant client singleton in api/src/db/qdrant_client.py - connection pooling, error handling, reconnection logic
- [ ] T079 [P] [Phase5] Implement Postgres client singleton in api/src/db/postgres_client.py - psycopg3 async connection, query execution, transaction management

### FastAPI Application

- [ ] T080 [Phase5] Create FastAPI app in api/src/main.py - integrate all routes, middleware, error handlers, CORS configuration, startup/shutdown events
- [ ] T081 [Phase5] Configure CORS in api/src/main.py - allow Docusaurus origin (localhost:3000, production domain), credentials support

**Checkpoint Phase 5**: Backend API fully functional, all endpoints exposed, middleware operational

---

## Phase 6: Frontend Integration (4-5 days)

**Purpose**: Embed chatbot UI into Docusaurus textbook, implement citation linking

### API Client

- [ ] T082 [US1] [Phase6] Create API client in src/services/chatApi.ts - POST /api/v1/chat with TypeScript types, error handling, timeout (10s)
- [ ] T083 [US1] [Phase6] Create React Query hook in src/hooks/useChat.ts - useMutation for chat queries, loading states, error handling, retry logic

### Chat Widget Components

- [ ] T084 [US1] [Phase6] Create ChatWidget component in src/components/ChatWidget/index.tsx - main container, message list, input area, mode selector
- [ ] T085 [US1] [Phase6] Create ChatInput component in src/components/ChatWidget/ChatInput.tsx - textarea with character limit (500), submit button, loading spinner
- [ ] T086 [US1] [Phase6] Create ChatMessage component in src/components/ChatWidget/ChatMessage.tsx - message bubble with answer text, citations, timestamp, mode indicator
- [ ] T087 [US1,US4] [Phase6] Create CitationBadge component in src/components/ChatWidget/CitationBadge.tsx - clickable badge (superscript number), expandable preview (accordion), confidence indicator
- [ ] T088 [US1,US2,US3] [Phase6] Create ModeSelector component in src/components/ChatWidget/ModeSelector.tsx - radio buttons or dropdown for Book-Only / Selected-Text / General Knowledge

### Text Selection Components

- [ ] T089 [US2] [Phase6] Create SelectionCapture component in src/components/TextSelection/SelectionCapture.tsx - listen to text selection events, extract boundaries, show "Ask about selection" button
- [ ] T090 [US2] [Phase6] Create SelectionHighlight component in src/components/TextSelection/SelectionHighlight.tsx - visual highlight for selected text when in Selected-Text mode
- [ ] T091 [US2] [Phase6] Create useTextSelection hook in src/hooks/useTextSelection.ts - manage selection state, store selected_text, chapter context

### Citation Interaction

- [ ] T092 [US4] [Phase6] Implement citation click handler in src/hooks/useCitations.ts - map chunk_id to textbook location (chapter, section, paragraph)
- [ ] T093 [US4] [Phase6] Implement scroll-to-source in src/hooks/useCitations.ts - smooth scroll to textbook location, highlight referenced paragraph (200ms animation)
- [ ] T094 [US4] [Phase6] Create citation preview modal in src/components/ChatWidget/CitationPreview.tsx - show full chunk text, chapter/section context, confidence score

### Visual Styling

- [ ] T095 [US1,US2,US3] [Phase6] Create ChatWidget styles in src/components/ChatWidget/styles.module.css - blue accent for Book-Only, purple for Selected-Text, yellow/amber for General Knowledge
- [ ] T096 [US3] [Phase6] Implement General Knowledge warning banner in src/components/ChatWidget/ChatMessage.tsx - "⚠️ General AI Knowledge: This answer is not grounded in your textbook and may contain inaccuracies"
- [ ] T097 [Phase6] Implement mobile responsive design in src/components/ChatWidget/styles.module.css - full functionality on mobile devices, collapsible chat widget

### Integration with Docusaurus

- [ ] T098 [Phase6] Integrate ChatWidget into Docusaurus in src/theme/DocItem.tsx - embed widget in sidebar or floating button
- [ ] T099 [Phase6] Create chat widget toggle button in src/components/ChatWidget/ToggleButton.tsx - show/hide widget, preserve chat history during session
- [ ] T100 [Phase6] Implement persistent chat history in src/hooks/useChat.ts - store messages in sessionStorage, clear on page reload

**Checkpoint Phase 6**: Frontend fully integrated, chat widget embedded, citations functional

---

## Phase 7: Testing & Quality Assurance (5-6 days)

**Purpose**: Comprehensive testing across all layers and user journeys

### Unit Tests (Backend)

- [ ] T101 [P] [US1] [Phase7] Unit tests for embedding_service in api/tests/unit/test_embedding_service.py - mock OpenAI API, test caching, error handling, retry logic
- [ ] T102 [P] [US1] [Phase7] Unit tests for retrieval_service in api/tests/unit/test_retrieval_service.py - mock Qdrant, test vector search, reranking, context window enforcement
- [ ] T103 [P] [US1] [Phase7] Unit tests for generation_service in api/tests/unit/test_generation_service.py - mock OpenAI API, test prompt construction, streaming, temperature
- [ ] T104 [P] [US1,US4] [Phase7] Unit tests for citation_service in api/tests/unit/test_citation_service.py - test citation parsing, validation, grounding check, confidence scoring
- [ ] T105 [P] [US1,US2,US3] [Phase7] Unit tests for mode_router in api/tests/unit/test_mode_router.py - test mode validation, boundary enforcement, failure handling

### Integration Tests (Backend)

- [ ] T106 [US1] [Phase7] Integration test for RAG pipeline in api/tests/integration/test_rag_pipeline.py - end-to-end query → retrieval → generation → citation with real Qdrant (testcontainers)
- [ ] T107 [US1,US2,US3] [Phase7] Integration test for mode enforcement in api/tests/integration/test_mode_enforcement.py - verify mode boundaries never violated, no cross-mode contamination
- [ ] T108 [US6] [Phase7] Integration test for failure scenarios in api/tests/integration/test_failures.py - no relevant chunks, partial relevance, ambiguous query, context overflow

### Contract Tests (API)

- [ ] T109 [Phase7] Contract tests with Schemathesis in api/tests/contract/test_openapi.py - validate all endpoints against shared/openapi.yaml, test request/response schemas, error codes

### End-to-End Tests (Frontend)

- [ ] T110 [US1] [Phase7] E2E test for Book-Only mode in src/__tests__/e2e/test_book_only_mode.spec.ts - Playwright test: submit query, verify citation links, check answer grounding
- [ ] T111 [US2] [Phase7] E2E test for Selected-Text mode in src/__tests__/e2e/test_selected_text_mode.spec.ts - Playwright test: select text, submit query, verify only selection used
- [ ] T112 [US3] [Phase7] E2E test for General Knowledge mode in src/__tests__/e2e/test_general_knowledge_mode.spec.ts - Playwright test: activate mode, verify warning banner, check disclaimer
- [ ] T113 [US4] [Phase7] E2E test for citation interaction in src/__tests__/e2e/test_citations.spec.ts - Playwright test: click citation badge, verify scroll-to-source, check highlight animation

### Load & Performance Tests

- [ ] T114 [Phase7] Load test with Locust in api/tests/load/locustfile.py - simulate 100 concurrent users, verify p95 latency <3s, p99 latency <5s
- [ ] T115 [Phase7] Rate limiting test in api/tests/load/test_rate_limits.py - verify 10/hour (anonymous), 100/hour (authenticated), 1000/hour (premium), burst allowance
- [ ] T116 [Phase7] Cold start performance test in api/tests/performance/test_cold_start.py - measure Vercel function initialization time <1s, TTFB <500ms

### Test Data & Ground Truth

- [ ] T117 [Phase7] Create test dataset in api/tests/fixtures/ground_truth_qa.json - 50+ Q&A pairs with expected chunk_ids, confidence scores
- [ ] T118 [Phase7] Create edge case queries in api/tests/fixtures/edge_cases.json - ambiguous, malformed, adversarial queries for failure testing

### Test Coverage

- [ ] T119 [Phase7] Measure unit test coverage with pytest-cov - verify >80% coverage for all services, models, routes
- [ ] T120 [Phase7] Measure integration test coverage - verify all user journeys tested (US1-US6)
- [ ] T121 [Phase7] Create coverage report in api/tests/coverage/ - HTML report for review

**Checkpoint Phase 7**: All tests passing, coverage >80%, performance benchmarks met

---

## Phase 8: Deployment & Monitoring (3-4 days)

**Purpose**: Production deployment, monitoring, alerting, documentation

### Deployment Configuration

- [ ] T122 [Phase8] Finalize vercel.json configuration - production routes, function memory, timeout, environment variables
- [ ] T123 [Phase8] Create CI/CD pipeline in .github/workflows/deploy.yml - test → build → deploy on push to 002-rag-chatbot branch
- [ ] T124 [Phase8] Configure pre-commit hooks in .pre-commit-config.yaml - linting (ruff), formatting (black), type checking (mypy)

### Monitoring & Observability

- [ ] T125 [US5] [Phase8] Setup Sentry dashboards - error rate by type, latency percentiles (p50, p95, p99), request volume
- [ ] T126 [US5] [Phase8] Configure OpenTelemetry export - trace spans to Vercel Analytics or external OTLP collector
- [ ] T127 [US5] [Phase8] Create custom metrics in api/src/middleware/logger.py - retrieval success rate, citation accuracy, hallucination rate (manual sampling)

### Alerting

- [ ] T128 [US5] [Phase8] Configure Sentry alerts - error rate >5% → page on-call, latency p95 >5s → warning, vector DB unavailable → critical
- [ ] T129 [US5] [Phase8] Setup uptime monitoring with Vercel - health check endpoint, alerting on downtime

### Documentation

- [ ] T130 [P] [Phase8] Create API documentation with Swagger UI in api/src/main.py - auto-generate from OpenAPI spec
- [ ] T131 [P] [Phase8] Create runbook for common incidents in specs/002-rag-chatbot/runbooks/incidents.md - OpenAI rate limit exceeded, Qdrant timeout, cold start >3s
- [ ] T132 [P] [Phase8] Create quickstart guide in specs/002-rag-chatbot/quickstart.md - local development setup, environment variables, running tests
- [ ] T133 [P] [Phase8] Update main README.md - add RAG chatbot section, architecture diagram, deployment instructions

### Security Hardening

- [ ] T134 [Phase8] Implement input validation in api/src/middleware/validator.py - max query length 500 characters, profanity detection, injection detection
- [ ] T135 [Phase8] Implement CAPTCHA for suspicious patterns in api/src/middleware/rate_limiter.py - trigger CAPTCHA on rapid failed queries
- [ ] T136 [Phase8] Implement IP-based temporary blocks in api/src/middleware/rate_limiter.py - block IP for 1 hour on 10+ rate limit violations
- [ ] T137 [Phase8] Verify secret management - no API keys in client-side code, environment variables only, secret rotation capability

### Deployment

- [ ] T138 [Phase8] Deploy backend to Vercel production - verify all endpoints accessible, rate limiting operational
- [ ] T139 [Phase8] Deploy frontend to Vercel production - verify ChatWidget embedded, citations functional, modes working
- [ ] T140 [Phase8] Run smoke tests in production - submit test queries, verify responses, check citations, validate monitoring

**Checkpoint Phase 8**: Production deployment complete, monitoring operational, documentation published

---

## Phase 9: Validation & Launch (2-3 days)

**Purpose**: Final validation against success criteria, user acceptance testing

### Technical Validation

- [ ] T141 [Phase9] Validate uptime >99.9% over 7 days - monitor Vercel analytics
- [ ] T142 [Phase9] Validate API latency p95 <3s, p99 <5s - check Vercel performance metrics
- [ ] T143 [Phase9] Validate citation accuracy >95% - manual sampling of 100 responses
- [ ] T144 [Phase9] Validate hallucination rate <5% - grounding check violations analysis
- [ ] T145 [Phase9] Validate error rate <1% under normal load - Sentry metrics review
- [ ] T146 [Phase9] Validate mode boundary enforcement - automated test suite (zero violations)

### Quality Validation

- [ ] T147 [Phase9] User acceptance testing - 10 students test chatbot, provide feedback
- [ ] T148 [Phase9] Citation verification - verify all citations link to actual chunks, content supports claims
- [ ] T149 [Phase9] Edge case testing - test ambiguous queries, adversarial inputs, context overflow scenarios

### Operational Validation

- [ ] T150 [Phase9] Verify one-command deployment - test Vercel CLI deployment from local
- [ ] T151 [Phase9] Verify automated rollback capability - test rollback to previous version
- [ ] T152 [Phase9] Verify zero-downtime updates - deploy new version while monitoring uptime
- [ ] T153 [Phase9] Verify self-service troubleshooting - test runbook procedures

### Launch Readiness

- [ ] T154 [Phase9] Create launch announcement - blog post, changelog, feature highlights
- [ ] T155 [Phase9] Conduct team demo - walkthrough of all features, Q&A session
- [ ] T156 [Phase9] Create user tutorial - video or interactive guide for students
- [ ] T157 [Phase9] Enable chatbot in production - make widget visible to all users

**Checkpoint Phase 9**: Feature launched, success criteria validated, users onboarded

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 0 (Research)**: No dependencies - can start immediately
- **Phase 1 (Design)**: Depends on Phase 0 research completion
- **Phase 2 (Infrastructure)**: Depends on Phase 1 design completion - BLOCKS all implementation
- **Phase 3 (Document Processing)**: Depends on Phase 2 infrastructure setup
- **Phase 4 (Core Services)**: Depends on Phase 2 infrastructure setup - can run in parallel with Phase 3 after infrastructure ready
- **Phase 5 (Routes & Middleware)**: Depends on Phase 4 core services completion
- **Phase 6 (Frontend)**: Depends on Phase 5 backend API completion
- **Phase 7 (Testing)**: Depends on Phase 4, 5, 6 completion (requires full implementation)
- **Phase 8 (Deployment)**: Depends on Phase 7 testing completion
- **Phase 9 (Validation)**: Depends on Phase 8 deployment completion

### User Story Dependencies

- **US1 (Book-Only mode)**: Foundation for all other stories - MUST complete first
- **US2 (Selected-Text mode)**: Depends on US1 (uses same retrieval/generation services)
- **US3 (General Knowledge mode)**: Depends on US1 (adds mode to existing pipeline)
- **US4 (Citation interaction)**: Depends on US1 (requires citations to exist)
- **US5 (Monitoring)**: Cross-cutting - implement alongside US1-US4
- **US6 (Error handling)**: Cross-cutting - implement alongside US1-US4

### Critical Path

1. Phase 0 → Phase 1 → Phase 2 (CRITICAL - blocks all implementation)
2. Phase 2 → Phase 3 (document processing)
3. Phase 2 → Phase 4 (core services) → Phase 5 (API routes) → Phase 6 (frontend)
4. Phase 3, 4, 5, 6 → Phase 7 (testing) → Phase 8 (deployment) → Phase 9 (validation)

### Parallel Opportunities

**Within Phase 0**: All research tasks (T001-T005) and ADRs (T009-T011) can run in parallel
**Within Phase 1**: All model creation (T014-T017), API contract docs (T018-T021) can run in parallel
**Within Phase 2**: All service provisioning (T024-T028) and config tasks (T031-T032) can run in parallel
**Within Phase 4**: Embedding service (T054), retrieval service (T055-T058), generation service (T059-T061) can run in parallel initially
**Within Phase 6**: API client (T082-T083), chat components (T084-T088), selection components (T089-T091) can run in parallel
**Within Phase 7**: All unit tests (T101-T105), documentation tasks (T130-T133) can run in parallel

---

## Implementation Strategy

### MVP First (Critical Path to First Demo)

1. **Phase 0**: Research validation (3 days)
2. **Phase 1**: Design artifacts (5 days)
3. **Phase 2**: Infrastructure setup (2 days) - CRITICAL BLOCKER
4. **Phase 3**: Document ingestion (3 days)
5. **Phase 4**: Core services for US1 only (T054-T064) (4 days)
6. **Phase 5**: API routes for US1 only (T069, T072-T080) (3 days)
7. **Phase 6**: Frontend for US1 only (T082-T088, T092-T099) (4 days)
8. **Phase 7**: Basic testing (T106, T110, T119) (2 days)
9. **Phase 8**: Deploy MVP (T122-T124, T138-T140) (2 days)

**MVP Timeline**: 28 days (US1 Book-Only mode functional)

### Incremental Delivery

After MVP (US1), add features incrementally:
- **Sprint 2**: Add US2 (Selected-Text mode) + US4 (Citation interaction) - 5 days
- **Sprint 3**: Add US3 (General Knowledge mode) - 3 days
- **Sprint 4**: Add US5 (Monitoring) + US6 (Error handling) - 4 days
- **Sprint 5**: Full testing + deployment (Phase 7-9) - 7 days

**Full Feature Timeline**: 47 days (6.7 weeks)

### Quality Gates

- After Phase 2: Infrastructure smoke test (can connect to all services)
- After Phase 4: Core services unit tests passing (>80% coverage)
- After Phase 6: Frontend E2E tests passing (all user journeys)
- After Phase 7: Performance benchmarks met (p95 <3s)
- After Phase 8: Production smoke tests passing
- After Phase 9: User acceptance criteria met

---

## Success Metrics

### Technical Metrics
- [ ] API latency p95 <3s, p99 <5s
- [ ] Citation accuracy >95% (manual sampling)
- [ ] Hallucination rate <5%
- [ ] Test coverage >80%
- [ ] Uptime >99.9% over 30 days
- [ ] Mode boundary violations: 0

### User Experience Metrics
- [ ] User satisfaction >4.0/5.0
- [ ] Query success rate >90%
- [ ] Citation click-through rate >30%
- [ ] Time to first token <500ms (p95)

### Operational Metrics
- [ ] One-command deployment
- [ ] Zero-downtime updates
- [ ] Self-service troubleshooting
- [ ] Cost per query <$0.05

---

## Notes

- **[P]** = Parallelizable (different files, no dependencies)
- **[Story]** = User story label (US1-US6) for traceability
- **Phases 0-2** are blocking - no implementation can begin until infrastructure is ready
- **US1 (Book-Only mode)** is the critical path - all other stories depend on it
- Commit after each task or logical group
- Run tests continuously (TDD where applicable)
- Document decisions in ADRs when making significant architectural choices

---

**Tasks Generated**: 157 tasks across 9 phases
**Estimated Timeline**: 4-6 weeks (28 days MVP, 47 days full feature)
**Status**: Ready for Implementation
