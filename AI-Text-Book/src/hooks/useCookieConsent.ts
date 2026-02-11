import { useState, useEffect, useCallback } from 'react';
import {
  CookiePreferences,
  CookieConsentState,
  DEFAULT_COOKIE_PREFERENCES,
  COOKIE_CONSENT_KEY,
  COOKIE_CONSENT_EXPIRY_DAYS,
} from '../types/cookie';

export function useCookieConsent() {
  const [state, setState] = useState<CookieConsentState>({
    hasConsent: false,
    preferences: null,
    showBanner: false,
    showPreferencesModal: false,
  });

  // Load preferences from localStorage on mount
  useEffect(() => {
    const loadPreferences = () => {
      try {
        const stored = localStorage.getItem(COOKIE_CONSENT_KEY);
        if (stored) {
          const preferences: CookiePreferences = JSON.parse(stored);

          // Check if consent is still valid (within expiry period)
          const consentDate = new Date(preferences.consentTimestamp);
          const now = new Date();
          const daysSinceConsent = Math.floor(
            (now.getTime() - consentDate.getTime()) / (1000 * 60 * 60 * 24)
          );

          if (daysSinceConsent <= COOKIE_CONSENT_EXPIRY_DAYS) {
            setState({
              hasConsent: true,
              preferences,
              showBanner: false,
              showPreferencesModal: false,
            });
          } else {
            // Consent expired, show banner again
            setState((prev) => ({
              ...prev,
              showBanner: true,
            }));
          }
        } else {
          // No consent found, show banner
          setState((prev) => ({
            ...prev,
            showBanner: true,
          }));
        }
      } catch (error) {
        console.error('Error loading cookie preferences:', error);
        setState((prev) => ({
          ...prev,
          showBanner: true,
        }));
      }
    };

    loadPreferences();
  }, []);

  // Save preferences to localStorage
  const savePreferences = useCallback((preferences: CookiePreferences) => {
    try {
      localStorage.setItem(COOKIE_CONSENT_KEY, JSON.stringify(preferences));
      setState({
        hasConsent: true,
        preferences,
        showBanner: false,
        showPreferencesModal: false,
      });
    } catch (error) {
      console.error('Error saving cookie preferences:', error);
    }
  }, []);

  // Accept all cookies
  const acceptAll = useCallback(() => {
    const preferences: CookiePreferences = {
      essential: true,
      analytics: true,
      preferences: true,
      consentTimestamp: new Date().toISOString(),
      consentVersion: '1.0',
    };
    savePreferences(preferences);
  }, [savePreferences]);

  // Reject non-essential cookies
  const rejectNonEssential = useCallback(() => {
    const preferences: CookiePreferences = {
      essential: true,
      analytics: false,
      preferences: false,
      consentTimestamp: new Date().toISOString(),
      consentVersion: '1.0',
    };
    savePreferences(preferences);
  }, [savePreferences]);

  // Save custom preferences
  const saveCustomPreferences = useCallback(
    (analytics: boolean, prefs: boolean) => {
      const preferences: CookiePreferences = {
        essential: true, // Always true
        analytics,
        preferences: prefs,
        consentTimestamp: new Date().toISOString(),
        consentVersion: '1.0',
      };
      savePreferences(preferences);
    },
    [savePreferences]
  );

  // Open preferences modal
  const openPreferencesModal = useCallback(() => {
    setState((prev) => ({
      ...prev,
      showPreferencesModal: true,
    }));
  }, []);

  // Close preferences modal
  const closePreferencesModal = useCallback(() => {
    setState((prev) => ({
      ...prev,
      showPreferencesModal: false,
    }));
  }, []);

  // Close banner (without saving - used when user clicks customize)
  const closeBanner = useCallback(() => {
    setState((prev) => ({
      ...prev,
      showBanner: false,
    }));
  }, []);

  return {
    hasConsent: state.hasConsent,
    preferences: state.preferences,
    showBanner: state.showBanner,
    showPreferencesModal: state.showPreferencesModal,
    acceptAll,
    rejectNonEssential,
    saveCustomPreferences,
    openPreferencesModal,
    closePreferencesModal,
    closeBanner,
  };
}
