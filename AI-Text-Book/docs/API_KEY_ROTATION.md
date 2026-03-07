# API Key Rotation Guide

> **T109** — Procedures for rotating all API keys without service downtime.

## Overview

This guide covers rotating the following secrets:

| Secret | Service | Rotation Frequency |
|--------|---------|-------------------|
| `OPENAI_API_KEY` | OpenAI | Every 90 days |
| `COHERE_API_KEY` | Cohere | Every 90 days |
| `QDRANT_API_KEY` | Qdrant Cloud | Every 90 days |
| `NEON_DATABASE_URL` | Neon Postgres | Every 180 days or on breach |
| `UPSTASH_REDIS_TOKEN` | Upstash Redis | Every 90 days |
| `SENTRY_DSN` | Sentry | On breach only |
| `CLOUDFLARE_TURNSTILE_SECRET_KEY` | Cloudflare | Every 180 days |

---

## Pre-rotation Checklist

- [ ] Inform the team (rotation causes a 5–10 minute deployment window).
- [ ] Confirm the new key is generated and tested in staging.
- [ ] Ensure Vercel environment variable update access.

---

## Rotation Procedures

### OpenAI API Key

```bash
# 1. Create a new key at: https://platform.openai.com/api-keys
# 2. Test the new key locally:
export OPENAI_API_KEY=<new-key>
cd api && python -c "
import os, openai
client = openai.OpenAI()
r = client.models.list()
print('OK — models available:', len(list(r)))
"

# 3. Update Vercel secret:
vercel env rm OPENAI_API_KEY production
vercel env add OPENAI_API_KEY production  # paste new key

# 4. Redeploy API:
cd api && vercel --prod

# 5. Revoke the old key from the OpenAI dashboard.
```

### Cohere API Key

```bash
# 1. Create a new key at: https://dashboard.cohere.com/api-keys
# 2. Test:
export COHERE_API_KEY=<new-key>
python -c "import cohere; c = cohere.Client(); print(c.check_api_key())"

# 3. Update Vercel:
vercel env rm COHERE_API_KEY production
vercel env add COHERE_API_KEY production

# 4. Redeploy + revoke old key.
```

### Qdrant Cloud API Key

```bash
# 1. Generate a new API key in Qdrant Cloud dashboard.
# 2. Test (DO NOT delete the old key yet):
export QDRANT_API_KEY=<new-key>
python api/scripts/provision_qdrant.py --dry-run

# 3. Update Vercel:
vercel env rm QDRANT_API_KEY production
vercel env add QDRANT_API_KEY production

# 4. Redeploy and verify health check:
curl https://ai-textbook-chatbot-api.vercel.app/api/v1/health

# 5. Delete old key from Qdrant Cloud.
```

### Neon Database URL

```bash
# Neon rotates credentials via branch reset or new role creation.
# 1. Create a new role in Neon console.
# 2. Grant SELECT, INSERT, UPDATE, DELETE on all tables:
#    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO new_role;
# 3. Update connection string:
vercel env rm NEON_DATABASE_URL production
vercel env add NEON_DATABASE_URL production
# 4. Redeploy and run health check.
# 5. Drop old role.
```

### Upstash Redis Token

```bash
# 1. Regenerate token in Upstash console (Settings → Reset Token).
# 2. Update Vercel:
vercel env rm UPSTASH_REDIS_TOKEN production
vercel env add UPSTASH_REDIS_TOKEN production
# 3. Redeploy. Rate limiting resumes on new token immediately.
```

---

## Emergency Rotation (Breach Response)

If a key is suspected to be compromised:

```bash
# 1. IMMEDIATELY revoke the old key (do NOT wait for testing).
# 2. Set the new key in Vercel (system continues running without the feature
#    until redeployed):
vercel env add <KEY_NAME> production
# 3. Trigger immediate redeployment:
vercel --prod --force
# 4. File a security incident in GitHub Issues with label `security`.
# 5. Notify stakeholders within 1 hour.
```

---

## Automated Rotation Script

```bash
# scripts/rotate_keys.sh — Interactive rotation helper
#!/usr/bin/env bash
set -euo pipefail

SERVICE=${1:-""}
if [[ -z "$SERVICE" ]]; then
  echo "Usage: $0 <openai|cohere|qdrant|neon|upstash>"
  exit 1
fi

echo "Rotating $SERVICE..."

case "$SERVICE" in
  openai)
    echo "1. Visit https://platform.openai.com/api-keys to create a new key."
    read -rsp "Paste new OPENAI_API_KEY: " NEW_KEY; echo
    vercel env rm OPENAI_API_KEY production --yes
    echo "$NEW_KEY" | vercel env add OPENAI_API_KEY production
    ;;
  cohere)
    echo "1. Visit https://dashboard.cohere.com/api-keys"
    read -rsp "Paste new COHERE_API_KEY: " NEW_KEY; echo
    vercel env rm COHERE_API_KEY production --yes
    echo "$NEW_KEY" | vercel env add COHERE_API_KEY production
    ;;
  *)
    echo "Unknown service: $SERVICE"
    exit 1
    ;;
esac

echo "Triggering redeployment..."
vercel --prod

echo "Done. Remember to revoke the old key!"
```

---

## Verification After Rotation

```bash
# Health check
curl https://ai-textbook-chatbot-api.vercel.app/api/v1/health | jq .

# Smoke test
curl -X POST https://ai-textbook-chatbot-api.vercel.app/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is ROS2?", "mode": "book_only"}'
```

Expected: `200 OK` with non-empty `answer` field.

---

*Last reviewed: 2026-02-28*
