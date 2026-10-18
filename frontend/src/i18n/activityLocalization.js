/**
 * Dynamic Activity Content Localization
 * Provides language-aware activity instructions and answer options.
 * Follows the Canonical Multilingual Activity Contract:
 * - Child-facing views fail-closed to approved Sinhala when Sinhala is active.
 * - Researcher view presents clean instructions and displays warnings in distinct status containers.
 * - Demonstrates language switching and localized dynamic content (demonstration UI support).
 */
import { getLocale, t } from './config.js';

// Canonical Demonstration Activities Contract (§4)
export const DEMONSTRATION_ACTIVITIES = {
  'ACT-ANIMAL-001': {
    activity_id: 'ACT-ANIMAL-001',
    activity_type: 'animal_naming',
    title: {
      en: 'Name the Animal',
      si: 'සත්වයා නම් කරන්න'
    },
    instruction: {
      en: 'Look at this picture. What animal do you see?',
      si: 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?'
    },
    options: [
      {
        id: 'cat',
        labels: {
          en: 'Cat',
          si: 'පූසා'
        }
      },
      {
        id: 'dog',
        labels: {
          en: 'Dog',
          si: 'බල්ලා'
        }
      },
      {
        id: 'rabbit',
        labels: {
          en: 'Rabbit',
          si: 'හාවා'
        }
      }
    ],
    target_skill: 'animal_naming',
    localization_status: {
      en: 'AVAILABLE',
      si: 'DRAFT_DEMONSTRATION'
    }
  },
  'ACT-OBJECT-001': {
    activity_id: 'ACT-OBJECT-001',
    activity_type: 'object_identification',
    title: {
      en: 'Object Identification',
      si: 'වස්තු හඳුනාගැනීම'
    },
    instruction: {
      en: 'Show what we use to write with.',
      si: 'ලිවීම සඳහා භාවිත කරන්නේ කුමක්දැයි පෙන්වන්න.'
    },
    options: [
      {
        id: 'pencil',
        labels: {
          en: 'Pencil',
          si: 'පැන්සල'
        }
      },
      {
        id: 'book',
        labels: {
          en: 'Book',
          si: 'පොත'
        }
      },
      {
        id: 'apple',
        labels: {
          en: 'Apple',
          si: 'ඇපල්'
        }
      }
    ],
    target_skill: 'object_identification',
    localization_status: {
      en: 'AVAILABLE',
      si: 'DRAFT_DEMONSTRATION'
    }
  },
  'ACT-BOOK-001': {
    activity_id: 'ACT-BOOK-001',
    activity_type: 'picture_matching',
    title: {
      en: 'Book Finder',
      si: 'පොත සෙවීම'
    },
    instruction: {
      en: 'Find and touch the book.',
      si: 'පොතේ පින්තූරය සොයා තෝරන්න.'
    },
    options: [
      {
        id: 'book',
        labels: {
          en: 'Book',
          si: 'පොත'
        }
      },
      {
        id: 'pencil',
        labels: {
          en: 'Pencil',
          si: 'පැන්සල'
        }
      },
      {
        id: 'ball',
        labels: {
          en: 'Ball',
          si: 'බෝලය'
        }
      }
    ],
    target_skill: 'picture_matching',
    localization_status: {
      en: 'AVAILABLE',
      si: 'DRAFT_DEMONSTRATION'
    }
  },
  'ACT-FOOD-001': {
    activity_id: 'ACT-FOOD-001',
    activity_type: 'category_recognition',
    title: {
      en: 'Food Selection',
      si: 'ආහාර තේරීම'
    },
    instruction: {
      en: 'Show what we can eat.',
      si: 'අපට ආහාරයට ගත හැකි දේ කුමක්දැයි පෙන්වන්න.'
    },
    options: [
      {
        id: 'apple',
        labels: {
          en: 'Apple',
          si: 'ඇපල්'
        }
      },
      {
        id: 'car',
        labels: {
          en: 'Car',
          si: 'මෝටර් රථය'
        }
      },
      {
        id: 'book',
        labels: {
          en: 'Book',
          si: 'පොත'
        }
      }
    ],
    target_skill: 'category_recognition',
    localization_status: {
      en: 'AVAILABLE',
      si: 'DRAFT_DEMONSTRATION'
    }
  },
  'ACT-ODD-001': {
    activity_id: 'ACT-ODD-001',
    activity_type: 'odd_one_out',
    title: {
      en: 'Odd One Out',
      si: 'නොගැලපෙන රූපය සෙවීම'
    },
    instruction: {
      en: 'Find the picture that does not belong.',
      si: 'මෙහි නොගැලපෙන රූපය තෝරන්න.'
    },
    options: [
      {
        id: 'apple',
        labels: {
          en: 'Apple',
          si: 'ඇපල්'
        }
      },
      {
        id: 'banana',
        labels: {
          en: 'Banana',
          si: 'කෙසෙල්'
        }
      },
      {
        id: 'car',
        labels: {
          en: 'Car',
          si: 'මෝටර් රථය'
        }
      }
    ],
    target_skill: 'odd_one_out',
    localization_status: {
      en: 'AVAILABLE',
      si: 'DRAFT_DEMONSTRATION'
    }
  },
  'ACT-SHAPE-001': {
    activity_id: 'ACT-SHAPE-001',
    activity_type: 'shape_match',
    title: {
      en: 'Shape Match',
      si: 'හැඩතල ගැලපීම'
    },
    instruction: {
      en: 'Touch the red circle.',
      si: 'රතු පාට වෘත්තය ස්පර්ශ කරන්න.'
    },
    options: [
      {
        id: 'circle',
        labels: {
          en: 'Red Circle',
          si: 'රතු වෘත්තය'
        }
      },
      {
        id: 'square',
        labels: {
          en: 'Blue Square',
          si: 'නිල් සමචතුරස්‍රය'
        }
      },
      {
        id: 'triangle',
        labels: {
          en: 'Yellow Triangle',
          si: 'කහ ත්‍රිකෝණය'
        }
      }
    ],
    target_skill: 'shape_match',
    localization_status: {
      en: 'AVAILABLE',
      si: 'DRAFT_DEMONSTRATION'
    }
  }
};

// Aliases for task codes across systems
DEMONSTRATION_ACTIVITIES['TASK-001'] = DEMONSTRATION_ACTIVITIES['ACT-ANIMAL-001'];
DEMONSTRATION_ACTIVITIES['VOC-NAMING-001'] = DEMONSTRATION_ACTIVITIES['ACT-ANIMAL-001'];
DEMONSTRATION_ACTIVITIES['TASK-002'] = DEMONSTRATION_ACTIVITIES['ACT-OBJECT-001'];
DEMONSTRATION_ACTIVITIES['VOC-NAMING-002'] = DEMONSTRATION_ACTIVITIES['ACT-OBJECT-001'];
DEMONSTRATION_ACTIVITIES['TASK-003'] = DEMONSTRATION_ACTIVITIES['ACT-BOOK-001'];
DEMONSTRATION_ACTIVITIES['VOC-MATCH-001'] = DEMONSTRATION_ACTIVITIES['ACT-BOOK-001'];
DEMONSTRATION_ACTIVITIES['TASK-006'] = DEMONSTRATION_ACTIVITIES['ACT-FOOD-001'];
DEMONSTRATION_ACTIVITIES['VOC-CAT-001'] = DEMONSTRATION_ACTIVITIES['ACT-FOOD-001'];
DEMONSTRATION_ACTIVITIES['TASK-007'] = DEMONSTRATION_ACTIVITIES['ACT-ODD-001'];
DEMONSTRATION_ACTIVITIES['VOC-ODD-001'] = DEMONSTRATION_ACTIVITIES['ACT-ODD-001'];
DEMONSTRATION_ACTIVITIES['TASK-017'] = DEMONSTRATION_ACTIVITIES['ACT-SHAPE-001'];

// Curated Sinhala translations for core seed tasks / activities
export const CURATED_ACTIVITY_SINHALA = {
  'TASK-001': {
    title: 'සත්වයා නම් කරන්න',
    instruction: 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?',
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
    title: 'සත්වයා නම් කරන්න',
    instruction: 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?',
    options: {
      'Cat': 'පූසා',
      'Dog': 'බල්ලා',
      'Rabbit': 'හාවා',
      'cat': 'පූසා',
      'dog': 'බල්ලා',
      'rabbit': 'හාවා'
    }
  },
  'VOC-NAMING-001': {
    title: 'සත්වයා නම් කරන්න',
    instruction: 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?',
    options: {
      'Cat': 'පූසා',
      'Dog': 'බල්ලා',
      'Rabbit': 'හාවා',
      'cat': 'පූසා',
      'dog': 'බල්ලා',
      'rabbit': 'හාවා'
    }
  },
  'TASK-002': {
    title: 'වස්තු හඳුනාගැනීම',
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
  'ACT-OBJECT-001': {
    title: 'වස්තු හඳුනාගැනීම',
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
  'VOC-NAMING-002': {
    title: 'වස්තු හඳුනාගැනීම',
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
  'TASK-003': {
    title: 'පොත සෙවීම',
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
  'ACT-BOOK-001': {
    title: 'පොත සෙවීම',
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
  'VOC-MATCH-001': {
    title: 'පොත සෙවීම',
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
  'TASK-006': {
    title: 'ආහාර තේරීම',
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
  'ACT-FOOD-001': {
    title: 'ආහාර තේරීම',
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
  'VOC-CAT-001': {
    title: 'ආහාර තේරීම',
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
  'TASK-007': {
    title: 'නොගැලපෙන රූපය සෙවීම',
    instruction: 'මෙහි නොගැලපෙන රූපය තෝරන්න.',
    options: {}
  },
  'ACT-ODD-001': {
    title: 'නොගැලපෙන රූපය සෙවීම',
    instruction: 'මෙහි නොගැලපෙන රූපය තෝරන්න.',
    options: {}
  },
  'VOC-ODD-001': {
    title: 'නොගැලපෙන රූපය සෙවීම',
    instruction: 'මෙහි නොගැලපෙන රූපය තෝරන්න.',
    options: {}
  },
  'TASK-017': {
    title: 'හැඩතල ගැලපීම',
    instruction: 'රතු පාට වෘත්තය ස්පර්ශ කරන්න.',
    options: {
      'Red Circle': 'රතු වෘත්තය',
      'Blue Square': 'නිල් සමචතුරස්‍රය',
      'Yellow Triangle': 'කහ ත්‍රිකෝණය'
    }
  },
  'ACT-SHAPE-001': {
    title: 'හැඩතල ගැලපීම',
    instruction: 'රතු පාට වෘත්තය ස්පර්ශ කරන්න.',
    options: {
      'Red Circle': 'රතු වෘත්තය',
      'Blue Square': 'නිල් සමචතුරස්‍රය',
      'Yellow Triangle': 'කහ ත්‍රිකෝණය'
    }
  }
};

export const COMMON_TASK_TITLES = {
  'Name the Animal': 'සත්වයා නම් කරන්න',
  'Object Identification': 'වස්තු හඳුනාගැනීම',
  'Book Finder': 'පොත සෙවීම',
  'Food Selection': 'ආහාර තේරීම',
  'Odd One Out': 'නොගැලපෙන රූපය සෙවීම',
  'Shape Match': 'හැඩතල ගැලපීම'
};

// Known instruction string translations
export const KNOWN_INSTRUCTION_SINHALA = {
  'Look at this picture. What animal do you see?': 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?',
  'What animal is this?': 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?',
  'Look at the picture. Tell me what animal you see.': 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?',
  'Look at the animal. What is it?': 'මෙම පින්තූරය බලන්න. ඔබට පෙනෙන සත්වයා කුමක්ද?',
  'Show what we use to write with.': 'ලිවීම සඳහා භාවිත කරන්නේ කුමක්දැයි පෙන්වන්න.',
  'Find and touch the book.': 'පොතේ පින්තූරය සොයා තෝරන්න.',
  'Show what we can eat.': 'අපට ආහාරයට ගත හැකි දේ කුමක්දැයි පෙන්වන්න.',
  'Find the picture that does not belong.': 'මෙහි නොගැලපෙන රූපය තෝරන්න.',
  'Touch the red circle.': 'රතු පාට වෘත්තය ස්පර්ශ කරන්න.'
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

// Locale Normalization (§5)
export function normalizeContentLocale(locale) {
  if (!locale) return 'en';
  const normalized = String(locale).toLowerCase().trim();
  if (normalized === 'si' || normalized.startsWith('si-') || normalized.startsWith('si_')) {
    return 'si';
  }
  return 'en';
}

export function isSinhalaActive() {
  const loc = getLocale();
  return normalizeContentLocale(loc) === 'si';
}

// Localized Content Resolver (§6)
export function resolveLocalizedText(values, requestedLocale = 'en') {
  const normLocale = normalizeContentLocale(requestedLocale);

  if (typeof values === 'object' && values !== null) {
    const requestedText = values[normLocale]?.trim();
    if (requestedText) {
      return {
        text: requestedText,
        requestedLocale: normLocale,
        resolvedLocale: normLocale,
        usedFallback: false,
        missing: false
      };
    }

    const englishText = values.en?.trim();
    if (englishText) {
      return {
        text: englishText,
        requestedLocale: normLocale,
        resolvedLocale: 'en',
        usedFallback: normLocale !== 'en',
        missing: false
      };
    }

    return {
      text: '',
      requestedLocale: normLocale,
      resolvedLocale: null,
      usedFallback: false,
      missing: true
    };
  }

  if (typeof values === 'string' && values.trim()) {
    const isSinhala = /[\u0D80-\u0DFF]/.test(values);
    if (isSinhala) {
      return {
        text: values.trim(),
        requestedLocale: normLocale,
        resolvedLocale: 'si',
        usedFallback: normLocale !== 'si',
        missing: false
      };
    } else {
      return {
        text: values.trim(),
        requestedLocale: normLocale,
        resolvedLocale: 'en',
        usedFallback: normLocale !== 'en',
        missing: false
      };
    }
  }

  return {
    text: '',
    requestedLocale: normLocale,
    resolvedLocale: null,
    usedFallback: false,
    missing: true
  };
}

/**
 * Resolves localized activity instruction.
 * Section 8 contract: Never prepends technical warnings into the instruction text.
 * Simple View fails-closed to localized unavailable message when Sinhala is absent.
 * Researcher View returns clean English text so the caller can render warnings separately.
 */
export function getLocalizedInstruction(activity, localeOrFallback = '', optionsOrContext = false) {
  if (!activity) return '';

  let locale = null;
  let fallbackText = '';
  let isChildFacing = false;
  let viewMode = 'simple';
  let taskContext = null;

  if (typeof localeOrFallback === 'string') {
    const norm = normalizeContentLocale(localeOrFallback);
    if (localeOrFallback === 'si' || localeOrFallback.toLowerCase().startsWith('si-') || localeOrFallback.toLowerCase().startsWith('si_') || localeOrFallback === 'en' || localeOrFallback.toLowerCase().startsWith('en-')) {
      locale = norm;
    } else {
      fallbackText = localeOrFallback;
    }
  }

  if (typeof optionsOrContext === 'boolean') {
    isChildFacing = optionsOrContext;
    viewMode = optionsOrContext ? 'simple' : 'researcher';
  } else if (typeof optionsOrContext === 'object' && optionsOrContext !== null) {
    if (optionsOrContext.isChildView !== undefined) isChildFacing = Boolean(optionsOrContext.isChildView);
    if (optionsOrContext.isChildFacing !== undefined) isChildFacing = Boolean(optionsOrContext.isChildFacing);
    if (optionsOrContext.viewMode) {
      viewMode = optionsOrContext.viewMode;
      if (viewMode === 'simple') isChildFacing = true;
    }
    if (optionsOrContext.task) taskContext = optionsOrContext.task;
  }

  const activeLocale = normalizeContentLocale(locale || getLocale());
  const isSi = activeLocale === 'si';

  // 1. Explicit canonical multi-lingual instruction object { en: ..., si: ... }
  const instructionObj = (activity.instruction && typeof activity.instruction === 'object')
    ? activity.instruction
    : (taskContext?.instruction && typeof taskContext.instruction === 'object' ? taskContext.instruction : null);

  if (instructionObj) {
    const res = resolveLocalizedText(instructionObj, activeLocale);
    if (!res.missing) {
      if (!res.usedFallback || !isSi) {
        return res.text;
      }
      // Sinhala requested but missing from object
      if (isChildFacing || viewMode === 'simple') {
        return t('localization.activityUnavailableInSinhala', {}, 'si') || 'මෙම ක්‍රියාකාරකම සිංහල භාෂාවෙන් තවම ලබා ගත නොහැක.';
      }
      return res.text; // Clean English in researcher view
    }
  }

  // 2. Direct property child_friendly_instruction_si
  if (isSi && (activity.child_friendly_instruction_si || taskContext?.child_friendly_instruction_si)) {
    return activity.child_friendly_instruction_si || taskContext.child_friendly_instruction_si;
  }

  // 3. Demo activity lookup by code
  const code = activity.task_code || activity.activity_id || activity.id || taskContext?.task_code || taskContext?.activity_id || taskContext?.id;
  if (code) {
    if (DEMONSTRATION_ACTIVITIES[code]) {
      const demo = DEMONSTRATION_ACTIVITIES[code];
      const res = resolveLocalizedText(demo.instruction, activeLocale);
      if (!res.missing && (!res.usedFallback || !isSi)) {
        return res.text;
      }
    }
    if (CURATED_ACTIVITY_SINHALA[code]) {
      if (isSi) {
        return CURATED_ACTIVITY_SINHALA[code].instruction;
      }
    }
  }

  // 4. Match by English instruction text if known
  const presented = activity.presented_instruction || activity.child_friendly_instruction || activity.instruction_shown || activity.original_instruction;
  if (isSi && presented) {
    if (/[\u0D80-\u0DFF]/.test(presented)) {
      return presented;
    }
    const cleanPresented = presented.trim();
    if (KNOWN_INSTRUCTION_SINHALA[cleanPresented]) {
      return KNOWN_INSTRUCTION_SINHALA[cleanPresented];
    }
  }

  // 5. If English locale, return English text cleanly
  if (!isSi) {
    if (activity.instruction && typeof activity.instruction === 'object' && activity.instruction.en) {
      return activity.instruction.en;
    }
    if (activity.presented_instruction || activity.child_friendly_instruction) {
      return activity.presented_instruction || activity.child_friendly_instruction;
    }
    if (code && DEMONSTRATION_ACTIVITIES[code]?.instruction?.en) {
      return DEMONSTRATION_ACTIVITIES[code].instruction.en;
    }
    return presented || fallbackText;
  }

  // 6. Sinhala missing handling: Fail closed in Simple View, return clean English in Researcher View
  if (isChildFacing || viewMode === 'simple') {
    return t('localization.activityUnavailableInSinhala', {}, 'si') || 'මෙම ක්‍රියාකාරකම සිංහල භාෂාවෙන් තවම ලබා ගත නොහැක.';
  } else {
    // Researcher view returns clean text (technical marker is rendered outside in container)
    return presented || fallbackText;
  }
}

/**
 * Returns structured result for instruction resolution including fallback metadata.
 */
export function resolveLocalizedInstruction(activity, locale = null, context = {}) {
  const normLocale = normalizeContentLocale(locale || getLocale());
  let isChildFacing = false;
  let viewMode = 'simple';
  if (typeof context === 'boolean') {
    isChildFacing = context;
    viewMode = context ? 'simple' : 'researcher';
  } else if (typeof context === 'object' && context !== null) {
    if (context.isChildView !== undefined) isChildFacing = Boolean(context.isChildView);
    if (context.isChildFacing !== undefined) isChildFacing = Boolean(context.isChildFacing);
    if (context.viewMode) {
      viewMode = context.viewMode;
      if (viewMode === 'simple') isChildFacing = true;
    }
  }

  const text = getLocalizedInstruction(activity, normLocale, context);
  const isSinhala = /[\u0D80-\u0DFF]/.test(text);
  const unavailableMsg = t('localization.activityUnavailableInSinhala', {}, 'si') || 'මෙම ක්‍රියාකාරකම සිංහල භාෂාවෙන් තවම ලබා ගත නොහැක.';
  const isUnavailable = text === unavailableMsg;
  const usedFallback = normLocale === 'si' && (!isSinhala || isUnavailable);

  return {
    text,
    requestedLocale: normLocale,
    resolvedLocale: isSinhala && !isUnavailable ? 'si' : (text ? 'en' : null),
    usedFallback,
    missing: !text
  };
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

  const activeLocale = normalizeContentLocale(locale || getLocale());
  const isSi = activeLocale === 'si';

  const code = activity?.task_code || activity?.activity_id || activity?.id;
  const curated = code ? CURATED_ACTIVITY_SINHALA[code]?.options : null;
  const demoActivity = code ? DEMONSTRATION_ACTIVITIES[code] : null;

  return opts.map(opt => {
    let raw = '';
    let label = '';

    if (typeof opt === 'object' && opt !== null) {
      raw = opt.id || opt.raw || opt.label || String(opt);
      if (isSi) {
        label = opt.labels?.si || opt.si || (curated && opt.id && curated[opt.id]) || (curated && curated[raw]) || COMMON_OPTION_TRANSLATIONS[opt.id] || COMMON_OPTION_TRANSLATIONS[opt.label] || opt.label || raw;
      } else {
        label = opt.labels?.en || opt.en || opt.label || raw;
      }
    } else {
      raw = String(opt);
      if (isSi) {
        const demoOpt = demoActivity?.options?.find(o => o.id === raw || o.id === raw.toLowerCase());
        label = demoOpt?.labels?.si || (curated && curated[raw]) || (curated && curated[raw.toLowerCase()]) || COMMON_OPTION_TRANSLATIONS[raw] || COMMON_OPTION_TRANSLATIONS[raw.toLowerCase()] || raw;
      } else {
        const demoOpt = demoActivity?.options?.find(o => o.id === raw || o.id === raw.toLowerCase());
        label = demoOpt?.labels?.en || raw.charAt(0).toUpperCase() + raw.slice(1);
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

export function getLocalizedTaskTitle(task, locale = null) {
  if (!task) return '';
  const activeLocale = normalizeContentLocale(locale || getLocale());
  const isSi = activeLocale === 'si';

  if (!isSi) {
    if (typeof task.title === 'object' && task.title !== null) {
      return task.title.en || task.title.label || '';
    }
    const code = task.task_code || task.activity_id || task.id;
    if (code && DEMONSTRATION_ACTIVITIES[code]?.title?.en) {
      return DEMONSTRATION_ACTIVITIES[code].title.en;
    }
    return task.title || task.name || '';
  }

  // Sinhala mode
  if (typeof task.title === 'object' && task.title !== null) {
    if (task.title.si) return task.title.si;
  }
  const code = task.task_code || task.activity_id || task.id;
  if (code && DEMONSTRATION_ACTIVITIES[code]?.title?.si) {
    return DEMONSTRATION_ACTIVITIES[code].title.si;
  }
  if (code && CURATED_ACTIVITY_SINHALA[code]?.title) {
    return CURATED_ACTIVITY_SINHALA[code].title;
  }
  const rawTitle = typeof task.title === 'string' ? task.title : (task.name || '');
  if (COMMON_TASK_TITLES[rawTitle]) {
    return COMMON_TASK_TITLES[rawTitle];
  }
  const translated = t('activity.nameTheAnimal', {}, activeLocale);
  if (rawTitle.toLowerCase().includes('animal') && translated !== 'activity.nameTheAnimal') {
    return translated;
  }
  return rawTitle;
}

// Demonstration Activity Validator (§10)
export function validateDemonstrationActivity(activity) {
  const errors = [];

  if (!activity?.title?.en?.trim()) errors.push("MISSING_TITLE_EN");
  if (!activity?.title?.si?.trim()) errors.push("MISSING_TITLE_SI");
  if (!activity?.instruction?.en?.trim()) errors.push("MISSING_INSTRUCTION_EN");
  if (!activity?.instruction?.si?.trim()) errors.push("MISSING_INSTRUCTION_SI");

  for (const option of activity?.options ?? []) {
    if (!option.labels?.en?.trim()) {
      errors.push(`MISSING_OPTION_EN:${option.id}`);
    }
    if (!option.labels?.si?.trim()) {
      errors.push(`MISSING_OPTION_SI:${option.id}`);
    }
  }

  return errors;
}
