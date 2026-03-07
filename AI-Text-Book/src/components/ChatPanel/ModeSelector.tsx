/**
 * ModeSelector Component
 * T069 [US3] — Three mode buttons for switching chat answering modes.
 * T073 [US3] — Mode indicator UI with color coding:
 *   Book-Only: blue | Selected-Text: purple | General Knowledge: amber
 */

import React from 'react';
import { Mode, MODE_CONFIGS } from '../../types/mode';
import styles from './styles.module.css';

export interface ModeSelectorProps {
  /** Currently active mode */
  currentMode: Mode;
  /** Callback when user switches mode */
  onModeChange: (mode: Mode) => void;
  /** Whether selector is disabled (e.g. during streaming) */
  disabled?: boolean;
}

/** Color tokens per mode — T073 */
const MODE_COLORS: Record<Mode, string> = {
  [Mode.BOOK_ONLY]: 'blue',
  [Mode.SELECTED_TEXT]: 'purple',
  [Mode.GENERAL_KNOWLEDGE]: 'amber',
};

/**
 * ModeSelector — Button group for switching between the three answering modes.
 */
export default function ModeSelector({
  currentMode,
  onModeChange,
  disabled = false,
}: ModeSelectorProps): JSX.Element {
  return (
    <div className={styles.modeSelectorButtons} role="group" aria-label="Answering mode">
      {Object.values(Mode).map((mode) => {
        const config = MODE_CONFIGS[mode];
        const isActive = mode === currentMode;
        const color = MODE_COLORS[mode];

        return (
          <button
            key={mode}
            type="button"
            onClick={() => !disabled && onModeChange(mode)}
            disabled={disabled}
            aria-pressed={isActive}
            title={config.description}
            className={`${styles.modeSelectorBtn} ${styles[`modeSelectorBtn_${color}`]} ${
              isActive ? styles.modeSelectorBtnActive : ''
            }`}
            data-testid={`mode-btn-${mode}`}
          >
            <span className={styles.modeSelectorIcon}>{config.icon}</span>
            <span className={styles.modeSelectorLabel}>{config.label}</span>
          </button>
        );
      })}
    </div>
  );
}

/**
 * ModeBadge — Compact indicator showing the current mode with its color.
 * T073 [US3]
 */
export function ModeBadge({ mode }: { mode: Mode }): JSX.Element {
  const config = MODE_CONFIGS[mode];
  const color = MODE_COLORS[mode];
  return (
    <span
      className={`${styles.modeBadge} ${styles[`modeBadge_${color}`]}`}
      data-testid="mode-badge"
      aria-label={`Current mode: ${config.label}`}
    >
      {config.icon} {config.label}
    </span>
  );
}
