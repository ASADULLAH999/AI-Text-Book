#!/usr/bin/env bash
# T125 — Load test with Apache Bench (1,000 concurrent users)
# Usage: ./scripts/load_test.sh [API_URL]

set -euo pipefail

API_URL="${1:-http://localhost:8000}"
RESULTS_DIR="load-test-results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$RESULTS_DIR"

echo "=== AI Textbook API Load Test ==="
echo "Target: $API_URL"
echo "Timestamp: $TIMESTAMP"
echo ""

# Prepare request body
cat > /tmp/chat_request.json << 'EOF'
{"message": "What is ROS2?", "mode": "book_only"}
EOF

# ── Test 1: Baseline (10 concurrent, 100 requests) ───────────────────────────
echo "--- Test 1: Baseline (10 concurrent) ---"
ab -n 100 -c 10 \
   -p /tmp/chat_request.json \
   -T 'application/json' \
   -H 'Accept: application/json' \
   "${API_URL}/api/v1/chat" \
   > "$RESULTS_DIR/baseline_${TIMESTAMP}.txt" 2>&1
echo "Done. Results: $RESULTS_DIR/baseline_${TIMESTAMP}.txt"

# ── Test 2: Medium load (50 concurrent, 500 requests) ────────────────────────
echo ""
echo "--- Test 2: Medium load (50 concurrent) ---"
ab -n 500 -c 50 \
   -p /tmp/chat_request.json \
   -T 'application/json' \
   -H 'Accept: application/json' \
   "${API_URL}/api/v1/chat" \
   > "$RESULTS_DIR/medium_${TIMESTAMP}.txt" 2>&1
echo "Done. Results: $RESULTS_DIR/medium_${TIMESTAMP}.txt"

# ── Test 3: High load (100 concurrent, 1000 requests) ────────────────────────
echo ""
echo "--- Test 3: High load (100 concurrent) ---"
ab -n 1000 -c 100 \
   -p /tmp/chat_request.json \
   -T 'application/json' \
   -H 'Accept: application/json' \
   "${API_URL}/api/v1/chat" \
   > "$RESULTS_DIR/high_${TIMESTAMP}.txt" 2>&1
echo "Done. Results: $RESULTS_DIR/high_${TIMESTAMP}.txt"

# ── Test 4: Health endpoint (1000 concurrent baseline) ───────────────────────
echo ""
echo "--- Test 4: Health endpoint (stress test) ---"
ab -n 10000 -c 1000 \
   -H 'Accept: application/json' \
   "${API_URL}/api/v1/health" \
   > "$RESULTS_DIR/health_stress_${TIMESTAMP}.txt" 2>&1
echo "Done. Results: $RESULTS_DIR/health_stress_${TIMESTAMP}.txt"

# ── Parse results ─────────────────────────────────────────────────────────────
echo ""
echo "=== Results Summary ==="
for f in "$RESULTS_DIR"/*_${TIMESTAMP}.txt; do
  TEST_NAME=$(basename "$f" | sed "s/_${TIMESTAMP}\.txt//")
  echo ""
  echo "--- $TEST_NAME ---"
  grep -E "Requests per second|Time per request|Failed requests|Percentage of the requests" "$f" || true
done

echo ""
echo "Full results saved to: $RESULTS_DIR/"
