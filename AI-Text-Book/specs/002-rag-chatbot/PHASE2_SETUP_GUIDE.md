# Phase 2: Infrastructure Setup Guide

**Feature:** RAG-Powered Textbook Chatbot (002-rag-chatbot)
**Date:** 2026-02-10

This guide walks you through completing Phase 2 infrastructure setup.

---

## Prerequisites

✅ **Already Provisioned (User confirmed):**
- Qdrant Cloud collection (1536 dims, cosine similarity)
- Neon Serverless Postgres database
- OpenAI API key
- Cohere API key (optional)

---

## Step 1: Configure Environment Variables

### 1.1 Copy Environment Template

```bash
cp .env.example .env.local
```

### 1.2 Fill in Your Credentials

Edit `.env.local` and set the following **required** variables:

```bash
# Vector Database (Qdrant Cloud)
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=textbook_chunks

# Database (Neon Serverless Postgres)
NEON_DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# AI Services (REQUIRED)
OPENAI_API_KEY=sk-your_openai_api_key_here

# AI Services (OPTIONAL)
COHERE_API_KEY=your_cohere_api_key_here  # Optional
```

**Optional** (for production features):
```bash
# Rate Limiting (Upstash Redis) - Optional for development
UPSTASH_REDIS_URL=https://your-redis.upstash.io
UPSTASH_REDIS_TOKEN=your_upstash_token_here

# Error Tracking (Sentry) - Optional
SENTRY_DSN=https://your_sentry_dsn@sentry.io/project_id
```

---

## Step 2: Install Python Dependencies

```bash
cd api
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (API framework)
- Qdrant & Postgres clients
- OpenAI, Cohere, LangChain (AI/ML)
- Pydantic, Sentry (validation & monitoring)
- pytest (testing)

---

## Step 3: Verify Infrastructure

Run the infrastructure verification script to test all connections:

```bash
cd api
python scripts/verify_infrastructure.py
```

**Expected Output:**
```
1. Environment Variables
✓ QDRANT_URL: https://...
✓ QDRANT_API_KEY: pJ8k9...
✓ NEON_DATABASE_URL: postgresql://...
✓ OPENAI_API_KEY: sk-proj...

2. Qdrant Vector Database
✓ Connected to Qdrant
✓ Collection verified/created

3. Neon Postgres Database
✓ Connected to Postgres
⚠ No tables found (migrations not run)

4. OpenAI API
✓ OpenAI client initialized
✓ Generated embedding (dim: 1536)

5. Optional Services
⚠ Cohere API configured (optional)
⚠ Upstash Redis not configured (optional)
⚠ Sentry not configured (optional)

6. File Structure
✓ All required files present

✓ ALL CORE INFRASTRUCTURE VERIFIED
```

### Troubleshooting

**Connection Errors:**
- Verify credentials in `.env.local`
- Check network/firewall settings
- Ensure services are active (not paused/suspended)

**Missing Dependencies:**
- Run `pip install -r requirements.txt` again
- Try upgrading pip: `pip install --upgrade pip`

---

## Step 4: Run Database Migrations

Create database tables:

```bash
cd api
python scripts/run_migrations.py
```

**Expected Output:**
```
Testing database connection...
✓ Connected to: your_database

Executing: 001_create_chunk_metadata.sql
✓ 001_create_chunk_metadata.sql completed successfully

Executing: 002_create_query_logs.sql
✓ 002_create_query_logs.sql completed successfully

Executing: 003_create_analytics.sql
✓ 003_create_analytics.sql completed successfully

Verifying database schema...
Found tables: ['analytics', 'chunk_metadata', 'query_logs']
✓ All expected tables exist

Table statistics:
  chunk_metadata: 0 rows
  query_logs: 0 rows
  analytics: 0 rows

Database setup complete!
```

### Verify Migrations

```bash
python scripts/run_migrations.py --verify-only
```

---

## Step 5: Test End-to-End (Optional)

Run a quick test of the complete infrastructure:

```bash
cd api
python -c "
import asyncio
from services.embedding_service import get_embedding_service
from db.qdrant_client import qdrant_client
from db.postgres_client import postgres_client

async def test():
    # Test embedding
    service = get_embedding_service()
    embedding = await service.embed_text('Hello world')
    print(f'✓ Embedding: {len(embedding)} dims')

    # Test Qdrant
    await qdrant_client.ensure_collection_exists()
    print('✓ Qdrant: Collection ready')

    # Test Postgres
    await postgres_client.get_connection()
    print('✓ Postgres: Connected')

    print('All services operational!')

asyncio.run(test())
"
```

---

## Phase 2 Checklist

After completing all steps, verify:

- [x] T024-T028: External services provisioned (Qdrant, Neon, OpenAI)
- [x] T031: `.env.example` created
- [x] T032: `vercel.json` configured
- [x] T033-T035: Migration files created
- [ ] **T036: Migrations executed** ← Complete this step
- [x] T037-T039: Monitoring configured (Sentry, logging)

---

## Next Steps

Once Phase 2 is complete:

### Option A: Run Document Ingestion (Phase 3)

Process your textbook content:

```bash
cd api
python scripts/ingest_pipeline.py --textbook-dir .. --data-dir data
```

This will:
1. Extract markdown files from `docs/`
2. Parse metadata (chapters, sections)
3. Chunk content semantically (1024 chars, 10% overlap)
4. Generate embeddings (OpenAI)
5. Upload to Qdrant
6. Sync metadata to Postgres
7. Validate chunk quality

**Estimated Time:** 10-30 minutes (depending on textbook size)

### Option B: Proceed to Phase 4

Implement core RAG services:
- `retrieval_service.py` - Vector search + reranking
- `generation_service.py` - LLM orchestration
- `citation_service.py` - Citation validation
- `mode_router.py` - Mode boundary enforcement

---

## Common Issues

### Issue: "NEON_DATABASE_URL must be set"
**Solution:** Check `.env.local` exists and contains correct URL

### Issue: "Failed to connect to Qdrant"
**Solution:**
- Verify `QDRANT_URL` and `QDRANT_API_KEY`
- Check Qdrant Cloud dashboard (cluster not paused)

### Issue: "OpenAI API rate limit"
**Solution:**
- Wait and retry (rate limits reset after 1 minute)
- Upgrade OpenAI plan for higher limits

### Issue: "Migration already exists"
**Solution:** This is normal - migrations are idempotent

---

## Support

If you encounter issues:

1. Check logs for detailed error messages
2. Verify all environment variables are set correctly
3. Run `python scripts/verify_infrastructure.py` to diagnose
4. Check service dashboards (Qdrant, Neon, OpenAI)

---

**Status:** Phase 2 infrastructure ready for implementation
**Next:** Run migrations (`python api/scripts/run_migrations.py`)
