import { useState, useEffect, useCallback } from 'react';
import { getLocale, setLocale, subscribeLocale, t } from './config.js';

/**
 * React hook to access translations and trigger component re-render on locale switch.
 * @param {string} [namespace=''] - Optional namespace prefix (e.g. 'playground', 'nav')
 */
export function useTranslation(namespace = '') {
  const [currentLocale, setCurrentLocale] = useState(getLocale());

  useEffect(() => {
    const unsubscribe = subscribeLocale(newLocale => {
      setCurrentLocale(newLocale);
    });
    return unsubscribe;
  }, []);

  const translate = useCallback((key, params = {}) => {
    const knownNamespaces = [
      'app', 'nav', 'common', 'playground', 'childModal', 'risk',
      'skills', 'support', 'status', 'safety', 'results', 'evaluation',
      'language_selector', 'probe', 'governance'
    ];
    const parts = key.split('.');
    const fullKey = (namespace && !knownNamespaces.includes(parts[0])) ? `${namespace}.${key}` : key;
    return t(fullKey, params);
  }, [currentLocale, namespace]);

  const resolvedLanguage = (currentLocale === 'si' || currentLocale === 'si-LK') ? 'si' : 'en';

  return {
    t: translate,
    locale: currentLocale,
    resolvedLanguage,
    setLocale
  };
}

export function useLocale() {
  return useTranslation();
}

export default useTranslation;
