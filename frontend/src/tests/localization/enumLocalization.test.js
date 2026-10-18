import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import {
  localizeSkill,
  localizeSupport,
  localizeRisk,
  localizeStatus
} from '../../i18n/enumLocalization.js';

describe('Enum and Internal Value Localization Tests (Plan §12.4)', () => {
  test('raw skill enums do not appear in Sinhala output', () => {
    const rawSkills = [
      'animal_naming',
      'object_identification',
      'picture_matching',
      'vocabulary_expansion',
      'sentence_completion',
      'instruction_following'
    ];

    for (const raw of rawSkills) {
      const localized = localizeSkill(raw, 'si');
      assert.notEqual(localized, raw, `Skill enum ${raw} must not be rendered raw in Sinhala`);
      assert.ok(/[\u0D80-\u0DFF]/.test(localized), `Localized skill must contain Sinhala Unicode characters: ${localized}`);
    }
  });

  test('raw support enums do not appear in Sinhala output', () => {
    const rawSupports = [
      'independent',
      'mild',
      'moderate',
      'strong',
      'strong_visual_cue',
      'verbal_prompt',
      'gestural_cue',
      'modeling',
      'prompted',
      'visually_supported',
      'modelled',
      'fully_assisted'
    ];

    for (const raw of rawSupports) {
      const localized = localizeSupport(raw, 'si');
      assert.notEqual(localized, raw, `Support enum ${raw} must not be rendered raw in Sinhala`);
      assert.ok(/[\u0D80-\u0DFF]/.test(localized), `Localized support must contain Sinhala Unicode characters: ${localized}`);
    }
  });

  test('raw risk enums do not appear in Sinhala output', () => {
    const rawRisks = ['low', 'moderate', 'high', 'critical'];

    for (const raw of rawRisks) {
      const localized = localizeRisk(raw, 'si');
      assert.notEqual(localized, raw, `Risk enum ${raw} must not be rendered raw in Sinhala`);
      assert.ok(/[\u0D80-\u0DFF]/.test(localized), `Localized risk must contain Sinhala Unicode characters: ${localized}`);
    }
  });

  test('status enums localize correctly in both English and Sinhala', () => {
    assert.equal(localizeStatus('completed', 'en'), 'Completed');
    assert.equal(localizeStatus('completed', 'si'), 'සම්පූර්ණයි');

    assert.equal(localizeStatus('correct', 'en'), 'Correct');
    assert.equal(localizeStatus('correct', 'si'), 'නිවැරදියි');

    assert.equal(localizeStatus('incorrect', 'en'), 'Incorrect');
    assert.equal(localizeStatus('incorrect', 'si'), 'වැරදියි');
  });

  test('English mode formats raw snake_case enums cleanly without underscores', () => {
    const skillEn = localizeSkill('animal_naming', 'en');
    assert.equal(skillEn, 'Animal Naming');
    assert.ok(!skillEn.includes('_'), 'No raw underscores in English display');

    const supportEn = localizeSupport('strong_visual_cue', 'en');
    assert.equal(supportEn, 'Strong Visual Cue');
    assert.ok(!supportEn.includes('_'), 'No raw underscores in English display');
  });
});
