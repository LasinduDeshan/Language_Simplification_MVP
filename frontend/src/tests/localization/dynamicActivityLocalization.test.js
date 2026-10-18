import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import { getLocalizedInstruction, getLocalizedOptions } from '../../i18n/activityLocalization.js';

describe('Dynamic Activity Content Localization Tests (Plan §12.3)', () => {
  test('resolves curated Sinhala instruction for animal naming activity in si locale', () => {
    const task = {
      task_code: 'ACT-ANIMAL-001',
      child_friendly_instruction: 'Look at the picture. Tell me what animal you see.'
    };

    const instEn = getLocalizedInstruction(task, 'en');
    assert.equal(instEn, 'Look at the picture. Tell me what animal you see.');

    const instSi = getLocalizedInstruction(task, 'si');
    assert.equal(instSi, 'පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්දැයි කියන්න.');
  });

  test('resolves instruction with explicit instruction.en and instruction.si contract', () => {
    const task = {
      instruction: {
        en: 'Point to the big dog.',
        si: 'ලොකු බල්ලාට ඇඟිල්ල දිගු කරන්න.'
      }
    };

    assert.equal(getLocalizedInstruction(task, 'en'), 'Point to the big dog.');
    assert.equal(getLocalizedInstruction(task, 'si'), 'ලොකු බල්ලාට ඇඟිල්ල දිගු කරන්න.');
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

  test('fails closed in child view when Sinhala content is missing for unreviewed task', () => {
    const task = {
      task_code: 'UNREVIEWED-TASK-999',
      child_friendly_instruction: 'Some unreviewed complex English prompt'
    };

    // For child view, should return approved child-safe placeholder or marked instruction
    const siChildInst = getLocalizedInstruction(task, 'si', { isChildView: true });
    assert.ok(
      siChildInst.includes('පින්තූරය බලන්න') || siChildInst.includes('අපි විනෝද වෙමු'),
      `Child view must fail closed to approved Sinhala rather than unreviewed English: ${siChildInst}`
    );

    // For researcher view, clearly marked fallback warning is permitted
    const siResearcherInst = getLocalizedInstruction(task, 'si', { isChildView: false });
    assert.ok(
      siResearcherInst.includes('[') || siResearcherInst.includes('fallback') || siResearcherInst.length > 0,
      'Researcher view may present marked fallback'
    );
  });

  test('getLocalizedOptions accepts (activity, rawOptions, locale) signature and produces renderable strings', () => {
    const rawOptions = ['cat', 'dog', 'rabbit'];
    const options = getLocalizedOptions({ id: 'TASK-001' }, rawOptions, 'si');
    assert.equal(options.length, 3);
    for (const opt of options) {
      assert.equal(typeof opt.raw, 'string');
      assert.equal(typeof opt.label, 'string');
      assert.equal(typeof opt.emoji, 'string');
    }
  });
});

