/**
 * TermHighlightToggle Component
 * T093 [US5] — Toggle switch for enabling/disabling key term highlighting.
 *
 * Renders a labeled toggle that persists the user's preference via
 * useTermDetection (localStorage-backed).
 */

import React from 'react';
import styles from './styles.module.css';

export interface TermHighlightToggleProps {
  /** Current highlighting state */
  enabled: boolean;
  /** Called when user flips the toggle */
  onToggle: () => void;
}

/**
 * TermHighlightToggle — accessible checkbox styled as a toggle switch.
 */
export default function TermHighlightToggle({
  enabled,
  onToggle,
}: TermHighlightToggleProps): JSX.Element {
  return (
    <label
      className={styles.termHighlightToggle}
      data-testid="term-highlight-toggle"
      aria-label={`Key term highlighting is ${enabled ? 'on' : 'off'}`}
    >
      <input
        type="checkbox"
        checked={enabled}
        onChange={onToggle}
        className={styles.termHighlightToggleInput}
        data-testid="term-highlight-toggle-input"
        aria-checked={enabled}
      />
      <span>Highlight key terms</span>
    </label>
  );
}
