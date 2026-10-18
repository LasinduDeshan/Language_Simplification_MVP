import React, { useState, useEffect, useRef } from 'react';
import { Globe, ChevronDown, Check } from 'lucide-react';
import { getLocale, setLocale, subscribeLocale, t } from '../../i18n/config.js';

export function LanguageSelector({ id = "language-selector" }) {
  const [current, setCurrent] = useState(getLocale());
  const [isOpen, setIsOpen] = useState(false);
  const [announcement, setAnnouncement] = useState('');
  const containerRef = useRef(null);

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

  // Close on click outside and escape key (Plan §9)
  useEffect(() => {
    function handleClickOutside(event) {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, []);

  const isSi = current === 'si' || current === 'si-LK';
  const currentLabel = isSi ? t('language_selector.sinhala') : t('language_selector.english');

  const handleSelect = (localeCode) => {
    setLocale(localeCode);
    setIsOpen(false);
  };

  return (
    <div
      className="language-control"
      id={`${id}-container`}
      ref={containerRef}
      style={{ position: 'relative', display: 'inline-block' }}
    >
      <button
        id={id}
        type="button"
        className="language-trigger-btn"
        onClick={() => setIsOpen(prev => !prev)}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label={t('language_selector.label')}
        style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: '7px 12px',
          borderRadius: '10px',
          border: '1px solid var(--border-color, rgba(255, 255, 255, 0.15))',
          backgroundColor: 'rgba(30, 41, 59, 0.8)',
          color: 'var(--text-primary, #f8fafc)',
          fontSize: '0.85rem',
          fontWeight: 600,
          cursor: 'pointer',
          outline: 'none',
          transition: 'all 0.15s ease',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}
      >
        <Globe size={16} style={{ color: '#818cf8' }} />
        <span>{currentLabel}</span>
        <ChevronDown
          size={14}
          style={{
            transform: isOpen ? 'rotate(180deg)' : 'none',
            transition: 'transform 0.2s ease',
            color: 'var(--text-secondary, #94a3b8)'
          }}
        />
      </button>

      {isOpen && (
        <div
          className="language-menu"
          role="listbox"
          aria-label={t('language_selector.label')}
          style={{
            position: 'absolute',
            top: 'calc(100% + 8px)',
            right: 0,
            width: 'max-content',
            minWidth: '180px',
            padding: '6px',
            borderRadius: '12px',
            backgroundColor: '#111827',
            border: '1px solid var(--border-color, rgba(255,255,255,0.12))',
            boxShadow: '0 16px 36px rgba(0, 0, 0, 0.45)',
            zIndex: 1000,
            backdropFilter: 'blur(16px)',
            animation: 'fadeIn 0.15s ease-out'
          }}
        >
          <button
            type="button"
            role="option"
            aria-selected={!isSi}
            className={`language-option-item ${!isSi ? 'active' : ''}`}
            onClick={() => handleSelect('en-LK')}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '8px 12px',
              border: 0,
              borderRadius: '8px',
              backgroundColor: !isSi ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
              color: !isSi ? '#a5b4fc' : 'var(--text-primary, #f8fafc)',
              fontSize: '0.875rem',
              fontWeight: !isSi ? 700 : 500,
              cursor: 'pointer',
              textAlign: 'left'
            }}
          >
            <span>{t('language_selector.english')}</span>
            {!isSi && <Check size={16} style={{ color: '#818cf8' }} />}
          </button>

          <button
            type="button"
            role="option"
            aria-selected={isSi}
            className={`language-option-item ${isSi ? 'active' : ''}`}
            onClick={() => handleSelect('si-LK')}
            style={{
              width: '100%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '8px 12px',
              border: 0,
              borderRadius: '8px',
              backgroundColor: isSi ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
              color: isSi ? '#a5b4fc' : 'var(--text-primary, #f8fafc)',
              fontSize: '0.875rem',
              fontWeight: isSi ? 700 : 500,
              cursor: 'pointer',
              textAlign: 'left'
            }}
          >
            <span>{t('language_selector.sinhala')}</span>
            {isSi && <Check size={16} style={{ color: '#818cf8' }} />}
          </button>
        </div>
      )}

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
