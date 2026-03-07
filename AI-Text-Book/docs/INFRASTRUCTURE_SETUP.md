# Infrastructure Setup Guide

This guide walks you through provisioning the required cloud infrastructure for the RAG-Powered Textbook Chatbot.

## Overview

The application requires three managed services:

1. **Qdrant Cloud** - Vector database for embeddings
2. **Neon Serverless Postgres** - Relational database for conversations and metadata
3. **OpenAI API** - LLM and embedding generation

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed
- Git installed
- GitHub account
- Credit card (for service free tiers - won't be charged unless you exceed limits)

---

## 1. Qdrant Cloud Setup (T004)

### Create Qdrant Account

1. Visit [Qdrant Cloud Console](https://cloud.qdrant.io/)
2. Sign up with GitHub or email
3. Verify your email address

### Create a Cluster

1. Click **"Create Cluster"**
2. Choose configuration:
   - **Name**: `ai-textbook-production`
   - **Cloud Provider**: AWS, GCP, or Azure
   - **Region**: Choose closest to your users
   - **Cluster Size**: Free tier (1GB RAM, 1 vCPU)
3. Click **"Create"**
4. Wait 2-3 minutes for provisioning

### Get API Credentials

1. Navigate to cluster dashboard
2. Copy **Cluster URL** (format: `https://xxxxx.qdrant.io:6333`)
3. Click **"API Keys"** → **"Create API Key"**
4. Copy the API key (starts with `qdrant_`)
5. Store securely - it won't be shown again

### Configure Environment

```bash
# Add to .env file
QDRANT_URL=https://your-cluster.qdrant.io:6333
QDRANT_API_KEY=your-qdrant-api-key-here
```

### Provision Collection

```bash
# Install dependencies
pip install -r api/requirements.txt

# Create the collection
python api/scripts/provision_qdrant.py --create

# Verify collection
python api/scripts/provision_qdrant.py --info
```

**Expected output:**
```
✅ Collection 'textbook_chunks' created successfully!
   Vector size: 3072
   Distance metric: Cosine
   HNSW parameters: M=16, ef_construct=100
```

### Troubleshooting Qdrant

**Connection timeout:**
- Check firewall rules allow port 6333
- Verify QDRANT_URL includes protocol (https://)
- Ensure API key is correct

**Collection already exists:**
```bash
# Check existing collection
python api/scripts/provision_qdrant.py --info

# Delete and recreate if needed
python api/scripts/provision_qdrant.py --delete
python api/scripts/provision_qdrant.py --create
```

---

## 2. Neon Serverless Postgres Setup (T005)

### Create Neon Account

1. Visit [Neon Console](https://console.neon.tech/signup)
2. Sign up with GitHub or email
3. Verify your email

### Create a Project

1. Click **"Create Project"**
2. Configure:
   - **Name**: `ai-textbook-rag`
   - **Postgres Version**: 15 or higher
   - **Region**: Same as Qdrant for low latency
   - **Compute**: Shared (free tier)
3. Click **"Create Project"**

### Get Connection String

1. Navigate to project dashboard
2. Click **"Connection Details"**
3. Select **"Pooled connection"** (for serverless)
4. Copy the connection string:
   ```
   postgresql://user:pass@ep-xxxxx.region.aws.neon.tech/dbname?sslmode=require
   ```

### Configure Environment

```bash
# Add to .env file
DATABASE_URL=postgresql://user:pass@ep-xxxxx.region.aws.neon.tech/dbname?sslmode=require

# OR configure individually
POSTGRES_HOST=ep-xxxxx.region.aws.neon.tech
POSTGRES_PORT=5432
POSTGRES_DB=ai_textbook
POSTGRES_USER=your-username
POSTGRES_PASSWORD=your-password
POSTGRES_SSL_MODE=require
```

### Initialize Database

```bash
# Test connection
python api/scripts/provision_neon.py --check

# Run migrations to create tables
python api/scripts/provision_neon.py --init

# Verify database status
python api/scripts/provision_neon.py --status
```

**Expected output:**
```
✅ Connection successful!
   Database: ai_textbook
   Server: ep-xxxxx.region.aws.neon.tech:5432

✅ All required tables exist: conversations, messages, citations, feedback
```

### Enable Neon Features

**Auto-suspend** (recommended for cost savings):
1. Go to project settings
2. Enable "Auto-suspend compute after inactivity"
3. Set to 5 minutes

**Connection Pooling** (required for serverless):
1. Already enabled by default
2. Use pooled connection string (includes `?sslmode=require`)

### Troubleshooting Neon

**SSL connection failed:**
- Ensure `?sslmode=require` is in connection string
- Use pooled connection, not direct

**Schema initialization fails:**
- Check that migrations file exists: `api/src/db/migrations/001_initial_schema.sql`
- Run migrations manually: `python api/scripts/run_migrations.py`

**Too many connections:**
- Use pooled connection string
- Check POSTGRES_POOL_MAX in .env (default: 10)

---

## 3. OpenAI API Setup

### Get API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign in or create account
3. Navigate to **API Keys** section
4. Click **"Create new secret key"**
5. Name it: `ai-textbook-rag`
6. Copy the key (starts with `sk-`)

### Configure Environment

```bash
# Add to .env file
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_ORG_ID=org-your-organization-id-here
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
OPENAI_CHAT_MODEL=gpt-4
OPENAI_FALLBACK_MODEL=gpt-3.5-turbo
```

### Set Usage Limits (Recommended)

1. Go to **Settings** → **Billing**
2. Set monthly budget limit ($50 recommended for development)
3. Enable email alerts at 75% and 90%

### Test API Access

```bash
# Run a test embedding
python -c "
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
response = client.embeddings.create(
    model='text-embedding-3-large',
    input='Hello, world!'
)
print(f'✅ OpenAI API working! Vector size: {len(response.data[0].embedding)}')
"
```

**Expected output:**
```
✅ OpenAI API working! Vector size: 3072
```

---

## 4. GitHub Repository Setup (T008)

### Initialize Repository

If not already done:

```bash
# Initialize git
git init

# Add remote
git remote add origin https://github.com/yourusername/AI-Text-Book.git

# Create main branch
git checkout -b main
git add .
git commit -m "Initial commit"
git push -u origin main
```

### Set Up Branch Protection Rules

#### Via GitHub Web UI:

1. Go to repository **Settings** → **Branches**
2. Click **"Add branch protection rule"**
3. Configure for `main` branch:

**Branch name pattern:** `main`

**Protection rules:**
- ☑ Require a pull request before merging
  - ☑ Require approvals (1 required)
  - ☑ Dismiss stale pull request approvals when new commits are pushed
- ☑ Require status checks to pass before merging
  - ☑ Require branches to be up to date before merging
  - Status checks: `build`, `test`, `lint`
- ☑ Require conversation resolution before merging
- ☑ Require signed commits (optional but recommended)
- ☑ Include administrators (recommended for consistency)
- ☑ Restrict who can push to matching branches
  - Add: Maintainers and specific users/teams
- ☑ Allow force pushes: **Disabled**
- ☑ Allow deletions: **Disabled**

4. Click **"Create"** or **"Save changes"**

#### Via GitHub CLI:

```bash
# Install GitHub CLI if not already installed
# macOS: brew install gh
# Windows: winget install GitHub.cli
# Linux: See https://cli.github.com/

# Authenticate
gh auth login

# Create branch protection rule
gh api repos/:owner/:repo/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["build","test","lint"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null \
  --field required_linear_history=false \
  --field allow_force_pushes=false \
  --field allow_deletions=false \
  --field required_conversation_resolution=true

echo "✅ Branch protection rules configured for main branch"
```

### Create Development Branch

```bash
# Create and switch to development branch
git checkout -b develop
git push -u origin develop

# Set develop as default branch for PRs (optional)
gh repo edit --default-branch develop
```

### Configure GitHub Actions (Optional)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r api/requirements.txt
      - run: pytest api/tests/

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run lint
```

### Verify Branch Protection

```bash
# Check branch protection status
gh api repos/:owner/:repo/branches/main/protection | jq '.'

# Try to push directly to main (should fail)
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "Test direct push"
git push  # Should be rejected

# Clean up test
git reset --hard HEAD~1
```

**Expected output:**
```
❌ remote: error: GH006: Protected branch update failed
❌ remote: error: Cannot push to protected branch 'main'
```

---

## 5. Verify Complete Setup

Run the full verification script:

```bash
# Create verification script
cat > verify_setup.sh << 'EOF'
#!/bin/bash

echo "🔍 Verifying infrastructure setup..."

# Check Qdrant
echo "\n1️⃣ Checking Qdrant Cloud..."
python api/scripts/provision_qdrant.py --check && echo "✅ Qdrant OK" || echo "❌ Qdrant FAILED"

# Check Neon
echo "\n2️⃣ Checking Neon Postgres..."
python api/scripts/provision_neon.py --check && echo "✅ Neon OK" || echo "❌ Neon FAILED"

# Check OpenAI
echo "\n3️⃣ Checking OpenAI API..."
python -c "from openai import OpenAI; import os; OpenAI(api_key=os.getenv('OPENAI_API_KEY')).models.list()" && echo "✅ OpenAI OK" || echo "❌ OpenAI FAILED"

# Check GitHub
echo "\n4️⃣ Checking GitHub branch protection..."
gh api repos/:owner/:repo/branches/main/protection >/dev/null 2>&1 && echo "✅ GitHub OK" || echo "⚠️  GitHub branch protection not set"

echo "\n✅ Setup verification complete!"
EOF

chmod +x verify_setup.sh
./verify_setup.sh
```

---

## Cost Estimates (Free Tier Limits)

### Qdrant Cloud (Free Tier)
- **Storage**: 1GB vector storage
- **Compute**: Shared, auto-scaling
- **Limit**: ~50,000 chunks (1KB each)
- **Monthly Cost**: $0

### Neon Serverless Postgres (Free Tier)
- **Storage**: 3GB database size
- **Compute**: 100 compute hours/month
- **Connections**: Unlimited (pooled)
- **Monthly Cost**: $0

### OpenAI API (Pay-as-you-go)
- **Embeddings**: $0.13 per 1M tokens (text-embedding-3-large)
- **Chat**: $5.00 per 1M input tokens (GPT-4)
- **Estimated for 10,000 queries/day**:
  - Embeddings: ~$2/month
  - Chat: ~$50/month
- **Total**: ~$50-60/month

### Total Infrastructure Cost
- **Development**: ~$5-10/month
- **Production (10K queries/day)**: ~$50-60/month

---

## Security Checklist

- [ ] All API keys stored in `.env` file
- [ ] `.env` file added to `.gitignore`
- [ ] No secrets committed to repository
- [ ] Branch protection enabled on `main`
- [ ] SSL/TLS enabled for all database connections
- [ ] API rate limiting configured
- [ ] Monthly budget alerts set up
- [ ] Access logs enabled for all services
- [ ] Regular backup strategy defined

---

## Troubleshooting

### Common Issues

**"Module not found" errors:**
```bash
pip install -r api/requirements.txt
npm install
```

**Connection timeout:**
- Check firewall rules
- Verify API URLs and ports
- Test with curl/telnet

**Authentication failed:**
- Regenerate API keys
- Check key format (no extra spaces)
- Verify environment variables loaded

**Database migration errors:**
- Check SQL syntax in migration files
- Ensure database user has CREATE TABLE permissions
- Run migrations manually one by one

### Getting Help

- **Qdrant**: https://qdrant.tech/documentation/
- **Neon**: https://neon.tech/docs/introduction
- **OpenAI**: https://platform.openai.com/docs
- **GitHub Issues**: Create an issue in this repository

---

## Next Steps

After completing infrastructure setup:

1. ✅ Run `verify_setup.sh` to confirm all services
2. ✅ Process sample textbook content (Task T024)
3. ✅ Run ingestion pipeline validation (Task T025)
4. ✅ Start implementing User Story 1 (Phase 3)

**Congratulations! Your infrastructure is ready! 🎉**
