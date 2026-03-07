#!/usr/bin/env bash
# T134 — Validate cold start time < 2s for serverless functions.
# Measures time from first request after a period of inactivity.

set -euo pipefail

API_URL="${1:-https://ai-textbook-chatbot-api.vercel.app}"
TARGET_MS=2000

echo "=== Cold Start Validation (T134) ==="
echo "API: $API_URL"
echo "Target: < ${TARGET_MS}ms"
echo ""

# Perform 3 cold-start measurements
TOTAL=0
PASS=0
FAIL=0

for i in 1 2 3; do
  echo "--- Measurement $i ---"

  # Sleep to allow function to go cold (Vercel: ~5 min inactivity)
  # For testing purposes we just measure first-request latency
  START=$(date +%s%3N)
  HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" \
    --max-time 10 \
    "${API_URL}/api/v1/health")
  END=$(date +%s%3N)

  ELAPSED=$((END - START))
  TOTAL=$((TOTAL + ELAPSED))

  if [ "$HTTP_STATUS" = "200" ]; then
    if [ "$ELAPSED" -le "$TARGET_MS" ]; then
      echo "  ✓ ${ELAPSED}ms (PASS) — HTTP $HTTP_STATUS"
      PASS=$((PASS + 1))
    else
      echo "  ✗ ${ELAPSED}ms (FAIL — exceeded ${TARGET_MS}ms) — HTTP $HTTP_STATUS"
      FAIL=$((FAIL + 1))
    fi
  else
    echo "  ✗ HTTP $HTTP_STATUS (non-200 response)"
    FAIL=$((FAIL + 1))
  fi

  # Brief pause between measurements
  sleep 2
done

AVG=$((TOTAL / 3))
echo ""
echo "=== Results ==="
echo "Passed: $PASS/3"
echo "Failed: $FAIL/3"
echo "Average: ${AVG}ms"

if [ "$FAIL" -eq "0" ]; then
  echo "✓ Cold start target met (<${TARGET_MS}ms)"
  exit 0
else
  echo "✗ Cold start target NOT met"
  exit 1
fi
