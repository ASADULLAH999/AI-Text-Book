/**
 * TermTooltip Component
 * T091 [US5] — Hover tooltip displaying a key term's definition.
 *
 * Shown when a user hovers (desktop) or taps (mobile) a highlighted term.
 * Includes a "More about [term]" action that pre-fills the chatbot query (T094).
 */

import React, { useRef, useEffect } from 'react';
import type { GlossaryTerm } from '../../hooks/useTermDetection';
import styles from './styles.module.css';

export interface TermTooltipProps {
  /** The term whose definition is shown */
  term: GlossaryTerm;
  /** Position relative to the highlighted word */
  position: { x: number; y: number };
  /** Called when user clicks "More about [term]" — pre-fills the chat query (T094) */
  onAskMore: (query: string) => void;
  /** Called when tooltip should close */
  onClose: () => void;
}

/**
 * TermTooltip — floating definition card anchored near a highlighted term.
 */
export default function TermTooltip({
  term,
  position,
  onAskMore,
  onClose,
}: TermTooltipProps): JSX.Element {
  const tooltipRef = useRef<HTMLDivElement>(null);

  // Close on outside click or Escape
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (tooltipRef.current && !tooltipRef.current.contains(e.target as Node)) {
        onClose();
      }
    };
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };

    document.addEventListener('mousedown', handleClickOutside, true);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside, true);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [onClose]);

  // Clamp to viewport width
  const left = Math.min(position.x, window.innerWidth - 320);
  const top = position.y - 8; // above the word

  const tooltipStyle: React.CSSProperties = {
    position: 'fixed',
    left,
    top,
    transform: 'translateY(-100%)',
    zIndex: 9998,
  };

  return (
    <div
      ref={tooltipRef}
      style={tooltipStyle}
      className={styles.termTooltip}
      role="tooltip"
      aria-label={`Definition of ${term.term}`}
      data-testid="term-tooltip"
    >
      {/* Header */}
      <div className={styles.termTooltipHeader}>
        <span className={styles.termTooltipIcon}>📚</span>
        <span className={styles.termTooltipTitle}>{term.term}</span>
        {term.category && (
          <span className={styles.termTooltipCategory}>{term.category}</span>
        )}
        <button
          className={styles.termTooltipClose}
          onClick={onClose}
          aria-label="Close definition"
          data-testid="term-tooltip-close"
        >
          ×
        </button>
      </div>

      {/* Definition */}
      <p className={styles.termTooltipDefinition}>{term.definition}</p>

      {/* Related terms */}
      {term.related && term.related.length > 0 && (
        <div className={styles.termTooltipRelated}>
          <span className={styles.termTooltipRelatedLabel}>Related: </span>
          {term.related.slice(0, 4).join(', ')}
        </div>
      )}

      {/* T094 — "More about [term]" action */}
      <button
        className={styles.termTooltipAskMore}
        onClick={() => onAskMore(`Tell me more about ${term.term}`)}
        data-testid="term-ask-more"
        aria-label={`Open chatbot with a question about ${term.term}`}
      >
        ✨ More about {term.term}
      </button>
    </div>
  );
}
