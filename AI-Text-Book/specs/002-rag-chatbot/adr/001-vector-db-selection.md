# ADR 001: Vector Database Selection

**Status**: ✅ Accepted
**Date**: 2026-02-05
**Decision Makers**: AI Textbook Platform Team
**Technical Area**: Infrastructure / Data Storage

---

## Context

The RAG-powered textbook chatbot requires a vector database for semantic search over textbook content. The database must support:
- High-dimensional embeddings (1536 dimensions for OpenAI text-embedding-3-small)
- Fast similarity search (<200ms query latency)
- Metadata filtering (chapter, section, page number, heading hierarchy)
- Scalability to 500-800 chunks (~200,000 words of textbook content)
- Managed service with minimal operational overhead (constitutional mandate)

The database will be queried on every user question to retrieve relevant textbook chunks for answer generation.

---

## Decision

We will use **Qdrant Cloud** as our vector database.

---

## Alternatives Considered

### Option 1: Qdrant Cloud ✅ SELECTED
**Pros**:
- Free tier: 1GB storage (~600-800 chunks at 1536 dimensions)
- Query latency: <200ms for vector similarity search
- Rich metadata filtering: Supports complex filters on chapter, section, page, heading
- Python SDK: Well-documented, async support, connection pooling
- Managed service: 99.9% SLA, automatic scaling, no operational overhead
- Cost: $25/month for 4GB if scaling beyond free tier

**Cons**:
- Free tier storage limited to 1GB (may require paid plan for large textbooks)
- Less mature than Pinecone (founded 2021 vs 2019)

**Evaluation Score**: 9/10

### Option 2: Pinecone
**Pros**:
- Fastest latency: <100ms for vector search
- Mature platform: Industry leader, robust features
- Free tier: 1M vectors, 1 index
- Excellent documentation and community support

**Cons**:
- Free tier limited to 1 index (no staging/testing environments)
- More expensive: $70/month for standard plan vs $25/month (Qdrant)
- Less flexible metadata filtering than Qdrant
- Higher vendor lock-in risk

**Evaluation Score**: 7.5/10

### Option 3: Weaviate Cloud
**Pros**:
- Excellent metadata filtering: GraphQL-based queries
- Free tier: 500MB storage
- Strong schema validation and type safety
- Good Python SDK

**Cons**:
- Smaller free tier: 500MB vs 1GB (Qdrant)
- Query latency: <250ms (slower than Qdrant/Pinecone)
- More complex setup: Requires schema definition upfront
- Less community support than Pinecone/Qdrant

**Evaluation Score**: 7/10

### Option 4: Chroma (Self-Hosted)
**Pros**:
- Completely free (no cloud costs)
- Simple Python API
- Local development friendly

**Cons**:
- ❌ **Violates constitutional mandate**: Requires self-hosting, manual maintenance
- No managed service: Operational overhead for backups, scaling, monitoring
- Basic metadata filtering compared to managed alternatives
- Variable latency depending on hardware

**Evaluation Score**: 4/10 (constitutionally prohibited)

---

## Rationale

**Qdrant Cloud** was selected because it provides the best balance of:
1. **Performance**: <200ms latency meets our p95 <3s budget with room for LLM generation
2. **Cost**: Free tier sufficient for MVP (600-800 chunks), paid tier ($25/month) fits budget
3. **Features**: Rich metadata filtering essential for chapter-scoped queries and citation formatting
4. **Constitutional Compliance**: Managed service eliminates operational overhead
5. **Scalability**: Easy upgrade path to paid tiers as textbook content grows

**Key Decision Factors**:
- Qdrant's free tier (1GB) accommodates our current textbook size with room for expansion
- Metadata filtering capabilities enable QueryContext.chapter_filter feature (spec requirement)
- Python SDK quality supports asyncio for serverless function integration
- $25/month paid tier (if needed) is 65% cheaper than Pinecone's $70/month

**Trade-offs Accepted**:
- Slightly slower than Pinecone (<200ms vs <100ms) – acceptable within p95 <3s budget
- Smaller ecosystem than Pinecone – mitigated by excellent documentation and active community

---

## Consequences

### Positive
- ✅ Meets all performance requirements (latency, metadata filtering, scalability)
- ✅ Fits within operational budget ($0-$25/month depending on usage)
- ✅ Complies with constitutional mandates (managed service, no self-hosting)
- ✅ Enables chapter-scoped queries for better answer relevance
- ✅ Reduces operational complexity (no database administration)

### Negative
- ⚠️ Free tier storage limited to 1GB – may require paid plan for large textbooks (>1M words)
- ⚠️ Vendor lock-in to Qdrant Cloud (migration cost if switching providers)
- ⚠️ Less mature than Pinecone (potential for undiscovered edge cases)

### Mitigation Strategies
- **Storage monitoring**: Alert at 80% usage (800MB), plan upgrade before hitting limit
- **Migration path**: Design abstraction layer for vector DB client (easy to swap implementations)
- **Fallback strategy**: Implement keyword search fallback if Qdrant unavailable

---

## Implementation Notes

### Connection Configuration
```python
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY"),
    timeout=5.0  # 5s timeout for queries
)

# Create collection during setup
client.create_collection(
    collection_name="textbook_chunks",
    vectors_config=VectorParams(
        size=1536,  # OpenAI text-embedding-3-small dimensions
        distance=Distance.COSINE  # Cosine similarity for semantic search
    )
)
```

### Query Pattern
```python
# Vector search with metadata filtering
results = client.search(
    collection_name="textbook_chunks",
    query_vector=query_embedding,
    limit=10,  # top_k candidates
    query_filter={
        "must": [
            {"key": "chapter", "match": {"value": "Chapter 3"}}
        ]
    }
)
```

### Monitoring
- Track query latency (p50, p95, p99) in Sentry
- Monitor storage usage via Qdrant Cloud dashboard
- Alert on query errors (connection failures, timeouts)

---

## References

- [Qdrant Cloud Documentation](https://qdrant.tech/documentation/cloud/)
- [Qdrant Python SDK](https://github.com/qdrant/qdrant-client)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- Research Document: `specs/002-rag-chatbot/research.md` (Section 1)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-05 | AI Textbook Platform Team | Initial decision |

---

**Next Review Date**: 2026-05-05 (3 months after implementation)
**Status**: ✅ Accepted and implemented in Phase 2
