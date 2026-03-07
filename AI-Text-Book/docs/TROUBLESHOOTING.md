# Troubleshooting Guide

> **T139** — Common errors and how to fix them.

---

## Frontend Issues

### Chat panel doesn't appear

**Symptoms**: No chat button in the bottom-right corner.

**Causes and fixes**:
1. **JavaScript error during load**: Open browser console (F12) and check for errors.
2. **CSS module not loaded**: Ensure `npm run build` completes without errors.
3. **React.lazy error**: Check if the ChatPanel chunk failed to load. Look for `ChunkLoadError` in the console.
   - Fix: Clear browser cache and reload (Ctrl+Shift+R).
4. **Component threw during render**: Check Sentry for `React Error Boundary` events.

### Term tooltips not showing

1. Check that `data/glossary.json` exists and is valid JSON.
2. Ensure the `useTermDetection` hook is imported correctly in the component.
3. Check browser console for `Cannot read properties of undefined` errors.

### Chat sends but receives no response

1. Check browser Network tab — is the `/api/v1/chat` request returning an error?
2. Check `REACT_APP_API_URL` is set correctly in `.env`.
3. Test the API directly: `curl -X POST $API_URL/api/v1/chat -H "Content-Type: application/json" -d '{"message":"test","mode":"book_only"}'`

---

## Backend Issues

### `ImportError: No module named 'services'`

```bash
# Wrong: running from repo root
python -m pytest api/tests/

# Correct: run from api/ with PYTHONPATH
cd api && PYTHONPATH=src python -m pytest tests/
```

### `QdrantClientException: collection not found`

```bash
# Re-provision the collection
cd api && python scripts/provision_qdrant.py
# Then re-upload chunks
python scripts/upload_to_qdrant.py
```

### `openai.AuthenticationError`

- Check `OPENAI_API_KEY` is set in `.env` and Vercel environment variables.
- Verify the key is not expired or revoked.

### `asyncpg.exceptions.InvalidPasswordError`

- Check `NEON_DATABASE_URL` connection string.
- Ensure IP allowlist in Neon console includes your IP.

### Rate limit errors (429) in development

- Disable rate limiting: comment out `app.add_middleware(RateLimiterMiddleware)` in `main.py`.
- Or set `UPSTASH_REDIS_URL=""` to disable Redis rate limiting.

### `CircuitBreaker[qdrant] OPEN`

- Qdrant Cloud is unavailable. Check https://status.qdrant.io.
- Wait 60 seconds for the circuit breaker to probe (HALF_OPEN).
- Or restart the API function to reset the circuit breaker state.

---

## Build Issues

### `TypeError: Cannot read properties of undefined (reading 'themes')`

Check `docusaurus.config.ts` — ensure `prism-react-renderer` is installed:
```bash
npm install prism-react-renderer
```

### TypeScript errors on `webpack` types

```bash
npm install --save-dev webpack
```

### `@axe-core/playwright` not found (E2E tests)

```bash
npm install --save-dev @axe-core/playwright
```

---

## Common Environment Variable Issues

| Error | Likely Cause |
|-------|-------------|
| `OPENAI_API_KEY not set` | Missing from `.env` |
| `CORS error in browser` | `FRONTEND_URL` not set or wrong domain |
| `Rate limit disabled: Redis not configured` | `UPSTASH_REDIS_URL` not set (OK in dev) |
| `Sentry DSN not configured` | `SENTRY_DSN` not set (OK in dev) |

---

## Getting Help

1. Check [GitHub Issues](https://github.com/ASADULLAH999/ai-textbook/issues)
2. Search error message in project Sentry
3. Review logs: `vercel logs --since 1h`
4. See [Runbook](./RUNBOOK.md) for operational procedures

---

*Last reviewed: 2026-02-28*
