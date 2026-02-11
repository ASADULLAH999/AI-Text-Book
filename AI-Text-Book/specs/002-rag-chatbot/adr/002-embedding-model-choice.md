# ADR 002: Embedding Model Selection

**Status**: ✅ Accepted
**Date**: 2026-02-05
**Decision Makers**: AI Textbook Platform Team
**Technical Area**: Machine Learning / Natural Language Processing

---

## Context

The RAG-powered chatbot requires an embedding model to convert textbook chunks and user queries into dense vector representations for semantic search. The embedding model must:
- Generate high-quality embeddings for educational/technical content
- Support context windows large enough for textbook chunks (512-1024 tokens)
- Operate within cost constraints (<$50/month operational budget)
- Integrate with serverless architecture (API-based or deployable in 512MB functions)
- Provide consistent, deterministic embeddings for caching

The model will be used for:
1. **One-time ingestion**: Embed ~600-800 textbook chunks (450,000 tokens total)
2. **Query-time embedding**: Embed user queries (~50 tokens average, 10,000/month)

---

## Decision

We will use **OpenAI text-embedding-3-small** for both textbook chunk and query embeddings.

---

## Alternatives Considered

### Option 1: OpenAI text-embedding-3-small ✅ SELECTED
**Specs**:
- Dimensions: 1536
- Cost: $0.02 per 1M tokens
- Context window: 8191 tokens
- MTEB score: 62.3%
- Latency: ~50ms per request

**Pros**:
- Best cost/performance ratio: $0.02/1M tokens vs $0.13/1M (3-large)
- 8191 token context window handles large chunks (512-1024 tokens)
- 1536 dimensions balance accuracy and Qdrant storage efficiency
- API-based service (constitutional mandate: no custom infrastructure)
- OpenAI reliability: 99.9% SLA, excellent uptime
- Consistent embeddings for caching (deterministic output)

**Cons**:
- 2.3% lower accuracy than text-embedding-3-large (62.3% vs 64.6% MTEB)
- API dependency (requires network calls, potential latency)
- Rate limits: 3000 tokens/min on free tier (requires batching during ingestion)

**Cost Analysis**:
- Ingestion: 600 chunks × 750 tokens avg = 450,000 tokens = **$0.009** (one-time)
- Query: 10,000 queries/month × 50 tokens avg = 500,000 tokens = **$0.01/month**
- **Total**: ~$0.02/month (0.04% of $50 budget)

**Evaluation Score**: 9.5/10

### Option 2: OpenAI text-embedding-3-large
**Specs**:
- Dimensions: 3072
- Cost: $0.13 per 1M tokens
- Context window: 8191 tokens
- MTEB score: 64.6%
- Latency: ~80ms per request

**Pros**:
- 2.3% better accuracy than 3-small (64.6% vs 62.3% MTEB)
- Same 8191 token context window
- Same API reliability and uptime

**Cons**:
- **6.5x higher cost**: $0.13/1M vs $0.02/1M tokens
- **2x larger vectors**: 3072 dims doubles Qdrant storage requirements
- +30ms latency per query (80ms vs 50ms)
- Marginal accuracy improvement (2.3%) doesn't justify 6.5x cost increase

**Cost Analysis**:
- Ingestion: 450,000 tokens = **$0.06** (one-time)
- Query: 500,000 tokens/month = **$0.065/month**
- **Total**: ~$0.13/month (0.26% of budget)
- **Qdrant storage**: 2x larger vectors reduce free tier capacity (600 chunks → 300 chunks)

**Evaluation Score**: 6/10 (not cost-effective)

### Option 3: Sentence-Transformers (Local)
**Specs**:
- Model: all-MiniLM-L6-v2
- Dimensions: 384
- Cost: Free (compute only)
- Context window: 256 tokens
- MTEB score: ~58%
- Latency: ~100ms per batch (CPU)

**Pros**:
- No API costs (compute only)
- Offline capability (no network dependency)
- Fast inference with batching

**Cons**:
- ❌ **Violates serverless mandate**: Requires local model deployment (~90MB)
- Lower accuracy: 58% MTEB vs 62.3% (OpenAI 3-small)
- Smaller context window: 256 tokens vs 8191 (cannot handle full chunks)
- Model loading adds cold start latency (+500ms)
- Memory footprint reduces available space in 512MB function

**Evaluation Score**: 4/10 (constitutional violation + accuracy concerns)

### Option 4: Cohere embed-english-v3
**Specs**:
- Dimensions: 1024
- Cost: $0.10 per 1M tokens
- Context window: 512 tokens
- MTEB score: 64.5%
- Latency: ~70ms per request

**Pros**:
- Similar accuracy to OpenAI 3-large (64.5% MTEB)
- API-based service (constitutional compliance)
- Good Python SDK

**Cons**:
- **5x higher cost**: $0.10/1M vs $0.02/1M (OpenAI 3-small)
- **Smaller context window**: 512 tokens vs 8191 (limits chunk size)
- Less mature API: Fewer integrations, smaller community
- +20ms latency vs OpenAI 3-small

**Cost Analysis**:
- Ingestion: 450,000 tokens = **$0.045** (one-time)
- Query: 500,000 tokens/month = **$0.05/month**
- **Total**: ~$0.10/month (0.20% of budget)
- **Context window limitation**: Chunks must be <512 tokens (reduces granularity)

**Evaluation Score**: 5.5/10 (cost + context window constraints)

---

## Rationale

**OpenAI text-embedding-3-small** was selected because it provides:
1. **Best Cost/Performance Ratio**: $0.02/1M tokens with 62.3% MTEB accuracy
2. **Large Context Window**: 8191 tokens handles our largest chunks (1024 tokens) comfortably
3. **Optimal Dimensions**: 1536 dims balance accuracy and Qdrant storage efficiency
4. **Constitutional Compliance**: API-based service, no local deployment required
5. **Reliability**: OpenAI 99.9% SLA, proven uptime, excellent error handling

**Key Decision Factors**:
- **Cost efficiency**: Total cost ~$0.02/month (0.04% of budget) vs $0.13/month (3-large)
- **Context window**: 8191 tokens vs 512 (Cohere) enables flexible chunking strategy
- **Accuracy trade-off**: 2.3% accuracy difference (62.3% vs 64.6%) not material for textbook retrieval
- **Storage efficiency**: 1536 dims vs 3072 (3-large) doubles Qdrant free tier capacity

**Trade-offs Accepted**:
- 2.3% lower accuracy than text-embedding-3-large – acceptable given cost savings and storage efficiency
- API dependency – mitigated by embedding caching and exponential backoff retry strategy
- Rate limits (3000 tokens/min) – handled by batching during ingestion phase

---

## Consequences

### Positive
- ✅ Minimal cost impact (<$0.02/month = 0.04% of operational budget)
- ✅ Flexible chunking strategy (512-1024 tokens supported by 8191 context window)
- ✅ Doubles Qdrant free tier capacity (1536 dims vs 3072 for 3-large)
- ✅ Fast query latency (~50ms per embedding, negligible in p95 <3s budget)
- ✅ No operational overhead (API-based, no model deployment)

### Negative
- ⚠️ 2.3% lower accuracy than text-embedding-3-large (62.3% vs 64.6% MTEB)
- ⚠️ API dependency introduces network latency and potential failures
- ⚠️ Rate limits on free tier (3000 tokens/min) require batching during ingestion

### Mitigation Strategies
- **Accuracy**: Cross-encoder reranking compensates for embedding quality (ADR 003)
- **API failures**: Cache embeddings locally, retry with exponential backoff
- **Rate limits**: Batch ingestion requests (100 chunks per call), respect rate limits with delays

---

## Implementation Notes

### Embedding Generation (Ingestion)
```python
import openai
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
def generate_embeddings(texts: list[str]) -> list[list[float]]:
    """Generate embeddings with retry logic for rate limit handling."""
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
        encoding_format="float"
    )
    return [item.embedding for item in response.data]

# Batch process chunks (100 per request to respect rate limits)
for i in range(0, len(chunks), 100):
    batch = chunks[i:i+100]
    embeddings = generate_embeddings([chunk.text for chunk in batch])
    # Cache embeddings locally
    save_embeddings_to_cache(batch, embeddings)
```

### Query Embedding (Real-time)
```python
async def embed_query(query: str) -> list[float]:
    """Embed user query with caching."""
    # Check cache first (optional optimization)
    cached = get_cached_embedding(query)
    if cached:
        return cached

    # Generate embedding
    response = await openai.embeddings.acreate(
        model="text-embedding-3-small",
        input=query,
        encoding_format="float"
    )
    embedding = response.data[0].embedding

    # Cache for future queries
    cache_embedding(query, embedding)
    return embedding
```

### Cost Monitoring
```python
# Track embedding API usage in Postgres analytics table
INSERT INTO embedding_usage (
    date,
    tokens_used,
    cost_usd,
    request_type
) VALUES (
    CURRENT_DATE,
    token_count,
    token_count * 0.00000002,  # $0.02/1M tokens
    'query'  # or 'ingestion'
);
```

### Fallback Strategy
- **Primary**: OpenAI text-embedding-3-small API
- **Fallback 1**: Use pre-computed embeddings from cache (query-time only)
- **Fallback 2**: Queue embedding request, retry with exponential backoff
- **Fallback 3**: Degrade to keyword search if embedding API unavailable (graceful degradation)

---

## Performance Validation

### Expected Metrics
- **Ingestion latency**: 450,000 tokens / 3000 tokens/min = 150 minutes (one-time)
- **Query latency**: ~50ms per query embedding (negligible in p95 <3s budget)
- **Retrieval precision**: >85% Precision@3 (validated in Phase 3 experiments)
- **Cost**: <$0.02/month (well within $50 budget)

### Validation Experiments (Phase 3)
- **Experiment 1**: Measure Precision@3 on 50 ground-truth Q&A pairs
- **Experiment 2**: Compare 3-small vs 3-large accuracy improvement (justify cost difference)
- **Experiment 3**: Measure cache hit rate for query embeddings (optimize costs)

---

## References

- [OpenAI Embeddings Documentation](https://platform.openai.com/docs/guides/embeddings)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [OpenAI Pricing](https://openai.com/pricing)
- Research Document: `specs/002-rag-chatbot/research.md` (Section 2)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-05 | AI Textbook Platform Team | Initial decision |

---

**Next Review Date**: 2026-05-05 (3 months after implementation)
**Status**: ✅ Accepted and implemented in Phase 3-4
