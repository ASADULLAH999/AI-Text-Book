/**
 * useTone Hook
 * T083 [US4] — Manages tone state with localStorage persistence.
 *
 * Unlike mode (sessionStorage, session-scoped), tone is a user preference
 * that persists across sessions via localStorage.
 */

import { useState, useCallback } from 'react';
import { Tone, DEFAULT_TONE } from '../types/tone';

const LOCAL_STORAGE_TONE_KEY = 'chatbot_tone';

/**
 * Read tone preference from localStorage.
 * Falls back to DEFAULT_TONE (Neutral) if not set or invalid.
 */
function readToneFromStorage(): Tone {
  try {
    const stored = localStorage.getItem(LOCAL_STORAGE_TONE_KEY);
    if (stored && Object.values(Tone).includes(stored as Tone)) {
      return stored as Tone;
    }
  } catch {
    // localStorage unavailable (SSR / private browsing edge cases)
  }
  return DEFAULT_TONE;
}

/**
 * Persist tone preference to localStorage.
 */
function writeToneToStorage(tone: Tone): void {
  try {
    localStorage.setItem(LOCAL_STORAGE_TONE_KEY, tone);
  } catch {
    // Ignore write failures silently
  }
}

/**
 * useTone hook return type
 */
export interface UseToneReturn {
  currentTone: Tone;
  setTone: (tone: Tone) => void;
}

/**
 * useTone — manages tone preference with localStorage persistence.
 */
export function useTone(): UseToneReturn {
  const [currentTone, setToneState] = useState<Tone>(readToneFromStorage);

  const setTone = useCallback((tone: Tone) => {
    writeToneToStorage(tone);
    setToneState(tone);
  }, []);

  return { currentTone, setTone };
}
