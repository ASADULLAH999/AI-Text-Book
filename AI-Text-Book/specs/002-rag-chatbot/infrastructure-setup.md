# Infrastructure Setup Guide

**Feature ID:** 002-rag-chatbot
**Phase:** 2 (Infrastructure Setup)
**Created:** 2026-02-05
**Status:** Ready for Execution

---

## Overview

This guide provides step-by-step instructions for provisioning all external services required for the RAG chatbot. Follow tasks T024-T036 in order.

**Estimated Time**: 2-3 hours
**Cost**: $0/month (all free tiers)

---

## Prerequisites

- GitHub account (for Vercel authentication)
- Credit card (required for some free tier signups, not charged)
- Email address for service notifications

---

## Task T024: Provision Qdrant Cloud

**Purpose**: Vector database for semantic search over textbook chunks

### Step 1: Sign Up for Qdrant Cloud

1. Visit https://cloud.qdrant.io/
2. Click "Sign Up" → Sign up with GitHub (recommended)
3. Verify email address

### Step 2: Create a Cluster

1. Click "Create Cluster"
2. **Cluster Name**: `textbook-rag-prod`
3. **Plan**: Free tier (1GB storage, 100 collections)
4. **Region**: US East (or closest to your users)
5. Click "Create"

### Step 3: Get API Credentials

1. Navigate to cluster details
2. Copy **Cluster URL** (format: `https://xxx.cloud.qdrant.io:6333`)
3. Generate **API Key**:
   - Click "API Keys" tab
   - Click "Create API Key"
   - Copy key (shown once only - save it!)

### Step 4: Save Credentials

```bash
# Add to your environment variables (DO NOT commit)
QDRANT_URL=https://xxx.cloud.qdrant.io:6333
QDRANT_API_KEY=your_api_key_here
```

**✅ Verification**: Test connection with curl:
```bash
curl -X GET "$QDRANT_URL/collections" \
  -H "api-key: $QDRANT_API_KEY"
# Expected: {"result": {"collections": []}, "status": "ok", "time": 0.001}
```

---

## Task T025: Provision Neon Serverless Postgres

**Purpose**: Relational database for chunk metadata, query logs, analytics

### Step 1: Sign Up for Neon

1. Visit https://neon.tech/
2. Click "Sign Up" → Sign up with GitHub (recommended)
3. Skip onboarding wizard (click "Skip for now")

### Step 2: Create a Database

1. Click "Create a project"
2. **Project Name**: `textbook-rag-prod`
3. **Database Name**: `rag_chatbot`
4. **Region**: US East (same as Qdrant)
5. **Plan**: Free tier (10GB storage, unlimited queries)
6. Click "Create Project"

### Step 3: Get Connection String

1. Navigate to project dashboard
2. Copy **Connection String** (Pooled connection)
   - Format: `postgres://user:password@host.neon.tech/dbname?sslmode=require`

### Step 4: Save Credentials

```bash
# Add to your environment variables
NEON_DATABASE_URL=postgres://user:password@host.neon.tech/dbname?sslmode=require
```

**✅ Verification**: Test connection with psql:
```bash
psql "$NEON_DATABASE_URL" -c "SELECT version();"
# Expected: PostgreSQL version info
```

---

## Task T026: Setup Upstash Redis

**Purpose**: Edge-compatible rate limiting (Redis KV store)

### Step 1: Sign Up for Upstash

1. Visit https://upstash.com/
2. Click "Sign Up" → Sign up with GitHub
3. Complete email verification

### Step 2: Create a Redis Database

1. Click "Create Database"
2. **Database Name**: `textbook-rag-ratelimit`
3. **Type**: Regional (Global is paid)
4. **Region**: US East (same as Qdrant/Neon)
5. **Plan**: Free tier (10k commands/day)
6. Click "Create"

### Step 3: Get Connection Details

1. Navigate to database details
2. Copy **REST URL** (format: `https://xxx.upstash.io`)
3. Copy **REST Token**

### Step 4: Save Credentials

```bash
# Add to your environment variables
UPSTASH_REDIS_URL=https://xxx.upstash.io
UPSTASH_REDIS_TOKEN=your_token_here
```

**✅ Verification**: Test connection with curl:
```bash
curl -X POST "$UPSTASH_REDIS_URL/SET/test/value" \
  -H "Authorization: Bearer $UPSTASH_REDIS_TOKEN"
# Expected: {"result":"OK"}
```

---

## Task T027: Setup Sentry

**Purpose**: Error tracking and performance monitoring

### Step 1: Sign Up for Sentry

1. Visit https://sentry.io/signup/
2. Sign up with GitHub
3. Choose **Developer** plan (free)

### Step 2: Create a Project

1. Click "Create Project"
2. **Platform**: Python (FastAPI)
3. **Project Name**: `textbook-rag-api`
4. **Team**: Your default team
5. Click "Create Project"

### Step 3: Get DSN

1. Navigate to **Settings** → **Projects** → `textbook-rag-api`
2. Click "Client Keys (DSN)"
3. Copy **DSN** (format: `https://xxx@xxx.ingest.sentry.io/xxx`)

### Step 4: Save Credentials

```bash
# Add to your environment variables
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
```

**✅ Verification**: Test with Python:
```python
import sentry_sdk
sentry_sdk.init(dsn="your_dsn_here")
sentry_sdk.capture_message("Test from setup")
# Check Sentry dashboard for test event
```

---

## Task T028: Obtain OpenAI API Key

**Purpose**: Embeddings (text-embedding-3-small) and LLM (gpt-4-turbo)

### Step 1: Sign Up for OpenAI

1. Visit https://platform.openai.com/signup
2. Sign up with email or Google
3. Verify email and phone number

### Step 2: Add Payment Method

1. Navigate to **Settings** → **Billing**
2. Click "Add payment method"
3. Enter credit card details
4. Set usage limit: $10/month (recommended for MVP)

### Step 3: Create API Key

1. Navigate to **API Keys**
2. Click "Create new secret key"
3. **Name**: `textbook-rag-chatbot`
4. **Permissions**: All (default)
5. Copy key (shown once only - save it!)

### Step 4: Save Credentials

```bash
# Add to your environment variables
OPENAI_API_KEY=sk-xxx
```

**✅ Verification**: Test with curl:
```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
# Expected: List of available models
```

---

## Task T029: Setup Vercel Project

**Purpose**: Serverless deployment platform for API and frontend

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
```

### Step 2: Login to Vercel

```bash
vercel login
# Follow browser authentication flow
```

### Step 3: Link Project

```bash
cd F:/project/practice/hackthon/AI-Text-Book
vercel link
# Follow prompts:
# - Create new project? Yes
# - Project name: textbook-rag-chatbot
# - Link to existing directory? Yes
```

### Step 4: Verify Project

```bash
vercel ls
# Expected: Project listed
```

**✅ Verification**: Project appears in Vercel dashboard at https://vercel.com/dashboard

---

## Task T030: Configure Environment Variables in Vercel

**Purpose**: Inject secrets into serverless functions

### Step 1: Add Environment Variables via CLI

```bash
# Qdrant
vercel env add QDRANT_URL production
# Paste: https://xxx.cloud.qdrant.io:6333

vercel env add QDRANT_API_KEY production
# Paste: your_qdrant_api_key

# Neon Postgres
vercel env add NEON_DATABASE_URL production
# Paste: postgres://user:password@host.neon.tech/dbname

# OpenAI
vercel env add OPENAI_API_KEY production
# Paste: sk-xxx

# Upstash
vercel env add UPSTASH_REDIS_URL production
# Paste: https://xxx.upstash.io

vercel env add UPSTASH_REDIS_TOKEN production
# Paste: your_redis_token

# Sentry
vercel env add SENTRY_DSN production
# Paste: https://xxx@xxx.ingest.sentry.io/xxx
```

### Step 2: Add for Development/Preview

```bash
# Copy all production env vars to preview and development
vercel env pull .env.local
```

**✅ Verification**: Check Vercel dashboard → Project → Settings → Environment Variables (7 secrets should be listed)

---

## Task T031: Create .env.example File

**Purpose**: Document required environment variables for local development

File created at: `F:\project\practice\hackthon\AI-Text-Book\.env.example`

---

## Task T032: Create vercel.json Configuration

**Purpose**: Configure serverless function routes, memory, and timeout

File created at: `F:\project\practice\hackthon\AI-Text-Book\api\vercel.json`

---

## Task T033-T035: Create Postgres Migrations

**Purpose**: Initialize database schema for chunk metadata, query logs, and analytics

Migration files created at:
- `api/src/db/migrations/001_create_chunk_metadata.sql`
- `api/src/db/migrations/002_create_query_logs.sql`
- `api/src/db/migrations/003_create_analytics.sql`

---

## Task T036: Run Migrations Against Neon Database

### Step 1: Install psql (if not installed)

**Windows**:
```bash
# Install PostgreSQL client tools
choco install postgresql
```

**macOS**:
```bash
brew install postgresql
```

**Linux**:
```bash
sudo apt-get install postgresql-client
```

### Step 2: Run Migrations

```bash
cd F:/project/practice/hackthon/AI-Text-Book/api

# Run migration 1
psql "$NEON_DATABASE_URL" -f src/db/migrations/001_create_chunk_metadata.sql

# Run migration 2
psql "$NEON_DATABASE_URL" -f src/db/migrations/002_create_query_logs.sql

# Run migration 3
psql "$NEON_DATABASE_URL" -f src/db/migrations/003_create_analytics.sql
```

### Step 3: Verify Schema

```bash
psql "$NEON_DATABASE_URL" -c "\dt"
# Expected output:
# List of relations
#  Schema |     Name       | Type  |  Owner
# --------+----------------+-------+---------
#  public | chunk_metadata | table | user
#  public | query_logs     | table | user
#  public | analytics      | table | user
```

**✅ Verification**: All 3 tables exist in database

---

## Cost Summary

| Service | Free Tier | Paid Tier (if needed) |
|---------|-----------|----------------------|
| **Qdrant Cloud** | 1GB storage (600-800 chunks) | $25/month (4GB) |
| **Neon Postgres** | 10GB storage, unlimited queries | $19/month (Pro) |
| **Upstash Redis** | 10k commands/day | $0.20 per 100k commands |
| **Sentry** | 5k events/month | $26/month (Team) |
| **OpenAI API** | Pay-per-use (set limit: $10/month) | Variable usage-based |
| **Vercel** | 100GB bandwidth, 100 functions/hr | $20/month (Pro) |
| **Total** | ~$10/month (OpenAI usage) | ~$100/month (all paid tiers) |

**Expected Cost for MVP**: $10-15/month (OpenAI usage only, all other services on free tier)

---

## Troubleshooting

### Qdrant Connection Fails
- Verify cluster is active in dashboard
- Check API key is correct (regenerate if needed)
- Ensure cluster URL includes port `:6333`

### Neon Database Connection Timeout
- Verify connection string includes `?sslmode=require`
- Check database is active (auto-pauses after 5 min inactivity)
- Test with `psql` before using in application

### Upstash Rate Limit Errors
- Free tier: 10k commands/day
- Upgrade to paid tier if exceeded
- Implement request deduplication

### Sentry Events Not Appearing
- Verify DSN is correct
- Check project is not in "Paused" state
- Ensure Sentry SDK is initialized before errors occur

### OpenAI API Errors
- Verify API key starts with `sk-`
- Check billing is active (add payment method)
- Monitor usage in OpenAI dashboard
- Respect rate limits (3000 tokens/min on free tier)

### Vercel Deployment Fails
- Check all environment variables are set
- Verify Python version is 3.11+ in `vercel.json`
- Review build logs in Vercel dashboard
- Ensure `requirements.txt` includes all dependencies

---

## Security Checklist

- [ ] All API keys stored as environment variables (not in code)
- [ ] `.env` file added to `.gitignore`
- [ ] `.env.example` created with placeholder values
- [ ] Vercel environment variables set to "Production" only
- [ ] Qdrant API key regenerated after initial testing
- [ ] Neon database credentials not shared publicly
- [ ] OpenAI API key has usage limits set ($10/month)
- [ ] Sentry project visibility set to "Private"
- [ ] Upstash Redis token not exposed in client-side code

---

## Next Steps

After completing Phase 2, proceed to:
- **Phase 3**: Document Processing Pipeline (ingest textbook content)
- **Phase 4**: Backend API - Core Services (implement RAG pipeline)

---

**Document Status**: ✅ **READY FOR EXECUTION**
**Last Updated**: 2026-02-05
