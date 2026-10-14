import React, { useState, useEffect } from 'react';
import { t, subscribeLocale } from '../../i18n/config.js';

export function LocalizedText({ i18nKey, params = {}, as: Component = 'span', className = '', ...props }) {
  const [, setTick] = useState(0);

  useEffect(() => {
    const unsubscribe = subscribeLocale(() => setTick(t => t + 1));
    return unsubscribe;
  }, []);

  return (
    <Component className={className} {...props}>
      {t(i18nKey, params)}
    </Component>
  );
}

export default LocalizedText;
