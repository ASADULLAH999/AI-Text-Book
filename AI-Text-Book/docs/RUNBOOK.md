# Operational Runbook

> **T124** — Common operational procedures for the AI Textbook RAG Chatbot.

## On-Call Quick Reference

| Issue | First Action | Escalation |
|-------|-------------|-----------|
| API 5xx errors | Check Sentry → restart Vercel function | Page on-call engineer |
| Rate limit complaints | Check Upstash Redis usage | Increase limits in `.env` |
| Slow responses (>5s) | Check Qdrant Cloud status | Failover to BM25 |
| Chatbot gives wrong answers | Check Qdrant collection | Re-index affected chapters |
| High costs | Check OpenAI usage dashboard | Reduce top_k, increase cache TTL |

---

## Runbook 1 — API Returns 500 Errors

**Symptoms**: Users see "Something went wrong" in the chat. Sentry alerts firing.

**Steps**:
1. Check Sentry for the error:
   ```
   https://sentry.io/organizations/<org>/issues/?query=level%3Aerror
   ```
2. Check Vercel function logs:
   ```bash
   vercel logs --since 1h
   ```
3. Test the health endpoint:
   ```bash
   curl https://ai-textbook-chatbot-api.vercel.app/api/v1/health
   ```
4. If Qdrant is down:
   - Check https://status.qdrant.io
   - The circuit breaker will open after 5 failures; wait for it to recover
   - Force-open circuit: set `QDRANT_CIRCUIT_BREAKER_DISABLED=true` in env
5. If OpenAI is down:
   - Check https://status.openai.com
   - The retry decorator will retry 3× with exponential backoff
6. If Neon Postgres is down:
   - Check https://neon.tech/status
   - Most chat features still work without Postgres (citation metadata is in Qdrant)

---

## Runbook 2 — High Latency (P95 > 5s)

**Symptoms**: Sentry latency alert. Users complain about slow responses.

**Steps**:
1. Identify which stage is slow using pipeline traces in Sentry:
   - Look for `event: rag_pipeline_trace` logs
   - Check `spans_ms.embed`, `spans_ms.retrieve`, `spans_ms.generate`
2. If `embed` is slow (> 500ms):
   - Check OpenAI embeddings endpoint status
   - Batch size might be too large; reduce `BATCH_EMBED_SIZE` env var
3. If `retrieve` is slow (> 1000ms):
   - Check Qdrant Cloud cluster status
   - Verify HNSW index parameters in Qdrant dashboard
   - Ensure `top_k` is ≤ 20 (`RAG_TOP_K` env var)
4. If `generate` is slow (> 3000ms):
   - Check OpenAI GPT-4o status
   - Reduce `RAG_MAX_TOKENS` from 8000 to 4000
5. Check cache hit rate (should be > 30% for repeated queries):
   ```bash
   # Look for 'cached: true' in logs
   vercel logs | grep '"cached": true' | wc -l
   ```

---

## Runbook 3 — Rate Limit Complaints

**Symptoms**: Users get 429 errors. Rate limit exceeded alerts.

**Steps**:
1. Check current usage in Upstash Redis dashboard
2. Identify offending IP/user:
   ```bash
   vercel logs | grep 'rate_limit_exceeded' | grep -o 'ip:[0-9.]*' | sort | uniq -c | sort -rn | head
   ```
3. If legitimate users are being blocked:
   - Increase `CHATBOT_RATE_LIMIT_AUTHENTICATED` env var (default: 100/hr)
   - Increase `CHATBOT_RATE_LIMIT_ANONYMOUS` env var (default: 10/hr)
4. If it's a bot attack:
   - Enable CAPTCHA: set `CLOUDFLARE_TURNSTILE_SECRET_KEY` and site key
   - Reduce `CAPTCHA_BURST_THRESHOLD` (default: 30 req/60s)
   - Consider blocking IPs in Cloudflare dashboard

---

## Runbook 4 — Incorrect or Hallucinated Answers

**Symptoms**: Users report wrong answers. Citation accuracy below 95%.

**Steps**:
1. Identify the failing query from logs:
   ```bash
   vercel logs | grep '"refused": false' | grep '"grounding_score": 0\.'
   ```
2. Test the query manually:
   ```bash
   curl -X POST https://ai-textbook-chatbot-api.vercel.app/api/v1/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "<failing query>", "mode": "book_only"}'
   ```
3. Check if the relevant content is in Qdrant:
   ```python
   # api/scripts/validate_chunks.py --query "failing query"
   cd api && python scripts/validate_chunks.py --search "failing query"
   ```
4. If content is missing: re-run ingestion for the affected chapter:
   ```bash
   cd api
   python scripts/chunk_textbook.py --chapter <chapter-slug>
   python scripts/generate_embeddings.py --chapter <chapter-slug>
   python scripts/upload_to_qdrant.py --chapter <chapter-slug>
   ```
5. If content exists but retrieval fails: adjust `RAG_SIMILARITY_THRESHOLD` (default: 0.7)

---

## Runbook 5 — Secret / API Key Rotation

See `docs/API_KEY_ROTATION.md` for step-by-step rotation procedures.

**Emergency (suspected breach)**:
1. Immediately revoke the compromised key from the provider dashboard
2. Set the new key in Vercel: `vercel env add <KEY_NAME> production`
3. Force redeploy: `vercel --prod --force`
4. File a GitHub issue with label `security`

---

## Runbook 6 — Database Migration

**Steps**:
1. Back up current schema:
   ```bash
   cd api && python scripts/run_migrations.py --dry-run
   ```
2. Run migration in staging first
3. Apply to production:
   ```bash
   cd api && NEON_DATABASE_URL=$PROD_DB python scripts/run_migrations.py
   ```
4. Verify application health after migration

---

## Common Vercel CLI Commands

```bash
# View recent logs
vercel logs --since 1h

# List deployments
vercel ls

# Roll back to previous deployment
vercel rollback

# Check environment variables
vercel env ls production

# Force redeploy
vercel --prod --force
```

---

*Last reviewed: 2026-02-28*
