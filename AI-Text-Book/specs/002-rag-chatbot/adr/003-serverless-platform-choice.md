# ADR 003: Serverless Platform Selection

**Status**: ✅ Accepted
**Date**: 2026-02-05
**Decision Makers**: AI Textbook Platform Team
**Technical Area**: Infrastructure / Deployment

---

## Context

The RAG-powered chatbot backend requires a serverless platform for deploying the FastAPI application. The platform must:
- Support Python 3.11+ runtime for FastAPI and AI/ML libraries (OpenAI SDK, Qdrant client, sentence-transformers)
- Handle cold starts efficiently (<1s initialization) to meet p95 <3s latency requirement
- Provide sufficient timeout (≥10s) for RAG pipeline execution (embedding + retrieval + reranking + LLM generation)
- Allocate adequate memory (≥512MB) for loading reranker model (~150MB) + dependencies
- Offer generous free tier to support MVP and moderate traffic (100-500 users)
- Comply with constitutional mandate: no manually started servers, stateless functions only

The platform will host:
1. **POST /api/v1/chat**: Main RAG pipeline endpoint (query → embedding → retrieval → generation → response)
2. **GET /api/v1/health**: Health check endpoint for monitoring
3. **GET /api/v1/chunks**: Admin endpoint for chunk inspection

---

## Decision

We will use **Vercel** as the primary serverless platform with **Fly.io** as a fallback for long-running queries.

**Deployment Strategy**:
- **Vercel (Primary)**: All RAG pipeline requests (target: 95% of traffic)
- **Fly.io (Fallback)**: Queries exceeding Vercel timeout (10s) routed to Fly.io API

---

## Alternatives Considered

### Option 1: Vercel ✅ SELECTED (Primary)
**Specs**:
- Cold start: <1s (can be optimized to <500ms with pre-warming)
- Timeout: 10s (hobby), 60s (pro)
- Memory: 512MB (hobby), 1GB (pro)
- Python support: ✅ Python 3.11 with full asyncio
- Free tier: 100GB bandwidth, 100 serverless invocations/hour

**Pros**:
- Fast cold start: <1s meets requirement (target <500ms with pre-warming)
- One-command deployment: `vercel deploy` (excellent DX)
- Built-in edge caching: Upstash integration for rate limiting
- Generous free tier: 100GB bandwidth sufficient for MVP + moderate traffic
- Excellent Python support: FastAPI, asyncio, AI/ML libraries work out-of-box
- Zero configuration: Automatic HTTPS, CDN, scaling

**Cons**:
- 10s timeout (hobby): Tight budget for RAG pipeline (target p95 <3s, p99 <5s)
- 512MB memory (hobby): Limited for large models (reranker ~150MB fits with 350MB margin)
- Regional limitations: Primary region cannot be changed after deployment

**Cost Analysis**:
- Free tier: $0/month (100GB bandwidth, 100 invocations/hour)
- Pro tier (if needed): $20/month (60s timeout, 1GB memory, 1TB bandwidth)
- **Expected**: Stay on free tier for MVP (10k queries/month = 0.46 invocations/min)

**Evaluation Score**: 9/10

### Option 2: Fly.io ✅ SELECTED (Fallback)
**Specs**:
- Cold start: <500ms (faster than Vercel)
- Timeout: 5 minutes (default), configurable up to 30 minutes
- Memory: 256MB-8GB (flexible)
- Python support: ✅ Docker containers, full control
- Free tier: Limited (3 shared-cpu VMs, 160GB bandwidth)

**Pros**:
- **Fastest cold start**: <500ms (faster than Vercel)
- **Long timeout**: 5min default (handles complex queries comfortably)
- **Flexible memory**: 256MB-8GB (can scale for larger models)
- Docker-based: Full control over runtime environment
- Global edge: Deploy to multiple regions for low latency

**Cons**:
- More complex deployment: Requires Dockerfile, fly.toml config
- Smaller free tier: 160GB bandwidth vs 100GB (Vercel)
- Manual scaling configuration: Not as automatic as Vercel
- Requires monitoring setup: No built-in analytics (unlike Vercel)

**Cost Analysis**:
- Free tier: $0/month (3 shared-cpu VMs, 160GB bandwidth)
- Paid tier (if needed): $1.94/month per VM (1GB memory)
- **Expected**: Stay on free tier for fallback traffic (<5% of requests)

**Evaluation Score**: 8.5/10 (excellent fallback, more complex deployment)

### Option 3: AWS Lambda
**Specs**:
- Cold start: 1-3s (slower than Vercel/Fly.io)
- Timeout: 15 minutes
- Memory: 128MB-10GB
- Python support: ✅ Python 3.11
- Free tier: 1M requests/month, 400k GB-seconds compute

**Pros**:
- Massive free tier: 1M requests/month (far exceeds our needs)
- Long timeout: 15min (handles any query complexity)
- Flexible memory: 128MB-10GB (can scale infinitely)
- Mature platform: Battle-tested, extensive documentation

**Cons**:
- **Slower cold start**: 1-3s (exceeds <1s requirement)
- Complex deployment: Requires AWS SAM/CDK, IAM configuration
- More expensive at scale: $0.20 per 1M requests after free tier
- Vendor lock-in: AWS ecosystem dependencies (API Gateway, CloudWatch)

**Cost Analysis**:
- Free tier: $0/month (1M requests/month)
- Paid tier: $0.20 per 1M requests + $0.0000166667 per GB-second
- **Expected**: Stay on free tier (10k requests/month = 1% of free tier)

**Evaluation Score**: 7/10 (powerful but complex, slow cold start)

### Option 4: Cloudflare Workers
**Specs**:
- Cold start: <10ms (fastest)
- Timeout: 30s (CPU time), 50ms for subrequests
- Memory: 128MB
- Python support: ⚠️ Python in beta (Pyodide-based, limited libraries)
- Free tier: 100k requests/day

**Pros**:
- **Ultra-fast cold start**: <10ms (edge-native)
- Generous free tier: 100k requests/day = 3M requests/month
- Global edge network: Low latency worldwide
- Simple deployment: Wrangler CLI

**Cons**:
- ❌ **Limited Python support**: Pyodide-based, not all libraries work (OpenAI SDK, sentence-transformers incompatible)
- **128MB memory**: Too small for reranker model (~150MB)
- **30s CPU timeout**: Tight for RAG pipeline with reranking
- Edge constraints: No persistent connections (Qdrant client may fail)

**Evaluation Score**: 4/10 (Python limitations are blocking)

---

## Rationale

**Vercel (Primary) + Fly.io (Fallback)** was selected because:
1. **Vercel Strengths**: Fast cold start (<1s), easy deployment, generous free tier, excellent Python support
2. **Fly.io Strengths**: Longer timeout (5min), faster cold start (<500ms), Docker flexibility
3. **Complementary**: Vercel handles 95% of traffic (fast queries), Fly.io handles edge cases (slow queries >10s)

**Key Decision Factors**:
- **Cold start**: Vercel <1s meets requirement (optimizable to <500ms)
- **Timeout**: Vercel 10s sufficient for p95 <3s target (Fly.io fallback for p99 >5s)
- **Memory**: Vercel 512MB fits reranker model + dependencies (~400MB total)
- **Cost**: Both stay on free tiers for MVP + moderate traffic
- **Deployment**: Vercel one-command deploy, Fly.io Docker-based (more control)

**Trade-offs Accepted**:
- Vercel 10s timeout (hobby) requires tight optimization – mitigated by Fly.io fallback
- Two platforms increase complexity – justified by reliability and cost savings
- Fly.io free tier limits (3 VMs) – sufficient for fallback traffic (<5% requests)

---

## Consequences

### Positive
- ✅ Fast cold start (<1s Vercel, <500ms Fly.io) meets latency requirements
- ✅ Long timeout fallback (Fly.io 5min) handles complex queries gracefully
- ✅ Generous free tiers on both platforms ($0 cost for MVP)
- ✅ One-command deployment (Vercel) simplifies iteration
- ✅ Graceful degradation: Automatic failover to Fly.io for slow queries

### Negative
- ⚠️ Two platforms increase operational complexity (monitoring, deployment)
- ⚠️ Vercel 10s timeout (hobby) requires optimization (target p95 <3s, p99 <5s)
- ⚠️ Fallback routing logic adds complexity to API gateway

### Mitigation Strategies
- **Timeout optimization**: Lazy model loading, efficient imports, caching
- **Pre-warming**: Health check endpoints to keep Vercel functions warm
- **Monitoring**: Unified logging (Sentry) tracks requests across both platforms
- **Fallback logic**: Simple timeout detection → route to Fly.io API

---

## Implementation Notes

### Vercel Deployment Configuration (`vercel.json`)
```json
{
  "functions": {
    "api/src/main.py": {
      "runtime": "python3.11",
      "memory": 512,
      "maxDuration": 10
    }
  },
  "env": {
    "QDRANT_URL": "@qdrant-url",
    "QDRANT_API_KEY": "@qdrant-api-key",
    "OPENAI_API_KEY": "@openai-api-key",
    "NEON_DATABASE_URL": "@neon-database-url",
    "UPSTASH_REDIS_URL": "@upstash-redis-url",
    "SENTRY_DSN": "@sentry-dsn",
    "FLY_IO_FALLBACK_URL": "@flyio-fallback-url"
  },
  "routes": [
    { "src": "/api/v1/(.*)", "dest": "api/src/main.py" }
  ]
}
```

### Fly.io Deployment Configuration (`fly.toml`)
```toml
app = "rag-chatbot-fallback"
primary_region = "iad"  # US East

[build]
  dockerfile = "Dockerfile"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0  # Scale to zero when idle
  max_machines_running = 3

[[services.ports]]
  port = 80
  handlers = ["http"]
  force_https = true

[[services.ports]]
  port = 443
  handlers = ["tls", "http"]

[services.concurrency]
  type = "connections"
  hard_limit = 25
  soft_limit = 20

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 1024
```

### Fallback Routing Logic
```python
import httpx
from fastapi import Request, HTTPException

VERCEL_TIMEOUT = 10  # seconds
FLYIO_FALLBACK_URL = os.getenv("FLY_IO_FALLBACK_URL")

async def chat_endpoint(request: ChatRequest):
    try:
        # Execute RAG pipeline with timeout
        async with asyncio.timeout(VERCEL_TIMEOUT - 1):  # Reserve 1s buffer
            return await execute_rag_pipeline(request)
    except asyncio.TimeoutError:
        # Query exceeded Vercel timeout, route to Fly.io
        logger.warning(f"Query timeout, routing to Fly.io fallback")
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{FLYIO_FALLBACK_URL}/api/v1/chat",
                json=request.dict(),
                timeout=60  # Fly.io has 5min timeout
            )
            return response.json()
```

### Cold Start Optimization
```python
# Global scope (persists across warm invocations)
_reranker_model = None

def get_reranker_model():
    """Lazy load reranker model on first request."""
    global _reranker_model
    if _reranker_model is None:
        from sentence_transformers import CrossEncoder
        _reranker_model = CrossEncoder('ms-marco-MiniLM-L-12-v2')
    return _reranker_model

# Pre-warm function (called by health check)
@app.on_event("startup")
async def warmup():
    """Pre-load models and connections during cold start."""
    get_reranker_model()  # Load reranker
    await qdrant_client.connect()  # Establish Qdrant connection
    await postgres_client.connect()  # Establish Postgres connection
```

### Monitoring Strategy
- **Sentry**: Unified error tracking across Vercel + Fly.io
- **Vercel Analytics**: Track request volume, latency, bandwidth usage
- **Fly.io Metrics**: Monitor VM usage, fallback request volume
- **Custom Metrics**: Log timeout events (Vercel → Fly.io transitions)

---

## Performance Validation (Phase 8: Experiment 3)

### Cold Start Benchmark
**Hypothesis**: Vercel function pre-warming reduces cold start from 1.2s → <500ms

**Method**:
1. Deploy FastAPI function to Vercel without pre-warming
2. Measure cold start latency (P95, P99) with 100 cold invocations
3. Configure Vercel function pre-warming (health check every 5min)
4. Re-measure cold start latency with pre-warming enabled
5. Compare TTFB (Time to First Byte)

**Success Criteria**:
- Cold start reduces from 1.2s → <500ms with pre-warming
- Warm invocation latency <100ms
- Pre-warming cost <$5/month (included in Vercel free tier)

### Timeout Analysis
**Measure**:
- % of queries exceeding 10s timeout (target: <5%)
- Fallback routing success rate (target: 100%)
- Fly.io latency for slow queries (target: <30s)

---

## Migration Path (If Needed)

### Scenario: Vercel timeout (10s) becomes blocking
**Option 1**: Upgrade to Vercel Pro ($20/month for 60s timeout)
**Option 2**: Shift primary traffic to Fly.io (requires DNS + routing changes)
**Option 3**: Optimize RAG pipeline to fit within 10s (remove reranking, use GPT-3.5)

### Scenario: Cost exceeds budget
**Option 1**: Optimize bandwidth usage (compression, caching)
**Option 2**: Migrate to AWS Lambda (larger free tier, 1M requests/month)
**Option 3**: Self-host on Fly.io with auto-scaling (last resort, violates serverless mandate)

---

## References

- [Vercel Python Documentation](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Fly.io Documentation](https://fly.io/docs/)
- [FastAPI Deployment Guide](https://fastapi.tiangolo.com/deployment/)
- Research Document: `specs/002-rag-chatbot/research.md` (Section 4)

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-02-05 | AI Textbook Platform Team | Initial decision (Vercel + Fly.io) |

---

**Next Review Date**: 2026-05-05 (3 months after implementation)
**Status**: ✅ Accepted, Vercel implemented in Phase 2, Fly.io fallback in Phase 5
