"""
Chat mode services package.
T077 [US3] — Mode boundary enforcement and router.

The three modes and their invariants:
  book_only       — strict textbook grounding, citations required
  selected_text   — zero vector searches, selection context only
  general_knowledge — soft retrieval, no grounding gate, disclaimer shown
"""

from typing import Literal, Union

from .book_only import BookOnlyMode, get_book_only_mode
from .selected_text import SelectedTextMode, get_selected_text_mode
from .general_knowledge import GeneralKnowledgeMode, get_general_knowledge_mode

# ---------------------------------------------------------------------------
# Allowed mode literals — must match the enum in src/types/mode.ts
# ---------------------------------------------------------------------------

VALID_MODES = frozenset({"book_only", "selected_text", "general_knowledge"})

ModeValue = Literal["book_only", "selected_text", "general_knowledge"]


# ---------------------------------------------------------------------------
# T077 [US3] — Mode boundary enforcement
# ---------------------------------------------------------------------------

class ModeBoundaryError(ValueError):
    """Raised when an invalid or disallowed mode is requested."""


def enforce_mode_boundary(mode: str) -> ModeValue:
    """
    Validate and return the mode string.

    Args:
        mode: Raw mode string from API request.

    Returns:
        Validated mode string (type-narrowed to ModeValue).

    Raises:
        ModeBoundaryError: If mode is not in VALID_MODES.
    """
    if mode not in VALID_MODES:
        raise ModeBoundaryError(
            f"Invalid mode '{mode}'. Must be one of: {sorted(VALID_MODES)}"
        )
    return mode  # type: ignore[return-value]


def get_mode_handler(
    mode: str,
) -> Union[BookOnlyMode, SelectedTextMode, GeneralKnowledgeMode]:
    """
    Return the correct singleton mode handler for the given mode string.

    This is the single routing point — all mode dispatch goes through here
    so boundary violations are caught in one place.

    Args:
        mode: Validated mode string (call enforce_mode_boundary first).

    Returns:
        Mode handler instance.

    Raises:
        ModeBoundaryError: If mode string is unrecognised (second guard).
    """
    validated = enforce_mode_boundary(mode)

    if validated == "book_only":
        return get_book_only_mode()
    if validated == "selected_text":
        return get_selected_text_mode()
    if validated == "general_knowledge":
        return get_general_knowledge_mode()

    # Unreachable — enforce_mode_boundary already raised, but kept for type-safety
    raise ModeBoundaryError(f"No handler registered for mode '{mode}'")


__all__ = [
    # Classes
    "BookOnlyMode",
    "SelectedTextMode",
    "GeneralKnowledgeMode",
    # Singletons
    "get_book_only_mode",
    "get_selected_text_mode",
    "get_general_knowledge_mode",
    # Boundary enforcement
    "VALID_MODES",
    "ModeValue",
    "ModeBoundaryError",
    "enforce_mode_boundary",
    "get_mode_handler",
]
