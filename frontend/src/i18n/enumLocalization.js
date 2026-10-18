/**
 * Localized mappings for internal domain enums.
 * Prevents raw technical identifiers (e.g., animal_naming, strong_visual_cue)
 * from being rendered directly in user-facing UI.
 */
import { t, getLocale } from './config.js';

export const ENUM_CATEGORY_MAPS = {
  skills: {
    animal_naming: 'skills.animal_naming',
    object_identification: 'skills.object_identification',
    picture_matching: 'skills.picture_matching',
    vocabulary_expansion: 'skills.vocabulary_expansion',
    sentence_completion: 'skills.sentence_completion',
    instruction_following: 'skills.instruction_following',
    listening_comprehension: 'skills.listening_comprehension',
    phonological_awareness: 'skills.phonological_awareness',
    word_recognition: 'skills.word_recognition',
    reading_comprehension: 'skills.reading_comprehension'
  },
  support: {
    independent: 'support.independent',
    mild: 'support.mild',
    moderate: 'support.moderate',
    strong: 'support.strong',
    strong_visual_cue: 'support.strong_visual_cue',
    verbal_prompt: 'support.verbal_prompt',
    gestural_cue: 'support.gestural_cue',
    modeling: 'support.modeling',
    full_assistance: 'support.full_assistance'
  },
  risk: {
    low: 'risk.low',
    moderate: 'risk.moderate',
    high: 'risk.high',
    critical: 'risk.critical',
    unknown: 'risk.unknown'
  },
  status: {
    completed: 'status.completed',
    abandoned: 'status.abandoned',
    refused: 'status.refused',
    timeout: 'status.timeout',
    correct: 'status.correct',
    incorrect: 'status.incorrect',
    partially_correct: 'status.partially_correct',
    pass: 'status.pass',
    fail: 'status.fail',
    review: 'status.review',
    active: 'status.active',
    pending: 'status.pending'
  }
};

export function localizeEnum(category, value, locale = null) {
  if (!value) return '';
  const key = `${category}.${value}`;
  const translated = t(key, {}, locale);
  if (translated !== key) {
    return translated;
  }
  // Humanize fallback if no direct translation
  return String(value)
    .replace(/_/g, ' ')
    .replace(/\b\w/g, char => char.toUpperCase());
}

export const supportLabelKeys = {
  STRONG_CHILD_FRIENDLY: 'support.strongChildFriendly',
  MODERATE_CHILD_FRIENDLY: 'support.moderateChildFriendly',
  STANDARD: 'support.standard',
  strong_child_friendly: 'support.strongChildFriendly',
  moderate_child_friendly: 'support.moderateChildFriendly',
  standard: 'support.standard',
  strong: 'support.strongChildFriendly',
  moderate: 'support.moderateChildFriendly'
};

export function localizeSkill(skill, locale = null) {
  if (!skill) return '';
  if (String(skill).startsWith('skills.')) {
    const direct = t(skill, {}, locale);
    if (direct !== skill) return direct;
  }
  return localizeEnum('skills', skill, locale);
}

export function localizeSupport(support, locale = null) {
  if (!support) return '';
  if (String(support).startsWith('support.')) {
    const direct = t(support, {}, locale);
    if (direct !== support) return direct;
  }
  const key = supportLabelKeys[support] || supportLabelKeys[String(support).toUpperCase()] || supportLabelKeys[String(support).toLowerCase()];
  if (key) {
    const translated = t(key, {}, locale);
    if (translated !== key) {
      return translated;
    }
  }
  return localizeEnum('support', support, locale);
}

export function localizeRisk(risk, locale = null) {
  return localizeEnum('risk', risk, locale);
}

export function localizeStatus(status, locale = null) {
  return localizeEnum('status', status, locale);
}
