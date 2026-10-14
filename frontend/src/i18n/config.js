/**
 * Stage 29 i18n configuration and text resolution service.
 */
import enTranslations from './en.json';
import siTranslations from './si.json';
import { getStoredLocalePreference, setStoredLocalePreference } from './storagePolicy.js';
import { resolveLocale, DEFAULT_LOCALE } from './localeRegistry.js';

const TRANSLATIONS = {
  'en-LK': enTranslations,
  'si-LK': siTranslations
};

let currentLocale = getStoredLocalePreference();
const listeners = new Set();

export function getLocale() {
  return currentLocale;
}

export function setLocale(newLocale) {
  const resolved = resolveLocale(newLocale);
  if (!resolved) {
    console.warn(`[i18n] Cannot switch to unsupported locale: ${newLocale}`);
    return;
  }

  currentLocale = resolved.locale;
  setStoredLocalePreference(currentLocale);

  // Update DOM language attributes
  if (typeof document !== 'undefined') {
    document.documentElement.lang = resolved.language;
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
export function t(key, params = {}) {
  const dict = TRANSLATIONS[currentLocale] || TRANSLATIONS[DEFAULT_LOCALE];
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
    return Object.entries(params).reduce((str, [k, v]) => str.replace(`{${k}}`, v), val);
  }

  return val;
}

// Initial DOM sync on load
if (typeof document !== 'undefined') {
  const initial = resolveLocale(currentLocale) || resolveLocale(DEFAULT_LOCALE);
  document.documentElement.lang = initial.language;
  document.documentElement.setAttribute('data-locale', initial.locale);
  document.documentElement.dir = initial.direction;
}
