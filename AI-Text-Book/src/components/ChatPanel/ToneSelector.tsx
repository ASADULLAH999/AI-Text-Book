/**
 * ToneSelector Component
 * T081 [US4] — Dropdown for selecting response tone.
 * T082 [US4] — Uses the Tone enum (Academic, Beginner-Friendly, Concise, Detailed, Neutral).
 *
 * Tone affects language style only — citations and accuracy remain unchanged.
 */

import React from 'react';
import { Tone, TONE_CONFIGS, DEFAULT_TONE } from '../../types/tone';
import styles from './styles.module.css';

export interface ToneSelectorProps {
  /** Currently active tone */
  currentTone: Tone;
  /** Callback when user changes tone */
  onToneChange: (tone: Tone) => void;
  /** Whether selector is disabled */
  disabled?: boolean;
}

/**
 * ToneSelector — dropdown for picking response language style.
 */
export default function ToneSelector({
  currentTone,
  onToneChange,
  disabled = false,
}: ToneSelectorProps): JSX.Element {
  const currentConfig = TONE_CONFIGS[currentTone];

  return (
    <div className={styles.toneSelectorWrapper} data-testid="tone-selector">
      <label htmlFor="tone-select" className={styles.toneSelectorLabel}>
        Tone:
      </label>
      <div className={styles.toneSelectorControl}>
        <select
          id="tone-select"
          value={currentTone}
          onChange={(e) => onToneChange(e.target.value as Tone)}
          disabled={disabled}
          className={styles.toneSelectorSelect}
          data-testid="tone-select"
          aria-label="Select response tone"
          title={currentConfig.description}
        >
          {Object.values(Tone).map((tone) => {
            const config = TONE_CONFIGS[tone];
            return (
              <option key={tone} value={tone}>
                {config.icon} {config.label}
              </option>
            );
          })}
        </select>
        <span className={styles.toneSelectorDesc} aria-live="polite">
          {currentConfig.description}
        </span>
      </div>
    </div>
  );
}
