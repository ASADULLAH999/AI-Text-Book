"""
T128/T129/T130 — Validate quality targets:
  - T128: Citation accuracy > 95% on 500 queries
  - T129: Hallucination rate < 5% on 500 queries
  - T130: Grounding rate > 90% on 500 queries

Usage:
    python scripts/validate_quality.py --api-url http://localhost:8000 --n 50
"""

import argparse
import asyncio
import json
import time
from typing import List, Dict, Any

import httpx

# Representative test queries with expected content presence
TEST_QUERIES = [
    {"q": "What is ROS2?", "expect_keywords": ["ros2", "robot", "framework", "middleware"]},
    {"q": "Explain SLAM navigation", "expect_keywords": ["slam", "map", "localization"]},
    {"q": "What is a ROS2 node?", "expect_keywords": ["node", "publish", "subscribe"]},
    {"q": "How does Nav2 work?", "expect_keywords": ["nav2", "navigation", "path"]},
    {"q": "What is Gazebo simulation?", "expect_keywords": ["gazebo", "simulation", "robot"]},
    {"q": "Explain behavior trees in robotics", "expect_keywords": ["behavior", "tree", "action"]},
    {"q": "What is URDF format?", "expect_keywords": ["urdf", "robot", "joint", "link"]},
    {"q": "How does Isaac Sim work?", "expect_keywords": ["isaac", "simulation", "nvidia"]},
    {"q": "What is domain randomization?", "expect_keywords": ["domain", "randomization", "training"]},
    {"q": "Explain TF2 transforms", "expect_keywords": ["tf2", "transform", "coordinate"]},
]


async def evaluate_response(response: Dict[str, Any], query_info: Dict) -> Dict[str, bool]:
    """Evaluate a single response for quality metrics."""
    answer = response.get("message", "").lower()
    citations = response.get("citations", [])
    refused = response.get("refused", False)

    # Citation accuracy: response has at least 1 citation with score > 0.6
    has_citation = len(citations) > 0
    high_quality_citation = any(c.get("score", 0) > 0.6 for c in citations)
    citation_accurate = has_citation and high_quality_citation

    # Hallucination: response contains expected keywords (grounded in content)
    expected_keywords = query_info.get("expect_keywords", [])
    keywords_found = sum(1 for k in expected_keywords if k in answer)
    keyword_coverage = keywords_found / max(len(expected_keywords), 1)
    # Low keyword coverage + no citations = potential hallucination
    not_hallucinated = refused or (keyword_coverage >= 0.3 and has_citation)

    # Grounding: answer is not a generic refusal, has citations
    grounded = not refused and has_citation and keyword_coverage >= 0.2

    return {
        "citation_accurate": citation_accurate,
        "not_hallucinated": not_hallucinated,
        "grounded": grounded,
        "refused": refused,
        "citations_count": len(citations),
        "keyword_coverage": round(keyword_coverage, 2),
    }


async def run_quality_validation(api_url: str, n: int, concurrency: int) -> dict:
    """Run quality validation across n queries."""
    queries = [TEST_QUERIES[i % len(TEST_QUERIES)] for i in range(n)]
    results = []
    errors = 0

    async with httpx.AsyncClient() as client:
        semaphore = asyncio.Semaphore(concurrency)

        async def evaluate_one(q_info: dict) -> Dict | None:
            async with semaphore:
                try:
                    resp = await client.post(
                        f"{api_url}/api/v1/chat",
                        json={"message": q_info["q"], "mode": "book_only"},
                        timeout=30.0,
                    )
                    if resp.status_code == 200:
                        return await evaluate_response(resp.json(), q_info)
                    return None
                except Exception as e:
                    print(f"  Error: {e}")
                    return None

        tasks = [evaluate_one(q) for q in queries]
        print(f"Running {n} quality evaluation requests...")
        raw_results = await asyncio.gather(*tasks)

    for r in raw_results:
        if r is None:
            errors += 1
        else:
            results.append(r)

    if not results:
        return {"error": "All requests failed"}

    total = len(results)
    citation_accuracy = sum(1 for r in results if r["citation_accurate"]) / total
    hallucination_rate = 1 - (sum(1 for r in results if r["not_hallucinated"]) / total)
    grounding_rate = sum(1 for r in results if r["grounded"]) / total
    avg_citations = sum(r["citations_count"] for r in results) / total

    return {
        "total_evaluated": total,
        "errors": errors,
        "metrics": {
            "citation_accuracy": round(citation_accuracy, 3),
            "hallucination_rate": round(hallucination_rate, 3),
            "grounding_rate": round(grounding_rate, 3),
            "avg_citations_per_response": round(avg_citations, 2),
        },
        "targets": {
            "citation_accuracy_target": 0.95,
            "hallucination_rate_target": 0.05,
            "grounding_rate_target": 0.90,
            "citation_accuracy_pass": citation_accuracy >= 0.95,
            "hallucination_rate_pass": hallucination_rate <= 0.05,
            "grounding_rate_pass": grounding_rate >= 0.90,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Validate response quality targets")
    parser.add_argument("--api-url", default="http://localhost:8000")
    parser.add_argument("--n", type=int, default=50, help="Number of test queries")
    parser.add_argument("--concurrency", type=int, default=5)
    args = parser.parse_args()

    print("=== Response Quality Validation (T128/T129/T130) ===")
    print(f"API: {args.api_url}")
    print(f"Queries: {args.n}")
    print()

    result = asyncio.run(run_quality_validation(args.api_url, args.n, args.concurrency))

    print(json.dumps(result, indent=2))
    print()

    targets = result.get("targets", {})
    all_pass = all([
        targets.get("citation_accuracy_pass", False),
        targets.get("hallucination_rate_pass", False),
        targets.get("grounding_rate_pass", False),
    ])

    m = result.get("metrics", {})
    t = result.get("targets", {})
    print(f"T128 Citation Accuracy   ({'PASS' if t.get('citation_accuracy_pass') else 'FAIL'}): "
          f"{m.get('citation_accuracy', 0):.1%} (target: ≥95%)")
    print(f"T129 Hallucination Rate  ({'PASS' if t.get('hallucination_rate_pass') else 'FAIL'}): "
          f"{m.get('hallucination_rate', 0):.1%} (target: ≤5%)")
    print(f"T130 Grounding Rate      ({'PASS' if t.get('grounding_rate_pass') else 'FAIL'}): "
          f"{m.get('grounding_rate', 0):.1%} (target: ≥90%)")
    print()

    if all_pass:
        print("✓ All quality targets met.")
        return 0
    else:
        print("✗ Some quality targets NOT met.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
