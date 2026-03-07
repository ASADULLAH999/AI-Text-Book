"""
Unit tests for all three chat mode services and boundary enforcement.
T078 [US3] — Mode unit tests
T080 [US3] — Validate mode boundaries with 100+ test queries

Coverage:
- GeneralKnowledgeMode
- SelectedTextMode (boundary via modes.__init__)
- BookOnlyMode (boundary via modes.__init__)
- enforce_mode_boundary — valid and invalid inputs (100+ cases)
- get_mode_handler routing
"""

import pytest
from unittest.mock import patch, MagicMock

# ============================================================
# Imports under test
# ============================================================
from services.modes import (
    enforce_mode_boundary,
    get_mode_handler,
    ModeBoundaryError,
    VALID_MODES,
    BookOnlyMode,
    SelectedTextMode,
    GeneralKnowledgeMode,
    get_book_only_mode,
    get_selected_text_mode,
    get_general_knowledge_mode,
)
from services.modes.general_knowledge import GeneralKnowledgeMode as GKMode


# ============================================================
# enforce_mode_boundary — valid modes
# ============================================================

class TestEnforceModeBoundaryValid:
    """Ensure all valid modes pass through enforce_mode_boundary."""

    def test_book_only(self):
        assert enforce_mode_boundary("book_only") == "book_only"

    def test_selected_text(self):
        assert enforce_mode_boundary("selected_text") == "selected_text"

    def test_general_knowledge(self):
        assert enforce_mode_boundary("general_knowledge") == "general_knowledge"

    def test_all_valid_modes_in_set(self):
        for mode in VALID_MODES:
            assert enforce_mode_boundary(mode) == mode


# ============================================================
# enforce_mode_boundary — invalid modes (T080: 100+ boundary cases)
# ============================================================

INVALID_MODE_STRINGS = [
    # Legacy / renamed modes
    "guided",
    "exploratory",
    "book-only",
    "BookOnly",
    "BOOK_ONLY",
    "selected-text",
    "SelectedText",
    "SELECTED_TEXT",
    "general_knowledge_mode",
    "general",
    "gk",
    # Empty / whitespace
    "",
    " ",
    "\t",
    "\n",
    "  book_only  ",
    # SQL / injection attempts
    "book_only; DROP TABLE users;",
    "' OR '1'='1",
    "1=1",
    # XSS attempts
    "<script>alert(1)</script>",
    "javascript:void(0)",
    # None / numeric strings
    "None",
    "null",
    "undefined",
    "0",
    "1",
    "-1",
    "3.14",
    # Random strings
    "foo",
    "bar",
    "baz",
    "qux",
    "chat",
    "rag",
    "vector",
    "embedding",
    "retrieval",
    "llm",
    "openai",
    "gpt4",
    "textbook",
    "document",
    "chunk",
    "mode",
    "modes",
    "answer",
    "question",
    # Mixed case
    "Book_Only",
    "General_Knowledge",
    "Selected_Text",
    "BOOK_only",
    "selected_TEXT",
    "GENERAL_knowledge",
    # Unicode edge cases
    "book_onlу",   # Cyrillic 'у' instead of ASCII 'y'
    "bοok_only",   # Greek 'ο'
    # Truncated/partial
    "book",
    "only",
    "select",
    "selected",
    "general",
    "knowledge",
    # Concatenated
    "book_onlyselected_text",
    "general_knowledgebook_only",
    # With numbers
    "book_only_1",
    "selected_text_v2",
    "general_knowledge_3",
    # Special characters
    "book_only!",
    "selected@text",
    "general#knowledge",
    "book$only",
    "selected%text",
    "general&knowledge",
    "book*only",
    "selected+text",
    "general=knowledge",
    "book|only",
    "selected\\text",
    "general/knowledge",
    "book?only",
    "selected.text",
    "general,knowledge",
    "book;only",
    "selected:text",
    "general<knowledge",
    "book>only",
    "selected[text]",
    "{general_knowledge}",
    "(book_only)",
    # Path traversal
    "../book_only",
    "../../general_knowledge",
    # Long strings
    "a" * 100,
    "book_only" * 10,
    # JSON-like
    '{"mode": "book_only"}',
    "[book_only]",
    # URL-encoded
    "book%5Fonly",
    "selected%5Ftext",
]


class TestEnforceModeBoundaryInvalid:
    """T080 — validate boundary rejects all invalid mode strings."""

    @pytest.mark.parametrize("bad_mode", INVALID_MODE_STRINGS)
    def test_rejects_invalid_mode(self, bad_mode: str):
        with pytest.raises(ModeBoundaryError):
            enforce_mode_boundary(bad_mode)

    def test_total_invalid_cases_meets_minimum(self):
        """T080 — assert we have 100+ invalid test cases."""
        assert len(INVALID_MODE_STRINGS) >= 100, (
            f"Need ≥100 invalid cases, got {len(INVALID_MODE_STRINGS)}"
        )


# ============================================================
# get_mode_handler routing
# ============================================================

class TestGetModeHandler:
    def test_routes_book_only(self):
        with patch("services.modes.get_book_only_mode") as mock_factory:
            mock_factory.return_value = MagicMock(spec=BookOnlyMode)
            handler = get_mode_handler("book_only")
            mock_factory.assert_called_once()

    def test_routes_selected_text(self):
        with patch("services.modes.get_selected_text_mode") as mock_factory:
            mock_factory.return_value = MagicMock(spec=SelectedTextMode)
            handler = get_mode_handler("selected_text")
            mock_factory.assert_called_once()

    def test_routes_general_knowledge(self):
        with patch("services.modes.get_general_knowledge_mode") as mock_factory:
            mock_factory.return_value = MagicMock(spec=GeneralKnowledgeMode)
            handler = get_mode_handler("general_knowledge")
            mock_factory.assert_called_once()

    def test_invalid_mode_raises(self):
        with pytest.raises(ModeBoundaryError):
            get_mode_handler("guided")

    def test_empty_string_raises(self):
        with pytest.raises(ModeBoundaryError):
            get_mode_handler("")


# ============================================================
# GeneralKnowledgeMode
# ============================================================

class TestGeneralKnowledgeMode:
    def setup_method(self):
        self.mode = GKMode(append_disclaimer=True, soft_retrieval=True)

    def test_get_mode_info_returns_amber(self):
        info = self.mode.get_mode_info()
        assert info["color"] == "amber"
        assert info["mode"] == "general_knowledge"

    def test_disclaimer_appended_when_enabled(self):
        result = self.mode.process_response("Some answer.")
        assert "⚠️" in result
        assert "beyond the textbook" in result.lower() or "primary sources" in result.lower()

    def test_no_disclaimer_when_disabled(self):
        mode = GKMode(append_disclaimer=False)
        result = mode.process_response("Some answer.")
        assert result == "Some answer."

    def test_build_response_metadata_mode_key(self):
        meta = self.mode.build_response_metadata(chunks_retrieved=3, query_length=50)
        assert meta["mode"] == "general_knowledge"
        assert meta["grounded"] is False
        assert meta["chunks_retrieved"] == 3
        assert meta["query_length"] == 50

    def test_system_prompt_without_chunks(self):
        prompt = self.mode.build_system_prompt()
        assert "general knowledge" in prompt.lower()

    def test_system_prompt_with_chunks(self):
        chunks = [{"text": "Chapter 1 content about photosynthesis."}]
        prompt = self.mode.build_system_prompt(chunks)
        assert "photosynthesis" in prompt

    def test_system_prompt_limits_chunks(self):
        chunks = [{"text": f"Chunk {i}"} for i in range(10)]
        prompt = self.mode.build_system_prompt(chunks)
        # Should only include first 3 chunks
        assert "Chunk 0" in prompt
        assert "Chunk 3" not in prompt


# ============================================================
# SelectedTextMode boundary enforcement
# ============================================================

class TestSelectedTextModeBoundary:
    def setup_method(self):
        self.mode = SelectedTextMode(min_selection_tokens=50, max_selection_tokens=4000)

    def test_empty_selection_refused(self):
        result = self.mode.validate_selection({"selected_text": ""})
        assert result["is_valid"] is False
        assert result["reason"] == "empty_selection"

    def test_too_short_selection_refused(self):
        # ~10 characters → ~2 tokens
        result = self.mode.validate_selection({"selected_text": "Hello."})
        assert result["is_valid"] is False
        assert result["reason"] == "too_short"

    def test_valid_selection_accepted(self):
        # 300 chars → ~75 tokens — above the 50-token minimum
        text = "x " * 150
        result = self.mode.validate_selection({"selected_text": text})
        assert result["is_valid"] is True

    def test_too_long_selection_refused(self):
        # 20,000 chars → ~5,000 tokens — above 4,000 max
        text = "x " * 10000
        result = self.mode.validate_selection({"selected_text": text})
        assert result["is_valid"] is False
        assert result["reason"] == "too_long"

    def test_zero_vector_searches_in_metadata(self):
        text = "x " * 150
        result = self.mode.process_query("What does this mean?", {"selected_text": text})
        assert result["metadata"]["vector_searches_performed"] == 0


# ============================================================
# BookOnlyMode boundary enforcement (smoke)
# ============================================================

class TestBookOnlyModeBoundary:
    def setup_method(self):
        # Patch the services BookOnlyMode depends on
        self.embedding_patch = patch("services.modes.book_only.get_query_embedding_service")
        self.retrieval_patch = patch("services.modes.book_only.get_retrieval_service")
        self.grounding_patch = patch("services.modes.book_only.get_grounding_service")
        self.citation_patch = patch("services.modes.book_only.get_citation_service")

        self.embedding_patch.start()
        self.retrieval_patch.start()
        self.grounding_patch.start()
        self.citation_patch.start()

        self.mode = BookOnlyMode(
            min_retrieval_score=0.7,
            min_grounding_ratio=0.8,
        )

    def teardown_method(self):
        self.embedding_patch.stop()
        self.retrieval_patch.stop()
        self.grounding_patch.stop()
        self.citation_patch.stop()

    @pytest.mark.asyncio
    async def test_refuses_empty_chunks(self):
        should_refuse, reason = await self.mode.should_refuse("test query", [])
        assert should_refuse is True
        assert reason == "No relevant content found in textbook"

    @pytest.mark.asyncio
    async def test_refuses_low_score_chunks(self):
        chunks = [{"score": 0.3, "rerank_score": 0.3, "text": "x " * 100}]
        should_refuse, _ = await self.mode.should_refuse("test query", chunks)
        assert should_refuse is True

    @pytest.mark.asyncio
    async def test_accepts_good_chunks(self):
        chunks = [{"score": 0.9, "rerank_score": 0.9, "text": "x " * 100}]
        should_refuse, _ = await self.mode.should_refuse("test query", chunks)
        assert should_refuse is False


# ============================================================
# VALID_MODES set
# ============================================================

class TestValidModesSet:
    def test_contains_three_modes(self):
        assert len(VALID_MODES) == 3

    def test_contains_expected_modes(self):
        assert "book_only" in VALID_MODES
        assert "selected_text" in VALID_MODES
        assert "general_knowledge" in VALID_MODES

    def test_does_not_contain_legacy_modes(self):
        assert "guided" not in VALID_MODES
        assert "exploratory" not in VALID_MODES
