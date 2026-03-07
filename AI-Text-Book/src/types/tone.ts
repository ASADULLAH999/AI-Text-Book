/**
 * Response Tone Types
 * T082 [US4] — Tone enum and configuration for customising chatbot language style.
 *
 * Tone affects language style ONLY — citations and factual accuracy are never altered.
 * Persisted in localStorage so preference survives across sessions.
 */

/**
 * Available response tones.
 * These values are sent to the backend and must match api/src/services/prompts/tone_modifiers.py.
 */
export enum Tone {
  /** Balanced default — no special style applied */
  NEUTRAL = 'neutral',
  /** Formal academic language with precise terminology */
  ACADEMIC = 'academic',
  /** Plain language with analogies for beginners */
  BEGINNER_FRIENDLY = 'beginner_friendly',
  /** Brief, direct answers with minimal elaboration */
  CONCISE = 'concise',
  /** Comprehensive explanations with examples */
  DETAILED = 'detailed',
}

/**
 * Tone configuration object
 */
export interface ToneConfig {
  tone: Tone;
  label: string;
  description: string;
  icon: string;
}

/**
 * Tone configurations map
 */
export const TONE_CONFIGS: Record<Tone, ToneConfig> = {
  [Tone.NEUTRAL]: {
    tone: Tone.NEUTRAL,
    label: 'Neutral',
    description: 'Balanced, default response style',
    icon: '⚖️',
  },
  [Tone.ACADEMIC]: {
    tone: Tone.ACADEMIC,
    label: 'Academic',
    description: 'Formal language with precise terminology',
    icon: '🎓',
  },
  [Tone.BEGINNER_FRIENDLY]: {
    tone: Tone.BEGINNER_FRIENDLY,
    label: 'Beginner-Friendly',
    description: 'Plain language with analogies and examples',
    icon: '🌱',
  },
  [Tone.CONCISE]: {
    tone: Tone.CONCISE,
    label: 'Concise',
    description: 'Brief, direct answers with minimal elaboration',
    icon: '⚡',
  },
  [Tone.DETAILED]: {
    tone: Tone.DETAILED,
    label: 'Detailed',
    description: 'Comprehensive explanations with context and examples',
    icon: '📖',
  },
};

/** Default tone — used on new sessions and as fallback */
export const DEFAULT_TONE: Tone = Tone.NEUTRAL;

/**
 * Get tone configuration by tone value
 */
export function getToneConfig(tone: Tone): ToneConfig {
  return TONE_CONFIGS[tone];
}
