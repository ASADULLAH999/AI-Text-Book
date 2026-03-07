# Tasks — RAG-Powered Textbook Chatbot

## Document Control

**Version:** 1.0
**Created**: 2026-02-14
**Related**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md)

---

## Task Format

Each task follows this format:

```
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**Components**:

- `- [ ]`: Checkbox (required)
- `[TaskID]`: Sequential ID (T001, T002, etc.)
- `[P]`: Parallelizable marker (optional, only if task can run in parallel)
- `[Story]`: User story label (e.g., [US1], [US2] - required for user story phases only)
- Description: Clear action with exact file path

**Status**: 📋 Ready | 🚧 In Progress | ✅ Complete | ⏸️ Blocked

---

## Implementation Strategy

**MVP Scope**: User Story 1 (P1) - Ask Questions About Textbook Content

This is the minimum viable product that delivers core value. Complete Phase 1 (Setup), Phase 2 (Foundational), and Phase 3 (US1) for a functional chatbot.

**Incremental Delivery**:

1. **Sprint 1**: Phases 1-3 (MVP - Book-Only Q&A with citations)
2. **Sprint 2**: Phases 4-5 (P2 features - Text selection + Mode switching)
3. **Sprint 3**: Phases 6-7 (P3 features - Tone control + Key terms)
4. **Sprint 4**: Phase 8 (Polish + optimization)

---

## Phase 1 — Setup & Infrastructure

**Goal**: Initialize project structure, provision managed services, configure development environment.

**Independent Test**: `npm run build` succeeds, services reachable via API calls.

### Tasks

- [x] T001 Initialize project structure with api/ and src/ directories
- [x] T002 Create api/requirements.txt with FastAPI, Qdrant client, Neon client, OpenAI SDK
- [x] T003 Create package.json with React 18.x, Docusaurus 3.x, TypeScript 5.x
- [x] T004 [P] Provision Qdrant Cloud collection (textbook_chunks, 3072 dims, HNSW index) - Script: api/scripts/provision_qdrant.py
- [x] T005 [P] Provision Neon Serverless Postgres database - Script: api/scripts/provision_neon.py
- [x] T006 [P] Create .env.template with required environment variables
- [x] T007 Create api/src/config.py for environment configuration
- [x] T008 [P] Set up GitHub repository with branch protection rules - Script: .github/scripts/setup_branch_protection.sh
- [x] T009 Create .gitignore for Python and Node.js
- [x] T010 Create README.md with setup instructions

**Acceptance**: All infrastructure provisioned, dependencies installed, environment configured.

---

## Phase 2 — Foundational Components

**Goal**: Build blocking prerequisites required by all user stories - content ingestion, database schemas, core RAG pipeline.

**Independent Test**: Sample textbook chapter ingested, embeddings generated, vector search returns results.

### Tasks

- [x] T011 Create api/src/db/postgres_client.py with connection pooling
- [x] T012 Create api/src/db/qdrant_client.py with async search methods
- [x] T013 Create database schema in api/src/db/migrations/001_initial_schema.sql
- [x] T014 Create api/scripts/chunk_textbook.py for semantic chunking (512-1024 tokens, 10-15% overlap)
- [x] T015 Create api/scripts/generate_embeddings.py using text-embedding-3-large
- [x] T016 Create api/scripts/upload_to_qdrant.py for vector indexing
- [x] T017 Create api/scripts/parse_metadata.py to extract chapter/section hierarchy
- [x] T018 Create api/scripts/validate_chunks.py to verify chunk quality
- [x] T019 [P] Create api/src/models/chunk.py data model
- [x] T020 [P] Create api/src/models/conversation.py data model
- [x] T021 [P] Create api/src/models/message.py data model
- [x] T022 [P] Create api/src/models/citation.py data model
- [x] T023 Create api/scripts/run_migrations.py for database setup
- [x] T024 Process sample textbook content (docs/chapter-01/) into chunks
- [x] T025 Validate ingestion pipeline with 100 sample chunks

**Acceptance**: Textbook content chunked, embedded, indexed in Qdrant with metadata in Postgres.

---

## Phase 3 — User Story 1 (P1): Ask Questions About Textbook Content

**Goal**: Enable students to ask questions and receive cited, accurate answers from textbook content.

**Independent Test**: Ask "What caused World War I?" → Receive cited answer with confidence scores and source links.

**User Story**: Students reading the textbook can ask questions and receive accurate, cited answers derived exclusively from the textbook content.

### Backend Tasks

- [x] T026 [US1] Create api/src/services/rag/embedding.py for query embedding
- [x] T027 [US1] Create api/src/services/rag/retrieval.py for vector search (top-k=20, threshold=0.7)
- [x] T028 [US1] Implement reranking in api/src/services/rag/retrieval.py (top-n=5)
- [x] T029 [US1] Create api/src/services/rag/grounding.py for validation and hallucination detection
- [x] T030 [US1] Create api/src/services/modes/book_only.py with strict grounding logic
- [x] T031 [US1] Create api/src/services/citation_service.py for citation generation and validation
- [x] T032 [US1] Create api/src/api/v1/chat.py with POST /api/v1/chat endpoint
- [x] T033 [US1] Implement request validation in api/src/middleware/request_validator.py
- [x] T034 [US1] Create api/src/middleware/logger.py for structured JSON logging
- [x] T035 [US1] Create api/src/middleware/error_handler.py with standard error format
- [x] T036 [US1] Implement streaming response support in api/src/api/v1/chat.py
- [x] T037 [US1] Create refusal message template in api/src/services/modes/book_only.py

### Frontend Tasks

- [x] T038 [P] [US1] Create src/types/chat.ts with Message, Conversation interfaces
- [x] T039 [P] [US1] Create src/types/citation.ts with Citation interface
- [x] T040 [P] [US1] Create src/types/mode.ts with Mode enum
- [x] T041 [US1] Create src/services/chatApi.ts API client with fetch wrapper
- [x] T042 [US1] Create src/hooks/useChat.ts for chat state management
- [x] T043 [US1] Create src/components/ChatPanel/index.tsx collapsible panel
- [x] T044 [US1] Create src/components/ChatPanel/ChatInput.tsx with 500 char limit
- [x] T045 [US1] Create src/components/ChatPanel/MessageList.tsx with scroll virtualization
- [x] T046 [US1] Create src/components/Citation/CitationCard.tsx for source preview
- [x] T047 [US1] Create src/components/Citation/CitationPreview.tsx for hover tooltip
- [x] T048 [US1] Integrate ChatPanel into src/theme/DocPage.tsx
- [x] T049 [US1] Add citation click handling to navigate to source location

### Testing Tasks

- [x] T050 [P] [US1] Create api/tests/unit/test_retrieval.py
- [x] T051 [P] [US1] Create api/tests/unit/test_grounding.py
- [x] T052 [P] [US1] Create api/tests/unit/test_citation.py
- [x] T053 [US1] Create api/tests/integration/test_rag_pipeline.py for end-to-end flow
- [x] T054 [US1] Create tests/e2e/chat.spec.ts for user journey testing
- [x] T055 [US1] Validate citation accuracy > 95% on 100 test queries
- [x] T056 [US1] Validate hallucination rate < 5% on 100 test queries

**Acceptance**: Students can ask questions in Book-Only mode, receive cited answers within 3s (p95), click citations to view sources.

---

## Phase 4 — User Story 2 (P2): Select Text for Contextual Questions

**Goal**: Enable students to highlight text and ask questions constrained to that selection.

**Independent Test**: Highlight paragraph → Click "Ask AI about this" → Receive answer using only selected text.

**User Story**: Students can highlight specific text passages and ask questions constrained to only that selection.

### Tasks

- [x] T057 [US2] Create src/hooks/useTextSelection.ts to detect text selection within 100ms
- [x] T058 [US2] Create src/components/TextSelection/SelectionMenu.tsx contextual menu
- [x] T059 [US2] Add "Ask AI about this" button with 200ms display latency
- [x] T060 [US2] Implement selection boundary validation (50-4,000 tokens)
- [x] T061 [US2] Create api/src/services/modes/selected_text.py with zero vector search
- [x] T062 [US2] Add selection metadata logging in api/src/middleware/logger.py
- [x] T063 [US2] Create insufficient context refusal template
- [x] T064 [US2] Update src/services/chatApi.ts to pass selection context
- [x] T065 [US2] Add selection preview in src/components/ChatPanel/ChatInput.tsx
- [x] T066 [P] [US2] Create api/tests/unit/test_selected_text_mode.py
- [x] T067 [US2] Create tests/e2e/text-selection.spec.ts
- [x] T068 [US2] Validate zero vector searches in Selected-Text mode

**Acceptance**: Students can highlight text, trigger "Ask AI", receive answers derived only from selection.

---

## Phase 5 — User Story 3 (P2): Use Different Answering Modes

**Goal**: Enable mode switching between Book-Only, Selected-Text-Only, and General Knowledge.

**Independent Test**: Switch to General Knowledge mode → See amber badge + disclaimer → Ask question → Receive broader answer.

**User Story**: Students can switch between three distinct answering modes based on their learning needs.

### Tasks

- [x] T069 [US3] Create src/components/ChatPanel/ModeSelector.tsx with three mode buttons
- [x] T070 [US3] Implement mode state persistence in sessionStorage
- [x] T071 [US3] Create api/src/services/modes/general_knowledge.py
- [x] T072 [US3] Add mode enum validation in api/src/api/v1/chat.py
- [x] T073 [US3] Create mode indicator UI (Book-Only: blue, Selected-Text: purple, General: amber)
- [x] T074 [US3] Add General Knowledge disclaimer banner
- [x] T075 [US3] Implement mode reset to Book-Only on new session
- [x] T076 [US3] Add mode switch logging in api/src/middleware/logger.py
- [x] T077 [US3] Create mode boundary enforcement in api/src/services/modes/**init**.py
- [x] T078 [P] [US3] Create api/tests/unit/test_modes.py
- [x] T079 [US3] Create tests/e2e/modes.spec.ts
- [x] T080 [US3] Validate mode boundaries with 100+ test queries

**Acceptance**: Students can switch modes, see clear indicators, mode boundaries never violated (<1%).

---

## Phase 6 — User Story 4 (P3): Customize Response Tone

**Goal**: Enable tone selection to match student learning level.

**Independent Test**: Select "Beginner-Friendly" → Ask technical question → Receive simple language with analogies.

**User Story**: Students can select response tone to match their learning level and preferences.

### Tasks

- [x] T081 [US4] Create src/components/ChatPanel/ToneSelector.tsx dropdown
- [x] T082 [US4] Add tone enum (Academic, Beginner-Friendly, Concise, Detailed, Neutral)
- [x] T083 [US4] Implement tone persistence in localStorage
- [x] T084 [US4] Create tone prompt modifiers in api/src/services/prompts/tone_modifiers.py
- [x] T085 [US4] Validate tone doesn't alter citations in api/src/services/citation_service.py
- [x] T086 [US4] Add tone parameter to chat API request schema
- [x] T087 [P] [US4] Create api/tests/unit/test_tone_modifiers.py
- [x] T088 [US4] Validate citation consistency across tones (100 queries)

**Acceptance**: Students can select tone, language style changes while citations and accuracy remain consistent.

---

## Phase 7 — User Story 5 (P3): Explore Key Terms

**Goal**: Enable term exploration via hover tooltips and expandable cards.

**Independent Test**: Hover over "photosynthesis" → See definition tooltip → Click "More about photosynthesis" → Chat opens with query.

**User Story**: Students can hover over or click domain-specific terms to see definitions without interrupting reading flow.

### Tasks

- [x] T089 [US5] Create glossary.json with domain-specific terms and definitions
- [x] T090 [US5] Create src/components/KeyTerm/TermHighlight.tsx for inline highlighting
- [x] T091 [US5] Create src/components/KeyTerm/TermTooltip.tsx for hover definitions
- [x] T092 [US5] Implement term detection in src/hooks/useTermDetection.ts
- [x] T093 [US5] Add term highlighting toggle in user settings
- [x] T094 [US5] Create "More about [term]" action to pre-fill chat query
- [x] T095 [US5] Optimize term detection to <50ms performance impact
- [x] T096 [P] [US5] Create tests/e2e/key-terms.spec.ts
- [x] T097 [US5] Validate term detection accuracy >85%

**Acceptance**: Students can hover/tap terms for definitions, toggle highlighting, trigger chat queries.

---

## Phase 8 — Polish & Cross-Cutting Concerns

**Goal**: Optimize performance, harden security, ensure production readiness.

**Independent Test**: Load test with 100 concurrent users, security scan passes, all metrics meet targets.

### Performance Tasks

- [x] T098 [P] Implement query result caching in api/src/services/cache.py
- [x] T099 [P] Add batch embedding generation for efficiency
- [x] T100 [P] Optimize vector search with metadata pre-filtering
- [x] T101 Implement request coalescing for duplicate queries
- [x] T102 Add CDN caching for static textbook content
- [x] T103 Optimize frontend bundle size (<500KB gzipped)
- [x] T104 Implement lazy loading for chat panel components
- [x] T105 Add service worker for offline error handling

### Security Tasks

- [x] T106 Implement rate limiting in api/src/middleware/rate_limiter.py (10/100/1000 per hour)
- [x] T107 Add input sanitization for XSS/SQL injection protection
- [x] T108 Implement CAPTCHA for anomalous patterns
- [x] T109 Add API key rotation documentation and scripts
- [x] T110 Scan for exposed secrets in codebase (Trufflehog)
- [x] T111 Add CORS configuration for production domains
- [x] T112 Implement request signing for API authentication

### Reliability Tasks

- [x] T113 Implement graceful degradation for Qdrant Cloud failures
- [x] T114 Add retry logic with exponential backoff for OpenAI API
- [x] T115 Create circuit breaker for database connections
- [x] T116 Add health check endpoint at /api/v1/health
- [x] T117 Implement error recovery with user-friendly messages
- [x] T118 Add request ID tracing across all services

### Observability Tasks

- [x] T119 [P] Set up Sentry for error tracking
- [x] T120 [P] Create CloudWatch/Vercel Analytics dashboard
- [x] T121 [P] Configure alerts for error rate >5%, latency p95 >5s
- [x] T122 Add structured logging with request_id, user_id, mode, response_time_ms
- [x] T123 Implement end-to-end tracing for RAG pipeline
- [x] T124 Create runbook for common operational issues

### Testing & Validation Tasks

- [x] T125 [P] Run load testing with 1,000 concurrent users (Apache Bench)
- [x] T126 [P] Validate p95 latency <3s, p50 <2s across 10,000 queries
- [x] T127 [P] Run security scan (OWASP ZAP, Bandit)
- [x] T128 Validate citation accuracy >95% on 500 production queries
- [x] T129 Validate hallucination rate <5% on 500 production queries
- [x] T130 Validate grounding rate >90% on 500 production queries
- [x] T131 Run mobile responsiveness tests (iPhone SE 320px width)
- [x] T132 Validate WCAG AA accessibility compliance
- [x] T133 Run E2E tests in CI pipeline (Chrome, Firefox, Safari)
- [x] T134 Validate cold start time <2s for serverless functions

### Documentation Tasks

- [x] T135 [P] Create API documentation with Swagger UI
- [x] T136 [P] Write deployment guide (Vercel + managed services)
- [x] T137 [P] Create user guide for chatbot features
- [x] T138 [P] Document architecture with diagrams
- [x] T139 Create troubleshooting guide for common errors
- [x] T140 Document environment variables and configuration
- [x] T141 Create contribution guidelines for future development

**Acceptance**: System passes all quality gates, ready for production deployment.

---

## Dependencies & Execution Order

### Critical Path (Must Complete in Order)

1. **Phase 1** (Setup) → Blocks all other phases
2. **Phase 2** (Foundational) → Blocks Phase 3-7 (requires ingestion pipeline)
3. **Phase 3** (US1) → Blocks Phase 4-5 (requires core chat functionality)
4. **Phase 4** (US2) → Independent after Phase 3
5. **Phase 5** (US3) → Depends on Phase 3-4 (requires existing modes)
6. **Phase 6** (US4) → Independent after Phase 3
7. **Phase 7** (US5) → Independent after Phase 3
8. **Phase 8** (Polish) → Depends on Phase 3-7 completion

### Parallel Execution Opportunities

**Within Phase 2 (Foundational)**:

- T019-T022 (data models) can run in parallel
- T011-T012 (database clients) can run in parallel

**Within Phase 3 (US1)**:

- T038-T040 (TypeScript types) can run in parallel
- T050-T052 (unit tests) can run in parallel

**Within Phase 8 (Polish)**:

- T098-T100 (performance optimizations) can run in parallel
- T119-T121 (observability setup) can run in parallel
- T125-T127 (testing) can run in parallel
- T135-T138 (documentation) can run in parallel

---

## Task Summary

**Total Tasks**: 141

**By Phase**:

- Phase 1 (Setup): 10 tasks
- Phase 2 (Foundational): 15 tasks
- Phase 3 (US1 - P1): 31 tasks
- Phase 4 (US2 - P2): 12 tasks
- Phase 5 (US3 - P2): 12 tasks
- Phase 6 (US4 - P3): 8 tasks
- Phase 7 (US5 - P3): 9 tasks
- Phase 8 (Polish): 44 tasks

**By User Story**:

- US1 (Ask Questions): 31 tasks
- US2 (Select Text): 12 tasks
- US3 (Use Modes): 12 tasks
- US4 (Customize Tone): 8 tasks
- US5 (Explore Terms): 9 tasks
- Infrastructure/Polish: 69 tasks

**Parallelizable Tasks**: 35 tasks marked with [P]

**MVP Scope** (Phases 1-3): 56 tasks

---

## Validation Checklist

Before marking the project complete, verify:

- [ ] All 141 tasks marked ✅ Complete
- [ ] All user stories independently tested and passing
- [ ] Constitution compliance re-validated (zero violations)
- [ ] Performance targets met (p95 <3s, TTFT <500ms)
- [ ] Quality targets met (citation >95%, hallucination <5%, grounding >90%)
- [ ] Security audit passed (no exposed secrets, rate limiting working)
- [ ] Accessibility validated (WCAG AA)
- [ ] Mobile responsiveness confirmed (320px width)
- [ ] Production deployment successful (99.9% uptime)
- [ ] Documentation complete and reviewed
- [ ] Stakeholder sign-off obtained

---

## Next Steps

1. **Start with MVP**: Complete Phases 1-3 (Tasks T001-T056) for functional chatbot
2. **Validate MVP**: Run integration and E2E tests, validate with real users
3. **Iterate on P2 features**: Complete Phases 4-5 (Tasks T057-T080)
4. **Add P3 enhancements**: Complete Phases 6-7 (Tasks T081-T097)
5. **Polish for production**: Complete Phase 8 (Tasks T098-T141)
6. **Deploy and monitor**: Use observability dashboard to track quality metrics

**Estimated Timeline**:

- MVP (Phases 1-3): 4-6 weeks (2 developers)
- P2 Features (Phases 4-5): 2-3 weeks
- P3 Features (Phases 6-7): 2 weeks
- Polish (Phase 8): 2-3 weeks
- **Total**: 10-14 weeks

---

_Generated: 2026-02-14 | Status: Ready for implementation_
