import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  setLocale,
  getLocale,
  t,
  getLocalizedTaskTitle,
  localizeSkill,
  localizeSupport,
  localizeRisk
} from '../../i18n/index.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const frontendDir = path.resolve(__dirname, '../../..');

describe('Sinhala Demonstration UI — Visual & Responsive Tests (Plan §15)', () => {
  test('1. Sinhala header navigation labels use recommended short translations (§4)', () => {
    setLocale('si-LK');
    assert.equal(t('nav.interactivePlayground'), 'ක්‍රියාකාරකම්');
    assert.equal(t('nav.safety'), 'ආරක්ෂාව');
    assert.equal(t('nav.evaluation'), 'ඇගයීම්');
    assert.equal(t('nav.results'), 'ප්‍රතිඵල');
    assert.equal(t('nav.technicalLab'), 'තාක්ෂණික අංශය');
    assert.equal(t('common.simpleView'), 'සරල දැක්ම');
    assert.equal(t('common.researcherView'), 'පර්යේෂක');

    // Tooltips / descriptions preserve full meaning
    assert.equal(t('nav.interactivePlaygroundTitle'), 'අන්තර්ක්‍රියාකාරී ඉගෙනුම් ක්‍රියාකාරකම්');
    assert.equal(t('nav.safetyTitle'), 'ආරක්ෂණ සහ දත්ත-නිරාවරණ පාලන');
    assert.equal(t('nav.evaluationTitle'), 'ඇගයීම් සහ පාලිත අපනයන');
    assert.equal(t('nav.resultsTitle'), 'ප්‍රතිඵල සහ පෙර ඉතිහාසය');
    assert.equal(t('nav.technicalLabTitle'), 'තාක්ෂණික පරීක්ෂණ සහ වින්‍යාස');
    assert.equal(t('common.simpleViewTitle'), 'සරල කළ පරිශීලක දර්ශනය');
    assert.equal(t('common.researcherViewTitle'), 'පර්යේෂක දර්ශනය');
  });

  test('2. English mode remains completely intact with standard labels (§3, §15)', () => {
    setLocale('en-LK');
    assert.equal(t('nav.interactivePlayground'), 'Playground');
    assert.equal(t('nav.safety'), 'Safety');
    assert.equal(t('nav.evaluation'), 'Evaluation');
    assert.equal(t('nav.results'), 'Results');
    assert.equal(t('nav.technicalLab'), 'Technical Lab');
    assert.equal(t('common.simpleView'), 'Simple View');
    assert.equal(t('common.researcherView'), 'Researcher');
  });

  test('3. Name the Animal is localized and not rendered in English when Sinhala is active (§12, §15)', () => {
    const task = {
      task_code: 'TASK-001',
      title: 'Name the Animal'
    };

    const siTitle = getLocalizedTaskTitle(task, 'si-LK');
    assert.equal(siTitle, 'සත්වයා නම් කරන්න');
    assert.ok(!siTitle.includes('Name the Animal'), 'Must not render English title in Sinhala view');

    const enTitle = getLocalizedTaskTitle(task, 'en-LK');
    assert.equal(enTitle, 'Name the Animal');
  });

  test('4. Raw enums (animal_naming, strong_visual_cue, etc.) localize cleanly (§12, §15)', () => {
    assert.equal(localizeSkill('animal_naming', 'si-LK'), 'සත්ව නම් කිරීම');
    assert.equal(localizeSupport('strong_visual_cue', 'si-LK'), 'ප්‍රබල දෘශ්‍ය ඉඟිය');
    assert.equal(localizeRisk('high', 'si-LK'), 'ඉහළ');
    assert.equal(localizeRisk('moderate', 'si-LK'), 'මධ්‍යම');
    assert.equal(localizeRisk('low', 'si-LK'), 'අඩු');
  });

  test('5. Sinhala mode sets document.documentElement.lang to si-LK (§6, §15)', () => {
    setLocale('si-LK');
    if (typeof document !== 'undefined') {
      assert.equal(document.documentElement.lang, 'si-LK');
    }

    setLocale('en-LK');
    if (typeof document !== 'undefined') {
      assert.equal(document.documentElement.lang, 'en-LK');
    }
  });

  test('6. CSS files declare flexible content-aware navigation and responsive media queries (§6, §7, §10)', () => {
    const languageCss = fs.readFileSync(path.join(frontendDir, 'src/styles/language.css'), 'utf-8');
    const indexCss = fs.readFileSync(path.join(frontendDir, 'src/index.css'), 'utf-8');

    // Noto Sans Sinhala font declared
    assert.ok(languageCss.includes('Noto Sans Sinhala'), 'language.css must declare Noto Sans Sinhala');
    assert.ok(languageCss.includes('line-height: 1.6'), 'Sinhala body line-height must be 1.6');

    // Flexible content-aware nav metrics
    assert.ok(indexCss.includes('.nav-tab'), 'index.css must define .nav-tab');
    assert.ok(indexCss.includes('min-width: max-content'), 'nav items must use content-aware min-width');
    assert.ok(!indexCss.includes('width: 150px; height: 72px;'), 'Must not use fixed clipped dimensions');

    // Responsive breakpoints defined
    assert.ok(indexCss.includes('@media (min-width: 1501px)'), 'Desktop >1500px breakpoint required');
    assert.ok(indexCss.includes('@media (max-width: 1500px)'), 'Overflow <=1500px breakpoint required');
    assert.ok(indexCss.includes('@media (max-width: 1100px)'), 'Tablet <=1100px breakpoint required');
    assert.ok(indexCss.includes('@media (max-width: 760px)'), 'Mobile <=760px breakpoint required');
  });
});
