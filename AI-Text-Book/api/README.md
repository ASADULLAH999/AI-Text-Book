# RAG Chatbot API

Backend API for the RAG-Powered Textbook Chatbot (Feature 002-rag-chatbot)

---

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy template
cp ../.env.example ../.env.local

# Edit and fill in your credentials
# Required: QDRANT_URL, QDRANT_API_KEY, NEON_DATABASE_URL, OPENAI_API_KEY
```

### 3. Verify Infrastructure

```bash
python scripts/verify_infrastructure.py
```

### 4. Run Migrations

```bash
python scripts/run_migrations.py
```

### 5. Ingest Textbook Content

```bash
python scripts/ingest_pipeline.py --textbook-dir .. --data-dir data
```

### 6. Start Development Server

```bash
cd src
python main.py
```

API will be available at: http://localhost:8000

---

## Project Structure

```
api/
├── src/
│   ├── models/           # Pydantic data models
│   │   ├── chunk.py
│   │   ├── chat_request.py
│   │   ├── chat_response.py
│   │   ├── citation.py
│   │   └── errors.py
│   ├── services/         # Core business logic
│   │   └── embedding_service.py
│   ├── routes/           # API endpoints (to be implemented)
│   ├── middleware/       # Request/response middleware
│   │   ├── logger.py
│   │   ├── rate_limiter.py
│   │   └── auth_middleware.py
│   ├── db/               # Database clients
│   │   ├── migrations/   # SQL migration files
│   │   ├── qdrant_client.py
│   │   └── postgres_client.py
│   └── main.py           # FastAPI application
├── scripts/              # Utility scripts
│   ├── extract_markdown.py
│   ├── parse_metadata.py
│   ├── chunk_textbook.py
│   ├── generate_embeddings.py
│   ├── upload_to_qdrant.py
│   ├── sync_postgres.py
│   ├── validate_chunks.py
│   ├── ingest_pipeline.py          # Complete pipeline
│   ├── run_migrations.py
│   └── verify_infrastructure.py
├── tests/                # Test suite (to be implemented)
├── requirements.txt      # Python dependencies
├── vercel.json           # Vercel deployment config
└── README.md             # This file
```

---

## Available Scripts

### Infrastructure

- **`verify_infrastructure.py`** - Test all services (Qdrant, Postgres, OpenAI)
- **`run_migrations.py`** - Execute database migrations

### Document Processing

- **`extract_markdown.py`** - Extract markdown files
- **`parse_metadata.py`** - Parse frontmatter and headings
- **`chunk_textbook.py`** - Semantic chunking
- **`generate_embeddings.py`** - Generate OpenAI embeddings
- **`upload_to_qdrant.py`** - Upload to vector database
- **`sync_postgres.py`** - Sync metadata to Postgres
- **`validate_chunks.py`** - Validate chunk quality

### Pipeline Orchestrator

- **`ingest_pipeline.py`** - Run complete pipeline

```bash
# Full pipeline
python scripts/ingest_pipeline.py --textbook-dir .. --data-dir data

# Skip certain steps (for resuming)
python scripts/ingest_pipeline.py --skip-embedding --skip-upload
```

---

## API Endpoints

**Coming in Phase 4-5:**

- `POST /api/v1/chat` - Main chatbot endpoint
- `GET /api/v1/health` - Health check
- `GET /api/v1/chunks` - Admin chunk inspection

**Current:**
- `GET /` - API info
- `GET /api/v1/health` - Basic health check

---

## Development

### Run Tests

```bash
pytest
```

### Run with Hot Reload

```bash
cd src
python main.py  # Uses uvicorn with reload=True
```

### Lint and Format

```bash
# Format
black src/

# Lint
ruff check src/

# Type check
mypy src/
```

---

## Environment Variables

### Required

```bash
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_api_key
QDRANT_COLLECTION_NAME=textbook_chunks
NEON_DATABASE_URL=postgresql://...
OPENAI_API_KEY=sk-...
```

### Optional

```bash
COHERE_API_KEY=...              # Optional reranking
UPSTASH_REDIS_URL=...           # Optional rate limiting
UPSTASH_REDIS_TOKEN=...
SENTRY_DSN=...                  # Optional error tracking
RAG_CHUNK_SIZE=1024             # Chunk size
RAG_CHUNK_OVERLAP=0.1           # Overlap percentage
RAG_TOP_K=10                    # Vector search results
RAG_SIMILARITY_THRESHOLD=0.7    # Minimum similarity
```

---

## Deployment

### Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel --prod
```

Configuration in `vercel.json`

---

## Troubleshooting

### Connection Issues

```bash
# Test individual services
python scripts/verify_infrastructure.py
```

### Migration Issues

```bash
# Re-run migrations
python scripts/run_migrations.py

# Verify tables
python scripts/run_migrations.py --verify-only
```

### Embedding Issues

```bash
# Resume from cache
python scripts/generate_embeddings.py \
  --chunks data/chunks.json \
  --cache data/embeddings_cache.json
```

---

## Documentation

- **Setup Guide:** `../specs/002-rag-chatbot/PHASE2_SETUP_GUIDE.md`
- **Implementation Status:** `../specs/002-rag-chatbot/IMPLEMENTATION_STATUS.md`
- **Architecture:** `../specs/002-rag-chatbot/architecture.md`
- **API Contracts:** `../specs/002-rag-chatbot/api-contracts.md`

---

## Next Steps

1. ✅ Complete Phase 2 setup (this directory)
2. ⏳ Run document ingestion pipeline
3. ⏳ Implement Phase 4 core services (retrieval, generation, citation)
4. ⏳ Implement Phase 5 API routes
5. ⏳ Implement Phase 6 frontend integration

---

**Status:** Infrastructure complete, ready for document processing and core service implementation
