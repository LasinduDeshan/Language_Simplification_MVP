/**
 * Stage 36 i18n configuration and text resolution service.
 * Supports canonical application locales ('en', 'si') and regional identifiers ('en-LK', 'si-LK').
 */
import enTranslations from './en.json' with { type: 'json' };
import siTranslations from './si.json' with { type: 'json' };
import { getStoredLocalePreference, setStoredLocalePreference } from './storagePolicy.js';
import { resolveLocale, DEFAULT_LOCALE } from './localeRegistry.js';

export const SUPPORTED_LOCALES = ['en', 'si', 'en-LK', 'si-LK'];

const TRANSLATIONS = {
  'en-LK': enTranslations,
  'si-LK': siTranslations,
  'en': enTranslations,
  'si': siTranslations
};

let currentLocale = getStoredLocalePreference();
const listeners = new Set();

export function getLocale() {
  return currentLocale;
}

export function setLocale(newLocale) {
  if (!SUPPORTED_LOCALES.includes(newLocale)) {
    console.warn(`[i18n] Cannot switch to unsupported locale: ${newLocale}`);
    return;
  }

  const resolved = resolveLocale(newLocale);
  if (!resolved) {
    console.warn(`[i18n] Cannot resolve locale: ${newLocale}`);
    return;
  }

  currentLocale = resolved.locale;
  setStoredLocalePreference(currentLocale);

  // Synchronize localStorage with both app.locale and app_locale_preference
  try {
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('app.locale', resolved.language);
      localStorage.setItem('app_locale_preference', resolved.locale);
    }
  } catch (err) {
    console.warn('[i18n] Error syncing localStorage:', err);
  }

  // Update DOM language attributes
  if (typeof document !== 'undefined') {
    document.documentElement.lang = resolved.language === 'si' ? 'si-LK' : 'en-LK';
    document.documentElement.setAttribute('data-locale', resolved.locale);
    document.documentElement.dir = resolved.direction;
  }

  // Notify listeners
  listeners.forEach(cb => cb(currentLocale));
}

export function subscribeLocale(callback) {
  listeners.add(callback);
  return () => listeners.delete(callback);
}

/**
 * Nested key lookup with automatic fallback to default English.
 */
export function t(key, params = {}, localeOverride = null) {
  const activeLocale = localeOverride || currentLocale;
  const dict = TRANSLATIONS[activeLocale] || TRANSLATIONS[DEFAULT_LOCALE];
  const defaultDict = TRANSLATIONS[DEFAULT_LOCALE];

  const resolvePath = (obj, path) => {
    return path.split('.').reduce((prev, curr) => (prev && prev[curr] !== undefined) ? prev[curr] : undefined, obj);
  };

  let val = resolvePath(dict, key);
  if (val === undefined && dict !== defaultDict) {
    val = resolvePath(defaultDict, key);
  }

  if (val === undefined) {
    return key;
  }

  if (typeof val === 'string') {
    // Support both {param} and {{param}} syntax
    return Object.entries(params).reduce((str, [k, v]) => {
      return str.replace(new RegExp(`\\{\\{${k}\\}\\}|\\{${k}\\}`, 'g'), v);
    }, val);
  }

  return val;
}

// Initial DOM sync on load
if (typeof document !== 'undefined') {
  const initial = resolveLocale(currentLocale) || resolveLocale(DEFAULT_LOCALE);
  document.documentElement.lang = initial.language === 'si' ? 'si-LK' : 'en-LK';
  document.documentElement.setAttribute('data-locale', initial.locale);
  document.documentElement.dir = initial.direction;
}
