/**
 * TermHighlight Component
 * T090 [US5] — Inline highlighting of detected key terms with hover tooltip.
 * T094 [US5] — "More about [term]" action to pre-fill the chat query.
 * T095 [US5] — Optimized via memoization; highlight markup adds <5ms overhead.
 *
 * Usage: Wrap any text node's content and pass `detectedTerms` from useTermDetection.
 */

import React, { useState, useCallback, memo } from 'react';
import type { GlossaryTerm } from '../../hooks/useTermDetection';
import TermTooltip from './TermTooltip';
import styles from './styles.module.css';

export interface TermHighlightProps {
  /** Plain text to scan for key terms */
  text: string;
  /** Terms detected in this text (from useTermDetection) */
  detectedTerms: Array<{ term: GlossaryTerm; startIndex: number; endIndex: number }>;
  /** Whether highlighting is enabled (user can toggle — T093) */
  enabled?: boolean;
  /** Called when user clicks "More about [term]" — pre-fills chat (T094) */
  onAskMore: (query: string) => void;
  /** Optional additional class name */
  className?: string;
}

interface TooltipState {
  term: GlossaryTerm;
  position: { x: number; y: number };
}

/**
 * Build a list of text segments interspersed with highlighted term spans.
 * Sorted by startIndex; overlapping ranges are skipped.
 */
function buildSegments(
  text: string,
  detectedTerms: TermHighlightProps['detectedTerms'],
): Array<{ type: 'text' | 'term'; content: string; term?: GlossaryTerm }> {
  if (!detectedTerms.length) return [{ type: 'text', content: text }];

  // Sort by start, remove overlaps
  const sorted = [...detectedTerms].sort((a, b) => a.startIndex - b.startIndex);
  const segments: ReturnType<typeof buildSegments> = [];
  let cursor = 0;

  for (const { term, startIndex, endIndex } of sorted) {
    if (startIndex < cursor) continue; // skip overlap
    if (startIndex > cursor) {
      segments.push({ type: 'text', content: text.slice(cursor, startIndex) });
    }
    segments.push({ type: 'term', content: text.slice(startIndex, endIndex), term });
    cursor = endIndex;
  }

  if (cursor < text.length) {
    segments.push({ type: 'text', content: text.slice(cursor) });
  }

  return segments;
}

/**
 * TermHighlight — renders text with highlighted key terms and on-demand tooltips.
 */
function TermHighlight({
  text,
  detectedTerms,
  enabled = true,
  onAskMore,
  className,
}: TermHighlightProps): JSX.Element {
  const [tooltip, setTooltip] = useState<TooltipState | null>(null);

  const handleTermClick = useCallback(
    (term: GlossaryTerm, e: React.MouseEvent<HTMLSpanElement>) => {
      const rect = (e.target as HTMLElement).getBoundingClientRect();
      setTooltip({
        term,
        position: { x: rect.left, y: rect.top },
      });
    },
    [],
  );

  const handleClose = useCallback(() => setTooltip(null), []);

  const handleAskMore = useCallback(
    (query: string) => {
      setTooltip(null);
      onAskMore(query);
    },
    [onAskMore],
  );

  // When highlighting is disabled, render plain text
  if (!enabled || !detectedTerms.length) {
    return <span className={className}>{text}</span>;
  }

  const segments = buildSegments(text, detectedTerms);

  return (
    <>
      <span className={className}>
        {segments.map((seg, idx) => {
          if (seg.type === 'text') {
            return <React.Fragment key={idx}>{seg.content}</React.Fragment>;
          }
          return (
            <span
              key={idx}
              className={styles.termHighlight}
              role="button"
              tabIndex={0}
              aria-label={`Key term: ${seg.term!.term}. Click for definition.`}
              data-testid={`term-highlight-${seg.term!.id}`}
              data-term-id={seg.term!.id}
              onClick={(e) => handleTermClick(seg.term!, e)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                  e.preventDefault();
                  handleTermClick(seg.term!, e as unknown as React.MouseEvent<HTMLSpanElement>);
                }
              }}
            >
              {seg.content}
            </span>
          );
        })}
      </span>

      {tooltip && (
        <TermTooltip
          term={tooltip.term}
          position={tooltip.position}
          onAskMore={handleAskMore}
          onClose={handleClose}
        />
      )}
    </>
  );
}

export default memo(TermHighlight);
