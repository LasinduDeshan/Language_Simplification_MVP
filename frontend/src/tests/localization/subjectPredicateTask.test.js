import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import {
  getLocalizedTaskTitle,
  normalizeActivityPayload,
  resolveLocalizedInstruction,
  DEMONSTRATION_ACTIVITIES
} from '../../i18n/activityLocalization.js';
import { localizeSkill } from '../../i18n/enumLocalization.js';

describe('Subject & Predicate Grammar Task (GRAM-SI-SUBPRED-001) Localization & Governance', () => {
  const taskRecord = DEMONSTRATION_ACTIVITIES['GRAM-SI-SUBPRED-001'];

  test('Section 1: Task exists in curated demonstration catalog with alias', () => {
    assert.ok(taskRecord, 'GRAM-SI-SUBPRED-001 must exist in DEMONSTRATION_ACTIVITIES');
    assert.equal(taskRecord.task_code, 'GRAM-SI-SUBPRED-001');
    assert.equal(taskRecord.template_id, 'GRAM-SI-SUBPRED-001');

    const aliasRecord = DEMONSTRATION_ACTIVITIES['ACT-SUBPRED-001'];
    assert.ok(aliasRecord, 'ACT-SUBPRED-001 alias must exist in DEMONSTRATION_ACTIVITIES');
    assert.equal(aliasRecord.task_code, 'GRAM-SI-SUBPRED-001');
  });

  test('Section 2: Sinhala and English title resolution', () => {
    const payload = {
      task_code: 'GRAM-SI-SUBPRED-001',
      title: {
        en: 'Identifying the Subject and Predicate',
        si: 'උක්තය සහ ආඛ්‍යාතය හඳුනාගැනීම'
      }
    };

    assert.equal(
      getLocalizedTaskTitle(payload, 'si'),
      'උක්තය සහ ආඛ්‍යාතය හඳුනාගැනීම'
    );
    assert.equal(
      getLocalizedTaskTitle(payload, 'si-LK'),
      'උක්තය සහ ආඛ්‍යාතය හඳුනාගැනීම'
    );
    assert.equal(
      getLocalizedTaskTitle(payload, 'en'),
      'Identifying the Subject and Predicate'
    );
  });

  test('Section 3: Skill localization for SUBJECT_PREDICATE_IDENTIFICATION', () => {
    assert.equal(
      localizeSkill('subject_predicate_identification', 'si'),
      'උක්තය සහ ආඛ්‍යාතය හඳුනාගැනීම'
    );
    assert.equal(
      localizeSkill('SUBJECT_PREDICATE_IDENTIFICATION', 'si'),
      'උක්තය සහ ආඛ්‍යාතය හඳුනාගැනීම'
    );
    assert.equal(
      localizeSkill('subject_predicate_identification', 'en'),
      'Subject & Predicate Identification'
    );
  });

  test('Section 4: Linguistic invariants - Predicate is not only the verb', () => {
    assert.ok(taskRecord.items && taskRecord.items.length >= 5, 'Must contain at least 5 governed examples');

    for (const item of taskRecord.items) {
      assert.ok(item.sentence.includes(item.subject), `Sentence contains subject: ${item.subject}`);
      assert.ok(item.sentence.includes(item.predicate), `Sentence contains predicate: ${item.predicate}`);
      assert.ok(item.predicate.includes(item.verb), `Predicate contains verb: ${item.verb}`);
      assert.notEqual(item.predicate, item.verb, `Predicate '${item.predicate}' must not be only the verb '${item.verb}'`);
      assert.ok(item.predicate.length > item.verb.length, 'Predicate must have additional words besides the verb');
    }
  });

  test('Section 5: Adaptive instructions resolution for all strategy tiers', () => {
    const supportVersions = taskRecord.support_versions;
    assert.ok(supportVersions, 'Support versions must be present');

    assert.equal(supportVersions.mild_support.si, 'වාක්‍යය කවුරුන් හෝ කුමක් ගැනද සහ ඒ ගැන කියන දෙය කුමක්ද හඳුනාගන්න.');
    assert.equal(supportVersions.moderate_support.si, 'පළමුව උක්තය තෝරන්න. ඉන්පසු ආඛ්‍යාතය තෝරන්න.');
    assert.equal(supportVersions.strong_scaffold.si, 'කවුද හෝ කුමක්ද? ඒ ගැන කියන්නේ කුමක්ද?');
    assert.equal(supportVersions.strong_decomposed_step.si, 'පළමුව “කවුද?” කියා සොයා එය තෝරන්න. දැන් ඒ අය කරන දෙය තෝරන්න.');
  });

  test('Section 6: Governed safety and child delivery flags remain strictly false', () => {
    assert.equal(taskRecord.validation_status, 'draft');
    assert.equal(taskRecord.expert_validated, false);
    assert.equal(taskRecord.research_eligible, false);
    assert.equal(taskRecord.approved_for_child_delivery, false);
    assert.equal(taskRecord.approved_for_unsupervised_child_delivery, false);
    assert.equal(taskRecord.requires_expert_review, true);
  });

  test('Section 7: Two-stage selection logic evaluation helper', () => {
    const primary = taskRecord.items[0]; // ළමයා පොත කියවයි.
    assert.equal(primary.subject, 'ළමයා');
    assert.equal(primary.predicate, 'පොත කියවයි');
    assert.equal(primary.verb, 'කියවයි');

    // Case A: Correct selection
    const isSubjectCorrect = 'ළමයා' === primary.subject;
    const isPredicateCorrect = 'පොත කියවයි' === primary.predicate;
    assert.equal(isSubjectCorrect && isPredicateCorrect, true);

    // Case B: Incomplete predicate (verb only trap)
    const verbOnlyPred = 'කියවයි';
    const isVerbOnlyTrap = verbOnlyPred === primary.verb && verbOnlyPred !== primary.predicate;
    assert.equal(isVerbOnlyTrap, true);
  });
});
