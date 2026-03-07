# Quick Start: Infrastructure Setup (T004, T005, T008)

This guide helps you quickly set up the three core infrastructure components for the RAG chatbot.

**Estimated time:** 30-45 minutes

---

## Prerequisites

```bash
# Install required tools
# macOS
brew install python@3.11 gh

# Windows
winget install Python.Python.3.11
winget install GitHub.cli

# Linux (Ubuntu/Debian)
sudo apt install python3.11 python3-pip
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh
```

---

## Step 1: Install Python Dependencies (5 minutes)

```bash
# Navigate to project root
cd /path/to/AI-Text-Book

# Install Python dependencies
pip install -r api/requirements.txt

# Verify installation
python -c "import qdrant_client, psycopg2; print('✅ Dependencies installed')"
```

---

## Step 2: Set Up Qdrant Cloud (T004) - 15 minutes

### 2.1 Create Qdrant Account

1. Visit: https://cloud.qdrant.io/
2. Sign up with GitHub or email
3. Verify your email

### 2.2 Create a Cluster

1. Click **"Create Cluster"**
2. Settings:
   - Name: `ai-textbook-prod`
   - Region: Choose closest to you
   - Size: **Free tier** (1GB RAM)
3. Wait 2-3 minutes for provisioning

### 2.3 Get API Credentials

1. Go to cluster dashboard
2. Copy **Cluster URL**: `https://xxxxx.qdrant.io:6333`
3. Create **API Key**: Click "API Keys" → "Create API Key"
4. Save the key securely (shown only once)

### 2.4 Configure and Provision

```bash
# Create .env file from template
cp .env.template .env

# Edit .env and add Qdrant credentials
# QDRANT_URL=https://your-cluster.qdrant.io:6333
# QDRANT_API_KEY=your-api-key-here

# Source environment
export $(cat .env | xargs)

# Create the collection
python api/scripts/provision_qdrant.py --create

# Verify
python api/scripts/provision_qdrant.py --info
```

**Expected output:**
```
✅ Collection 'textbook_chunks' created successfully!
   Vector size: 3072
   Distance metric: Cosine
   HNSW parameters: M=16, ef_construct=100
```

**✅ T004 Complete!**

---

## Step 3: Set Up Neon Postgres (T005) - 10 minutes

### 3.1 Create Neon Account

1. Visit: https://console.neon.tech/signup
2. Sign up with GitHub or email
3. Verify your email

### 3.2 Create a Project

1. Click **"Create Project"**
2. Settings:
   - Name: `ai-textbook-rag`
   - Postgres: **Version 15+**
   - Region: Same as Qdrant
   - Compute: **Shared** (free tier)

### 3.3 Get Connection String

1. Go to project dashboard
2. Click **"Connection Details"**
3. Select **"Pooled connection"** (required for serverless)
4. Copy the connection string:
   ```
   postgresql://user:pass@ep-xxxxx.region.aws.neon.tech/dbname?sslmode=require
   ```

### 3.4 Configure and Initialize

```bash
# Add to .env file
# DATABASE_URL=postgresql://user:pass@ep-xxxxx.region.aws.neon.tech/dbname?sslmode=require

# Reload environment
export $(cat .env | xargs)

# Test connection
python api/scripts/provision_neon.py --check

# Initialize database schema
python api/scripts/provision_neon.py --init

# Verify
python api/scripts/provision_neon.py --status
```

**Expected output:**
```
✅ Connection successful!
   Database: ai_textbook
   Server: ep-xxxxx.region.aws.neon.tech:5432

✅ All required tables exist: conversations, messages, citations, feedback
```

**Optional:** Enable auto-suspend in Neon project settings (saves compute hours)

**✅ T005 Complete!**

---

## Step 4: Set Up GitHub Branch Protection (T008) - 10 minutes

### 4.1 Authenticate GitHub CLI

```bash
# Login to GitHub
gh auth login

# Follow prompts:
# - Select: GitHub.com
# - Select: HTTPS
# - Authenticate: Login with browser
# - Paste token or login in browser
```

### 4.2 Create CI Workflow (if needed)

```bash
# The setup script will create this automatically
# But you can verify it exists:
ls .github/workflows/ci.yml
```

### 4.3 Apply Branch Protection

```bash
# Run setup script (with dry-run first)
.github/scripts/setup_branch_protection.sh --dry-run

# Review output, then apply for real
.github/scripts/setup_branch_protection.sh

# Verify
gh api repos/:owner/:repo/branches/main/protection | jq '.required_status_checks, .required_pull_request_reviews'
```

**Expected output:**
```
✅ Branch protection rules applied successfully!

Protection rules:
{
  "required_status_checks": ["build", "test", "lint"],
  "required_approving_reviews": 1,
  "enforce_admins": true,
  "allow_force_pushes": false
}
```

### 4.4 Test Protection

```bash
# Try to push directly to main (should fail)
git checkout main
echo "test" >> test.txt
git add test.txt
git commit -m "Test direct push"
git push

# Expected: ❌ remote: error: GH006: Protected branch update failed

# Clean up
git reset --hard HEAD~1
```

**✅ T008 Complete!**

---

## Step 5: Verify All Infrastructure

Run the comprehensive verification script:

```bash
# Make sure all environment variables are loaded
export $(cat .env | xargs)

# Run verification
./scripts/verify_infrastructure.sh
```

**Expected output:**
```
╔════════════════════════════════════════════════════════════════╗
║  ✅ ALL CRITICAL INFRASTRUCTURE CHECKS PASSED!                 ║
╚════════════════════════════════════════════════════════════════╝

Your infrastructure is ready for development! 🎉
```

---

## Troubleshooting

### Qdrant Connection Issues

**Problem:** `Connection timeout`

**Solution:**
```bash
# Test connection
curl -v https://your-cluster.qdrant.io:6333/collections

# Check API key format (should start with qdrant_)
echo $QDRANT_API_KEY | cut -c1-10

# Regenerate API key if needed
```

### Neon Connection Issues

**Problem:** `SSL connection failed`

**Solution:**
```bash
# Ensure connection string has sslmode=require
echo $DATABASE_URL | grep sslmode

# Use pooled connection (not direct)
# Pooled: ep-xxxxx.pooler.region.aws.neon.tech
# Direct: ep-xxxxx.region.aws.neon.tech (don't use this)
```

### GitHub CLI Issues

**Problem:** `gh: command not found`

**Solution:**
```bash
# Install GitHub CLI
# macOS: brew install gh
# Windows: winget install GitHub.cli
# Linux: See https://cli.github.com/

# Verify installation
gh --version
```

**Problem:** `Branch protection failed - insufficient permissions`

**Solution:**
- You need **admin** access to the repository
- Check: GitHub repo → Settings → Manage access
- Ask repository owner to grant admin permissions

---

## Cost Summary

All three services have generous free tiers:

| Service | Free Tier | Estimated Cost |
|---------|-----------|----------------|
| Qdrant Cloud | 1GB storage, unlimited requests | $0/month |
| Neon Postgres | 3GB storage, 100 compute hours | $0/month |
| GitHub Actions | 2,000 minutes/month | $0/month |
| **Total** | | **$0/month** |

**Note:** You'll only pay if you exceed free tier limits, which is unlikely during development.

---

## Next Steps

✅ **Tasks T004, T005, T008 complete!**

Now you can proceed to:

1. **T024**: Process sample textbook content
   ```bash
   python api/scripts/chunk_textbook.py docs/chapter-01/
   ```

2. **T025**: Validate ingestion pipeline
   ```bash
   python api/scripts/validate_chunks.py
   ```

3. **Phase 3**: Begin User Story 1 implementation
   - Implement RAG retrieval service
   - Create chat API endpoint
   - Build frontend chat panel

---

## Quick Reference

### Useful Commands

```bash
# Qdrant
python api/scripts/provision_qdrant.py --check
python api/scripts/provision_qdrant.py --info

# Neon
python api/scripts/provision_neon.py --check
python api/scripts/provision_neon.py --status

# GitHub
gh api repos/:owner/:repo/branches/main/protection
gh workflow list

# Full verification
./scripts/verify_infrastructure.sh
```

### Environment Variables

```bash
# Quick check all variables
echo "Qdrant URL: ${QDRANT_URL:0:30}..."
echo "Qdrant Key: ${QDRANT_API_KEY:0:10}..."
echo "Database URL: ${DATABASE_URL:0:30}..."
```

### Documentation

- Qdrant: https://qdrant.tech/documentation/
- Neon: https://neon.tech/docs/introduction
- GitHub CLI: https://cli.github.com/manual/
- Full setup: [docs/INFRASTRUCTURE_SETUP.md](./INFRASTRUCTURE_SETUP.md)

---

**Questions or issues?** Check the [full infrastructure guide](./INFRASTRUCTURE_SETUP.md) or create an issue on GitHub.
