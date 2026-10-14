import { test, describe, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import {
  getStoredLocalePreference,
  setStoredLocalePreference,
  clearStoredLocalePreference,
  LOCALE_STORAGE_KEY
} from '../../i18n/storagePolicy.js';
import { DEFAULT_LOCALE } from '../../i18n/localeRegistry.js';

// Polyfill minimal localStorage for Node test runner
const storageMap = new Map();
global.localStorage = {
  getItem: (key) => storageMap.get(key) || null,
  setItem: (key, val) => storageMap.set(key, String(val)),
  removeItem: (key) => storageMap.delete(key),
  clear: () => storageMap.clear()
};

describe('Storage Policy and Corrupted Preference Tests', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  test('returns default locale en-LK when nothing is stored', () => {
    assert.equal(getStoredLocalePreference(), DEFAULT_LOCALE);
  });

  test('stores only canonical locale and retrieves it', () => {
    setStoredLocalePreference('si-LK');
    assert.equal(localStorage.getItem(LOCALE_STORAGE_KEY), 'si-LK');
    assert.equal(getStoredLocalePreference(), 'si-LK');
  });

  test('normalizes aliases (si -> si-LK, en -> en-LK)', () => {
    setStoredLocalePreference('si');
    assert.equal(localStorage.getItem(LOCALE_STORAGE_KEY), 'si-LK');
    assert.equal(getStoredLocalePreference(), 'si-LK');
  });

  test('falls back safely to default en-LK on corrupted or unrecognized string', () => {
    localStorage.setItem(LOCALE_STORAGE_KEY, 'corrupted_payload_random_123');
    assert.equal(getStoredLocalePreference(), DEFAULT_LOCALE);
  });

  test('falls back safely on empty or malicious object injection', () => {
    localStorage.setItem(LOCALE_STORAGE_KEY, '{"learner_id": 999}');
    assert.equal(getStoredLocalePreference(), DEFAULT_LOCALE);
  });

  test('ensures no learner data or diagnostic claims are in storage key', () => {
    setStoredLocalePreference('si-LK');
    const stored = localStorage.getItem(LOCALE_STORAGE_KEY);
    assert.equal(stored.includes('learner'), false);
    assert.equal(stored.includes('risk'), false);
    assert.equal(stored.includes('score'), false);
  });
});
