import { test, describe, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { getLocale, setLocale, subscribeLocale, t } from '../../i18n/config.js';
import { getStoredLocalePreference, setStoredLocalePreference } from '../../i18n/storagePolicy.js';

// Polyfill minimal localStorage for Node test runner
const storageMap = new Map();
global.localStorage = {
  getItem: (key) => storageMap.get(key) || null,
  setItem: (key, val) => storageMap.set(key, String(val)),
  removeItem: (key) => storageMap.delete(key),
  clear: () => storageMap.clear()
};

describe('Locale Switching, Persistence and Parameter Interpolation Tests (Plan §12.2, §12.5, §12.7)', () => {
  beforeEach(() => {
    // Reset to en before each test
    setLocale('en');
  });

  test('default locale is en or en-LK and resolves English translations', () => {
    assert.match(getLocale(), /^en(-LK)?$/);
    const title = t('playground.headerTitle');
    assert.equal(title, 'Guided Instructional Playground');
  });

  test('switches locale to Sinhala (si / si-LK) and updates resolved translations', () => {
    setLocale('si');
    assert.match(getLocale(), /^si(-LK)?$/);

    const title = t('playground.headerTitle');
    assert.equal(title, 'මඟපෙන්වන අධ්‍යාපනික පිටිය');

    const learnerProfile = t('playground.learnerProfile');
    assert.equal(learnerProfile, 'ඉගෙනුම්කරුගේ පැතිකඩ');
  });

  test('notifies subscribers on language change without full reload', () => {
    let notifiedLocale = null;
    const unsubscribe = subscribeLocale(loc => {
      notifiedLocale = loc;
    });

    setLocale('si');
    assert.match(notifiedLocale, /^si(-LK)?$/);

    setLocale('en');
    assert.match(notifiedLocale, /^en(-LK)?$/);

    unsubscribe();
  });

  test('persists selected locale preference in storage policy', () => {
    setLocale('si');
    const stored = getStoredLocalePreference();
    assert.match(stored, /^si(-LK)?$/);
  });

  test('parameter interpolation works correctly for {param} and {{param}} syntax in both locales', () => {
    // English
    setLocale('en');
    const enAttempt = t('playground.attemptCounter', { current: 2, total: 3 });
    assert.equal(enAttempt, 'Attempt 2 of 3');

    // Sinhala
    setLocale('si');
    const siAttempt = t('playground.attemptCounter', { current: 2, total: 3 });
    assert.equal(siAttempt, 'උත්සාහය 2 / 3');
  });

  test('reverts cleanly to English with zero regression', () => {
    setLocale('si');
    assert.match(getLocale(), /^si(-LK)?$/);

    setLocale('en');
    assert.match(getLocale(), /^en(-LK)?$/);

    const title = t('playground.headerTitle');
    assert.equal(title, 'Guided Instructional Playground');

    const brand = t('nav.brandTitle');
    assert.equal(brand, 'Adaptive Language MVP');
  });

  test('rejects unsupported locales and preserves existing state', () => {
    setLocale('si');
    setLocale('unsupported_es');
    assert.match(getLocale(), /^si(-LK)?$/);
  });
});
