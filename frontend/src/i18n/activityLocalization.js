/**
 * Dynamic Activity Content Localization
 * Provides language-aware activity instructions and answer options.
 * Follows the Section 8 contract:
 * - Child-facing views fail-closed or use approved Sinhala items when Sinhala is active.
 * - Researcher view shows marked fallbacks when Sinhala variant is missing.
 */
import { getLocale, t } from './config.js';

// Curated Sinhala translations for core seed tasks / activities
export const CURATED_ACTIVITY_SINHALA = {
  // TASK-001 / ACT-ANIMAL-001
  'TASK-001': {
    instruction: 'පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්දැයි කියන්න.',
    options: {
      'Cat': 'පූසා',
      'Dog': 'බල්ලා',
      'Rabbit': 'හාවා',
      'cat': 'පූසා',
      'dog': 'බල්ලා',
      'rabbit': 'හාවා'
    }
  },
  'ACT-ANIMAL-001': {
    instruction: 'පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්දැයි කියන්න.',
    options: {
      'Cat': 'පූසා',
      'Dog': 'බල්ලා',
      'Rabbit': 'හාවා',
      'cat': 'පූසා',
      'dog': 'බල්ලා',
      'rabbit': 'හාවා'
    }
  },
  // TASK-002 / ACT-OBJECT-001
  'TASK-002': {
    instruction: 'ලිවීම සඳහා භාවිත කරන්නේ කුමක්දැයි පෙන්වන්න.',
    options: {
      'Pencil': 'පැන්සල',
      'Book': 'පොත',
      'Apple': 'ඇපල්',
      'pencil': 'පැන්සල',
      'book': 'පොත',
      'apple': 'ඇපල්'
    }
  },
  // TASK-003 / ACT-BOOK-001
  'TASK-003': {
    instruction: 'පොතේ පින්තූරය සොයා තෝරන්න.',
    options: {
      'Book': 'පොත',
      'Pencil': 'පැන්සල',
      'Ball': 'බෝලය',
      'book': 'පොත',
      'pencil': 'පැන්සල',
      'ball': 'බෝලය'
    }
  },
  // TASK-006 / ACT-FOOD-001
  'TASK-006': {
    instruction: 'අපට ආහාරයට ගත හැකි දේ කුමක්දැයි පෙන්වන්න.',
    options: {
      'Apple': 'ඇපල්',
      'Car': 'මෝටර් රථය',
      'Book': 'පොත',
      'apple': 'ඇපල්',
      'car': 'මෝටර් රථය',
      'book': 'පොත'
    }
  },
  // TASK-007 / ACT-ODD-001
  'TASK-007': {
    instruction: 'මෙහි නොගැලපෙන රූපය තෝරන්න.',
    options: {}
  },
  // TASK-017 / ACT-SHAPE-001
  'TASK-017': {
    instruction: 'රතු පාට වෘත්තය ස්පර්ශ කරන්න.',
    options: {
      'Red Circle': 'රතු වෘත්තය',
      'Blue Square': 'නිල් සමචතුරස්‍රය',
      'Yellow Triangle': 'කහ ත්‍රිකෝණය'
    }
  }
};

// General fallback vocabulary for common option words
export const COMMON_OPTION_TRANSLATIONS = {
  'Cat': 'පූසා', 'cat': 'පූසා',
  'Dog': 'බල්ලා', 'dog': 'බල්ලා',
  'Rabbit': 'හාවා', 'rabbit': 'හාවා',
  'Pencil': 'පැන්සල', 'pencil': 'පැන්සල',
  'Book': 'පොත', 'book': 'පොත',
  'Apple': 'ඇපල්', 'apple': 'ඇපල්',
  'Banana': 'කෙසෙල්', 'banana': 'කෙසෙල්',
  'Car': 'මෝටර් රථය', 'car': 'මෝටර් රථය',
  'Fish': 'මාළුවා', 'fish': 'මාළුවා',
  'Tree': 'ගස', 'tree': 'ගස',
  'Yes': 'ඔව්', 'yes': 'ඔව්',
  'No': 'නැත', 'no': 'නැත',
  'Red': 'රතු', 'red': 'රතු',
  'Blue': 'නිල්', 'blue': 'නිල්',
  'Yellow': 'කහ', 'yellow': 'කහ',
  'Circle': 'වෘත්තය', 'circle': 'වෘත්තය',
  'Square': 'සමචතුරස්‍රය', 'square': 'සමචතුරස්‍රය',
  'Triangle': 'ත්‍රිකෝණය', 'triangle': 'ත්‍රිකෝණය',
  'Boy': 'පිරිමි ළමයා', 'boy': 'පිරිමි ළමයා',
  'Girl': 'ගැහැණු ළමයා', 'girl': 'ගැහැණු ළමයා',
  'Star': 'තරුව', 'star': 'තරුව',
  'Bell': 'ඝණ්ටාරය', 'bell': 'ඝණ්ටාරය'
};

export function isSinhalaActive() {
  const loc = getLocale();
  return loc === 'si' || loc === 'si-LK';
}

export function getLocalizedInstruction(activity, localeOrFallback = '', optionsOrChildFacing = false) {
  if (!activity) return '';

  let locale = null;
  let fallbackText = '';
  let isChildFacing = false;

  if (typeof localeOrFallback === 'string') {
    if (localeOrFallback === 'si' || localeOrFallback === 'si-LK' || localeOrFallback === 'en' || localeOrFallback === 'en-LK') {
      locale = localeOrFallback;
    } else {
      fallbackText = localeOrFallback;
    }
  }

  if (typeof optionsOrChildFacing === 'boolean') {
    isChildFacing = optionsOrChildFacing;
  } else if (typeof optionsOrChildFacing === 'object' && optionsOrChildFacing !== null) {
    if (optionsOrChildFacing.isChildView !== undefined) isChildFacing = Boolean(optionsOrChildFacing.isChildView);
    if (optionsOrChildFacing.isChildFacing !== undefined) isChildFacing = Boolean(optionsOrChildFacing.isChildFacing);
  }

  const activeLocale = locale || getLocale();
  const isSi = activeLocale === 'si' || activeLocale === 'si-LK';

  if (isSi) {
    // 1. Explicit multi-lingual instruction object { en: ..., si: ... }
    if (activity.instruction && typeof activity.instruction === 'object') {
      if (activity.instruction.si) return activity.instruction.si;
    }
    // 2. Direct property child_friendly_instruction_si
    if (activity.child_friendly_instruction_si) {
      return activity.child_friendly_instruction_si;
    }
    // 3. Curated activity lookup
    const code = activity.task_code || activity.activity_id || activity.id;
    if (code && CURATED_ACTIVITY_SINHALA[code]?.instruction) {
      return CURATED_ACTIVITY_SINHALA[code].instruction;
    }
    // 4. If presented_instruction is already Sinhala (contains Sinhala Unicode range 0D80-0DFF)
    const presented = activity.presented_instruction || activity.child_friendly_instruction;
    if (presented && /[\u0D80-\u0DFF]/.test(presented)) {
      return presented;
    }

    // 5. Missing Sinhala translation handling
    if (isChildFacing) {
      // Fail-closed child-friendly instruction
      return t('childModal.defaultInstruction', {}, 'si');
    } else {
      // Researcher view with marked technical fallback
      return `${t('common.fallbackWarning', {}, 'si')} ${presented || fallbackText}`;
    }
  }

  // English locale
  if (activity.instruction && typeof activity.instruction === 'object' && activity.instruction.en) {
    return activity.instruction.en;
  }
  return activity.presented_instruction || activity.child_friendly_instruction || fallbackText;
}

export function getLocalizedOptions(activity, localeOrOptions = null, maybeLocale = null) {
  let opts = [];
  let locale = null;

  if (Array.isArray(localeOrOptions)) {
    opts = localeOrOptions;
    if (typeof maybeLocale === 'string') locale = maybeLocale;
  } else if (typeof localeOrOptions === 'string') {
    locale = localeOrOptions;
  }

  if (opts.length === 0 && activity?.options) {
    opts = activity.options;
  }
  if (!opts || !Array.isArray(opts)) return [];

  const activeLocale = locale || getLocale();
  const isSi = activeLocale === 'si' || activeLocale === 'si-LK';

  const code = activity?.task_code || activity?.activity_id || activity?.id;
  const curated = code ? CURATED_ACTIVITY_SINHALA[code]?.options : null;

  return opts.map(opt => {
    let raw = '';
    let label = '';

    if (typeof opt === 'object' && opt !== null) {
      raw = opt.id || opt.raw || opt.label || String(opt);
      if (isSi) {
        label = opt.labels?.si || opt.si || (curated && opt.id && curated[opt.id]) || COMMON_OPTION_TRANSLATIONS[opt.id] || COMMON_OPTION_TRANSLATIONS[opt.label] || opt.label || raw;
      } else {
        label = opt.labels?.en || opt.en || opt.label || raw;
      }
    } else {
      raw = String(opt);
      if (isSi) {
        label = (curated && curated[raw]) || COMMON_OPTION_TRANSLATIONS[raw] || raw;
      } else {
        label = raw.charAt(0).toUpperCase() + raw.slice(1);
      }
    }

    return {
      raw,
      label,
      emoji: getOptionEmoji(raw || label)
    };
  });
}

export function getOptionEmoji(opt) {
  const o = String(opt).toLowerCase();
  if (o.includes('cat') || o.includes('පූසා')) return '🐱';
  if (o.includes('dog') || o.includes('බල්ලා')) return '🐶';
  if (o.includes('rabbit') || o.includes('හාවා')) return '🐰';
  if (o.includes('pencil') || o.includes('පැන්සල')) return '✏️';
  if (o.includes('book') || o.includes('පොත')) return '📖';
  if (o.includes('apple') || o.includes('ඇපල්')) return '🍎';
  if (o.includes('banana') || o.includes('කෙසෙල්')) return '🍌';
  if (o.includes('car') || o.includes('මෝටර් රථය')) return '🚗';
  if (o.includes('fish') || o.includes('මාළුවා') || o.includes('water')) return '🐟';
  if (o.includes('tree') || o.includes('ගස')) return '🌳';
  if (o.includes('circle') || o.includes('වෘත්තය')) return '🔴';
  if (o.includes('square') || o.includes('සමචතුරස්‍රය')) return '🟦';
  if (o.includes('star') || o.includes('තරුව')) return '⭐';
  if (o.includes('bell') || o.includes('ඝණ්ටාරය')) return '🔔';
  if (o.includes('yes') || o.includes('ඔව්')) return '👍';
  if (o.includes('no') || o.includes('නැත')) return '👎';
  if (o.includes('girl') || o.includes('ගැහැණු')) return '👧';
  if (o.includes('boy') || o.includes('පිරිමි')) return '👦';
  return '✨';
}
