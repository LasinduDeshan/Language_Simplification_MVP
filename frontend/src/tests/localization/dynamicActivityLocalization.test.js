import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import {
  getLocalizedInstruction,
  getLocalizedOptions,
  normalizeContentLocale,
  resolveLocalizedText,
  resolveLocalizedInstruction,
  validateDemonstrationActivity,
  DEMONSTRATION_ACTIVITIES
} from '../../i18n/activityLocalization.js';
import { localizeSupport, supportLabelKeys } from '../../i18n/enumLocalization.js';

describe('Dynamic Activity Content Localization Tests (§11 & §12.3)', () => {
  // 11.1 Sinhala instruction test
  test('11.1 renders the Sinhala activity instruction', () => {
    const task = {
      task_code: 'ACT-ANIMAL-001'
    };

    const instSi = getLocalizedInstruction(task, 'si');
    assert.equal(instSi, 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?');
  });

  // 11.2 No English fallback in Simple View
  test('11.2 does not display the English instruction in Sinhala Simple View', () => {
    const task = {
      task_code: 'ACT-ANIMAL-001',
      instruction: {
        en: 'Look at this picture. What animal do you see?',
        si: 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?'
      }
    };

    const result = getLocalizedInstruction(task, 'si', { isChildView: true, viewMode: 'simple' });
    assert.doesNotMatch(result, /Look at this picture/i);
    assert.equal(result, 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?');
  });

  // 11.3 No technical marker in the instruction
  test('11.3 does not render the translation-pending technical marker in instruction', () => {
    const task = {
      task_code: 'ACT-ANIMAL-001'
    };

    const result = getLocalizedInstruction(task, 'si');
    assert.doesNotMatch(result, /සිංහල පරිවර්තනය බලාපොරොත්තුවෙන්/i);
    assert.doesNotMatch(result, /තාක්ෂණික පෙරනිමිය/i);
  });

  // 11.4 Locale normalization
  test('11.4 normalizes content locale variants correctly', () => {
    assert.equal(normalizeContentLocale('si'), 'si');
    assert.equal(normalizeContentLocale('si-LK'), 'si');
    assert.equal(normalizeContentLocale('SI-lk'), 'si');
    assert.equal(normalizeContentLocale('en-US'), 'en');
    assert.equal(normalizeContentLocale('en-LK'), 'en');
    assert.equal(normalizeContentLocale('en'), 'en');
    assert.equal(normalizeContentLocale(''), 'en');
    assert.equal(normalizeContentLocale(undefined), 'en');
  });

  // 11.5 Missing Sinhala behavior - fails closed in Simple View
  test('11.5 fails closed in Simple View when Sinhala content is absent', () => {
    const englishOnlyActivity = {
      task_code: 'UNTRANSLATED-999',
      instruction: {
        en: 'Look at this picture. What animal do you see?'
      }
    };

    const result = getLocalizedInstruction(englishOnlyActivity, 'si', { isChildView: true, viewMode: 'simple' });
    assert.equal(result, 'මෙම ක්‍රියාකාරකම සිංහල භාෂාවෙන් තවම ලබා ගත නොහැක.');
    assert.doesNotMatch(result, /Look at this picture/i);
    assert.doesNotMatch(result, /සිංහල පරිවර්තනය බලාපොරොත්තුවෙන්/i);
  });

  // 11.6 Dynamic enum localization for support level
  test('11.6 localizes the support level without raw English configuration strings', () => {
    const supportSi = localizeSupport('strong_child_friendly', 'si');
    assert.equal(supportSi, 'ඉහළ ළමා-හිතකාමී සහාය');
    assert.doesNotMatch(supportSi, /Strong Child Friendly/i);

    const supportKeySi = localizeSupport(supportLabelKeys.STRONG_CHILD_FRIENDLY, 'si');
    assert.equal(supportKeySi, 'ඉහළ ළමා-හිතකාමී සහාය');

    const supportEn = localizeSupport('strong_child_friendly', 'en');
    assert.equal(supportEn, 'Strong child-friendly support');
  });

  // 11.7 English regression
  test('11.7 continues to render the English instruction in English mode', () => {
    const task = {
      task_code: 'ACT-ANIMAL-001'
    };

    const result = getLocalizedInstruction(task, 'en');
    assert.equal(result, 'Look at this picture. What animal do you see?');
  });

  test('canonical multilingual contract resolution via resolveLocalizedText', () => {
    const textObject = {
      en: 'Name the Animal',
      si: 'සත්වයා නම් කරන්න'
    };

    const enRes = resolveLocalizedText(textObject, 'en');
    assert.equal(enRes.text, 'Name the Animal');
    assert.equal(enRes.usedFallback, false);

    const siRes = resolveLocalizedText(textObject, 'si-LK');
    assert.equal(siRes.text, 'සත්වයා නම් කරන්න');
    assert.equal(siRes.usedFallback, false);
    assert.equal(siRes.resolvedLocale, 'si');

    const missingSi = {
      en: 'English only content'
    };
    const missingRes = resolveLocalizedText(missingSi, 'si');
    assert.equal(missingRes.text, 'English only content');
    assert.equal(missingRes.usedFallback, true);
    assert.equal(missingRes.resolvedLocale, 'en');
  });

  test('validates demonstration activities against Canonical Contract (§10)', () => {
    const demo = DEMONSTRATION_ACTIVITIES['ACT-ANIMAL-001'];
    const errors = validateDemonstrationActivity(demo);
    assert.deepEqual(errors, [], 'Canonical demonstration activity must have zero validation errors');

    const invalid = {
      title: { en: 'Incomplete' },
      options: [{ id: 'opt1', labels: { en: 'Only En' } }]
    };
    const invErrors = validateDemonstrationActivity(invalid);
    assert.ok(invErrors.includes('MISSING_TITLE_SI'));
    assert.ok(invErrors.includes('MISSING_INSTRUCTION_EN'));
    assert.ok(invErrors.includes('MISSING_INSTRUCTION_SI'));
    assert.ok(invErrors.includes('MISSING_OPTION_SI:opt1'));
  });

  test('translates multiple choice options to Sinhala with emojis', () => {
    const task = {
      options: ['cat', 'dog', 'rabbit']
    };

    const enOpts = getLocalizedOptions(task, 'en');
    assert.equal(enOpts[0].label, 'Cat');
    assert.equal(enOpts[1].label, 'Dog');
    assert.equal(enOpts[2].label, 'Rabbit');

    const siOpts = getLocalizedOptions(task, 'si');
    assert.equal(siOpts[0].label, 'පූසා');
    assert.equal(siOpts[0].raw, 'cat');
    assert.equal(siOpts[0].emoji, '🐱');

    assert.equal(siOpts[1].label, 'බල්ලා');
    assert.equal(siOpts[1].raw, 'dog');
    assert.equal(siOpts[1].emoji, '🐶');

    assert.equal(siOpts[2].label, 'හාවා');
    assert.equal(siOpts[2].raw, 'rabbit');
    assert.equal(siOpts[2].emoji, '🐰');
  });

  test('resolves instruction when passed attempt object without task_code if task context is provided', () => {
    const attempt = {
      id: '9804bc7a-4b95-46f9-86c3-17bca87b0012',
      presented_instruction: 'Look at this picture. What animal do you see?',
      support_level: 'strong'
    };
    const task = {
      task_code: 'VOC-NAMING-001',
      title: 'Name the Animal'
    };

    const result = resolveLocalizedInstruction(attempt, 'si', { task, viewMode: 'simple' });
    assert.equal(result.text, 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?');
    assert.equal(result.usedFallback, false);
    assert.equal(result.resolvedLocale, 'si');
  });
});
