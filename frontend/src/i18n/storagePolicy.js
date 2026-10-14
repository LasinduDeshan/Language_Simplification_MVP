/**
 * Stage 29 Frontend Storage Policy
 * Persists ONLY the locale string. Strictly forbids learner or clinical data.
 */
import { resolveLocale, DEFAULT_LOCALE } from './localeRegistry.js';

export const LOCALE_STORAGE_KEY = 'app_locale_preference';

export function getStoredLocalePreference() {
  try {
    const raw = localStorage.getItem(LOCALE_STORAGE_KEY);
    if (!raw) return DEFAULT_LOCALE;

    // Validate against central registry
    const resolved = resolveLocale(raw);
    if (!resolved) {
      console.warn(`[i18n] Stored locale '${raw}' is unrecognized or corrupted. Falling back to '${DEFAULT_LOCALE}'.`);
      setStoredLocalePreference(DEFAULT_LOCALE);
      return DEFAULT_LOCALE;
    }

    return resolved.locale;
  } catch (err) {
    console.error('[i18n] Storage access error; using default locale:', err);
    return DEFAULT_LOCALE;
  }
}

export function setStoredLocalePreference(locale) {
  try {
    const resolved = resolveLocale(locale);
    const target = resolved ? resolved.locale : DEFAULT_LOCALE;
    localStorage.setItem(LOCALE_STORAGE_KEY, target);
    return target;
  } catch (err) {
    console.error('[i18n] Error setting stored locale:', err);
    return DEFAULT_LOCALE;
  }
}

export function clearStoredLocalePreference() {
  try {
    localStorage.removeItem(LOCALE_STORAGE_KEY);
  } catch (err) {
    console.error('[i18n] Error clearing stored locale:', err);
  }
}
