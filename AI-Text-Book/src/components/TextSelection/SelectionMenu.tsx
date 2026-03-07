/**
 * SelectionMenu Component
 * T058 [US2] — Contextual menu shown when text is selected.
 * T059 [US2] — "Ask AI about this" button with ≤200ms display latency.
 */

import React, { useEffect, useRef, useCallback } from 'react';
import { TextSelection } from '../../hooks/useTextSelection';
import styles from './styles.module.css';

export interface SelectionMenuProps {
  /** The active text selection. null hides the menu. */
  selection: TextSelection | null;
  /** Callback when "Ask AI about this" is triggered */
  onAskAI: (selectedText: string) => void;
  /** Callback when the menu is dismissed */
  onDismiss: () => void;
}

/**
 * SelectionMenu
 *
 * Renders a floating contextual menu anchored to the end of a text selection.
 * Appears within 200ms of selection (handled by useTextSelection's 80ms debounce
 * + near-instant React render).
 *
 * Shows validation feedback when the selection is outside the 50–4,000 token range.
 */
export default function SelectionMenu({
  selection,
  onAskAI,
  onDismiss,
}: SelectionMenuProps): JSX.Element | null {
  const menuRef = useRef<HTMLDivElement>(null);

  const handleAskAI = useCallback(() => {
    if (selection?.isValid && selection.text) {
      onAskAI(selection.text);
      onDismiss();
    }
  }, [selection, onAskAI, onDismiss]);

  // Close menu on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        onDismiss();
      }
    };

    if (selection) {
      // Use capture to catch clicks before they deselect text
      document.addEventListener('mousedown', handleClickOutside, true);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside, true);
    };
  }, [selection, onDismiss]);

  // Close menu on Escape
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onDismiss();
      }
    };

    if (selection) {
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [selection, onDismiss]);

  if (!selection) {
    return null;
  }

  const { position, isValid, invalidReason, tokenCount } = selection;

  // Position the menu slightly above and to the right of the selection end
  const menuStyle: React.CSSProperties = {
    position: 'fixed',
    left: Math.min(position.x, window.innerWidth - 200),
    top: position.y - 48, // Appear above the selection
    zIndex: 9999,
  };

  const invalidMessage =
    !isValid && invalidReason === 'too_short'
      ? `Selection too short (${tokenCount} tokens, min 50)`
      : !isValid && invalidReason === 'too_long'
      ? `Selection too long (${tokenCount} tokens, max 4,000)`
      : null;

  return (
    <div
      ref={menuRef}
      style={menuStyle}
      className={styles.selectionMenu}
      role="menu"
      aria-label="Text selection actions"
      data-testid="selection-menu"
    >
      {isValid ? (
        <button
          className={styles.askAIButton}
          onClick={handleAskAI}
          role="menuitem"
          data-testid="ask-ai-button"
          aria-label="Ask AI about the selected text"
          title="Ask AI about this selection"
        >
          <span className={styles.askAIIcon} aria-hidden="true">✨</span>
          Ask AI about this
        </button>
      ) : (
        <div className={styles.invalidSelection} role="menuitem" aria-disabled="true">
          <span className={styles.invalidIcon} aria-hidden="true">⚠️</span>
          <span className={styles.invalidText}>{invalidMessage}</span>
        </div>
      )}
    </div>
  );
}
