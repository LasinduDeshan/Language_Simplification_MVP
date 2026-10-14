import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const i18nDir = path.resolve(__dirname, '../../i18n');

describe('Translation Resource Governance Tests', () => {
  const metaPath = path.join(i18nDir, 'translations.meta.json');

  test('translations.meta.json exists and contains governed metadata', () => {
    assert.ok(fs.existsSync(metaPath), 'translations.meta.json must exist');
    const meta = JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
    assert.ok(meta.resources);
    assert.equal(meta.resources.length, 2);

    for (const res of meta.resources) {
      assert.equal(res.translation_status, 'technical_draft');
      assert.equal(res.approved_for_child_delivery, false);
      assert.equal(res.reviewed_by, null);
      assert.ok(res.authored_by_actor_id);
    }
  });

  test('SHA-256 hashes in translations.meta.json match resource files exactly', () => {
    const meta = JSON.parse(fs.readFileSync(metaPath, 'utf-8'));
    for (const res of meta.resources) {
      const filePath = path.join(i18nDir, res.resource_file);
      assert.ok(fs.existsSync(filePath), `Resource file ${res.resource_file} must exist`);
      const fileBytes = fs.readFileSync(filePath);
      const computedHash = crypto.createHash('sha256').update(fileBytes).digest('hex');
      assert.equal(computedHash, res.sha256, `Hash mismatch for ${res.resource_file}`);
    }
  });
});
