# 🚨 SECURITY ACTION PLAN - API KEY ROTATION

**Status:** ⚠️ CRITICAL - All keys exposed in git history
**Priority:** IMMEDIATE ACTION REQUIRED
**Date Created:** 2026-02-11

---

## ⚠️ EXPOSED CREDENTIALS

The following credentials were hardcoded and committed to git history:

### 1. Supabase
- **URL:** `https://zqyijbfkdomulinqnewb.supabase.co`
- **Anon Key:** `eyJhbGci...` (EXPOSED)
- **Location:** `.env.local` + `src/lib/supabase.ts` (hardcoded until commit 51a51f0)

### 2. Qdrant Vector Database
- **Cluster URL:** `https://ac174421-0bd8-4458-b642-6aff37d2ccc6.europe-west3-0.gcp.cloud.qdrant.io:6333`
- **API Key:** `eyJhbGci...` (EXPOSED)
- **Location:** `.env.local`

### 3. Neon Database
- **Connection String:** `postgresql://neondb_owner:REDACTED@ep-floral-queen-aihv59bd-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require`
- **Username:** `neondb_owner`
- **Password:** `REDACTED_NEON_PASSWORD` (EXPOSED)
- **Location:** `.env.local`

### 4. OpenAI
- **API Key:** `REDACTED_OPENAI_KEY` (EXPOSED)
- **Location:** `.env.local`

### 5. Cohere
- **API Key:** `REDACTED_COHERE_KEY` (EXPOSED)
- **Location:** `.env.local`

---

## 📋 ROTATION CHECKLIST

### [ ] Step 1: Supabase (CRITICAL)

1. **Go to Supabase Dashboard:**
   - URL: https://app.supabase.com/project/zqyijbfkdomulinqnewb/settings/api

2. **Reset the Anon/Public Key:**
   - Click "Reset" next to "anon public" key
   - **⚠️ WARNING:** This will invalidate all existing client sessions
   - Copy the new key

3. **Update Your .env.local:**
   ```bash
   NEXT_PUBLIC_SUPABASE_ANON_KEY=<NEW_KEY_HERE>
   ```

4. **Test the connection:**
   ```bash
   npm run dev
   # Try to sign in/sign up to verify it works
   ```

---

### [ ] Step 2: Qdrant Cloud

1. **Go to Qdrant Dashboard:**
   - URL: https://cloud.qdrant.io/

2. **Navigate to your cluster:**
   - Find cluster: `ac174421-0bd8-4458-b642-6aff37d2ccc6`
   - Go to "API Keys" section

3. **Delete the old key and create new:**
   - Delete: `eyJhbGci...`
   - Click "Create New API Key"
   - Copy the new key immediately (shown only once!)

4. **Update Your .env.local:**
   ```bash
   QDRANT_API_KEY=<NEW_KEY_HERE>
   ```

5. **Test the connection:**
   ```bash
   # From api/ directory
   python scripts/verify_infrastructure.py
   ```

---

### [ ] Step 3: Neon Database

1. **Go to Neon Console:**
   - URL: https://console.neon.tech/

2. **Navigate to your project:**
   - Find project: `ep-floral-queen-aihv59bd`
   - Go to Settings → Database → Reset Password

3. **Generate new password:**
   - Click "Reset Password"
   - Copy the new password

4. **Update Your .env.local:**
   ```bash
   NEON_DATABASE_URL=postgresql://neondb_owner:REDACTED@ep-floral-queen-aihv59bd-pooler.c-4.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

5. **Test the connection:**
   ```bash
   # From api/ directory
   python scripts/verify_infrastructure.py
   ```

---

### [ ] Step 4: OpenAI

1. **Go to OpenAI Platform:**
   - URL: https://platform.openai.com/api-keys

2. **Revoke the exposed key:**
   - Find key starting with: `sk-proj-htvhnuTZ...`
   - Click "Revoke" or delete icon
   - Confirm deletion

3. **Create new secret key:**
   - Click "Create new secret key"
   - Give it a name: "AI-Textbook-Production"
   - Copy the key immediately (shown only once!)

4. **Update Your .env.local:**
   ```bash
   OPENAI_API_KEY=sk-<NEW_KEY_HERE>
   ```

5. **Test the API:**
   ```bash
   # Quick test
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer $OPENAI_API_KEY"
   ```

---

### [ ] Step 5: Cohere

1. **Go to Cohere Dashboard:**
   - URL: https://dashboard.cohere.com/api-keys

2. **Delete the old key:**
   - Find key: `aHGPAF6Z5j1GGRwbhI...`
   - Click Delete

3. **Generate new production key:**
   - Click "Create API Key"
   - Select "Production" tier
   - Copy the new key

4. **Update Your .env.local:**
   ```bash
   COHERE_API_KEY=<NEW_KEY_HERE>
   ```

5. **Test the API:**
   ```bash
   # Quick test
   curl https://api.cohere.ai/v1/check-api-key \
     -H "Authorization: Bearer $COHERE_API_KEY"
   ```

---

## 🔒 POST-ROTATION STEPS

### [ ] 1. Verify .env.local is NOT tracked

```bash
git status
# Should show: nothing to commit, working tree clean
# If .env.local appears, run: git rm --cached .env.local
```

### [ ] 2. Delete the old .env.local file

```bash
# Backup first (just in case)
cp .env.local .env.local.backup

# Then update with new keys from template
cp .env.local.template .env.local
# Fill in all NEW keys
```

### [ ] 3. Run full system test

```bash
# Frontend
npm run dev

# Backend (in api/ directory)
python scripts/verify_infrastructure.py
python scripts/test_imports.py

# Try all features:
# - Sign in/Sign up
# - Quiz functionality
# - Search
# - API endpoints
```

### [ ] 4. Update any deployment secrets

If you've deployed to:
- **Vercel:** Update environment variables in project settings
- **GitHub Actions:** Update repository secrets
- **Docker:** Update docker-compose.yml or .env files
- **Any other platforms:** Update their environment variables

---

## 📊 ROTATION STATUS

| Service | Status | Rotated Date | Notes |
|---------|--------|--------------|-------|
| Supabase | ⚠️ PENDING | - | CRITICAL: Hardcoded in source |
| Qdrant | ⚠️ PENDING | - | Vector DB access |
| Neon DB | ⚠️ PENDING | - | Contains password |
| OpenAI | ⚠️ PENDING | - | API costs money |
| Cohere | ⚠️ PENDING | - | API costs money |

**Update this table as you complete each rotation!**

---

## 💰 POTENTIAL COST IMPLICATIONS

### If keys were compromised and used maliciously:

- **OpenAI:** Could rack up $100s-$1000s in API charges
- **Cohere:** Similar risk of unauthorized API usage
- **Supabase:** Database could be accessed/modified
- **Qdrant:** Vector data could be deleted/corrupted
- **Neon DB:** Full database access (read/write/delete)

### Action if you see suspicious activity:

1. **Check billing dashboards immediately**
2. **Contact support for each service**
3. **Enable rate limiting / spending caps**
4. **Review access logs**

---

## 📞 SUPPORT CONTACTS

- **Supabase:** https://supabase.com/dashboard/support/new
- **Qdrant:** support@qdrant.tech
- **Neon:** https://neon.tech/docs/introduction/support
- **OpenAI:** https://help.openai.com/
- **Cohere:** support@cohere.com

---

## ✅ COMPLETION

Once all keys are rotated:

```bash
# Mark this file as completed
echo "✅ All keys rotated on $(date)" >> SECURITY_ACTION_PLAN.md

# Commit the template
git add .env.local.template
git commit -m "docs: Add environment variable template (no secrets)"
```

---

**Remember:** Never commit real API keys to git again!
Use `.env.local` for secrets (already in .gitignore)
Use `.env.local.template` for documentation (safe to commit)
