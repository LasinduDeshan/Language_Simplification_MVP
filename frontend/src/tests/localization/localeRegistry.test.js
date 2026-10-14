import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { resolveLocale, isSupportedLocale, DEFAULT_LOCALE, LOCALE_REGISTRY } from '../../i18n/localeRegistry.js';

describe('Frontend Locale Registry Tests', () => {
  test('default locale is en-LK', () => {
    assert.equal(DEFAULT_LOCALE, 'en-LK');
  });

  test('resolves si-LK and en-LK with correct script and direction', () => {
    const si = resolveLocale('si-LK');
    assert.ok(si);
    assert.equal(si.language, 'si');
    assert.equal(si.script, 'Sinh');
    assert.equal(si.direction, 'ltr');

    const en = resolveLocale('en-LK');
    assert.ok(en);
    assert.equal(en.language, 'en');
    assert.equal(en.script, 'Latn');
    assert.equal(en.direction, 'ltr');
  });

  test('resolves aliases properly', () => {
    assert.deepEqual(resolveLocale('si'), resolveLocale('si-LK'));
    assert.deepEqual(resolveLocale('en'), resolveLocale('en-LK'));
  });

  test('rejects non-canonical or unsupported identifiers', () => {
    assert.equal(resolveLocale('SIN'), null);
    assert.equal(resolveLocale('sinhala'), null);
    assert.equal(resolveLocale('lk-si'), null);
    assert.equal(resolveLocale('fr-FR'), null);
    assert.equal(isSupportedLocale('fr-FR'), false);
  });
});
