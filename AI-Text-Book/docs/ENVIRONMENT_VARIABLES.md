# Environment Variables Reference

> **T140** — Complete reference for all environment variables.

## Backend (api/.env)

### Required — External Services

| Variable | Example | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | `sk-...` | OpenAI API key for embeddings and generation |
| `COHERE_API_KEY` | `...` | Cohere API key (optional reranking fallback) |
| `QDRANT_URL` | `https://xyz.qdrant.io` | Qdrant Cloud cluster URL |
| `QDRANT_API_KEY` | `...` | Qdrant Cloud API key |
| `QDRANT_COLLECTION_NAME` | `textbook_chunks` | Qdrant collection name |
| `NEON_DATABASE_URL` | `postgresql://...` | Neon Postgres connection string |
| `UPSTASH_REDIS_URL` | `https://...upstash.io` | Upstash Redis REST URL |
| `UPSTASH_REDIS_TOKEN` | `...` | Upstash Redis REST token |

### Required — Application

| Variable | Default | Description |
|----------|---------|-------------|
| `FRONTEND_URL` | — | Production frontend URL (for CORS) |
| `SENTRY_DSN` | — | Sentry DSN (disabled if not set) |
| `SENTRY_ENVIRONMENT` | `development` | Sentry environment label |

### Optional — RAG Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_TOP_K` | `10` | Number of chunks retrieved |
| `RAG_SIMILARITY_THRESHOLD` | `0.7` | Minimum vector similarity score |
| `RAG_TEMPERATURE` | `0.3` | Generation temperature (0=deterministic) |
| `RAG_MAX_TOKENS` | `8000` | Maximum tokens per generation |
| `RAG_CHUNK_SIZE` | `1024` | Token size per chunk |
| `RAG_CHUNK_OVERLAP` | `0.1` | Chunk overlap fraction |

### Optional — Security (T108, T112)

| Variable | Default | Description |
|----------|---------|-------------|
| `CLOUDFLARE_TURNSTILE_SECRET_KEY` | — | Enables CAPTCHA; disabled if not set |
| `CAPTCHA_BURST_THRESHOLD` | `30` | Requests per window to trigger CAPTCHA |
| `CAPTCHA_WINDOW_SECONDS` | `60` | Sliding window for anomaly detection |
| `API_SIGNING_SECRET` | — | HMAC signing secret; disabled if not set |
| `ENFORCE_REQUEST_SIGNING` | `false` | Set `true` to require signatures |
| `SIGNATURE_TTL_SECONDS` | `300` | Max age of a signed request (replay protection) |

### Optional — Rate Limiting (T106)

| Variable | Default | Description |
|----------|---------|-------------|
| `CHATBOT_RATE_LIMIT_ANONYMOUS` | `10` | Requests/hour for anonymous users |
| `CHATBOT_RATE_LIMIT_AUTHENTICATED` | `100` | Requests/hour for authenticated users |
| `CHATBOT_RATE_LIMIT_PREMIUM` | `1000` | Requests/hour for premium users |

### Optional — CORS (T111)

| Variable | Default | Description |
|----------|---------|-------------|
| `FRONTEND_URL_ALT` | — | Alternative frontend URL (e.g. Vercel preview) |
| `CORS_ORIGIN_1` | — | Additional allowed CORS origin |
| `CORS_ORIGIN_2` | — | Additional allowed CORS origin |

### Optional — Observability (T119, T121)

| Variable | Default | Description |
|----------|---------|-------------|
| `SENTRY_TRACES_SAMPLE_RATE` | `1.0` | Performance tracing sample rate (0–1) |
| `SENTRY_PROFILES_SAMPLE_RATE` | `1.0` | CPU profiling sample rate (0–1) |
| `ALERT_ERROR_RATE_THRESHOLD` | `0.05` | Error rate threshold for alerts |
| `ALERT_LATENCY_P95_MS` | `5000` | P95 latency threshold (ms) |

---

## Frontend (.env)

| Variable | Default | Description |
|----------|---------|-------------|
| `REACT_APP_API_URL` | `http://localhost:8000` | Backend API URL |
| `REACT_APP_API_TIMEOUT` | `30000` | Request timeout in ms |
| `REACT_APP_CF_TURNSTILE_SITE_KEY` | — | Cloudflare Turnstile site key (for CAPTCHA widget) |

---

## Setting Variables in Vercel

```bash
# Add a variable
vercel env add VARIABLE_NAME production

# Remove a variable
vercel env rm VARIABLE_NAME production

# List all variables
vercel env ls production

# Pull to local .env
vercel env pull .env.local
```

---

## Local Development Setup

```bash
# Copy template
cp .env.template .env

# Minimum required for local dev (with real services):
OPENAI_API_KEY=sk-...
QDRANT_URL=https://...
QDRANT_API_KEY=...
QDRANT_COLLECTION_NAME=textbook_chunks
NEON_DATABASE_URL=postgresql://...

# Optional for local dev (these features disabled if not set):
# UPSTASH_REDIS_URL=    → rate limiting disabled
# SENTRY_DSN=          → error tracking disabled
# CLOUDFLARE_TURNSTILE_SECRET_KEY=  → CAPTCHA disabled
```

---

*Last reviewed: 2026-02-28*
