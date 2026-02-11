# Feature Specification: RAG-Powered Textbook Chatbot

**Feature ID:** 002-rag-chatbot
**Feature Name:** Interactive Textbook with Embedded RAG Chatbot
**Version:** 1.0.0
**Status:** Draft
**Created:** 2026-02-05 
**Last Updated:** 2026-02-05

---

## Executive Summary

Build a production-grade, serverless RAG (Retrieval-Augmented Generation) chatbot embedded within the AI textbook platform. The chatbot enables students to ask questions and receive accurate, citation-backed answers grounded in textbook content, with strict mode boundaries and explicit error handling.

---

## Problem Statement

Students reading technical textbooks need immediate answers to questions without leaving the reading experience. Traditional solutions either:
- Redirect to external Q&A forums (context loss)
- Provide uncited AI answers (hallucination risk)
- Require manual search through dense material (friction)

**Goal:** Embed an intelligent chatbot that answers questions using only textbook content, with full citation traceability and configurable answering modes.

---

## Core Requirements

### 1. Answering Modes

The system supports **exactly three answering modes**:

#### 1.1 Book-Only Mode (Default)
- **Behavior:** Answers derived exclusively from textbook content
- **Constraint:** General knowledge strictly forbidden
- **Fallback Response:** "I cannot answer this question based on the available textbook content."
- **Validation:** Every sentence maps to a chunk ID with functional citation links

#### 1.2 Selected-Text-Only Mode
- **Behavior:** Uses only user-selected text as context
- **Constraint:** No additional chunks, summaries, or semantic expansion allowed
- **Fallback Response:** "The selected text does not contain enough information to answer this question."
- **Technical:** Selection boundaries preserved exactly; metadata logged

#### 1.3 General Knowledge Mode
- **Behavior:** Opt-in enhancement using LLM general knowledge
- **Constraint:** Requires explicit user activation
- **Visual Indicator:** Badge/banner with warning
- **Disclaimer:** "⚠️ General AI Knowledge: This answer is not grounded in your textbook and may contain inaccuracies."

**Mode Enforcement Rule:** Mode boundaries are mandatory and non-bypassable. Silent mode switching or cross-mode contamination is forbidden.

---

### 2. RAG Pipeline Architecture

#### 2.1 Document Processing
- **Chunking Strategy:** Semantic chunking with 10-15% overlap
- **Chunk Size:** 512-1024 tokens (configurable per textbook structure)
- **Metadata:** Chapter, section, page number, heading hierarchy
- **Deduplication:** Identical chunks merged with provenance tracking

#### 2.2 Retrieval Process (Non-Negotiable Order)
1. Query embedding generation
2. Vector similarity search (top-k candidates)
3. Metadata filtering (if applicable)
4. Reranking with cross-encoder
5. Context window enforcement
6. Final candidate selection

**Parameters:**
- `top_k`: 5-20 (configurable)
- `similarity_threshold`: 0.7 minimum
- `rerank_top_n`: 3-5 final chunks

#### 2.3 Quality Assurance Checks
- Relevance scoring for every retrieved chunk
- Cross-validation between query and answer
- Citation integrity verification
- Hallucination detection via grounding check

---

### 3. Citation & Attribution

**Every book-grounded answer MUST include:**
- Source chapter and section reference
- Unique chunk identifier for audit trail
- Confidence indicator (Low/Medium/High or numerical score)
- Visual distinction for cited vs. generated text

**Citation Format Example:**
```
[Answer content here]

📚 Sources:
• Chapter 3, Section 2.1 — "The Causes of World War I" (Confidence: High)
• Chapter 3, Section 2.3 — "Economic Factors" (Confidence: Medium)
```

**Validation Rules:**
- Citations must link to actual retrievable chunks
- Chunk content must support the cited claim
- Broken citation links trigger error alerts
- Users can view source text on demand

---

### 4. Failure Handling

| Scenario | Required Response |
|----------|------------------|
| No relevant chunks | "I couldn't find relevant information in the textbook to answer your question." |
| Partial relevance | "Based on partial information from [source], here's what I can answer: [content]. However, [missing aspects] are not covered." |
| Ambiguous query | "Your question could refer to multiple topics: [options]. Which did you mean?" |
| Context overflow | "The answer requires more context than can fit in a single response. Would you like me to focus on [specific aspect]?" |

**Prohibited Behaviors:**
- Silent failures
- Defaulting to general knowledge without warning
- Returning irrelevant content with high confidence
- Inventing citations

---

## Technical Architecture

### Technology Stack

**Tier 1 (Required):**
- **LLM Orchestration:** OpenAI Agents / ChatKit SDK
- **Vector Database:** Qdrant Cloud (Free Tier minimum)
- **Relational Database:** Neon Serverless Postgres
- **Embeddings:** OpenAI `text-embedding-3-small` or `text-embedding-3-large`
- **API Framework:** FastAPI (serverless deployment only)

**Tier 2 (Approved Hosting):**
- Vercel (preferred for frontend + serverless functions)
- Fly.io (alternative for API services)
- Cloudflare Workers (alternative for edge computing)
- AWS Lambda (alternative for serverless backend)

**Tier 3 (Support Services):**
- Sentry (error tracking)
- LogTail / BetterStack (logging)
- Upstash (rate limiting via Redis-compatible edge KV)

### Forbidden Technologies

The following are **permanently prohibited**:
- ❌ Redis (local or managed) for session state
- ❌ Client-side FastAPI processes
- ❌ Manually started background servers
- ❌ Long-running workers or daemons
- ❌ Stateful in-memory session storage
- ❌ Unmanaged databases requiring manual maintenance
- ❌ Custom vector indexing without managed services
- ❌ Synchronous blocking operations in request paths

**Rationale:** Serverless-first architecture eliminates operational overhead and ensures production reliability.

---

## API Contract

### Request Schema

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

### Response Schema

```json
{
  "answer": "Backpropagation is a supervised learning algorithm...",
  "mode": "book_only",
  "sources": [
    {
      "chunk_id": "chunk_4589",
      "chapter": "Chapter 3",
      "section": "Section 2.1",
      "title": "Neural Network Training",
      "confidence": 0.92,
      "excerpt": "Backpropagation computes gradients..."
    }
  ],
  "metadata": {
    "request_id": "req_xyz789",
    "latency_ms": 1234,
    "chunks_retrieved": 5,
    "chunks_used": 2
  }
}
```

### Error Response

```json
{
  "error": {
    "code": "RETRIEVAL_FAILED",
    "message": "No relevant textbook content found",
    "details": "Query: 'quantum mechanics basics'",
    "timestamp": "2026-02-05T10:30:00Z",
    "request_id": "req_abc123"
  }
}
```

---

## User Experience Requirements

### Visual Integration
- **Embedding Philosophy:** Chatbot feels embedded, not bolted on
- **UI Integration:** Seamless with textbook design
- **Persistent History:** Chat history within reading session
- **Mobile Responsive:** Full functionality on mobile devices

### Visual Distinction
- **Book-Grounded Answers:** Blue accent, book icon, citation badges
- **General AI Answers:** Yellow/amber accent, warning icon, disclaimer banner
- **Selected-Text Answers:** Purple accent, selection indicator

### Interaction Patterns

**Required Features:**
- Expandable citation previews (accordion or modal)
- Smooth scroll to source location in textbook
- Inline follow-up questions
- Reload-free interactions (SPA behavior)

**Prohibited Patterns:**
- Disruptive popups for primary interactions
- Full-page reloads on question submission
- Hidden loading states
- Dead-end error states

### Performance Benchmarks
- Response time: < 3 seconds (95th percentile)
- Time to first token: < 500ms
- Citation rendering: < 100ms after answer completion
- Scroll to source: < 200ms smooth animation

---

## Security & Reliability

### Rate Limiting (Mandatory)

| User Type | Requests/Hour |
|-----------|--------------|
| Anonymous | 10 |
| Authenticated | 100 |
| Premium | 1000 |

**Implementation:**
- Edge-based rate limiting (Upstash)
- Graceful error messages with retry-after headers
- Burst allowance: 2x base rate for 10 seconds

### Secrets Management
- No API keys in client-side code
- Environment variable injection only
- Secret rotation capability required
- No logging of sensitive data

### Abuse Protection
- Input validation (max query length: 500 characters)
- Profanity and injection detection
- CAPTCHA for suspicious patterns
- IP-based temporary blocks

### Graceful Degradation

| Dependency | Fallback Strategy |
|------------|------------------|
| Vector DB | Keyword search |
| LLM API | Queue + retry with backoff |
| Postgres | Serve cached responses |
| Embedding API | Use pre-computed embeddings |

### Data Privacy
- No persistent storage of queries without consent
- Anonymized analytics only
- GDPR-compliant data handling
- User data deletion capability

---

## Observability & Monitoring

### Logging Requirements

**Log Levels:**
- **ERROR:** System failures, exceptions
- **WARN:** Degraded performance, fallback activations
- **INFO:** Request flow, mode switches
- **DEBUG:** Retrieval details, chunking operations

**Structured Format:**
```json
{
  "timestamp": "2026-02-05T10:30:00Z",
  "level": "INFO",
  "request_id": "req_abc123",
  "user_id": "user_xyz789",
  "mode": "book_only",
  "query": "What caused WWI?",
  "chunks_retrieved": 5,
  "response_time_ms": 1234
}
```

### Metrics & Alerting

**Required Metrics:**
- Request latency (p50, p95, p99)
- Error rate by type
- Retrieval success rate
- Citation accuracy (manual sampling)
- User satisfaction scores

**Alert Thresholds:**
- Error rate > 5% → Page on-call
- Latency p95 > 5s → Warning
- Vector DB unavailable → Critical

### Tracing (OpenTelemetry)

**Trace Spans:**
- Query processing
- Embedding generation
- Vector search
- Reranking
- LLM generation
- Citation resolution

---

## Success Criteria

### Technical Validation
- ✅ Zero runtime conflicts in production
- ✅ No manual servers required
- ✅ All answers traceable to sources
- ✅ 99.9% uptime over 30 days
- ✅ < 1% error rate under normal load
- ✅ All API contracts validated

### Quality Validation
- ✅ 95%+ citation accuracy (sampled review)
- ✅ < 5% hallucination rate
- ✅ User satisfaction > 4.0/5.0
- ✅ Mode boundaries never violated

### Operational Validation
- ✅ One-command deployment
- ✅ Automated rollback capability
- ✅ Zero-downtime updates
- ✅ Self-service troubleshooting docs

### Maintainability Validation
- ✅ Linting and type checking pass
- ✅ 80%+ test coverage
- ✅ Architecture docs up-to-date
- ✅ Runbook for common incidents

---

## Testing Requirements

### Test Coverage

**Mandatory Test Types:**
- Unit Tests: 80%+ coverage, all critical paths
- Integration Tests: API contracts, RAG pipeline
- End-to-End Tests: All three mode user journeys
- Regression Tests: Citation accuracy, mode enforcement

### Test Data
- Representative textbook samples (3+ chapters)
- Edge case queries (ambiguous, malformed, adversarial)
- Known ground truth Q&A pairs (50+ minimum)

### Continuous Testing
- Pre-commit hooks for linting
- CI pipeline for test execution
- Nightly regression suite
- Weekly performance benchmarking

---

## Dependencies

**External Services:**
- Qdrant Cloud (vector database)
- Neon Postgres (relational database)
- OpenAI API (embeddings + LLM)
- Vercel/Fly.io (hosting)
- Upstash (rate limiting)

**Internal Dependencies:**
- Existing textbook content (Docusaurus platform)
- Authentication system (if applicable)
- Analytics tracking system

---

## Non-Goals

**Explicitly Out of Scope:**
- Real-time collaborative chat between students
- Voice-based query input
- Image or diagram-based question answering
- Content generation or textbook editing
- Integration with external knowledge bases beyond textbook
- Multi-turn dialogue state management across sessions

---

## Open Questions

1. **Textbook Content Format:** Are all chapters already in Markdown? Any PDFs requiring extraction?
2. **Authentication:** Should chatbot be accessible to anonymous users or require login?
3. **Analytics:** What user interaction metrics are most valuable for instructors?
4. **Localization:** Should chatbot support multiple languages beyond English?
5. **Offline Mode:** Is offline functionality required for mobile apps?

---

## Appendix: Glossary

**Chunk:** Semantically coherent segment of textbook content (512-1024 tokens) with embeddings and metadata.

**Grounding:** Verification that generated content is supported by retrieved source material.

**Hallucination:** Generated content not supported by textbook or factually incorrect.

**Mode Contamination:** Violation of mode boundaries (e.g., using general knowledge in Book-Only mode).

**Reranking:** Secondary scoring of retrieved chunks using cross-encoder models.

**Serverless:** Architecture where compute resources are managed by cloud provider with auto-scaling.

---

**Spec Version:** 1.0.0
**Next Review:** 2026-03-05
**Owner:** AI Textbook Platform Team
**Status:** Draft - Awaiting Approval
