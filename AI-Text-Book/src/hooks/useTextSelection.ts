/**
 * useTextSelection Hook
 * T057 [US2] — Detects text selection within 100ms, validates boundaries,
 * and provides selection context for the "Ask AI about this" feature.
 */

import { useState, useEffect, useCallback, useRef } from 'react';

/** Approximate characters per token (used for boundary validation) */
const CHARS_PER_TOKEN = 4;

/** Minimum tokens for a valid selection (50 tokens ≈ 200 chars) */
const MIN_TOKENS = 50;

/** Maximum tokens for a valid selection (4,000 tokens ≈ 16,000 chars) */
const MAX_TOKENS = 4000;

const MIN_CHARS = MIN_TOKENS * CHARS_PER_TOKEN;
const MAX_CHARS = MAX_TOKENS * CHARS_PER_TOKEN;

/** Detection debounce — stay under 100ms budget */
const DEBOUNCE_MS = 80;

export interface TextSelectionPosition {
  /** X coordinate for menu anchor (end of selection) */
  x: number;
  /** Y coordinate for menu anchor (top of selection bounding box) */
  y: number;
}

export interface TextSelection {
  /** The selected text */
  text: string;
  /** Approximate token count */
  tokenCount: number;
  /** Whether selection meets the 50–4,000 token boundary */
  isValid: boolean;
  /** Reason when isValid === false */
  invalidReason?: 'too_short' | 'too_long';
  /** Position info for contextual menu placement */
  position: TextSelectionPosition;
  /** The DOM Range for the selection */
  range?: Range;
}

export interface UseTextSelectionReturn {
  /** Current selection, or null when nothing is selected */
  selection: TextSelection | null;
  /** Clear the current selection programmatically */
  clearSelection: () => void;
  /** Whether a selection is active and valid */
  hasValidSelection: boolean;
}

/**
 * Estimate token count from character count (rough approximation).
 * For exact counts a proper tokenizer should be used;
 * this approximation is sufficient for UI boundary validation.
 */
function estimateTokens(text: string): number {
  return Math.ceil(text.trim().length / CHARS_PER_TOKEN);
}

/**
 * Validate token count against the 50–4,000 boundary.
 */
function validateBoundary(
  tokenCount: number,
): { isValid: boolean; reason?: 'too_short' | 'too_long' } {
  if (tokenCount < MIN_TOKENS) {
    return { isValid: false, reason: 'too_short' };
  }
  if (tokenCount > MAX_TOKENS) {
    return { isValid: false, reason: 'too_long' };
  }
  return { isValid: true };
}

/**
 * Get anchor position for the selection menu.
 * Returns coordinates relative to the viewport.
 */
function getSelectionPosition(range: Range): TextSelectionPosition {
  const rect = range.getBoundingClientRect();
  return {
    x: rect.right + window.scrollX,
    y: rect.top + window.scrollY,
  };
}

/**
 * useTextSelection
 *
 * Listens for selectionchange events, debounces within 80ms (under 100ms budget),
 * validates boundary constraints, and returns structured selection state.
 *
 * @param containerRef - Optional ref to constrain selection detection to a
 *   specific DOM container. When omitted, the whole document is monitored.
 */
export function useTextSelection(
  containerRef?: React.RefObject<HTMLElement>,
): UseTextSelectionReturn {
  const [selection, setSelection] = useState<TextSelection | null>(null);
  const debounceTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const clearSelection = useCallback(() => {
    setSelection(null);
    window.getSelection()?.removeAllRanges();
  }, []);

  const handleSelectionChange = useCallback(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      const domSelection = window.getSelection();

      if (
        !domSelection ||
        domSelection.isCollapsed ||
        domSelection.rangeCount === 0
      ) {
        setSelection(null);
        return;
      }

      const range = domSelection.getRangeAt(0);
      const text = domSelection.toString().trim();

      if (!text) {
        setSelection(null);
        return;
      }

      // If a container is provided, check that the selection is inside it
      if (containerRef?.current) {
        const container = containerRef.current;
        if (
          !container.contains(range.commonAncestorContainer)
        ) {
          setSelection(null);
          return;
        }
      }

      const tokenCount = estimateTokens(text);
      const { isValid, reason } = validateBoundary(tokenCount);
      const position = getSelectionPosition(range);

      setSelection({
        text,
        tokenCount,
        isValid,
        invalidReason: reason,
        position,
        range,
      });
    }, DEBOUNCE_MS);
  }, [containerRef]);

  // Clear selection on mousedown (user starting a new selection)
  const handleMouseDown = useCallback(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }
    setSelection(null);
  }, []);

  useEffect(() => {
    document.addEventListener('selectionchange', handleSelectionChange);
    document.addEventListener('mousedown', handleMouseDown);

    return () => {
      document.removeEventListener('selectionchange', handleSelectionChange);
      document.removeEventListener('mousedown', handleMouseDown);
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [handleSelectionChange, handleMouseDown]);

  return {
    selection,
    clearSelection,
    hasValidSelection: selection?.isValid === true,
  };
}

export { MIN_TOKENS, MAX_TOKENS, MIN_CHARS, MAX_CHARS, DEBOUNCE_MS };
