import React, { createContext, useContext, useCallback } from 'react';
import { Locale } from '../types/language';
import { CookiePreferences } from '../types/entities';
import { useLocalStorage } from '../hooks/useLocalStorage';

interface AppState {
  language: Locale;
  theme: 'light' | 'dark';
  cookiePreferences: CookiePreferences;
  sidebarOpen: boolean;
}

interface AppStateContextType {
  state: AppState;
  setLanguage: (locale: Locale) => void;
  setTheme: (theme: 'light' | 'dark') => void;
  setCookiePreferences: (prefs: CookiePreferences) => void;
  setSidebarOpen: (open: boolean) => void;
}

const AppStateContext = createContext<AppStateContextType | undefined>(undefined);

const DEFAULT_APP_STATE: AppState = {
  language: 'en',
  theme: 'dark',
  cookiePreferences: {
    essential: true,
    analytics: false,
    preferences: false,
    timestamp: Date.now(),
  },
  sidebarOpen: true,
};

export const AppStateProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, setState] = useLocalStorage<AppState>('app_state', DEFAULT_APP_STATE);

  const setLanguage = useCallback(
    (locale: Locale) => {
      setState((prev) => ({ ...prev, language: locale }));
      // Update HTML lang attribute
      document.documentElement.lang = locale;
      // Update RTL direction for Arabic/Urdu
      document.documentElement.dir = locale === 'ar' || locale === 'ur' ? 'rtl' : 'ltr';
    },
    [setState]
  );

  const setTheme = useCallback(
    (theme: 'light' | 'dark') => {
      setState((prev) => ({ ...prev, theme }));
      // Update Docusaurus theme
      const html = document.documentElement;
      html.setAttribute('data-theme', theme);
    },
    [setState]
  );

  const setCookiePreferences = useCallback(
    (prefs: CookiePreferences) => {
      setState((prev) => ({ ...prev, cookiePreferences: prefs }));
    },
    [setState]
  );

  const setSidebarOpen = useCallback(
    (open: boolean) => {
      setState((prev) => ({ ...prev, sidebarOpen: open }));
    },
    [setState]
  );

  const value: AppStateContextType = {
    state,
    setLanguage,
    setTheme,
    setCookiePreferences,
    setSidebarOpen,
  };

  return <AppStateContext.Provider value={value}>{children}</AppStateContext.Provider>;
};

export const useAppState = () => {
  const context = useContext(AppStateContext);
  if (context === undefined) {
    throw new Error('useAppState must be used within AppStateProvider');
  }
  return context;
};
