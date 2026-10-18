import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const i18nDir = path.resolve(__dirname, '../../i18n');

function flattenKeys(obj, prefix = '') {
  let keys = [];
  for (const [k, v] of Object.entries(obj)) {
    const fullKey = prefix ? `${prefix}.${k}` : k;
    if (v && typeof v === 'object' && !Array.isArray(v)) {
      keys = keys.concat(flattenKeys(v, fullKey));
    } else {
      keys.push(fullKey);
    }
  }
  return keys.sort();
}

describe('Translation Key Parity Tests (Plan §12.1, §12.6)', () => {
  const en = JSON.parse(fs.readFileSync(path.join(i18nDir, 'en.json'), 'utf-8'));
  const si = JSON.parse(fs.readFileSync(path.join(i18nDir, 'si.json'), 'utf-8'));

  test('all required namespaces exist in both English and Sinhala resources', () => {
    const requiredNamespaces = [
      'app', 'nav', 'common', 'playground', 'childModal', 'risk',
      'skills', 'support', 'status', 'safety', 'results', 'evaluation',
      'language_selector', 'probe', 'governance'
    ];

    for (const ns of requiredNamespaces) {
      assert.ok(en[ns], `Missing namespace ${ns} in en.json`);
      assert.ok(si[ns], `Missing namespace ${ns} in si.json`);
    }
  });

  test('100% key parity between en.json and si.json with zero missing keys', () => {
    const enKeys = flattenKeys(en);
    const siKeys = flattenKeys(si);

    const missingInSi = enKeys.filter(k => !siKeys.includes(k));
    const missingInEn = siKeys.filter(k => !enKeys.includes(k));

    assert.deepEqual(missingInSi, [], `Keys present in en.json but missing in si.json: ${missingInSi.join(', ')}`);
    assert.deepEqual(missingInEn, [], `Keys present in si.json but missing in en.json: ${missingInEn.join(', ')}`);
    assert.deepEqual(enKeys, siKeys, 'Key lists must be strictly identical');
  });

  test('childModal and playground namespaces have non-empty valid translations', () => {
    for (const [key, val] of Object.entries(si.childModal)) {
      assert.ok(typeof val === 'string' && val.trim().length > 0, `Empty translation for childModal.${key}`);
    }
    for (const [key, val] of Object.entries(si.playground)) {
      assert.ok(typeof val === 'string' && val.trim().length > 0, `Empty translation for playground.${key}`);
    }
  });
});
