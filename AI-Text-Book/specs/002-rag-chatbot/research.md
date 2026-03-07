# Research: RAG-Powered Textbook Chatbot

**Phase**: 0 (Research)
**Created**: 2026-02-14
**Status**: Complete
**Related Documents**: [spec.md](spec.md), [plan.md](plan.md)

---

## Purpose

This document consolidates research findings for technology choices, best practices, and design patterns required to implement the RAG-powered textbook chatbot system. All decisions are evaluated against constitutional requirements and project constraints.

---

## 1. LLM Selection

### Decision: OpenAI GPT-4 / GPT-3.5-turbo

**Rationale:**
- **Production-ready**: Proven reliability at scale with 99.9% uptime SLA
- **Streaming support**: Native SSE (Server-Sent Events) for < 500ms TTFT requirement
- **Function calling**: Built-in support for structured outputs and tool use
- **Cost efficiency**: GPT-3.5-turbo at $0.001/1K tokens meets <$0.10 per query budget
- **Context window**: 16K tokens (GPT-3.5) sufficient for 8,000 token context limit + system prompts

**Alternatives Considered:**
- **Anthropic Claude**: Strong reasoning but higher latency (no streaming at time of research)
- **Open-source (LLaMA 2, Mistral)**: Requires self-hosting, violates serverless-first principle
- **Cohere**: Limited ecosystem integration, higher cost per token

**Best Practices:**
- Use GPT-3.5-turbo for Book-Only/Selected-Text modes (cost optimization)
- Reserve GPT-4 for General Knowledge mode (higher reasoning requirements)
- Implement temperature=0 for deterministic responses in Book-Only mode
- Set max_tokens budgets per mode to control costs

---

## 2. Vector Database: Qdrant Cloud

### Decision: Qdrant Cloud (managed service)

**Rationale:**
- **Serverless-compatible**: Managed cloud offering, zero operational overhead
- **Performance**: < 100ms p95 search latency for 10K-50K vectors at 3,072 dimensions
- **Metadata filtering**: Native support for chapter/section/book_id filters
- **HNSW indexing**: Optimized for high-dimensional similarity search
- **Free tier**: 1GB storage sufficient for prototype, $0.50/GB/month for production
- **Python SDK**: First-class support with async operations

**Alternatives Considered:**
- **Pinecone**: Higher cost ($0.096/GB/month), no free tier
- **Weaviate Cloud**: Requires schema management, higher complexity
- **Elasticsearch with vector search**: Not purpose-built, higher latency
- **Self-hosted Qdrant**: Violates serverless-first constraint

**Configuration Best Practices:**
```python
# Collection Configuration
{
    "vectors": {
        "size": 3072,  # text-embedding-3-large
        "distance": "Cosine"  # Normalized dot product for speed
    },
    "hnsw_config": {
        "m": 16,              # Links per node (balance speed/accuracy)
        "ef_construct": 100   # Build-time precision
    },
    "optimizers_config": {
        "indexing_threshold": 10000  # Batch indexing threshold
    }
}
```

**Search Parameters:**
```python
# Query Configuration
{
    "limit": 20,              # Top-K candidates
    "score_threshold": 0.7,   # Minimum similarity
    "with_payload": True,     # Include metadata
    "with_vectors": False     # Exclude vectors (reduce transfer)
}
```

---

## 3. Embedding Model: OpenAI text-embedding-3-large

### Decision: text-embedding-3-large (3,072 dimensions)

**Rationale:**
- **State-of-the-art**: MTEB benchmark leader as of 2024
- **Dimensionality**: 3,072 dimensions balance precision and storage
- **Semantic understanding**: Superior for domain-specific educational content
- **Cost**: $0.00013/1K tokens (acceptable for one-time indexing + query embedding)
- **Consistency**: Same API as generation models (OpenAI SDK)

**Alternatives Considered:**
- **text-embedding-3-small (1,536 dims)**: 50% cheaper but 8-10% lower retrieval accuracy
- **text-embedding-ada-002**: Deprecated, lower performance
- **Sentence-BERT**: Requires self-hosting, violates serverless constraint
- **Cohere Embed**: Competitive but ecosystem fragmentation

**Batch Processing Strategy:**
```python
# Batch embedding generation
def embed_chunks_batch(chunks: List[str], batch_size: int = 100):
    """
    Process chunks in batches to optimize API calls.
    Rate limit: 3,000 RPM (OpenAI Tier 2)
    """
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        response = openai.Embedding.create(
            input=batch,
            model="text-embedding-3-large"
        )
        yield [item['embedding'] for item in response['data']]
```

**Best Practices:**
- Normalize embeddings before storage (L2 normalization for cosine similarity)
- Pre-compute embeddings for all chunks (one-time indexing cost)
- Cache query embeddings for identical queries (15-minute TTL)
- Use dimensionality reduction only if storage becomes constraint

---

## 4. Serverless Platform: Vercel Functions

### Decision: Vercel Serverless Functions (primary), AWS Lambda (fallback)

**Rationale:**
- **Zero cold starts**: Edge runtime for < 2s cold start requirement
- **Streaming responses**: Native support for SSE/streaming
- **Global CDN**: Edge network for < 3s p95 latency worldwide
- **Zero configuration**: Git-based deployment, auto-scaling
- **Cost**: Free tier (100GB-hrs/month), $20/month for production
- **Integration**: Seamless with Next.js/React frontend

**Alternatives Considered:**
- **AWS Lambda**: More configuration overhead, 5-10s cold starts without provisioned concurrency
- **Google Cloud Functions**: Limited streaming support, higher latency
- **Cloudflare Workers**: 10ms CPU limit insufficient for RAG pipeline

**Configuration Example:**
```javascript
// api/chat.js (Vercel Function)
export const config = {
  runtime: 'nodejs18.x',
  maxDuration: 30,  // 30s timeout for complex queries
  memory: 1024      // 1GB for LLM processing
};

export default async function handler(req, res) {
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');

  // Streaming response implementation
}
```

**Best Practices:**
- Use edge functions for latency-sensitive operations (< 100ms)
- Use serverless functions for compute-heavy tasks (embeddings, LLM calls)
- Implement connection pooling for database connections (Neon Postgres)
- Set appropriate timeout budgets per operation (30s max)

---

## 5. Relational Database: Neon Serverless Postgres

### Decision: Neon Serverless Postgres

**Rationale:**
- **Serverless-native**: Auto-scaling, branching, point-in-time recovery
- **Connection pooling**: Built-in pooler for serverless functions
- **Postgres compatibility**: Full SQL support, JSONB for flexible schemas
- **Performance**: < 50ms query latency for indexed lookups
- **Cost**: $0.16/compute-hour + $0.023/GB-month storage
- **Free tier**: 3GB storage, 100 compute-hours/month

**Alternatives Considered:**
- **Supabase**: Similar features but higher complexity (auth/storage bundled)
- **PlanetScale**: MySQL-based, less flexible JSONB support
- **AWS RDS Serverless**: Higher cold start times, complex configuration

**Schema Design Best Practices:**
```sql
-- Conversations table with JSONB metadata
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(255),
    book_id VARCHAR(255) NOT NULL,
    chapter_id INTEGER,
    mode VARCHAR(50) NOT NULL CHECK (mode IN ('book_only', 'selected_text', 'general_knowledge')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'active',
    metadata JSONB  -- Extensible for future fields
);

-- Optimized indexes
CREATE INDEX idx_conversations_user ON conversations(user_id);
CREATE INDEX idx_conversations_book ON conversations(book_id);
CREATE INDEX idx_conversations_created ON conversations(created_at DESC);

-- JSONB GIN index for metadata queries
CREATE INDEX idx_conversations_metadata ON conversations USING GIN (metadata);
```

**Connection Management:**
```python
# Use Neon connection pooler
DATABASE_URL = "postgresql://user:pass@pooler.neon.tech/db"

# Connection pool configuration
pool = asyncpg.create_pool(
    DATABASE_URL,
    min_size=1,      # Minimum connections
    max_size=10,     # Maximum connections
    max_inactive_connection_lifetime=300  # 5 minutes
)
```

---

## 6. RAG Pipeline Architecture

### Decision: Deterministic 5-stage pipeline

**Pipeline Stages:**
1. **Query Embedding** → 2. **Vector Search** → 3. **Metadata Filtering** → 4. **Reranking** → 5. **Context Window Validation**

**Rationale:**
- **Determinism**: Fixed order ensures consistent results (Constitutional Article 1.2)
- **Separation of concerns**: Each stage has clear input/output contracts
- **Testability**: Each stage can be tested independently
- **Observability**: Per-stage logging for debugging

**Stage 1: Query Embedding**
```python
async def embed_query(query: str) -> List[float]:
    """
    Generate query embedding with caching.

    Performance: < 200ms (p95)
    Error handling: Retry with exponential backoff (3 attempts)
    """
    cache_key = hash(query.lower().strip())

    # Check cache (15-minute TTL)
    if cached := await cache.get(cache_key):
        return cached

    # Generate embedding
    response = await openai.Embedding.acreate(
        input=query,
        model="text-embedding-3-large"
    )

    embedding = response['data'][0]['embedding']
    await cache.set(cache_key, embedding, ttl=900)  # 15 minutes

    return embedding
```

**Stage 2: Vector Search**
```python
async def vector_search(
    query_embedding: List[float],
    book_id: str,
    top_k: int = 20
) -> List[SearchResult]:
    """
    Search top-K candidates with metadata filtering.

    Performance: < 100ms (p95)
    Similarity threshold: 0.70 (Constitutional Article 4.2)
    """
    results = await qdrant_client.search(
        collection_name="textbook_chunks",
        query_vector=query_embedding,
        query_filter={
            "must": [
                {"key": "book_id", "match": {"value": book_id}}
            ]
        },
        limit=top_k,
        score_threshold=0.70,
        with_payload=True
    )

    return results
```

**Stage 3: Metadata Filtering**
```python
def filter_by_metadata(
    results: List[SearchResult],
    chapter_id: Optional[int] = None
) -> List[SearchResult]:
    """
    Apply chapter-level filtering if specified.

    Removes: Duplicates, out-of-scope chunks
    """
    filtered = results

    # Chapter constraint (if provided)
    if chapter_id:
        filtered = [r for r in filtered if r.payload['chapter'] == chapter_id]

    # Deduplication by chunk_id
    seen = set()
    deduplicated = []
    for r in filtered:
        chunk_id = r.payload['chunk_id']
        if chunk_id not in seen:
            seen.add(chunk_id)
            deduplicated.append(r)

    return deduplicated
```

**Stage 4: Reranking (Optional)**
```python
async def rerank_results(
    query: str,
    results: List[SearchResult],
    top_n: int = 5
) -> List[SearchResult]:
    """
    Rerank using cross-encoder for semantic relevance.

    Performance: < 300ms (p95)
    Optional: Enable only if retrieval relevance < 80%
    """
    # Use lightweight cross-encoder (e.g., ms-marco-MiniLM-L-6-v2)
    # For now, skip reranking and use vector similarity scores
    return results[:top_n]
```

**Stage 5: Context Window Validation**
```python
def validate_context_window(
    results: List[SearchResult],
    max_tokens: int = 8000
) -> List[SearchResult]:
    """
    Ensure retrieved content fits within context window.

    Max tokens: 8,000 (Constitutional Article 4.2)
    Truncation: Keep highest-scored chunks
    """
    total_tokens = 0
    validated = []

    for result in results:
        chunk_tokens = result.payload['word_count']

        if total_tokens + chunk_tokens <= max_tokens:
            validated.append(result)
            total_tokens += chunk_tokens
        else:
            break  # Stop at budget limit

    return validated
```

---

## 7. Document Chunking Strategy

### Decision: Semantic chunking with 10-15% overlap

**Rationale:**
- **Semantic coherence**: Preserve paragraph/section boundaries (no mid-sentence breaks)
- **Optimal size**: 512-1,024 tokens balances context and precision
- **Overlap**: 10-15% (51-154 tokens) ensures context continuity
- **Metadata preservation**: Chapter, section, page, heading hierarchy

**Implementation:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def chunk_textbook(content: str, metadata: dict) -> List[Chunk]:
    """
    Split textbook content into semantically coherent chunks.

    Chunk size: 512-1,024 tokens
    Overlap: 10-15% (51-154 tokens)
    Boundary: Sentence-level (no mid-sentence breaks)
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=128,  # ~12.5% overlap
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]  # Hierarchy of separators
    )

    chunks = splitter.split_text(content)

    # Enrich with metadata
    enriched_chunks = []
    for i, chunk_text in enumerate(chunks):
        chunk = Chunk(
            chunk_id=f"{metadata['chapter']}_s{metadata['section']}_p{i}",
            text=chunk_text,
            book_id=metadata['book_id'],
            chapter=metadata['chapter'],
            section=metadata['section'],
            page_number=metadata.get('page_number'),
            heading_hierarchy=metadata.get('heading_hierarchy'),
            word_count=len(chunk_text.split()),
            created_at=datetime.utcnow()
        )
        enriched_chunks.append(chunk)

    return enriched_chunks
```

**Best Practices:**
- Process chapters in parallel (async processing)
- Validate no mid-sentence breaks (regex check: `.*[.!?]\s*$`)
- Deduplicate identical chunks (hash-based detection)
- Store provenance for merged duplicates

---

## 8. Grounding Validation & Hallucination Detection

### Decision: Multi-layer validation with entailment checking

**Validation Methods:**

**Layer 1: Citation Mapping**
```python
def validate_citations(response: str, chunks: List[Chunk]) -> ValidationResult:
    """
    Parse response and map factual claims to source chunks.

    Returns: List of supported claims + unsupported claims
    """
    # Extract factual claims (NLP-based or regex)
    claims = extract_claims(response)

    supported = []
    unsupported = []

    for claim in claims:
        # Check if claim is supported by any chunk
        for chunk in chunks:
            if claim_entailed_by_chunk(claim, chunk.text):
                supported.append((claim, chunk.chunk_id))
                break
        else:
            unsupported.append(claim)

    return ValidationResult(
        supported=supported,
        unsupported=unsupported,
        grounding_rate=len(supported) / len(claims)
    )
```

**Layer 2: Entailment Checking (NLI Model)**
```python
async def check_entailment(response: str, sources: List[str]) -> float:
    """
    Use Natural Language Inference to validate response grounding.

    Model: Lightweight NLI (e.g., roberta-large-mnli)
    Threshold: 0.80 confidence (Constitutional Article 4.4)
    """
    # Combine sources into single context
    context = "\n\n".join(sources)

    # Run NLI model (hypothesis: response, premise: context)
    result = await nli_model.predict(
        premise=context,
        hypothesis=response
    )

    # Check if entailment score exceeds threshold
    entailment_score = result['entailment']

    return entailment_score >= 0.80
```

**Layer 3: Entity Extraction & Comparison**
```python
def detect_hallucinations(response: str, sources: List[str]) -> List[str]:
    """
    Compare entities in response vs. sources to detect fabrications.

    Returns: List of potentially hallucinated entities
    """
    # Extract named entities from response
    response_entities = extract_entities(response)

    # Extract named entities from sources
    source_entities = set()
    for source in sources:
        source_entities.update(extract_entities(source))

    # Identify entities in response not present in sources
    hallucinated = [
        entity for entity in response_entities
        if entity not in source_entities
        and not is_reasoning_artifact(entity)  # Allow synthesized reasoning
    ]

    return hallucinated
```

**Fallback Strategy:**
```python
async def validate_and_refine(
    response: str,
    chunks: List[Chunk],
    threshold: float = 0.95
) -> str:
    """
    Validate response and remove unsupported claims if necessary.

    Grounding threshold: 95% (Constitutional Article 10.2)
    """
    validation = validate_citations(response, chunks)

    if validation.grounding_rate < threshold:
        # Remove unsupported claims
        refined_response = remove_unsupported_claims(
            response,
            validation.unsupported
        )

        # Re-validate
        revalidation = validate_citations(refined_response, chunks)

        if revalidation.grounding_rate >= threshold:
            return refined_response
        else:
            # Fallback: Refusal message
            return generate_refusal_message(
                reason="Insufficient grounding",
                suggestions=["Rephrase question", "Enable General Knowledge"]
            )

    return response
```

---

## 9. Mode Enforcement Architecture

### Decision: Hard-coded mode enum + runtime validation

**Rationale:**
- **Immutability**: Three modes cannot be bypassed programmatically (Constitutional Article 3.4)
- **Type safety**: Enum prevents mode injection or manipulation
- **Audit trail**: Mode state logged for every interaction
- **Visual clarity**: Mode indicator always visible to user

**Implementation:**
```python
from enum import Enum
from typing import Literal

# Hard-coded mode enum
class AnsweringMode(str, Enum):
    BOOK_ONLY = "book_only"
    SELECTED_TEXT = "selected_text"
    GENERAL_KNOWLEDGE = "general_knowledge"

# Type-safe mode parameter
ModeType = Literal["book_only", "selected_text", "general_knowledge"]

class ModeEnforcer:
    """
    Enforce mode boundaries with runtime validation.

    Constitutional Article 3.4: Mode violations trigger system errors
    """

    @staticmethod
    def validate_mode(mode: str) -> AnsweringMode:
        """
        Validate mode is one of three allowed values.

        Raises: ValueError if invalid mode
        """
        try:
            return AnsweringMode(mode)
        except ValueError:
            raise ModeViolationError(
                f"Invalid mode: {mode}. Must be one of: {list(AnsweringMode)}"
            )

    @staticmethod
    def enforce_book_only(response: str, chunks: List[Chunk]) -> str:
        """
        Enforce Book-Only mode constraints.

        Requirements:
        - Every factual claim maps to chunk ID
        - No general knowledge fallback
        - Refusal if content insufficient
        """
        validation = validate_citations(response, chunks)

        if validation.grounding_rate < 1.0:  # 100% grounding required
            return generate_refusal_message(
                mode="book_only",
                reason="Insufficient textbook content"
            )

        return response

    @staticmethod
    def enforce_selected_text(
        response: str,
        selected_text: str,
        min_tokens: int = 50,
        max_tokens: int = 4000
    ) -> str:
        """
        Enforce Selected-Text mode constraints.

        Requirements:
        - Zero vector database queries
        - Answer derived only from selection
        - Selection size limits enforced
        """
        token_count = len(selected_text.split())

        if token_count < min_tokens:
            raise InsufficientContextError(
                f"Selection too short ({token_count} tokens). Minimum: {min_tokens}"
            )

        if token_count > max_tokens:
            raise ContextOverflowError(
                f"Selection too long ({token_count} tokens). Maximum: {max_tokens}"
            )

        # Verify response uses only selected text (no external retrieval)
        if not response_derived_from_selection(response, selected_text):
            raise ModeViolationError(
                "Response contaminated with external knowledge"
            )

        return response

    @staticmethod
    def enforce_general_knowledge(response: str) -> str:
        """
        Enforce General Knowledge mode constraints.

        Requirements:
        - Disclaimer shown on first use
        - Visual indicator always present
        - Can be disabled anytime
        """
        # Add disclaimer prefix
        disclaimer = (
            "⚠️ General AI Knowledge Mode Active\n\n"
            "This response is not grounded in your textbook and may contain inaccuracies. "
            "Use for exploration and supplementary learning only.\n\n"
        )

        return disclaimer + response
```

**Mode State Management:**
```python
class ConversationSession:
    """
    Manage mode state within a reading session.

    Constitutional Article 2.5: Mode persists within session, resets between sessions
    """

    def __init__(self, session_id: str, default_mode: AnsweringMode = AnsweringMode.BOOK_ONLY):
        self.session_id = session_id
        self.mode = default_mode
        self.mode_history = [(datetime.utcnow(), default_mode)]

    def switch_mode(self, new_mode: AnsweringMode) -> None:
        """
        Switch to new mode with audit logging.

        Logs: Timestamp, previous mode, new mode
        """
        old_mode = self.mode
        self.mode = ModeEnforcer.validate_mode(new_mode)

        # Log mode switch
        self.mode_history.append((datetime.utcnow(), self.mode))

        logger.info(
            "Mode switched",
            extra={
                "session_id": self.session_id,
                "old_mode": old_mode.value,
                "new_mode": self.mode.value,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

    def get_mode(self) -> AnsweringMode:
        """Get current mode."""
        return self.mode

    def reset_to_default(self) -> None:
        """Reset to Book-Only mode (session end)."""
        self.switch_mode(AnsweringMode.BOOK_ONLY)
```

---

## 10. Citation System Design

### Decision: Inline citations with chunk ID mapping

**Rationale:**
- **Traceability**: Every citation links to retrievable chunk (Constitutional Article 5.1)
- **Transparency**: Confidence scores reflect retrieval quality
- **Verifiability**: Users can navigate to source location

**Citation Format:**
```python
@dataclass
class Citation:
    """
    Citation with source reference and confidence.

    Constitutional Article 5.1: Required fields
    """
    chunk_id: str           # Unique chunk identifier (e.g., "ch3_s21_p2")
    chapter: int            # Chapter number
    section: str            # Section identifier
    title: str              # Section title
    confidence: str         # "high" | "medium" | "low"
    text_preview: str       # First 200 characters of chunk
    similarity_score: float # Vector similarity score (0.0-1.0)

def generate_citations(
    chunks: List[SearchResult]
) -> List[Citation]:
    """
    Generate citations from retrieved chunks.

    Confidence mapping:
    - High: similarity >= 0.85
    - Medium: 0.70 <= similarity < 0.85
    - Low: similarity < 0.70
    """
    citations = []

    for chunk in chunks:
        confidence = (
            "high" if chunk.score >= 0.85
            else "medium" if chunk.score >= 0.70
            else "low"
        )

        citation = Citation(
            chunk_id=chunk.payload['chunk_id'],
            chapter=chunk.payload['chapter'],
            section=chunk.payload['section'],
            title=chunk.payload['title'],
            confidence=confidence,
            text_preview=chunk.payload['text'][:200],
            similarity_score=chunk.score
        )

        citations.append(citation)

    return citations
```

**Response Format with Inline Citations:**
```json
{
  "answer": "The treaty of Versailles was signed in 1919 [1], imposing harsh reparations on Germany [2]. Economic factors contributed to political instability [3].",
  "citations": [
    {
      "id": 1,
      "chunk_id": "ch3_s21_p2",
      "chapter": 3,
      "section": "2.1",
      "title": "The Causes of World War I",
      "confidence": "high",
      "text_preview": "The Treaty of Versailles, signed on June 28, 1919, officially ended World War I...",
      "similarity_score": 0.89
    },
    {
      "id": 2,
      "chunk_id": "ch3_s21_p5",
      "chapter": 3,
      "section": "2.1",
      "title": "The Causes of World War I",
      "confidence": "high",
      "text_preview": "Germany was required to pay substantial war reparations...",
      "similarity_score": 0.87
    },
    {
      "id": 3,
      "chunk_id": "ch3_s23_p1",
      "chapter": 3,
      "section": "2.3",
      "title": "Economic Factors",
      "confidence": "medium",
      "text_preview": "The economic instability following the war led to...",
      "similarity_score": 0.76
    }
  ]
}
```

---

## 11. Performance Optimization Strategies

### 11.1 Caching Strategy

**Multi-layer caching:**
```python
class CacheLayer:
    """
    Three-tier caching for RAG pipeline.

    L1: Query embeddings (15-minute TTL)
    L2: Search results (5-minute TTL)
    L3: Generated responses (1-minute TTL, exact query match only)
    """

    def __init__(self):
        self.l1_cache = {}  # Query embeddings
        self.l2_cache = {}  # Search results
        self.l3_cache = {}  # Generated responses

    async def get_or_compute_embedding(self, query: str) -> List[float]:
        """L1: Cache query embeddings."""
        cache_key = hash_query(query)

        if cache_key in self.l1_cache:
            return self.l1_cache[cache_key]

        embedding = await embed_query(query)
        self.l1_cache[cache_key] = embedding

        return embedding

    async def get_or_search(
        self,
        query_embedding: List[float],
        filters: dict
    ) -> List[SearchResult]:
        """L2: Cache search results."""
        cache_key = hash_search_params(query_embedding, filters)

        if cache_key in self.l2_cache:
            return self.l2_cache[cache_key]

        results = await vector_search(query_embedding, **filters)
        self.l2_cache[cache_key] = results

        return results
```

### 11.2 Batch Processing

**Parallel chunk processing:**
```python
import asyncio

async def process_textbook_parallel(chapters: List[dict]) -> None:
    """
    Process chapters in parallel for faster indexing.

    Concurrency: 5 chapters at a time (balance API rate limits)
    """
    semaphore = asyncio.Semaphore(5)

    async def process_chapter(chapter: dict):
        async with semaphore:
            chunks = chunk_textbook(chapter['content'], chapter['metadata'])
            embeddings = await embed_chunks_batch(chunks)
            await upload_to_qdrant(chunks, embeddings)

    tasks = [process_chapter(chapter) for chapter in chapters]
    await asyncio.gather(*tasks)
```

### 11.3 Connection Pooling

**Persistent database connections:**
```python
# Neon Postgres connection pool
pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=2,
    max_size=10,
    max_inactive_connection_lifetime=300  # 5 minutes
)

# Qdrant client with connection reuse
qdrant_client = QdrantClient(
    url=QDRANT_URL,
    api_key=QDRANT_API_KEY,
    timeout=10  # 10s timeout
)
```

---

## 12. Error Handling & Resilience

### 12.1 Retry Strategy

**Exponential backoff for transient failures:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def call_openai_with_retry(prompt: str) -> str:
    """
    Call OpenAI API with exponential backoff retry.

    Retries: 3 attempts
    Backoff: 1s, 2s, 4s, 8s (capped at 10s)
    """
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            timeout=30
        )
        return response.choices[0].message.content
    except openai.error.RateLimitError:
        logger.warning("Rate limit hit, retrying...")
        raise  # Trigger retry
    except openai.error.APIError:
        logger.error("OpenAI API error, retrying...")
        raise  # Trigger retry
```

### 12.2 Circuit Breaker

**Prevent cascade failures:**
```python
class CircuitBreaker:
    """
    Circuit breaker for external dependencies.

    States: CLOSED (normal) → OPEN (failing) → HALF_OPEN (testing)
    Threshold: 5 failures in 60 seconds → OPEN
    Recovery: 30 second cooldown → HALF_OPEN
    """

    def __init__(self, failure_threshold: int = 5, timeout: int = 30):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = "CLOSED"
        self.last_failure_time = None

    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpen("Service unavailable")

        try:
            result = await func(*args, **kwargs)

            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0

            return result

        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()

            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"

            raise e
```

### 12.3 Graceful Degradation

**Fallback strategies:**
```python
async def answer_question_with_fallbacks(
    query: str,
    mode: AnsweringMode,
    context: dict
) -> dict:
    """
    RAG pipeline with graceful degradation.

    Fallback chain:
    1. Full RAG pipeline (vector search + LLM)
    2. Keyword search fallback (BM25) if vector DB down
    3. Cached response if LLM API down
    4. Clear error message if all fail
    """
    try:
        # Primary path: Full RAG pipeline
        return await full_rag_pipeline(query, mode, context)

    except VectorDBUnavailable:
        logger.warning("Vector DB down, falling back to keyword search")
        return await keyword_search_fallback(query, context)

    except LLMAPIUnavailable:
        logger.warning("LLM API down, checking cache")
        cached_response = await check_response_cache(query)

        if cached_response:
            return cached_response
        else:
            return generate_error_response(
                error_code="SERVICE_UNAVAILABLE",
                message="The AI service is temporarily unavailable. Please try again in a few moments.",
                recovery_actions=[
                    "Wait 1-2 minutes and retry",
                    "Browse related chapters manually",
                    "Contact support if issue persists"
                ]
            )

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return generate_error_response(
            error_code="INTERNAL_ERROR",
            message="An unexpected error occurred. Our team has been notified.",
            recovery_actions=["Try rephrasing your question", "Contact support"]
        )
```

---

## 13. Security Best Practices

### 13.1 Input Sanitization

**Prevent injection attacks:**
```python
import re
from html import escape

def sanitize_user_input(text: str, max_length: int = 500) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Protections:
    - XSS: HTML escaping
    - SQL injection: Parameterized queries (handled by ORM)
    - Prompt injection: Input filtering
    - Length limits: Prevent DoS
    """
    # Enforce length limit
    if len(text) > max_length:
        raise ValueError(f"Input too long (max {max_length} characters)")

    # Remove control characters
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

    # HTML escape for XSS prevention
    text = escape(text)

    # Detect prompt injection attempts
    injection_patterns = [
        r'ignore previous instructions',
        r'system:',
        r'<\|endoftext\|>',
        r'```python',  # Code execution attempts
    ]

    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            raise SuspiciousInputError("Potential injection detected")

    return text
```

### 13.2 Rate Limiting

**Prevent abuse:**
```python
from datetime import datetime, timedelta
import hashlib

class RateLimiter:
    """
    Token bucket rate limiter.

    Tiers:
    - Anonymous: 10 requests/hour
    - Authenticated: 100 requests/hour
    - Premium: 1000 requests/hour

    Burst allowance: 2x base rate for 10 seconds
    """

    def __init__(self, redis_client):
        self.redis = redis_client

        self.tiers = {
            "anonymous": {"rate": 10, "window": 3600, "burst": 20},
            "authenticated": {"rate": 100, "window": 3600, "burst": 200},
            "premium": {"rate": 1000, "window": 3600, "burst": 2000}
        }

    async def check_rate_limit(
        self,
        user_id: str,
        tier: str = "anonymous"
    ) -> dict:
        """
        Check if request is within rate limit.

        Returns: {"allowed": bool, "remaining": int, "reset_at": timestamp}
        """
        config = self.tiers[tier]

        # Redis key: rate_limit:{user_id}:{window}
        window_start = datetime.utcnow().replace(second=0, microsecond=0)
        key = f"rate_limit:{user_id}:{window_start.timestamp()}"

        # Increment counter
        current_count = await self.redis.incr(key)

        # Set expiry on first request
        if current_count == 1:
            await self.redis.expire(key, config["window"])

        # Check if within burst allowance
        allowed = current_count <= config["burst"]
        remaining = max(0, config["burst"] - current_count)
        reset_at = window_start + timedelta(seconds=config["window"])

        return {
            "allowed": allowed,
            "remaining": remaining,
            "reset_at": reset_at.isoformat(),
            "tier": tier
        }
```

### 13.3 API Key Management

**Secure secrets handling:**
```python
import os
from cryptography.fernet import Fernet

# Load secrets from environment variables (never hardcode)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Encrypt sensitive data at rest
encryption_key = os.getenv("ENCRYPTION_KEY").encode()
cipher = Fernet(encryption_key)

def encrypt_sensitive_field(data: str) -> str:
    """Encrypt sensitive data before storing."""
    return cipher.encrypt(data.encode()).decode()

def decrypt_sensitive_field(encrypted_data: str) -> str:
    """Decrypt sensitive data when retrieving."""
    return cipher.decrypt(encrypted_data.encode()).decode()

# Redact secrets from logs
import logging

class SensitiveFormatter(logging.Formatter):
    """Custom formatter to redact API keys from logs."""

    def format(self, record):
        message = super().format(record)

        # Redact patterns
        patterns = [
            (r'sk-[A-Za-z0-9]{48}', 'sk-***REDACTED***'),  # OpenAI keys
            (r'Bearer [A-Za-z0-9_-]+', 'Bearer ***REDACTED***'),  # Auth tokens
        ]

        for pattern, replacement in patterns:
            message = re.sub(pattern, replacement, message)

        return message

# Configure logger with sensitive formatter
logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
handler.setFormatter(SensitiveFormatter())
logger.addHandler(handler)
```

---

## 14. Testing Strategy

### 14.1 Unit Tests

**Test pyramid approach:**
```python
# tests/unit/test_grounding.py
import pytest
from services.rag.grounding import validate_citations, detect_hallucinations

def test_citation_validation_all_supported():
    """Test citation validation with fully supported response."""
    response = "The treaty was signed in 1919."
    chunks = [
        Chunk(text="The Treaty of Versailles was signed on June 28, 1919.", chunk_id="ch3_p1")
    ]

    result = validate_citations(response, chunks)

    assert result.grounding_rate == 1.0
    assert len(result.unsupported) == 0

def test_hallucination_detection():
    """Test detection of fabricated entities."""
    response = "The treaty was signed by President Lincoln in 1919."
    sources = ["The Treaty of Versailles was signed in 1919."]

    hallucinated = detect_hallucinations(response, sources)

    assert "President Lincoln" in hallucinated
```

### 14.2 Integration Tests

**End-to-end RAG pipeline:**
```python
# tests/integration/test_rag_pipeline.py
import pytest
from services.rag import full_rag_pipeline

@pytest.mark.asyncio
async def test_full_rag_pipeline():
    """Test complete RAG pipeline from query to response."""
    query = "What caused World War I?"
    mode = "book_only"
    context = {"book_id": "world_history_101"}

    response = await full_rag_pipeline(query, mode, context)

    # Assertions
    assert response['answer']
    assert len(response['citations']) > 0
    assert all(c['chunk_id'] for c in response['citations'])
    assert response['confidence_score'] > 0.7
    assert response['mode'] == "book_only"
```

### 14.3 Contract Tests

**API contract validation:**
```python
# tests/contract/test_api_contracts.py
from pydantic import ValidationError

def test_chat_request_schema():
    """Validate chat request follows contract."""
    valid_request = {
        "query": "What is photosynthesis?",
        "mode": "book_only",
        "book_id": "biology_101"
    }

    # Should not raise ValidationError
    ChatRequest(**valid_request)

    # Invalid mode should raise error
    invalid_request = {**valid_request, "mode": "invalid_mode"}

    with pytest.raises(ValidationError):
        ChatRequest(**invalid_request)
```

---

## 15. Research Summary & Recommendations

### Key Decisions Matrix

| Component | Decision | Rationale | Risk |
|-----------|----------|-----------|------|
| LLM | OpenAI GPT-3.5/4 | Production-ready, streaming, cost-effective | Vendor lock-in |
| Vector DB | Qdrant Cloud | Serverless, fast, metadata filtering | Limited free tier |
| Embeddings | text-embedding-3-large | SOTA performance, 3072 dims | Cost at scale |
| Serverless | Vercel Functions | Zero config, streaming, global CDN | Limited to Node.js runtime |
| Database | Neon Postgres | Serverless, branching, connection pooler | Pricing uncertainty |
| Chunking | Semantic (512-1024 tokens, 10-15% overlap) | Balances context and precision | Manual tuning needed |
| Grounding | Multi-layer (citation + NLI + entities) | High accuracy, low hallucination | Latency overhead |
| Mode Enforcement | Hard-coded enum + runtime validation | Constitutional compliance | Requires careful testing |
| Caching | 3-tier (embeddings, search, responses) | Reduces cost and latency | Cache invalidation complexity |

### Open Questions / Future Research

1. **Reranking Model Selection**: Evaluate cross-encoder models (ms-marco, colbert) for reranking stage
2. **Monitoring Stack**: Determine observability platform (Datadog, New Relic, Prometheus)
3. **A/B Testing Framework**: Plan experimentation for chunk size, overlap, similarity thresholds
4. **Content Updates**: Design incremental indexing strategy for textbook updates
5. **Multi-language Support**: Research embedding models for non-English content

### Next Steps (Phase 1: Design)

1. Generate `data-model.md` with detailed database schemas
2. Create `contracts/openapi.yaml` with full API specifications
3. Write `quickstart.md` for local development setup
4. Update constitution with any new constraints discovered during research

---

**Research Status**: ✅ Complete
**Ready for Phase 1**: Yes
**Blockers**: None
