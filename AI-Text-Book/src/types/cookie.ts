export interface CookiePreferences {
  essential: boolean; // Always true
  analytics: boolean;
  preferences: boolean;
  consentTimestamp: string; // ISO 8601 format
  consentVersion: string; // e.g., "1.0"
}

export interface CookieConsentState {
  hasConsent: boolean;
  preferences: CookiePreferences | null;
  showBanner: boolean;
  showPreferencesModal: boolean;
}

export const DEFAULT_COOKIE_PREFERENCES: CookiePreferences = {
  essential: true,
  analytics: false,
  preferences: false,
  consentTimestamp: new Date().toISOString(),
  consentVersion: '1.0',
};

export const COOKIE_CONSENT_KEY = 'cookie-consent-preferences';
export const COOKIE_CONSENT_EXPIRY_DAYS = 90;
