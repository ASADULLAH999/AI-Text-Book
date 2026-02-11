<!-- SYNC IMPACT REPORT (v1.0.0 → v2.0.0)
Version Type: MAJOR (Complete project pivot from Physical AI textbook to RAG-powered chatbot system)
Modified Principles:
  - Educational Excellence → Grounded Accuracy (strict citation requirements)
  - Token-Friendly Architecture → Serverless-First Reliability
  - User-Centric Design → Mode Enforcement + UX Laws
Added Sections:
  - Article III: Answering Modes (Immutable Law)
  - Article IV: RAG Pipeline Laws
  - Article V: Citation & Attribution Laws
  - Article VII: API Contract Law
  - Article VIII: Security & Reliability
  - Article IX: Observability & Monitoring
  - Article XI: Testing & Quality Assurance
Removed Sections:
  - Design System (Neural Circuitry theme - project specific)
  - Site Architecture (Docusaurus specific - moved to spec)
  - Feature Specifications (quiz, auth - moved to spec)
  - UI/UX Specifications (moved to spec)
  - Token Strategy (replaced with serverless principles)
Templates Updated:
  ⚠ spec-template.md - Must include RAG pipeline specs, mode definitions, citation requirements
  ⚠ plan-template.md - Must include serverless architecture validation, vector DB integration
  ⚠ tasks-template.md - Must include retrieval validation, grounding checks, mode enforcement tests
  ⚠ phr-template.prompt.md - May need RAG-specific prompt tracking fields
Follow-up TODOs:
  - Update all template files to reference constitutional principles
  - Add RAG-specific ADR guidance for vector DB and embedding choices
  - Review command files for RAG-specific instructions
  - Update CLAUDE.md with RAG chatbot context
-->

# Constitution — Interactive AI Textbook Platform with RAG Chatbot

## Project Identity

**Project Name:** Interactive Textbook with Embedded RAG Chatbot
**Primary Feature:** 002-rag-chatbot (Retrieval-Augmented Generation Chatbot)
**Development Model:** Spec-Driven Development (Claude Code CLI)
**System Type:** Serverless, Retrieval-Augmented Generation (RAG)
**Constitutional Version:** 2.0.0
**Ratified:** 2026-01-17
**Last Amended:** 2026-02-05

---

## Preamble

This constitution establishes the immutable foundation for the Interactive AI Textbook Platform, with a primary focus on production-grade, RAG-powered chatbot capabilities. It defines architectural principles, technical constraints, and behavioral laws that govern all system components.

**Constitutional Authority:** No implementation, agent, tool, MCP server, prompt, or integration may violate this constitution. Any code, design, or decision that conflicts with these principles is invalid and must be rejected.

**Scope:** This constitution applies to both the textbook platform infrastructure AND the embedded RAG chatbot system (feature 002-rag-chatbot). Feature-specific requirements are detailed in `specs/002-rag-chatbot/spec.md`.

---

## Article I: Core Principles

### 1.1 Grounded Accuracy

**Law:** All factual answers MUST be grounded in retrieved textbook content unless explicitly operating in general knowledge mode.

**Requirements:**
- No unsupported claims, hallucinations, or speculation permitted
- Every factual statement must trace to a retrievable source chunk
- Citation must be verifiable and auditable
- Confidence scores must accompany all book-grounded answers

**Rationale:** Educational integrity depends on accuracy. Students must trust that textbook-based answers reflect actual course material, not AI confabulation. This principle applies to all content generation, whether chatbot responses or static textbook pages.

### 1.2 Deterministic Behavior

**Law:** Given identical input and context, the system MUST produce consistent behavior.

**Requirements:**
- No hidden state transitions
- No memory drift across sessions
- No uncontrolled randomness in core logic
- Exception: Temperature-based generation variation permitted only in presentation layer

**Rationale:** Reproducibility is essential for debugging, testing, and user trust. Non-deterministic behavior creates unpredictable user experiences and impossible-to-trace bugs.

### 1.3 Strict Scope Enforcement

**Law:** System boundaries and modes must be explicitly defined and enforced at all times.

**Boundaries:**
- RAG chatbot modes are hard boundaries (Book-Only, Selected-Text-Only, General Knowledge)
- Cross-mode contamination is forbidden
- Scope violations must trigger explicit errors
- Feature boundaries clearly documented in specs

**Rationale:** Mixing knowledge sources or feature capabilities without clear boundaries leads to citation confusion and undermines grounding guarantees.

### 1.4 Separation of Concerns

**Law:** System components must remain logically isolated.

**Domains:**
- **Content Management:** Static textbook pages, navigation, structure
- **Retrieval:** Finding relevant content from vector database
- **Validation:** Verifying answer grounding and citation accuracy
- **Generation:** Producing natural language responses
- **Citation:** Linking answers to sources with metadata
- **Decision-Making:** Mode selection, routing, and orchestration

**Prohibition:** No component may silently assume responsibilities outside its designated scope.

**Rationale:** Modularity enables independent testing, replacement, and scaling of components without cascading failures.

### 1.5 Serverless-First Reliability

**Law:** The system MUST function without manual server processes.

**Requirements:**
- No local background services
- No persistent workers or daemons
- Stateless by design
- Self-healing through managed services
- Edge-compatible where possible

**Rationale:** Serverless architectures eliminate operational overhead, enable auto-scaling, reduce single points of failure, and align with modern cloud-native best practices.

### 1.6 Explicit Over Implicit

**Law:** All system behavior must be explicit and traceable.

**Requirements:**
- No magic defaults
- Clear error messages with actionable guidance
- Visible state transitions
- Auditable decision paths
- Comprehensive logging with structured data

**Rationale:** Implicit behavior creates debugging nightmares and violates educational transparency requirements. Users and developers must understand what the system is doing and why.

---

## Article II: Technical Architecture

### 2.1 Forbidden Technologies & Patterns

The following are **permanently prohibited**:

- ❌ Redis (local or managed) for session state
- ❌ Client-side FastAPI processes
- ❌ Manually started background servers
- ❌ Long-running workers or daemons
- ❌ Stateful in-memory session storage
- ❌ Unmanaged databases requiring manual maintenance
- ❌ Custom vector indexing without managed services
- ❌ Synchronous blocking operations in request paths

**Rationale:** These patterns violate serverless principles and introduce operational complexity incompatible with production-grade reliability.

### 2.2 Mandatory Architectural Characteristics

All implementations MUST exhibit:

- ✅ Serverless or edge-compatible execution
- ✅ Fully managed databases and vector stores
- ✅ Stateless request handling
- ✅ Explicit failure handling with user-visible errors
- ✅ Idempotent operations where applicable
- ✅ Graceful degradation patterns
- ✅ Observable logging and tracing
- ✅ API-first design with versioned contracts

### 2.3 Approved Technology Stack

**Tier 1 (Required for RAG Chatbot):**
- **LLM Orchestration:** OpenAI Agents / ChatKit SDK
- **Vector Database:** Qdrant Cloud (Free Tier minimum)
- **Relational Database:** Neon Serverless Postgres
- **Embeddings:** OpenAI `text-embedding-3-small` or `text-embedding-3-large`
- **API Framework:** FastAPI (serverless deployment only)

**Tier 1 (Required for Textbook Platform):**
- **Static Site Generator:** Docusaurus 3.x
- **Frontend Framework:** React 18.x
- **Styling:** CSS Modules + Custom CSS

**Tier 2 (Approved Hosting):**
- Vercel (preferred for frontend + serverless functions)
- Fly.io (alternative for API services)
- Cloudflare Workers (alternative for edge computing)
- AWS Lambda (alternative for serverless backend)
- GitHub Pages (static textbook hosting)

**Tier 3 (Approved Support Services):**
- Sentry (error tracking)
- LogTail / BetterStack (logging)
- Upstash (rate limiting via Redis-compatible edge KV)
- Plausible/Fathom (privacy-focused analytics)

**Amendment Process:** Technology substitutions require constitutional amendment with justification.

---

## Article III: RAG Chatbot Answering Modes (Immutable Law)

The RAG chatbot system supports **exactly three answering modes**. No additional modes may be introduced without constitutional amendment.

### 3.1 Book-Only Mode (Default)

**Status:** Default system behavior

**Rules:**
- Answers MUST be derived exclusively from textbook content
- General knowledge is **strictly forbidden**
- If textbook content is insufficient, respond:
  > "I cannot answer this question based on the available textbook content. The information needed is not present in the retrieved sections."

**Validation:**
- Every sentence must map to a chunk ID
- Citation links must be functional
- Confidence scores must be displayed

### 3.2 Selected-Text-Only Mode

**Status:** User-activated constraint mode

**Rules:**
- **Only** the user-selected text may be used as context
- No additional chunks, summaries, or inferred knowledge allowed
- No semantic expansion beyond selection boundaries
- If insufficient information exists, respond:
  > "The selected text does not contain enough information to answer this question. Please select additional context or rephrase your question."

**Technical Requirements:**
- Selection boundaries must be preserved exactly
- No chunk retrieval beyond selection
- Selection metadata must be logged

### 3.3 General Knowledge Mode

**Status:** Opt-in enhancement

**Rules:**
- Available **only** through explicit user activation
- Must display clear visual indicator (badge, banner, or label)
- Every response must include disclaimer:
  > "⚠️ General AI Knowledge: This answer is not grounded in your textbook and may contain inaccuracies."
- User must be able to disable at any time

**Restrictions:**
- Cannot override Book-Only or Selected-Text-Only modes
- Must maintain citation discipline when mixing with textbook content
- Clearly separate book-grounded vs. general knowledge statements

### 3.4 Mode Enforcement

**Law:** Mode boundaries are mandatory and non-bypassable.

**Violations:**
- Silent mode switching → System error

- Cross-mode contamination → Invalid response
- Unclear mode state → User notification required

---

## Article IV: RAG Pipeline Laws

### 4.1 Document Processing

**Mandatory Requirements:**
- **Chunking Strategy:** Semantic chunking with 10-15% overlap
- **Chunk Size:** 512-1024 tokens (configurable per textbook structure)
- **Metadata Preservation:** Chapter, section, page number, heading hierarchy
- **Deduplication:** Identical chunks must be merged with provenance tracking

### 4.2 Retrieval Process

**Pipeline Steps (Non-Negotiable Order):**
1. Query embedding generation
2. Vector similarity search (top-k candidates)
3. Metadata filtering (if applicable)
4. Reranking with cross-encoder
5. Context window enforcement
6. Final candidate selection

**Parameters:**
- `top_k`: 5-20 (user or admin configurable)
- `similarity_threshold`: 0.7 minimum (adjustable)
- `rerank_top_n`: 3-5 final chunks

### 4.3 Failure Handling

**Explicit Response Requirements:**

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

### 4.4 Quality Assurance

**Mandatory Checks:**
- Relevance scoring for every retrieved chunk
- Cross-validation between query and answer
- Citation integrity verification
- Hallucination detection via grounding check

---

## Article V: Citation & Attribution Laws

### 5.1 Citation Requirements

**Every book-grounded answer MUST include:**
- **Source Identification:** Chapter and section reference
- **Chunk Identifier:** Unique ID for retrieval audit
- **Confidence Indicator:** Low/Medium/High or numerical score
- **Visual Distinction:** Clear formatting for cited vs. generated text

**Format Example:**
```
[Answer content here]

📚 Sources:
• Chapter 3, Section 2.1 — "The Causes of World War I" (Confidence: High)
• Chapter 3, Section 2.3 — "Economic Factors" (Confidence: Medium)
```

### 5.2 Inline Citation Format

**Approved Patterns:**
- Superscript numbers: `According to the text[1], ...`
- Bracketed references: `The process [Section 4.2] involves...`
- Inline badges: `As explained in 📖 Ch3§2, ...`

**Prohibition:** Any factual output without citation is invalid.

**Validation Rules:**
- Citations must link to actual retrievable chunks
- Chunk content must support the cited claim
- Broken citation links must trigger error alerts
- User must be able to view source text on demand

---

## Article VI: User Experience Laws

### 6.1 Integration Philosophy

**Principle:** All features must feel **embedded and cohesive**, not bolted on.

**Requirements:**
- Seamless visual integration with textbook UI
- No jarring transitions or context switches
- Persistent state within reading session (where appropriate)
- Mobile-responsive design
- Consistent visual language across all features

### 6.2 Visual Distinction Requirements (RAG Chatbot)

**Mandatory UI Differentiation:**
- **Book-Grounded Answers:** Blue accent, book icon, citation badges
- **General AI Answers:** Yellow/amber accent, warning icon, disclaimer banner
- **Selected-Text Answers:** Purple accent, selection indicator

### 6.3 Interaction Patterns

**Required Features:**
- Expandable citation previews (accordion or modal)
- Smooth scroll to source location in textbook
- Inline follow-up questions (chatbot)
- Reload-free interactions (SPA behavior)

**Prohibited Patterns:**
- Disruptive popups or modals for primary interactions
- Full-page reloads on question submission
- Hidden loading states (must show progress)
- Dead-end error states (always offer recovery action)

### 6.4 Performance Standards

**Law:** UX enhancements must never compromise accuracy or reliability.

**Benchmarks:**
- Response time: < 3 seconds for 95th percentile
- Time to first token: < 500ms (streaming responses)
- Citation rendering: < 100ms after answer completion
- Scroll to source: < 200ms smooth animation
- Page load (textbook): < 2 seconds on 3G

---

## Article VII: API Contract Law

### 7.1 Schema Requirements

**Law:** All API requests and responses MUST follow explicit, versioned schemas.

**Mandatory Elements:**
- OpenAPI 3.0+ specification
- JSON Schema validation
- Required field enforcement
- Deprecation warnings for breaking changes

### 7.2 Versioning Policy

**Rules:**
- API version in URL path: `/api/v1/chat`
- Major version bump for breaking changes
- Minor version bump for backwards-compatible additions
- Deprecation notice period: minimum 90 days

### 7.3 Error Response Standard

**Required Format:**
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

**Error Visibility:**
- User-facing errors must be actionable
- Technical errors must be logged with request_id
- No generic "Something went wrong" messages

### 7.4 Decoupling Requirements

**Law:** Frontend and backend must remain loosely coupled.

**Enforcement:**
- No shared stateful sessions
- No client-side business logic duplication
- API-first development approach
- Contract testing in CI/CD

---

## Article VIII: Security & Reliability

### 8.1 Secrets Management

**Prohibitions:**
- API keys in client-side code
- Hardcoded credentials
- Secrets in version control
- Logging of sensitive data

**Requirements:**
- Environment variable injection
- Secret rotation capability
- Least-privilege access policies

### 8.2 Rate Limiting

**Law:** Rate limiting is mandatory for all API endpoints.

**Tiers:**
- Anonymous users: 10 requests/hour
- Authenticated users: 100 requests/hour
- Premium users: 1000 requests/hour

**Implementation:**
- Edge-based rate limiting (Upstash or similar)
- Graceful error messages with retry-after headers
- Burst allowance: 2x base rate for 10 seconds

### 8.3 Abuse Protection

**Required Safeguards:**
- Input validation (max query length: 500 characters)
- Profanity and injection detection
- CAPTCHA for suspicious patterns
- IP-based temporary blocks

### 8.4 Graceful Degradation

**Law:** All external dependencies must have fallback strategies.

**Failure Modes:**

| Dependency | Degradation Strategy |
|------------|---------------------|
| Vector DB | Fallback to keyword search |
| LLM API | Queue request, retry with backoff |
| Postgres | Serve cached responses |
| Embedding API | Use pre-computed embeddings |

### 8.5 Data Privacy

**Requirements:**
- No persistent storage of user queries without consent
- Anonymized analytics only
- GDPR-compliant data handling
- User data deletion capability

---

## Article IX: Observability & Monitoring

### 9.1 Logging Requirements

**Mandatory Log Levels:**
- **ERROR:** System failures, exceptions
- **WARN:** Degraded performance, fallback activations
- **INFO:** Request flow, mode switches
- **DEBUG:** Retrieval details, chunking operations

**Structured Logging:**
```json
{
  "timestamp": "2026-02-05T10:30:00Z",
  "level": "INFO",
  "request_id": "req_abc123",
  "user_id": "user_xyz789",
  "feature": "rag-chatbot",
  "mode": "book_only",
  "query": "What caused WWI?",
  "chunks_retrieved": 5,
  "response_time_ms": 1234
}
```

### 9.2 Metrics & Alerting

**Required Metrics:**
- Request latency (p50, p95, p99)
- Error rate by type and feature
- Retrieval success rate (RAG chatbot)
- Citation accuracy (manual sampling)
- User satisfaction (feedback scores)

**Alert Thresholds:**
- Error rate > 5% → Page on-call
- Latency p95 > 5s → Warning
- Vector DB unavailable → Critical
- Authentication failures spike → Investigation

### 9.3 Tracing

**Requirement:** End-to-end request tracing with OpenTelemetry or equivalent.

**Trace Spans (RAG Chatbot):**
- Query processing
- Embedding generation
- Vector search
- Reranking
- LLM generation
- Citation resolution

---

## Article X: Success Criteria (Definition of Done)

### 10.1 Technical Validation

The system is valid only if:

- ✅ Zero runtime conflicts in production
- ✅ No manual servers or background processes required
- ✅ All RAG answers traceable to sources via audit logs
- ✅ 99.9% uptime over 30-day period
- ✅ < 1% error rate under normal load
- ✅ All API contracts validated and versioned

### 10.2 Quality Validation

- ✅ 95%+ citation accuracy (sampled manual review)
- ✅ < 5% hallucination rate (grounding check)
- ✅ User satisfaction score > 4.0/5.0
- ✅ Mode boundaries never violated in testing
- ✅ Textbook content renders correctly across devices

### 10.3 Operational Validation

- ✅ One-command deployment
- ✅ Automated rollback capability
- ✅ Zero-downtime updates
- ✅ Self-service troubleshooting documentation

### 10.4 Maintainability Validation

- ✅ Codebase passes linting and type checking
- ✅ 80%+ test coverage (unit + integration)
- ✅ Architecture documentation up-to-date
- ✅ Runbook for common incidents

---

## Article XI: Testing & Quality Assurance

### 11.1 Test Coverage Requirements

**Mandatory Test Types:**
- **Unit Tests:** 80%+ coverage, all critical paths
- **Integration Tests:** API contract validation, RAG pipeline
- **End-to-End Tests:** User journeys for all three RAG modes
- **Regression Tests:** Citation accuracy, mode enforcement
- **Visual Regression Tests:** UI component consistency

### 11.2 Test Data Requirements

- Representative textbook samples (3+ chapters)
- Edge case queries (ambiguous, malformed, adversarial)
- Known ground truth Q&A pairs (50+ minimum)
- Browser compatibility test matrix

### 11.3 Continuous Testing

- Pre-commit hooks for linting
- CI pipeline for test execution
- Nightly regression suite
- Weekly performance benchmarking

---

## Article XII: Amendment Process

### 12.1 Amendment Authority

This constitution may be modified only through:

1. **Specification Updates:** Documented changes to project requirements
2. **Versioned Constitutional Changes:** Formal amendment proposals with rationale
3. **Full System Review:** Quarterly architecture review with stakeholders

### 12.2 Amendment Procedure

**Steps:**
1. Proposal submission with justification
2. Impact analysis (technical + user experience)
3. Review period (minimum 7 days)
4. Approval by project maintainer(s)
5. Version bump and changelog update
6. Template propagation

### 12.3 Emergency Amendments

**Criteria:** Critical security vulnerabilities or production-breaking bugs

**Fast-Track Process:**
- Immediate proposal + implementation
- Retroactive documentation within 48 hours
- Post-incident review within 7 days

---

## Article XIII: Enforcement

### 13.1 Violation Handling

**Categories:**
- **Critical Violations:** Security breaches, data loss → Immediate rollback
- **Major Violations:** Mode contamination, citation failure → Block deployment
- **Minor Violations:** Performance degradation → Warning + fix timeline

### 13.2 Audit Trail

**Requirements:**
- All architectural decisions logged
- Constitutional compliance checklist for PRs
- Quarterly constitutional review meetings

### 13.3 Dispute Resolution

**Process:**
1. Document the disagreement
2. Reference constitutional articles
3. Propose resolution options
4. Vote if needed (maintainer discretion)
5. Update constitution if precedent-setting

---

## Appendix A: Glossary

**Chunk:** A semantically coherent segment of textbook content, typically 512-1024 tokens, stored with embeddings and metadata.

**Grounding:** The process of verifying that generated content is supported by retrieved source material.

**Hallucination:** Generated content that is not supported by the textbook or is factually incorrect.

**Mode Contamination:** Violation of mode boundaries, e.g., using general knowledge in Book-Only mode.

**Reranking:** Secondary scoring of retrieved chunks using cross-encoder models for improved relevance.

**Serverless:** Architecture pattern where compute resources are managed by cloud provider, auto-scaling on demand.

---

## Appendix B: Quick Reference

### RAG Chatbot Mode Decision Tree
```
User Query
    ├─ Mode Selected?
    │   ├─ Book-Only → Retrieve chunks → Generate
    │   ├─ Selected-Text → Use selection only → Generate
    │   └─ General Knowledge → Warn user → Use LLM directly
    └─ No Mode → Default to Book-Only
```

### Citation Checklist
- [ ] Source chapter/section listed
- [ ] Chunk ID included
- [ ] Confidence score displayed
- [ ] User can click to view source
- [ ] Visual distinction from general text

### Deployment Checklist
- [ ] All tests passing
- [ ] API contracts validated
- [ ] Environment variables configured
- [ ] Rate limiting enabled
- [ ] Monitoring dashboards ready
- [ ] Rollback plan documented

---

## Signature Block

**Constitutional Version:** 2.0.0
**Effective Date:** 2026-02-05
**Next Review Date:** 2026-05-05
**Maintained By:** Project Core Team
**Status:** Active

**Amendment History:**
- v1.0.0 (2026-01-17): Initial ratification for Physical AI textbook platform
- v2.0.0 (2026-02-05): Major pivot to RAG-powered chatbot system; added Articles III-IX for RAG architecture
