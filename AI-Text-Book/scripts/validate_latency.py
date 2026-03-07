"""
T126 — Validate p95 latency <3s, p50 <2s across 10,000 queries.

Usage:
    python scripts/validate_latency.py --api-url http://localhost:8000 --n 1000

For production:
    python scripts/validate_latency.py --api-url https://ai-textbook-chatbot-api.vercel.app --n 10000
"""

import argparse
import asyncio
import json
import statistics
import time
from typing import List

import httpx

SAMPLE_QUERIES = [
    "What is ROS2?",
    "Explain SLAM navigation",
    "How does Isaac Sim work?",
    "What is a behavior tree?",
    "Explain TF2 transforms",
    "What is Nav2?",
    "How does URDF work?",
    "What is domain randomization?",
    "Explain sim-to-real transfer",
    "What is a ROS2 node?",
]

async def measure_single(client: httpx.AsyncClient, url: str, message: str) -> float:
    """Measure latency for a single request. Returns latency in ms or -1 on error."""
    payload = {"message": message, "mode": "book_only"}
    try:
        start = time.perf_counter()
        resp = await client.post(
            f"{url}/api/v1/chat",
            json=payload,
            timeout=30.0,
        )
        elapsed_ms = (time.perf_counter() - start) * 1000
        if resp.status_code == 200:
            return elapsed_ms
        else:
            print(f"  HTTP {resp.status_code} for query: {message[:40]}")
            return -1
    except Exception as e:
        print(f"  Error for query '{message[:40]}': {e}")
        return -1


async def run_validation(api_url: str, n: int, concurrency: int) -> dict:
    """Run latency validation with *n* requests, *concurrency* at a time."""
    latencies: List[float] = []
    errors = 0

    queries = [SAMPLE_QUERIES[i % len(SAMPLE_QUERIES)] for i in range(n)]

    async with httpx.AsyncClient() as client:
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_measure(msg: str) -> float:
            async with semaphore:
                return await measure_single(client, api_url, msg)

        tasks = [bounded_measure(q) for q in queries]

        print(f"Running {n} requests (concurrency={concurrency})...")
        results = await asyncio.gather(*tasks)

    for r in results:
        if r < 0:
            errors += 1
        else:
            latencies.append(r)

    if not latencies:
        return {"error": "All requests failed"}

    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]
    avg = statistics.mean(latencies)

    return {
        "total_requests": n,
        "successful": len(latencies),
        "errors": errors,
        "error_rate": errors / n,
        "latency_ms": {
            "min": round(min(latencies), 1),
            "p50": round(p50, 1),
            "p95": round(p95, 1),
            "p99": round(p99, 1),
            "max": round(max(latencies), 1),
            "avg": round(avg, 1),
        },
        "targets": {
            "p50_target_ms": 2000,
            "p95_target_ms": 3000,
            "p50_pass": p50 <= 2000,
            "p95_pass": p95 <= 3000,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Validate API latency targets")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--n", type=int, default=100, help="Number of requests")
    parser.add_argument("--concurrency", type=int, default=10, help="Concurrent requests")
    args = parser.parse_args()

    print(f"=== Latency Validation (T126) ===")
    print(f"API: {args.api_url}")
    print(f"Requests: {args.n} | Concurrency: {args.concurrency}")
    print()

    results = asyncio.run(run_validation(args.api_url, args.n, args.concurrency))

    print(json.dumps(results, indent=2))
    print()

    targets = results.get("targets", {})
    p50_pass = targets.get("p50_pass", False)
    p95_pass = targets.get("p95_pass", False)

    print(f"p50 ({'PASS' if p50_pass else 'FAIL'}): {results['latency_ms']['p50']}ms (target: 2000ms)")
    print(f"p95 ({'PASS' if p95_pass else 'FAIL'}): {results['latency_ms']['p95']}ms (target: 3000ms)")
    print()

    if p50_pass and p95_pass:
        print("✓ All latency targets met.")
        return 0
    else:
        print("✗ Latency targets NOT met.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
