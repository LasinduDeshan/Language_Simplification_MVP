import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import {
  getLocalizedInstruction,
  getLocalizedOptions,
  getLocalizedTaskTitle,
  safeText,
  normalizeContentLocale,
  normalizeActivityPayload,
  resolveLocalizedText,
  resolveLocalizedInstruction,
  normalizeLocalizedText,
  normalizeLocalizedToken,
  getLocalizedTokens,
  validateDemonstrationActivity,
  isUuid,
  DEMONSTRATION_ACTIVITIES
} from '../../i18n/activityLocalization.js';
import { localizeSupport, localizeSkill, supportLabelKeys } from '../../i18n/enumLocalization.js';

describe('Stage 36 Dynamic Activity Localization — 10 Required Unit Tests (§8)', () => {
  // 1. si-LK resolves instruction.si
  test('Unit Test 1: si-LK resolves instruction.si', () => {
    const payload = {
      id: 'task-101',
      instruction: {
        en: 'Look at this picture. What animal do you see?',
        si: 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?'
      }
    };
    const norm = normalizeActivityPayload(payload);
    const result = resolveLocalizedInstruction(norm, 'si-LK', { viewMode: 'simple' });
    assert.equal(result.text, 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?');
    assert.equal(result.resolvedLocale, 'si');
    assert.equal(result.usedFallback, false);
    assert.equal(result.missing, false);
  });

  // 2. SI-lk normalizes to si
  test('Unit Test 2: SI-lk normalizes to si', () => {
    assert.equal(normalizeContentLocale('SI-lk'), 'si');
    assert.equal(normalizeContentLocale('si-LK'), 'si');
    assert.equal(normalizeContentLocale('SI'), 'si');
    assert.equal(normalizeContentLocale('si_lk'), 'si');
  });

  // 3. Legacy instruction_si maps to instruction.si
  test('Unit Test 3: Legacy instruction_si maps to instruction.si via normalizeActivityPayload', () => {
    const legacyPayload = {
      id: 'task-legacy-01',
      title_en: 'Object Naming',
      title_si: 'වස්තු නම් කිරීම',
      instruction_en: 'Touch the pencil.',
      instruction_si: 'පැන්සල ස්පර්ශ කරන්න.'
    };
    const norm = normalizeActivityPayload(legacyPayload);
    assert.equal(norm.title.en, 'Object Naming');
    assert.equal(norm.title.si, 'වස්තු නම් කිරීම');
    assert.equal(norm.instruction.en, 'Touch the pencil.');
    assert.equal(norm.instruction.si, 'පැන්සල ස්පර්ශ කරන්න.');

    const result = resolveLocalizedInstruction(norm, 'si', { viewMode: 'simple' });
    assert.equal(result.text, 'පැන්සල ස්පර්ශ කරන්න.');
    assert.equal(result.resolvedLocale, 'si');
    assert.equal(result.usedFallback, false);
  });

  // 4. English scalar instruction does not masquerade as Sinhala
  test('Unit Test 4: English scalar instruction does not masquerade as Sinhala', () => {
    const englishScalarPayload = {
      activity_id: 'scalar-eng-001',
      title: 'Classroom cleanup',
      instruction: 'Before sitting on the rug, pack your crayons.'
    };
    const norm = normalizeActivityPayload(englishScalarPayload);
    assert.equal(norm.instruction.en, 'Before sitting on the rug, pack your crayons.');
    assert.equal(norm.instruction.si, null);

    // Simple view: must fail closed to unavailable notice and never show English
    const simpleResult = resolveLocalizedInstruction(norm, 'si', { viewMode: 'simple' });
    assert.equal(simpleResult.text, 'මෙම ක්‍රියාකාරකම සිංහල භාෂාවෙන් තවම ලබා ගත නොහැක.');
    assert.doesNotMatch(simpleResult.text, /Before sitting on the rug/i);
    assert.equal(simpleResult.resolvedLocale, null);
    assert.equal(simpleResult.usedFallback, true);
    assert.equal(simpleResult.missing, true);
  });

  // 5. A UUID activity with valid Sinhala displays Sinhala
  test('Unit Test 5: A UUID activity with valid Sinhala displays Sinhala', () => {
    const uuidActivity = {
      id: '17405b93-13bd-4a8a-9a1a-a0ee48164008',
      instruction: {
        en: 'Look at this picture. What animal do you see?',
        si: 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?'
      }
    };
    assert.ok(isUuid(uuidActivity.id));
    const result = resolveLocalizedInstruction(uuidActivity, 'si', { viewMode: 'simple' });
    assert.equal(result.text, 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?');
    assert.equal(result.resolvedLocale, 'si');
    assert.equal(result.usedFallback, false);
    assert.equal(result.missing, false);
  });

  // 6. A UUID activity without Sinhala returns missing: true and clean unavailable notice
  test('Unit Test 6: A UUID activity without Sinhala returns missing: true and does not match demo registry', () => {
    const uuidWithoutSinhala = {
      id: 'd85246c0-597e-4fb5-96ef-1678fac9233a',
      instruction: {
        en: 'Perform the multi-step geometric shape sorting task.'
      }
    };
    assert.ok(isUuid(uuidWithoutSinhala.id));
    const result = resolveLocalizedInstruction(uuidWithoutSinhala, 'si', { viewMode: 'simple' });
    assert.equal(result.missing, true);
    assert.equal(result.usedFallback, true);
    assert.equal(result.text, 'මෙම ක්‍රියාකාරකම සිංහල භාෂාවෙන් තවම ලබා ගත නොහැක.');
  });

  // 7. A known template_id may resolve through the governed registry
  test('Unit Test 7: A known template_id may resolve through the governed registry', () => {
    // Activity has a generated attempt UUID, but supplies a stable template_id
    const attemptWithTemplateId = {
      id: 'b848c772-520e-4361-bd38-16ef7b99c27f',
      template_id: 'VOC-NAMING-001',
      presented_instruction: 'Look at this picture. What animal do you see?'
    };
    const result = resolveLocalizedInstruction(attemptWithTemplateId, 'si', { viewMode: 'simple' });
    assert.equal(result.text, 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?');
    assert.equal(result.resolvedLocale, 'si');
    assert.equal(result.usedFallback, false);
  });

  // 8. Simple view never displays English when Sinhala is unavailable
  test('Unit Test 8: Simple view never displays English when Sinhala is unavailable', () => {
    const untranslatedTask = {
      id: '9cbd98a5-ddd1-4f02-9426-8ab26375223c',
      task_code: 'TASK-ENG-001',
      instruction: {
        en: 'Before sitting on the rug, pack your crayons and put your drawing paper in the green recycle bin.'
      }
    };
    const result = resolveLocalizedInstruction(untranslatedTask, 'si', { viewMode: 'simple', isChildView: true });
    assert.equal(result.text, 'මෙම ක්‍රියාකාරකම සිංහල භාෂාවෙන් තවම ලබා ගත නොහැක.');
    assert.doesNotMatch(result.text, /Before sitting on the rug/i);
    assert.doesNotMatch(result.text, /crayons/i);
    assert.doesNotMatch(result.text, /technical default/i);
    assert.doesNotMatch(result.text, /තාක්ෂණික පෙරනිමිය/i);
  });

  // 9. Researcher view isolates the warning from the instruction
  test('Unit Test 9: Researcher view isolates the warning from the instruction', () => {
    const untranslatedTask = {
      id: '9cbd98a5-ddd1-4f02-9426-8ab26375223c',
      task_code: 'TASK-ENG-001',
      instruction: {
        en: 'Before sitting on the rug, pack your crayons.'
      }
    };
    const result = resolveLocalizedInstruction(untranslatedTask, 'si', { viewMode: 'researcher', isChildView: false });
    // Text itself must remain clean English (no inline warning prefix)
    assert.equal(result.text, 'Before sitting on the rug, pack your crayons.');
    assert.doesNotMatch(result.text, /WARNING/i);
    assert.doesNotMatch(result.text, /සිංහල පරිවර්තනය බලාපොරොත්තුවෙන්/i);
    // Warning metadata is isolated in returned properties
    assert.equal(result.usedFallback, true);
    assert.equal(result.resolvedLocale, 'en');
    assert.equal(result.requestedLocale, 'si');
  });

  // 10. Support-level and target-skill labels remain localized
  test('Unit Test 10: Support-level and target-skill labels remain localized', () => {
    // Support levels
    assert.equal(localizeSupport('mild', 'si'), 'සුළු');
    assert.equal(localizeSupport('moderate', 'si'), 'මධ්‍යම ළමා-හිතකාමී සහාය');
    assert.equal(localizeSupport('strong', 'si'), 'ඉහළ ළමා-හිතකාමී සහාය');
    assert.equal(localizeSupport('strong_child_friendly', 'si'), 'ඉහළ ළමා-හිතකාමී සහාය');

    // Target skills
    assert.equal(localizeSkill('animal_naming', 'si'), 'සත්ව නම් කිරීම');
    assert.equal(localizeSkill('object_identification', 'si'), 'වස්තු හඳුනාගැනීම');
    assert.equal(localizeSkill('picture_matching', 'si'), 'පින්තූර ගැලපීම');
    assert.equal(localizeSkill('vocabulary_expansion', 'si'), 'වචන මාලාව පුළුල් කිරීම');
    assert.equal(localizeSkill('instruction_following', 'si'), 'උපදෙස් පිළිපැදීම');
    assert.equal(localizeSkill('sentence_completion', 'si'), 'වාක්‍ය සම්පූර්ණ කිරීම');
  });
});

describe('Stage 36 Runtime Activity Integration Scenarios (§8)', () => {
  test('Integration 1: Fetch a real Component 1 activity in Sinhala and assert Sinhala instruction rendering', () => {
    // Simulating Component 1 runtime response normalized through normalizeActivityPayload
    const c1ApiResponse = {
      id: 'b1151177-2184-4e4d-8a12-0e7c31485238',
      activity_id: 'b1151177-2184-4e4d-8a12-0e7c31485238',
      template_id: 'VOC-NAMING-001',
      task_code: 'VOC-NAMING-001',
      title_en: 'Name the Animal',
      title_si: 'සත්වයා නම් කරන්න',
      instruction_en: 'Look at this picture. What animal do you see?',
      instruction_si: 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?',
      content_language_status: { en: 'AVAILABLE', si: 'AVAILABLE' }
    };

    const normalized = normalizeActivityPayload(c1ApiResponse);
    const instruction = getLocalizedInstruction(normalized, 'si', { viewMode: 'simple' });
    assert.equal(instruction, 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?');

    const title = getLocalizedTaskTitle(normalized, 'si');
    assert.equal(title, 'සත්වයා නම් කරන්න');
  });

  test('Integration 2: Fetch an English-only runtime activity and assert clean unavailable notice in simple view', () => {
    const englishRuntimeTask = {
      id: '9cbd98a5-ddd1-4f02-9426-8ab26375223c',
      activity_id: '9cbd98a5-ddd1-4f02-9426-8ab26375223c',
      template_id: 'TASK-ENG-001',
      task_code: 'TASK-ENG-001',
      title_en: 'Classroom Clean-Up Instruction',
      title_si: null,
      instruction_en: 'Before sitting on the rug, pack your crayons.',
      instruction_si: null,
      content_language_status: { en: 'AVAILABLE', si: 'UNAVAILABLE' }
    };

    const normalized = normalizeActivityPayload(englishRuntimeTask);
    const simpleInstruction = getLocalizedInstruction(normalized, 'si', { viewMode: 'simple' });
    assert.equal(simpleInstruction, 'මෙම ක්‍රියාකාරකම සිංහල භාෂාවෙන් තවම ලබා ගත නොහැක.');
    assert.doesNotMatch(simpleInstruction, /Before sitting/i);
  });

  test('Integration 3: Switch en -> si -> en without stale cached instruction text', () => {
    const activity = {
      id: 'act-switch-test',
      instruction: {
        en: 'Touch the red circle.',
        si: 'රතු පාට වෘත්තය ස්පර්ශ කරන්න.'
      }
    };

    const normalized = normalizeActivityPayload(activity);

    // Initial English
    const en1 = getLocalizedInstruction(normalized, 'en');
    assert.equal(en1, 'Touch the red circle.');

    // Switch to Sinhala
    const si = getLocalizedInstruction(normalized, 'si');
    assert.equal(si, 'රතු පාට වෘත්තය ස්පර්ශ කරන්න.');

    // Switch back to English
    const en2 = getLocalizedInstruction(normalized, 'en');
    assert.equal(en2, 'Touch the red circle.');
    assert.equal(en2, en1);
  });

  test('Integration 4: Reload a persisted Sinhala session attempt and retain localized content', () => {
    // Persisted attempt restored from session history
    const restoredAttempt = {
      id: '17405b93-13bd-4a8a-9a1a-a0ee48164008',
      activity_session_id: 'sess-889922',
      template_id: 'VOC-NAMING-001',
      presented_instruction: 'Choose: cat or dog.',
      instruction_si: 'තෝරන්න: පූසා හෝ බල්ලා.',
      support_level: 'strong'
    };

    const normalized = normalizeActivityPayload(restoredAttempt);
    const result = resolveLocalizedInstruction(normalized, 'si', { viewMode: 'simple' });
    assert.equal(result.text, 'තෝරන්න: පූසා හෝ බල්ලා.');
    assert.equal(result.resolvedLocale, 'si');
    assert.equal(result.usedFallback, false);
  });

  test('React Child Safety: getLocalizedOptions returns primitive strings and never {en, si} objects', () => {
    // Activity with normalized { en, si } option labels
    const activityWithNormalizedOptions = {
      id: 'task-opt-test',
      options: [
        { id: 'cat', label: { en: 'Cat', si: 'පූසා' } },
        { id: 'dog', label: { en: 'Dog', si: 'බල්ලා' } },
        { id: 'custom', label: { en: 'Custom Item', si: 'විශේෂ අයිතමය' } }
      ]
    };

    // English mode
    const enOpts = getLocalizedOptions(activityWithNormalizedOptions, 'en');
    for (const opt of enOpts) {
      assert.equal(typeof opt.raw, 'string');
      assert.equal(typeof opt.label, 'string');
      assert.notEqual(typeof opt.label, 'object');
    }
    assert.equal(enOpts[0].label, 'Cat');
    assert.equal(enOpts[1].label, 'Dog');
    assert.equal(enOpts[2].label, 'Custom Item');

    // Sinhala mode
    const siOpts = getLocalizedOptions(activityWithNormalizedOptions, 'si');
    for (const opt of siOpts) {
      assert.equal(typeof opt.raw, 'string');
      assert.equal(typeof opt.label, 'string');
      assert.notEqual(typeof opt.label, 'object');
    }
    assert.equal(siOpts[0].label, 'පූසා');
    assert.equal(siOpts[1].label, 'බල්ලා');
    assert.equal(siOpts[2].label, 'විශේෂ අයිතමය');
  });

  test('React Child Safety: getLocalizedTaskTitle returns primitive strings and never {en, si} objects', () => {
    const taskWithNormalizedTitle = {
      id: 'task-title-test',
      title: {
        en: 'Animal Identification',
        si: 'සතුන් හඳුනාගැනීම'
      }
    };

    const enTitle = getLocalizedTaskTitle(taskWithNormalizedTitle, 'en');
    assert.equal(typeof enTitle, 'string');
    assert.notEqual(typeof enTitle, 'object');
    assert.equal(enTitle, 'Animal Identification');

    const siTitle = getLocalizedTaskTitle(taskWithNormalizedTitle, 'si');
    assert.equal(typeof siTitle, 'string');
    assert.notEqual(typeof siTitle, 'object');
    assert.equal(siTitle, 'සතුන් හඳුනාගැනීම');
  });

  test('React Child Safety: safeText extracts primitive string safely from objects, strings, and primitives', () => {
    assert.equal(safeText({ en: 'Hello', si: 'ආයුබෝවන්' }, 'en'), 'Hello');
    assert.equal(safeText({ en: 'Hello', si: 'ආයුබෝවන්' }, 'si'), 'ආයුබෝවන්');
    assert.equal(safeText('plain string'), 'plain string');
    assert.equal(safeText(null), '');
    assert.equal(safeText(undefined), '');
    assert.equal(safeText(42), '42');
  });

  // Stage 36 Dynamic Token and Activity Localization Tests
  test('Stage 36: GRAM-WORD-001 localization in Sinhala and English', () => {
    const gramTask = DEMONSTRATION_ACTIVITIES['GRAM-WORD-001'];
    assert.ok(gramTask);
    const norm = normalizeActivityPayload(gramTask);

    // English resolution
    const enTitle = getLocalizedTaskTitle(norm, 'en');
    assert.equal(enTitle, 'Word Ordering: S-V-O Sentence');
    const enInstruction = getLocalizedInstruction(norm, 'en');
    assert.equal(enInstruction, 'Put the words in the correct order.');
    const enTokens = getLocalizedTokens(norm, 'en');
    assert.equal(enTokens.length, 3);
    assert.equal(enTokens[0].text, 'The boy');
    assert.equal(enTokens[1].text, 'likes');
    assert.equal(enTokens[2].text, 'apples');

    // Sinhala resolution
    const siTitle = getLocalizedTaskTitle(norm, 'si');
    assert.equal(siTitle, 'කර්තෘ–ක්‍රියා–කර්ම වාක්‍යය පෙළගස්වන්න');
    const siInstruction = getLocalizedInstruction(norm, 'si');
    assert.equal(siInstruction, 'වචන නිවැරදි අනුපිළිවෙළට සකස් කරන්න.');
    const siTokens = getLocalizedTokens(norm, 'si');
    assert.equal(siTokens.length, 3);
    assert.equal(siTokens[0].text, 'පිරිමි ළමයා');
    assert.equal(siTokens[1].text, 'කැමතියි');
    assert.equal(siTokens[2].text, 'ඇපල්වලට');

    // Target skill resolution
    assert.equal(localizeSkill(norm.target_skill, 'en'), 'S-V-O Word Order');
    assert.equal(localizeSkill(norm.target_skill, 'si'), 'කර්තෘ–ක්‍රියා–කර්ම වචන අනුපිළිවෙළ');
    assert.equal(localizeSkill('word_order_svo', 'si'), 'කර්තෘ–ක්‍රියා–කර්ම වචන අනුපිළිවෙළ');
    assert.equal(localizeSkill('Word Order Svo', 'si'), 'කර්තෘ–ක්‍රියා–කර්ම වචන අනුපිළිවෙළ');
  });

  test('Stage 36: resolveLocalizedText fail-closed contract vs allowFallback', () => {
    const bilingual = { en: 'Hello', si: 'ආයුබෝවන්' };
    const englishOnly = { en: 'Welcome to class' };

    // Bilingual: Sinhala resolved without fallback
    const resSi = resolveLocalizedText(bilingual, 'si');
    assert.equal(resSi.text, 'ආයුබෝවන්');
    assert.equal(resSi.resolvedLocale, 'si');
    assert.equal(resSi.usedFallback, false);
    assert.equal(resSi.missing, false);

    // English-only object: Fail-closed when Sinhala is requested
    const failClosedObj = resolveLocalizedText(englishOnly, 'si');
    assert.equal(failClosedObj.text, null);
    assert.equal(failClosedObj.resolvedLocale, null);
    assert.equal(failClosedObj.usedFallback, false);
    assert.equal(failClosedObj.missing, true);

    // English-only object with allowFallback: true (researcher view)
    const allowedFallbackObj = resolveLocalizedText(englishOnly, 'si', { allowFallback: true });
    assert.equal(allowedFallbackObj.text, 'Welcome to class');
    assert.equal(allowedFallbackObj.resolvedLocale, 'en');
    assert.equal(allowedFallbackObj.usedFallback, true);
    assert.equal(allowedFallbackObj.missing, false);

    // English scalar string: Fail-closed when Sinhala is requested
    const failClosedStr = resolveLocalizedText('English text only', 'si');
    assert.equal(failClosedStr.text, null);
    assert.equal(failClosedStr.resolvedLocale, null);
    assert.equal(failClosedStr.usedFallback, false);
    assert.equal(failClosedStr.missing, true);
  });

  test('Stage 36: normalizeLocalizedText and normalizeLocalizedToken', () => {
    // normalizeLocalizedText
    const objText = normalizeLocalizedText({ en: 'Cat', si: 'පූසා' });
    assert.deepEqual(objText, { en: 'Cat', si: 'පූසා' });

    const strEn = normalizeLocalizedText('Dog');
    assert.deepEqual(strEn, { en: 'Dog', si: null });

    const strSi = normalizeLocalizedText('බල්ලා');
    assert.deepEqual(strSi, { en: null, si: 'බල්ලා' });

    // normalizeLocalizedToken
    const tokenObj = normalizeLocalizedToken({
      token_id: 'tok-1',
      order: 1,
      text: { en: 'The boy', si: 'පිරිමි ළමයා' }
    });
    assert.equal(tokenObj.token_id, 'tok-1');
    assert.equal(tokenObj.order, 1);
    assert.equal(tokenObj.text.en, 'The boy');
    assert.equal(tokenObj.text.si, 'පිරිමි ළමයා');
  });
});
