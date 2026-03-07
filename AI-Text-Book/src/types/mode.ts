/**
 * Chat Mode Types
 * Defines the three answering modes for the chatbot (US3 — Phase 5).
 */

/**
 * Answering mode for the chatbot.
 * Three modes match backend services in api/src/services/modes/.
 */
export enum Mode {
  /** Strictly from textbook content only (blue) */
  BOOK_ONLY = 'book_only',
  /** Answers derived solely from user-selected text passage (purple) */
  SELECTED_TEXT = 'selected_text',
  /** Broader exploration using general knowledge (amber) */
  GENERAL_KNOWLEDGE = 'general_knowledge',
}

/**
 * Mode configuration
 */
export interface ModeConfig {
  mode: Mode;
  label: string;
  description: string;
  icon: string;
  requiresTextbook: boolean;
  allowsExternalSources: boolean;
}

/**
 * Mode configurations map
 */
export const MODE_CONFIGS: Record<Mode, ModeConfig> = {
  [Mode.BOOK_ONLY]: {
    mode: Mode.BOOK_ONLY,
    label: 'Book Only',
    description: 'Answers derived exclusively from textbook content with citations',
    icon: '📚',
    requiresTextbook: true,
    allowsExternalSources: false,
  },
  [Mode.SELECTED_TEXT]: {
    mode: Mode.SELECTED_TEXT,
    label: 'Selected Text',
    description: 'Answers derived solely from the text passage you highlighted',
    icon: '🎯',
    requiresTextbook: false,
    allowsExternalSources: false,
  },
  [Mode.GENERAL_KNOWLEDGE]: {
    mode: Mode.GENERAL_KNOWLEDGE,
    label: 'General Knowledge',
    description: 'Broader exploration beyond the textbook using general knowledge',
    icon: '🌐',
    requiresTextbook: false,
    allowsExternalSources: true,
  },
};

/**
 * Get mode configuration by mode value
 */
export function getModeConfig(mode: Mode): ModeConfig {
  return MODE_CONFIGS[mode];
}

/**
 * Check if mode requires textbook content
 */
export function requiresTextbook(mode: Mode): boolean {
  return MODE_CONFIGS[mode].requiresTextbook;
}

/**
 * Check if mode allows external sources
 */
export function allowsExternalSources(mode: Mode): boolean {
  return MODE_CONFIGS[mode].allowsExternalSources;
}
