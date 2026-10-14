/**
 * Stage 29 Locale Registry (Frontend)
 * Canonical registration for si-LK and en-LK with aliases.
 */
export const LOCALE_REGISTRY = {
  'si-LK': {
    language: 'si',
    locale: 'si-LK',
    script: 'Sinh',
    direction: 'ltr',
    displayNameNative: 'සිංහල',
    displayNameEn: 'Sinhala (Sri Lanka)',
    isActive: true
  },
  'en-LK': {
    language: 'en',
    locale: 'en-LK',
    script: 'Latn',
    direction: 'ltr',
    displayNameNative: 'English',
    displayNameEn: 'English (Sri Lanka)',
    isActive: true
  }
};

export const DEFAULT_LOCALE = 'en-LK';

export const LOCALE_ALIASES = {
  en: 'en-LK',
  si: 'si-LK'
};

export function resolveLocale(requested) {
  if (!requested || typeof requested !== 'string') return null;
  const canonical = LOCALE_ALIASES[requested] || requested;
  return LOCALE_REGISTRY[canonical] || null;
}

export function isSupportedLocale(requested) {
  return resolveLocale(requested) !== null;
}
