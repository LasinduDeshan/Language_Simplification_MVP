import React, { useState, useEffect } from 'react';
import { getLocale, setLocale, subscribeLocale, t } from '../../i18n/config.js';

export function LanguageSelector({ id = "language-selector" }) {
  const [current, setCurrent] = useState(getLocale());
  const [announcement, setAnnouncement] = useState('');

  useEffect(() => {
    const unsubscribe = subscribeLocale(newLocale => {
      setCurrent(newLocale);
      const isSi = newLocale === 'si' || newLocale === 'si-LK';
      const msg = isSi
        ? 'භාෂාව සිංහල ලෙස වෙනස් විය'
        : 'Language changed to English';
      setAnnouncement(msg);
    });
    return unsubscribe;
  }, []);

  const handleChange = (e) => {
    const selected = e.target.value;
    setLocale(selected);
  };

  const selectedValue = (current === 'si' || current === 'si-LK') ? 'si-LK' : 'en-LK';

  return (
    <div className="language-selector-container" id={`${id}-container`} style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
      <label htmlFor={id} style={{ fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-secondary, #94a3b8)' }}>
        {t('language_selector.label')}:
      </label>
      <select
        id={id}
        value={selectedValue}
        onChange={handleChange}
        aria-label={t('language_selector.label')}
        style={{
          padding: '6px 12px',
          borderRadius: '8px',
          border: '1px solid var(--border-color, rgba(255,255,255,0.15))',
          backgroundColor: 'var(--bg-surface-elevated, #1e293b)',
          color: 'var(--text-primary, #f8fafc)',
          fontSize: '0.875rem',
          cursor: 'pointer',
          outline: 'none'
        }}
      >
        <option value="en-LK">{t('language_selector.english')}</option>
        <option value="si-LK">{t('language_selector.sinhala')}</option>
      </select>

      {/* Screen reader live region */}
      <span
        aria-live="polite"
        style={{ position: 'absolute', width: '1px', height: '1px', margin: '-1px', overflow: 'hidden', clip: 'rect(0,0,0,0)' }}
      >
        {announcement}
      </span>
    </div>
  );
}

export default LanguageSelector;
