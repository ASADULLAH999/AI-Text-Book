"""
Citation Accuracy Validation — T055 [US1]
Target: > 95% citation accuracy on 100 test queries

Validation criteria:
1. Each generated citation must be structurally valid (required fields present)
2. Citation source must match the chunk's metadata
3. Citation text must be a substring of (or equal to) the source chunk text
4. Citation score must reflect retrieval relevance (> 0)
5. No duplicate citations per response
6. Preview is a non-empty truncation of the chunk text

Run:
    cd api
    pytest tests/unit/test_citation_accuracy_validation.py -v --tb=short
"""

import pytest
import random
import string
from typing import List, Dict, Any
from services.citation_service import CitationService


# ---------------------------------------------------------------------------
# Test data generation
# ---------------------------------------------------------------------------

CHAPTERS = [
    "Chapter 1: Introduction to AI",
    "Chapter 2: Machine Learning Fundamentals",
    "Chapter 3: Neural Networks",
    "Chapter 4: Deep Learning",
    "Chapter 5: Computer Vision",
    "Chapter 6: Natural Language Processing",
    "Chapter 7: Robotics",
    "Chapter 8: Reinforcement Learning",
    "Chapter 9: Ethics in AI",
    "Chapter 10: Applications",
]

SECTIONS = [
    "Overview", "Core Concepts", "Advanced Topics",
    "Practical Applications", "Case Studies", "Summary",
]

SAMPLE_TEXTS = [
    "Neural networks are computational models inspired by the biological structure of the brain.",
    "Gradient descent is an optimization algorithm used to minimize the loss function.",
    "Convolutional neural networks excel at image recognition tasks.",
    "Recurrent neural networks process sequential data through hidden states.",
    "Transformer architectures use attention mechanisms for sequence modeling.",
    "Backpropagation computes gradients of the loss with respect to parameters.",
    "Batch normalization stabilizes training by normalizing layer activations.",
    "Dropout regularization prevents overfitting by randomly dropping neurons.",
    "Transfer learning leverages pre-trained models for new tasks.",
    "Reinforcement learning optimizes policies through reward maximization.",
    "Support vector machines find optimal hyperplanes for classification.",
    "Decision trees partition feature space using hierarchical splits.",
    "Random forests aggregate multiple decision trees to reduce variance.",
    "Principal component analysis reduces dimensionality through eigendecomposition.",
    "K-means clustering assigns data points to nearest cluster centroids.",
    "Natural language processing transforms text into structured representations.",
    "Word embeddings map words to dense vector representations.",
    "Attention mechanisms compute weighted sums over input sequences.",
    "BERT uses bidirectional context for language understanding tasks.",
    "GPT generates text autoregressively from learned language distributions.",
]


def generate_test_chunk(idx: int) -> Dict[str, Any]:
    """Generate a deterministic test chunk."""
    text_idx = idx % len(SAMPLE_TEXTS)
    chapter_idx = idx % len(CHAPTERS)
    section_idx = idx % len(SECTIONS)
    page = (idx % 50) + 1

    return {
        "chunk_id": f"chunk-{idx:04d}",
        "text": SAMPLE_TEXTS[text_idx],
        "score": 0.7 + (idx % 30) / 100.0,  # 0.70 – 0.99
        "rerank_score": 0.75 + (idx % 25) / 100.0,
        "metadata": {
            "chapter": CHAPTERS[chapter_idx],
            "section": SECTIONS[section_idx],
            "heading": f"Section {section_idx + 1}.{idx % 5 + 1}",
            "page_number": page,
        },
    }


def generate_100_test_scenarios() -> List[Dict[str, Any]]:
    """Generate 100 test scenarios, each with 3–5 chunks."""
    random.seed(42)
    scenarios = []
    for i in range(100):
        chunk_count = random.randint(3, 5)
        chunks = [generate_test_chunk((i * 7 + j) % len(SAMPLE_TEXTS)) for j in range(chunk_count)]
        # Ensure unique chunk IDs per scenario
        for j, chunk in enumerate(chunks):
            chunk["chunk_id"] = f"scenario-{i:03d}-chunk-{j}"
        scenarios.append({
            "scenario_id": i,
            "query": f"Question about topic {i}: {SAMPLE_TEXTS[i % len(SAMPLE_TEXTS)][:50]}?",
            "chunks": chunks,
        })
    return scenarios


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

def validate_citation_accuracy(
    citation: Dict[str, Any],
    source_chunk: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Validate that a citation accurately represents its source chunk.

    Returns a dict with:
        is_accurate: bool
        errors: list of error descriptions
        checks: dict of individual check results
    """
    errors = []
    checks = {}

    # Check 1: Structural validity
    required_fields = ["id", "number", "chunk_id", "text", "source", "score", "preview"]
    missing_fields = [f for f in required_fields if f not in citation]
    checks["structural_validity"] = len(missing_fields) == 0
    if missing_fields:
        errors.append(f"Missing fields: {missing_fields}")

    # Check 2: chunk_id matches source
    checks["chunk_id_match"] = citation.get("chunk_id") == source_chunk.get("chunk_id")
    if not checks["chunk_id_match"]:
        errors.append(f"chunk_id mismatch: {citation.get('chunk_id')} != {source_chunk.get('chunk_id')}")

    # Check 3: Text matches source chunk
    checks["text_match"] = citation.get("text") == source_chunk.get("text", "")
    if not checks["text_match"]:
        errors.append("Citation text does not match source chunk text")

    # Check 4: Source metadata accuracy
    source = citation.get("source", {})
    chunk_meta = source_chunk.get("metadata", {})
    checks["chapter_match"] = source.get("chapter") == chunk_meta.get("chapter")
    checks["section_match"] = source.get("section") == chunk_meta.get("section")
    checks["page_match"] = source.get("page_number") == chunk_meta.get("page_number")

    if not checks["chapter_match"]:
        errors.append(f"Chapter mismatch: {source.get('chapter')} != {chunk_meta.get('chapter')}")
    if not checks["section_match"]:
        errors.append(f"Section mismatch: {source.get('section')} != {chunk_meta.get('section')}")

    # Check 5: Score is positive
    checks["positive_score"] = citation.get("score", 0) > 0
    if not checks["positive_score"]:
        errors.append(f"Citation score not positive: {citation.get('score')}")

    # Check 6: Preview is a prefix of source text
    preview = citation.get("preview", "")
    source_text = source_chunk.get("text", "")
    if preview.endswith("..."):
        # Truncated — verify prefix
        checks["preview_accuracy"] = source_text.startswith(preview[:-3])
    else:
        # Full text — must match
        checks["preview_accuracy"] = preview == source_text
    if not checks["preview_accuracy"]:
        errors.append("Citation preview does not accurately represent source text")

    is_accurate = len(errors) == 0
    return {"is_accurate": is_accurate, "errors": errors, "checks": checks}


# ---------------------------------------------------------------------------
# T055: Main Validation Test — 100 queries, >95% accuracy required
# ---------------------------------------------------------------------------

class TestCitationAccuracy:
    """Validate citation accuracy meets the >95% threshold on 100 test queries."""

    @pytest.fixture(scope="class")
    def service(self):
        return CitationService()

    @pytest.fixture(scope="class")
    def scenarios(self):
        return generate_100_test_scenarios()

    def test_citation_accuracy_exceeds_95_percent(self, service, scenarios):
        """
        T055: Citation accuracy > 95% on 100 test queries.

        For each scenario:
        1. Generate citations from chunks
        2. Validate each citation against its source chunk
        3. Calculate accuracy rate
        """
        total_citations = 0
        accurate_citations = 0
        failures = []

        for scenario in scenarios:
            chunks = scenario["chunks"]
            citations = service.generate_citations(chunks)
            deduped = service.deduplicate_citations(citations)

            for i, (citation, chunk) in enumerate(zip(deduped, chunks)):
                total_citations += 1
                validation = validate_citation_accuracy(citation, chunk)

                if validation["is_accurate"]:
                    accurate_citations += 1
                else:
                    failures.append({
                        "scenario_id": scenario["scenario_id"],
                        "citation_index": i,
                        "errors": validation["errors"],
                    })

        accuracy_rate = accurate_citations / total_citations if total_citations > 0 else 0.0
        accuracy_pct = accuracy_rate * 100

        # Report failures for debugging
        if failures:
            sample_failures = failures[:5]
            failure_summary = "\n".join(
                f"  Scenario {f['scenario_id']}, citation {f['citation_index']}: {f['errors']}"
                for f in sample_failures
            )
        else:
            failure_summary = "None"

        assert accuracy_rate >= 0.95, (
            f"Citation accuracy {accuracy_pct:.1f}% < 95% required.\n"
            f"Total citations: {total_citations}\n"
            f"Accurate: {accurate_citations}\n"
            f"Failed: {len(failures)}\n"
            f"Sample failures:\n{failure_summary}"
        )

    def test_all_citations_structurally_valid(self, service, scenarios):
        """All 100 scenarios must produce structurally valid citations."""
        for scenario in scenarios:
            citations = service.generate_citations(scenario["chunks"])
            for citation in citations:
                result = service.validate_citation(citation)
                assert result["is_valid"], (
                    f"Scenario {scenario['scenario_id']}: {result['errors']}"
                )

    def test_no_scenario_produces_empty_citations(self, service, scenarios):
        """Every scenario with chunks should produce at least one citation."""
        for scenario in scenarios:
            if scenario["chunks"]:
                citations = service.generate_citations(scenario["chunks"])
                assert len(citations) > 0, (
                    f"Scenario {scenario['scenario_id']} produced no citations"
                )

    def test_citation_numbers_are_sequential_per_response(self, service, scenarios):
        """Citation numbers within each response must be sequential starting at 1."""
        for scenario in scenarios[:20]:  # Check first 20 for speed
            citations = service.generate_citations(scenario["chunks"])
            for i, citation in enumerate(citations):
                assert citation["number"] == i + 1, (
                    f"Scenario {scenario['scenario_id']}: "
                    f"expected number {i+1}, got {citation['number']}"
                )

    def test_deduplication_preserves_accuracy(self, service, scenarios):
        """Deduplication should not introduce inaccuracies."""
        for scenario in scenarios[:20]:
            chunks = scenario["chunks"]
            # Add duplicate chunk
            if chunks:
                dup_chunks = chunks + [chunks[0]]
                citations = service.generate_citations(dup_chunks)
                deduped = service.deduplicate_citations(citations)

                # Deduplicated citations should still be valid
                for citation in deduped:
                    result = service.validate_citation(citation)
                    assert result["is_valid"]

    def test_citations_preserve_chapter_information(self, service, scenarios):
        """100% of citations must include chapter information (no 'Unknown Chapter')."""
        unknown_count = 0
        total = 0

        for scenario in scenarios:
            citations = service.generate_citations(scenario["chunks"])
            for citation in citations:
                total += 1
                if citation["source"].get("chapter") == "Unknown Chapter":
                    unknown_count += 1

        unknown_rate = unknown_count / total if total > 0 else 0
        assert unknown_rate == 0.0, (
            f"{unknown_count}/{total} citations have 'Unknown Chapter' — "
            f"all test chunks should have chapter metadata"
        )

    def test_score_range_validity(self, service, scenarios):
        """All citation scores must be between 0.0 and 1.0."""
        for scenario in scenarios:
            citations = service.generate_citations(scenario["chunks"])
            for citation in citations:
                assert 0.0 <= citation["score"] <= 1.0, (
                    f"Citation score {citation['score']} out of range [0, 1]"
                )

    def test_preview_max_length_enforced(self, service, scenarios):
        """Citation previews must not exceed 153 characters (150 + '...')."""
        for scenario in scenarios:
            citations = service.generate_citations(scenario["chunks"])
            for citation in citations:
                preview = citation.get("preview", "")
                assert len(preview) <= 153, (
                    f"Preview too long: {len(preview)} chars"
                )
