# Architecture Documentation

> **T138** — System architecture for the RAG-Powered AI Textbook Chatbot.

## System Overview

```
Browser (Docusaurus)
│
├── ChatPanel ──────────────────────────────────────────────────────────┐
│   ├── ModeSelector (Book-Only | Selected-Text | General)             │
│   ├── ToneSelector (Neutral | Academic | Beginner | Concise | Detail)│
│   ├── MessageList (citations, streaming)                              │
│   └── ChatInput (500 char limit, selection preview)                  │
│                                                                       │
├── TextSelection ───────────────────────────────────────────────────── │
│   └── SelectionMenu → "Ask AI about this" → prefills ChatInput       │
│                                                                       │
└── KeyTerm ─────────────────────────────────────────────────────────── │
    ├── TermHighlight (inline dashed underlines)                        │
    └── TermTooltip → "More about [term]" → prefills ChatInput         │
                                                                        ▼
                                                          API: /api/v1/chat
                                                                        │
                                               ┌─────────────────────────────┐
                                               │     FastAPI (Vercel)         │
                                               │  ──────────────────────────  │
                                               │  Middleware Stack:           │
                                               │  1. CORS                     │
                                               │  2. ErrorHandler             │
                                               │  3. RequestValidator (T107)  │
                                               │  4. CaptchaMiddleware (T108) │
                                               │  5. RequestSigning (T112)    │
                                               │  6. StructuredLogging (T122) │
                                               │  7. RateLimiter (T106)       │
                                               └─────────────────────────────┘
                                                                        │
                                               ┌─────────────────────────────┐
                                               │     RAG Pipeline             │
                                               │                              │
                                               │  Query → Embedding (T099)   │
                                               │       → Cache check (T098)  │
                                               │       → Qdrant search (T100)│
                                               │       → Rerank               │
                                               │       → Generate (Claude)    │
                                               │       → Cite (T085)          │
                                               │       → Trace (T123)         │
                                               └─────────────────────────────┘
```

---

## Component Breakdown

### Frontend (Docusaurus + React)

| Component | Path | Responsibility |
|-----------|------|---------------|
| `ChatPanel` | `src/components/ChatPanel/` | Main chat UI shell |
| `ChatInput` | `src/components/ChatPanel/ChatInput.tsx` | Message input with 500-char limit |
| `MessageList` | `src/components/ChatPanel/MessageList.tsx` | Virtualized message display |
| `ModeSelector` | `src/components/ChatPanel/ModeSelector.tsx` | Book-Only/Selected-Text/General |
| `ToneSelector` | `src/components/ChatPanel/ToneSelector.tsx` | Response tone selection |
| `Citation` | `src/components/Citation/` | Citation cards and hover previews |
| `TextSelection` | `src/components/TextSelection/` | Selection detection + menu |
| `KeyTerm` | `src/components/KeyTerm/` | Term highlighting + tooltips |

### Backend (FastAPI)

| Module | Path | Responsibility |
|--------|------|---------------|
| `main.py` | `api/src/main.py` | App bootstrap, middleware registration |
| `chat.py` | `api/src/api/v1/chat.py` | Chat endpoint (POST /api/v1/chat) |
| `orchestrator.py` | `api/src/services/rag/orchestrator.py` | RAG pipeline coordination |
| `embedding.py` | `api/src/services/rag/embedding.py` | OpenAI text-embedding-3-large |
| `retrieval.py` | `api/src/services/rag/retrieval.py` | Qdrant vector search + reranking |
| `grounding.py` | `api/src/services/rag/grounding.py` | Hallucination detection |
| `citation_service.py` | `api/src/services/citation_service.py` | Citation generation and validation |
| `cache.py` | `api/src/services/cache.py` | TTL LRU cache + request coalescing |
| `resilience.py` | `api/src/services/resilience.py` | Retry, circuit breaker, fallback |
| `tone_modifiers.py` | `api/src/services/prompts/tone_modifiers.py` | Tone system prompt modifiers |

### Modes

| Mode | Path | Behavior |
|------|------|---------|
| `book_only` | `api/src/services/modes/book_only.py` | Strict grounding, refuses off-topic |
| `selected_text` | `api/src/services/modes/selected_text.py` | Zero vector searches, uses selection |
| `general_knowledge` | `api/src/services/modes/general_knowledge.py` | Relaxed grounding, disclaimer |

---

## Data Flow

### Book-Only Query

```
1. User submits "What is ROS2?" (mode=book_only, tone=neutral)
2. RequestValidator sanitizes input (XSS, SQLi, length)
3. RateLimiter checks Upstash Redis
4. Cache.get(sha256(query+mode+tone)) → miss
5. Embedding: text-embedding-3-large → 3072-dim vector
6. Qdrant search: top-k=20, threshold=0.7, pre-filter by chapter
7. Reranker: weighted score (0.6×vector + 0.3×overlap + 0.1×metadata)
8. Generator: OpenAI GPT-4o with tone-modified system prompt
9. CitationService: extracts [1][2] references from generated text
10. Cache.set(key, response, ttl=3600)
11. PipelineTracer.log_summary() → structured JSON log
12. Response: {message, citations, metadata}
```

### Selected-Text Query

```
1. User selects "ROS2 uses DDS for communication" + asks "What is DDS?"
2. Selection validated: 50–4,000 tokens
3. selected_text mode: no Qdrant vector search
4. Selection injected as primary context in system prompt
5. Response grounded in selection (not whole book)
```

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Vector DB | Qdrant Cloud | HNSW index, managed, 3072-dim support |
| Embeddings | text-embedding-3-large | Highest quality for RAG tasks |
| Reranking | Custom weighted score | Avoids Cohere API latency in critical path |
| Generation | GPT-4o | Best instruction-following for citations |
| Cache | In-process TTL LRU + Redis | Low latency for dev; Redis for multi-instance |
| Frontend framework | Docusaurus 3 | Built-in MDX, search, i18n |

For more ADRs see: `history/adr/`

---

## Performance Characteristics

| Metric | Target | Implementation |
|--------|--------|---------------|
| TTFT (first token) | < 500ms | Streaming SSE |
| p50 latency | < 2s | Cache + batch embed |
| p95 latency | < 3s | Retry with backoff |
| Bundle size | < 500KB gzipped | Code splitting, lazy ChatPanel |
| Term detection | < 50ms | Module-level regex index |

---

*Last reviewed: 2026-02-28*
