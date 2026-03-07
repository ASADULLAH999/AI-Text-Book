# Observability Setup Guide

> **T120 / T121** — Vercel Analytics, Sentry, and alert configuration.

## 1. Vercel Analytics (Frontend)

Vercel Analytics provides Core Web Vitals and page-view tracking with zero additional configuration for Vercel-hosted projects.

### Enable in Vercel Dashboard

1. Open your project in the [Vercel Dashboard](https://vercel.com).
2. Go to **Analytics** tab → **Enable Analytics**.
3. No code changes required for page views.

### Custom Event Tracking (optional)

Install the Vercel Analytics SDK if you need custom events:

```bash
npm install @vercel/analytics
```

Add to `src/theme/Root.tsx`:

```tsx
import { Analytics } from '@vercel/analytics/react';

export default function Root({ children }) {
  return (
    <>
      {children}
      <Analytics />
    </>
  );
}
```

### Key Metrics to Monitor

| Metric | Target | Alert Threshold |
|--------|--------|----------------|
| LCP (Largest Contentful Paint) | < 2.5s | > 4.0s |
| FID (First Input Delay) | < 100ms | > 300ms |
| CLS (Cumulative Layout Shift) | < 0.1 | > 0.25 |
| Page views per day | — | < 50% of baseline |

---

## 2. Sentry (Backend Error Tracking)

Sentry is already initialized in `api/src/main.py`. Configure in `.env`:

```env
SENTRY_DSN=https://<key>@<org>.ingest.sentry.io/<project>
SENTRY_ENVIRONMENT=production
SENTRY_TRACES_SAMPLE_RATE=0.1   # 10% of transactions
SENTRY_PROFILES_SAMPLE_RATE=0.05  # 5% profiling
```

### Key Sentry Alerts to Configure

In the Sentry project → **Alerts** → **Create Alert Rule**:

**Alert 1: Error Rate**
```
Name: High Error Rate
Condition: error count > 50 in 5 minutes
Notification: email + Slack #alerts
```

**Alert 2: P95 Latency**
```
Name: Slow Response Time
Condition: p95(response_time) > 5000ms in last 15 minutes
Query: transaction:/api/v1/chat
Notification: email + Slack #alerts
```

**Alert 3: Unhandled Exceptions**
```
Name: New Unhandled Exception
Condition: new issue created
Priority: high
Notification: immediate email
```

---

## 3. T121 — Alert Configuration

### Backend Health Alerts (via Upstash / Vercel)

Configure in `.env`:
```env
# Alert thresholds
ALERT_ERROR_RATE_THRESHOLD=0.05      # 5% error rate
ALERT_LATENCY_P95_MS=5000            # 5s p95 latency
ALERT_LATENCY_P50_MS=2000            # 2s p50 latency
ALERT_MIN_SUCCESS_RATE=0.95          # 95% success rate
```

### GitHub Actions Alert Workflow

```yaml
# .github/workflows/health-check.yml
name: API Health Check
on:
  schedule:
    - cron: '*/5 * * * *'  # Every 5 minutes

jobs:
  health:
    runs-on: ubuntu-latest
    steps:
      - name: Check API health
        run: |
          STATUS=$(curl -sf https://ai-textbook-chatbot-api.vercel.app/api/v1/health | jq -r '.status')
          if [ "$STATUS" != "healthy" ]; then
            echo "::error::API health check failed: $STATUS"
            exit 1
          fi
```

### Vercel Deployment Notifications

In Vercel → **Settings** → **Git** → **Deploy Hooks**, add notifications for:
- Failed deployments → Slack / email
- Successful production deployments → Slack #deployments

---

## 4. Key Dashboards

### Custom Dashboard Queries (Sentry Discover)

```sql
-- Top error routes
SELECT transaction, count() as errors
FROM transactions
WHERE level = "error"
GROUP BY transaction
ORDER BY errors DESC
LIMIT 10

-- P95 latency by route
SELECT transaction, p95(transaction.duration)
FROM transactions
GROUP BY transaction
ORDER BY p95(transaction.duration) DESC
```

### Log Queries (Vercel Log Explorer)

```
-- Failed chat requests
status:5xx path:/api/v1/chat

-- Rate-limited requests
"rate_limit_exceeded"

-- Slow requests (>3s)
duration:>3000 path:/api/v1/chat
```

---

*Last reviewed: 2026-02-28*
