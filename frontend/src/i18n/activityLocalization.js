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
  'Touch the red circle.': 'රතු පාට වෘත්තය ස්පර්ශ කරන්න.',
  'Choose: cat or dog.': 'තෝරන්න: පූසා හෝ බල්ලා.',
  'Choose: cat, dog, or rabbit.': 'තෝරන්න: පූසා, බල්ලා හෝ හාවා.',
  'Choose: pencil or book.': 'තෝරන්න: පැන්සල හෝ පොත.',
  'Choose: apple or car.': 'තෝරන්න: ඇපල් හෝ මෝටර් රථය.',
  'Find the different one.': 'වෙනස් රූපය සොයන්න.',
  'Touch: circle or square.': 'තෝරන්න: රතු වෘත්තය හෝ නිල් සමචතුරස්‍රය.'
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

export function isUuid(str) {
  if (typeof str !== 'string') return false;
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(str.trim());
}

/**
 * Universal Multilingual Activity Adapter (§5)
 * Normalizes fixtures, Component 1/API activities, database-loaded tasks,
 * generated/personalized activities, and restored session state.
 */
export function normalizeActivityPayload(raw) {
  if (!raw || typeof raw !== 'object') return null;

  const rawTitle = raw.title;
  const rawInstruction = raw.instruction;

  const titleEn = (typeof rawTitle === 'object' && rawTitle !== null)
    ? (rawTitle.en ?? raw.title_en ?? null)
    : (raw.title_en ?? (typeof rawTitle === 'string' ? rawTitle : null));

  const titleSi = (typeof rawTitle === 'object' && rawTitle !== null)
    ? (rawTitle.si ?? raw.title_si ?? null)
    : (raw.title_si ?? null);

  const rawInstEn = (typeof rawInstruction === 'object' && rawInstruction !== null)
    ? (rawInstruction.en ?? raw.instruction_en ?? null)
    : (raw.instruction_en ?? (typeof rawInstruction === 'string' ? rawInstruction : null));

  const instructionEn = rawInstEn
    ?? raw.presented_instruction
    ?? raw.child_friendly_instruction
    ?? raw.instruction_shown
    ?? raw.original_instruction
    ?? null;

  const rawInstSi = (typeof rawInstruction === 'object' && rawInstruction !== null)
    ? (rawInstruction.si ?? raw.instruction_si ?? null)
    : (raw.instruction_si ?? null);

  const instructionSi = rawInstSi
    ?? raw.child_friendly_instruction_si
    ?? raw.presented_instruction_si
    ?? null;

  // Options normalization
  let options = raw.options ?? null;
  if (Array.isArray(options)) {
    options = options.map(opt => {
      if (typeof opt === 'object' && opt !== null) {
        return {
          id: opt.id ?? opt.raw ?? opt.label ?? String(opt),
          label: {
            en: opt.label?.en ?? opt.labels?.en ?? opt.en ?? (typeof opt.label === 'string' ? opt.label : (opt.raw || opt.id)),
            si: opt.label?.si ?? opt.labels?.si ?? opt.si ?? null,
          }
        };
      }
      return {
        id: String(opt),
        label: {
          en: String(opt),
          si: null
        }
      };
    });
  }

  return {
    ...raw,
    activity_id: raw.activity_id ?? raw.id ?? null,
    template_id: raw.template_id ?? raw.task_code ?? raw.code ?? null,
    task_code: raw.task_code ?? raw.template_id ?? null,
    title: {
      en: titleEn,
      si: titleSi,
    },
    instruction: {
      en: instructionEn,
      si: instructionSi,
    },
    options,
    content_language_status: raw.content_language_status ?? {
      en: instructionEn ? 'AVAILABLE' : 'UNAVAILABLE',
      si: instructionSi ? 'AVAILABLE' : 'UNAVAILABLE',
    }
  };
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
 * Resolves localized activity instruction following Section 6 Precedence:
 * 1. Use the activity's own non-empty instruction.si.
 * 2. Use a governed localization registry entry keyed by exact stable activity/template ID.
 * 3. In researcher view only, show English with a separate fallback warning.
 * 4. In simple/child preview, show the clean unavailable notice and no English instruction.
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

  // Normalize activity and taskContext payloads (§5)
  const normAct = normalizeActivityPayload(activity);
  const normTask = taskContext ? normalizeActivityPayload(taskContext) : null;

  // English requested: return English instruction cleanly
  if (!isSi) {
    return normAct?.instruction?.en
      || normTask?.instruction?.en
      || fallbackText
      || '';
  }

  // Precedence 1 (§6): Use activity's own non-empty instruction.si
  if (normAct?.instruction?.si && typeof normAct.instruction.si === 'string' && normAct.instruction.si.trim()) {
    return normAct.instruction.si.trim();
  }
  if (normTask?.instruction?.si && typeof normTask.instruction.si === 'string' && normTask.instruction.si.trim()) {
    return normTask.instruction.si.trim();
  }

  // Precedence 2 (§6): Use governed localization registry entry keyed by exact stable activity/template ID
  // Do NOT attempt to resolve a raw UUID through the demonstration registry
  const stableIdCandidate = normAct?.template_id
    || normTask?.template_id
    || normAct?.task_code
    || normTask?.task_code
    || (normAct?.activity_id && !isUuid(normAct.activity_id) ? normAct.activity_id : null)
    || (normAct?.id && !isUuid(normAct.id) ? normAct.id : null);

  if (stableIdCandidate) {
    if (DEMONSTRATION_ACTIVITIES[stableIdCandidate]?.instruction?.si) {
      return DEMONSTRATION_ACTIVITIES[stableIdCandidate].instruction.si;
    }
    if (CURATED_ACTIVITY_SINHALA[stableIdCandidate]?.instruction) {
      return CURATED_ACTIVITY_SINHALA[stableIdCandidate].instruction;
    }
  }

  // Also match curated known instruction strings if exact phrase has official Sinhala
  const enPresented = (normAct?.instruction?.en || normTask?.instruction?.en || '').trim();
  if (enPresented && KNOWN_INSTRUCTION_SINHALA[enPresented]) {
    return KNOWN_INSTRUCTION_SINHALA[enPresented];
  }

  // Precedence 3 & 4 (§6): Sinhala field missing
  if (isChildFacing || viewMode === 'simple') {
    // 4. In simple/child preview, show clean unavailable notice and no English instruction
    return t('localization.activityUnavailableInSinhala', {}, 'si') || 'මෙම ක්‍රියාකාරකම සිංහල භාෂාවෙන් තවම ලබා ගත නොහැක.';
  }

  // 3. In researcher view only, show English with a separate fallback warning
  return normAct?.instruction?.en || normTask?.instruction?.en || fallbackText || '';
}

/**
 * Returns structured result for instruction resolution including fallback metadata (§7).
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

  const normAct = normalizeActivityPayload(activity);
  const text = getLocalizedInstruction(activity, normLocale, context);
  const isSinhala = /[\u0D80-\u0DFF]/.test(text);
  const unavailableMsg = t('localization.activityUnavailableInSinhala', {}, 'si') || 'මෙම ක්‍රියාකාරකම සිංහල භාෂාවෙන් තවම ලබා ගත නොහැක.';
  const isUnavailable = text === unavailableMsg;
  const usedFallback = normLocale === 'si' && (!isSinhala || isUnavailable);

  const resolution = {
    text,
    requestedLocale: normLocale,
    resolvedLocale: isSinhala && !isUnavailable ? 'si' : (isUnavailable ? null : (text ? 'en' : null)),
    usedFallback,
    missing: !text || (normLocale === 'si' && isUnavailable)
  };

  // Section 7 debug logging (metadata only - never learner responses or protected text)
  if (typeof window !== 'undefined' && (window.__DEBUG_LOCALIZATION__ || window.__STAGE36_DEBUG__)) {
    console.debug("activity-localization", {
      activityId: normAct?.activity_id ?? null,
      templateId: normAct?.template_id ?? null,
      requestedLocale: normLocale,
      availableLocales: Object.keys(normAct?.instruction ?? {}).filter(k => Boolean(normAct?.instruction?.[k])),
      resolvedLocale: resolution.resolvedLocale,
      usedFallback: resolution.usedFallback,
      missing: resolution.missing,
    });
  }

  return resolution;
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
      const optLabelObj = typeof opt.label === 'object' && opt.label !== null ? opt.label : null;
      const optLabelStr = typeof opt.label === 'string' ? opt.label : null;
      const optLabelsObj = typeof opt.labels === 'object' && opt.labels !== null ? opt.labels : null;

      raw = (typeof opt.id === 'string' && opt.id)
        || (typeof opt.raw === 'string' && opt.raw)
        || optLabelStr
        || optLabelObj?.en
        || optLabelObj?.si
        || (opt.id ? String(opt.id) : (opt.raw ? String(opt.raw) : ''));

      if (isSi) {
        label = optLabelObj?.si
          || optLabelsObj?.si
          || (typeof opt.si === 'string' && opt.si)
          || (curated && opt.id && curated[opt.id])
          || (curated && curated[raw])
          || (opt.id && COMMON_OPTION_TRANSLATIONS[opt.id])
          || (optLabelStr && COMMON_OPTION_TRANSLATIONS[optLabelStr])
          || (raw && COMMON_OPTION_TRANSLATIONS[raw])
          || optLabelStr
          || optLabelObj?.en
          || raw;
      } else {
        label = optLabelObj?.en
          || optLabelsObj?.en
          || (typeof opt.en === 'string' && opt.en)
          || optLabelStr
          || (curated && opt.id && curated[opt.id])
          || raw;
      }

      if (typeof label === 'object' && label !== null) {
        label = label[activeLocale] || label.en || label.si || String(raw);
      }
      if (typeof raw === 'object' && raw !== null) {
        raw = raw[activeLocale] || raw.en || raw.si || String(raw);
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

    if (typeof label === 'object' && label !== null) {
      label = label[activeLocale] || label.en || label.si || String(raw);
    }
    if (typeof raw === 'object' && raw !== null) {
      raw = raw[activeLocale] || raw.en || raw.si || String(raw);
    }

    return {
      raw: String(raw),
      label: String(label),
      emoji: getOptionEmoji(raw || label)
    };
  });
}

export function getOptionEmoji(opt) {
  let text = '';
  if (typeof opt === 'string') {
    text = opt;
  } else if (typeof opt === 'object' && opt !== null) {
    text = opt.en || opt.si || (typeof opt.label === 'string' ? opt.label : (opt.label?.en || opt.label?.si)) || opt.id || '';
  }
  const o = String(text || '').toLowerCase();
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
      const titleStr = task.title.en || task.title.label || task.title.si;
      if (titleStr) return String(titleStr);
    }
    const code = task.task_code || task.activity_id || task.id;
    if (code && DEMONSTRATION_ACTIVITIES[code]?.title?.en) {
      return DEMONSTRATION_ACTIVITIES[code].title.en;
    }
    const res = task.title || task.name || '';
    return typeof res === 'object' && res !== null ? (res.en || res.si || '') : String(res || '');
  }

  // Sinhala mode
  if (typeof task.title === 'object' && task.title !== null) {
    if (task.title.si) return String(task.title.si);
    if (task.title.en) return String(task.title.en);
  }
  const code = task.task_code || task.activity_id || task.id;
  if (code && DEMONSTRATION_ACTIVITIES[code]?.title?.si) {
    return DEMONSTRATION_ACTIVITIES[code].title.si;
  }
  if (code && CURATED_ACTIVITY_SINHALA[code]?.title) {
    return CURATED_ACTIVITY_SINHALA[code].title;
  }
  const rawTitle = typeof task.title === 'string' ? task.title : (task.name || '');
  if (typeof rawTitle === 'object' && rawTitle !== null) {
    return String(rawTitle.si || rawTitle.en || '');
  }
  if (COMMON_TASK_TITLES[rawTitle]) {
    return COMMON_TASK_TITLES[rawTitle];
  }
  const translated = t('activity.nameTheAnimal', {}, activeLocale);
  if (String(rawTitle).toLowerCase().includes('animal') && translated !== 'activity.nameTheAnimal') {
    return translated;
  }
  return String(rawTitle || '');
}

/**
 * Universal safe string extractor that unwraps { en, si } objects or returns string representation
 */
export function safeText(val, locale = null) {
  if (val === null || val === undefined) return '';
  if (typeof val === 'string') return val;
  if (typeof val === 'object') {
    const activeLocale = normalizeContentLocale(locale || getLocale());
    return val[activeLocale] || val.si || val.en || '';
  }
  return String(val);
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
