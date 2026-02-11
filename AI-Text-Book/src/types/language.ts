export type Locale = 'en' | 'ur' | 'ar' | 'zh' | 'es';

export interface LocaleConfig {
  code: Locale;
  label: string;
  dir: 'ltr' | 'rtl';
  flag?: string;
}

export interface LanguagePreferences {
  locale: Locale;
  updated_at: number;
}

export interface Translations {
  [key: string]: string | Translations;
}

export interface LanguageState {
  current_locale: Locale;
  available_locales: Locale[];
  is_rtl: boolean;
  translations?: Translations;
}
