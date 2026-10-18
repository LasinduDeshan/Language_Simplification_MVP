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
  localizeStatus
} from './enumLocalization.js';

export {
  getLocalizedInstruction,
  getLocalizedOptions,
  getOptionEmoji,
  isSinhalaActive
} from './activityLocalization.js';

export {
  resolveLocale,
  isSupportedLocale,
  DEFAULT_LOCALE,
  LOCALE_REGISTRY
} from './localeRegistry.js';
