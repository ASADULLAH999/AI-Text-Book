# Deployment Guide

> **T136** — Step-by-step guide to deploy the AI Textbook frontend and backend.

## Architecture Overview

```
┌─────────────────────┐     ┌──────────────────────┐
│   Vercel (Frontend) │────▶│  Vercel (API)         │
│   Docusaurus SPA    │     │  FastAPI + Python 3.11 │
└─────────────────────┘     └──────────────────────┘
                                       │
               ┌───────────────────────┼──────────────────┐
               ▼                       ▼                  ▼
        ┌──────────┐          ┌──────────────┐   ┌──────────────┐
        │  Qdrant  │          │     Neon     │   │   Upstash    │
        │  Cloud   │          │  Serverless  │   │    Redis     │
        │ (vectors)│          │  Postgres    │   │  (rate limit)│
        └──────────┘          └──────────────┘   └──────────────┘
```

---

## Prerequisites

- Node.js 20.x
- Python 3.11
- Vercel CLI: `npm install -g vercel`
- All managed services provisioned (see `docs/INFRASTRUCTURE_SETUP.md`)

---

## Step 1 — Environment Setup

```bash
cp .env.template .env
# Fill in all required values:
# OPENAI_API_KEY, COHERE_API_KEY, QDRANT_URL, QDRANT_API_KEY,
# QDRANT_COLLECTION_NAME, NEON_DATABASE_URL, UPSTASH_REDIS_URL,
# UPSTASH_REDIS_TOKEN, SENTRY_DSN, FRONTEND_URL
```

---

## Step 2 — Ingest Textbook Content

```bash
cd api

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python scripts/run_migrations.py

# Chunk textbook
python scripts/chunk_textbook.py --input ../docs/ --output data/chunks/

# Generate embeddings
python scripts/generate_embeddings.py --input data/chunks/

# Upload to Qdrant
python scripts/upload_to_qdrant.py --input data/chunks/

# Validate ingestion
python scripts/validate_chunks.py
```

---

## Step 3 — Deploy API

```bash
cd api

# Configure Vercel environment variables
vercel env add OPENAI_API_KEY production
vercel env add COHERE_API_KEY production
vercel env add QDRANT_URL production
vercel env add QDRANT_API_KEY production
vercel env add QDRANT_COLLECTION_NAME production
vercel env add NEON_DATABASE_URL production
vercel env add UPSTASH_REDIS_URL production
vercel env add UPSTASH_REDIS_TOKEN production
vercel env add SENTRY_DSN production
vercel env add SENTRY_ENVIRONMENT production  # "production"
vercel env add FRONTEND_URL production        # e.g. https://ai-textbook.example.com

# Deploy
vercel --prod

# Verify
curl https://ai-textbook-chatbot-api.vercel.app/api/v1/health
```

**API Documentation**: After deployment, visit `/api/v1/docs` for the Swagger UI (T135).

---

## Step 4 — Deploy Frontend

```bash
# From repo root

# Install dependencies
npm ci

# Set environment variable for API URL
echo "REACT_APP_API_URL=https://ai-textbook-chatbot-api.vercel.app" >> .env

# Build and deploy
vercel --prod
```

The root `vercel.json` handles:
- CDN caching headers for static assets (T102)
- Rewriting `/api/*` to the API Vercel deployment

---

## Step 5 — Verify Deployment

```bash
# 1. Health check
curl https://api.your-domain.com/api/v1/health

# 2. Smoke test
curl -X POST https://api.your-domain.com/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is ROS2?", "mode": "book_only"}'

# 3. Latency validation
python scripts/validate_latency.py --api-url https://api.your-domain.com --n 50

# 4. Quality validation
python scripts/validate_quality.py --api-url https://api.your-domain.com --n 20
```

---

## Step 6 — Configure Monitoring

See `docs/OBSERVABILITY_SETUP.md` for:
- Sentry error tracking setup
- Vercel Analytics
- Alert configuration (T121)

---

## Rollback Procedure

```bash
# List recent deployments
vercel ls

# Roll back to previous
vercel rollback

# Or deploy a specific commit
git checkout <commit-sha>
vercel --prod
```

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | ✓ | OpenAI API key |
| `COHERE_API_KEY` | ✓ | Cohere reranking key |
| `QDRANT_URL` | ✓ | Qdrant Cloud cluster URL |
| `QDRANT_API_KEY` | ✓ | Qdrant Cloud API key |
| `QDRANT_COLLECTION_NAME` | ✓ | Collection name (default: `textbook_chunks`) |
| `NEON_DATABASE_URL` | ✓ | Neon Postgres connection string |
| `UPSTASH_REDIS_URL` | ✓ | Upstash Redis REST URL |
| `UPSTASH_REDIS_TOKEN` | ✓ | Upstash Redis token |
| `SENTRY_DSN` | ✓ | Sentry DSN for error tracking |
| `FRONTEND_URL` | ✓ | Frontend URL for CORS |
| `SENTRY_ENVIRONMENT` | | `production` or `staging` |
| `CLOUDFLARE_TURNSTILE_SECRET_KEY` | | Enables CAPTCHA (T108) |
| `API_SIGNING_SECRET` | | Enables request signing (T112) |
| `ENFORCE_REQUEST_SIGNING` | | `true` to enforce signing |
| `CHATBOT_RATE_LIMIT_ANONYMOUS` | | Requests/hr for anonymous (default: 10) |
| `CHATBOT_RATE_LIMIT_AUTHENTICATED` | | Requests/hr for authenticated (default: 100) |
| `RAG_TOP_K` | | Vector search top-k (default: 10) |
| `RAG_SIMILARITY_THRESHOLD` | | Min similarity score (default: 0.7) |
| `RAG_MAX_TOKENS` | | Max generation tokens (default: 8000) |

---

*Last reviewed: 2026-02-28*
