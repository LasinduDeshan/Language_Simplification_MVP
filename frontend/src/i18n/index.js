export {
  t,
  getLocale,
  setLocale,
  subscribeLocale,
  SUPPORTED_LOCALES
} from './config.js';

export { useTranslation, useLocale } from './useTranslation.js';

export {
  localizeEnum,
  localizeSkill,
  localizeSupport,
  localizeRisk,
  localizeStatus,
  supportLabelKeys
} from './enumLocalization.js';

export {
  getLocalizedInstruction,
  getLocalizedOptions,
  getLocalizedTaskTitle,
  getOptionEmoji,
  isSinhalaActive,
  normalizeContentLocale,
  resolveLocalizedText,
  resolveLocalizedInstruction,
  normalizeActivityPayload,
  isUuid,
  validateDemonstrationActivity,
  DEMONSTRATION_ACTIVITIES,
  CURATED_ACTIVITY_SINHALA
} from './activityLocalization.js';

export {
  resolveLocale,
  isSupportedLocale,
  DEFAULT_LOCALE,
  LOCALE_REGISTRY
} from './localeRegistry.js';
