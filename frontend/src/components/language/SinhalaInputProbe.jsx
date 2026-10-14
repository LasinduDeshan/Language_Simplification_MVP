import React, { useState } from 'react';
import { countGraphemes, validateGraphemeLimit } from '../../i18n/graphemeSegmenter.js';
import { t, getLocale } from '../../i18n/config.js';

export function SinhalaInputProbe({ maxGraphemes = 100, onVerify }) {
  const [text, setText] = useState('ක්‍ෂීරපායී සතුන්');
  const [verificationResult, setVerificationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const graphemeInfo = validateGraphemeLimit(text, maxGraphemes, getLocale());
  const rawLength = text.length; // UTF-16 code units

  const handleVerify = async () => {
    setIsLoading(true);
    try {
      // Calculate code points
      const codePoints = Array.from(text).map(c => `U+${c.codePointAt(0).toString(16).toUpperCase().padStart(4, '0')}`);
      const payload = {
        test_id: `PROBE-${Date.now()}`,
        payload: text,
        expected_code_points: codePoints,
        category: "interactive_probe"
      };

      const response = await fetch('/api/v1/localization/probe/round-trip', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        throw new Error(`HTTP error ${response.status}`);
      }

      const data = await response.json();
      setVerificationResult(data);
      if (onVerify) onVerify(data);
    } catch (err) {
      setVerificationResult({
        status: 'FAILED',
        error: err.message
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      className="sinhala-input-probe"
      id="sinhala-input-probe"
      style={{
        padding: '1.25rem',
        borderRadius: '12px',
        backgroundColor: 'var(--bg-surface-elevated, #1e293b)',
        border: '1px solid var(--border-color, rgba(255,255,255,0.1))',
        maxWidth: '600px',
        margin: '1rem 0'
      }}
    >
      <h3 style={{ margin: '0 0 0.75rem 0', fontSize: '1.1rem', color: 'var(--text-primary, #f8fafc)' }}>
        {t('probe.title')}
      </h3>

      <div style={{ marginBottom: '0.75rem' }}>
        <textarea
          id="sinhala-probe-textarea"
          className="sinhala-input"
          lang="si"
          rows={3}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={t('probe.input_placeholder')}
          style={{
            width: '100%',
            padding: '10px 12px',
            borderRadius: '8px',
            border: graphemeInfo.isValid ? '1px solid var(--border-color, rgba(255,255,255,0.2))' : '1px solid #ef4444',
            backgroundColor: 'var(--bg-primary, #0b0f19)',
            color: 'var(--text-primary, #f8fafc)',
            fontSize: '1rem',
            resize: 'vertical',
            outline: 'none',
            boxSizing: 'border-box'
          }}
        />
      </div>

      {/* Counters Display */}
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', color: 'var(--text-secondary, #94a3b8)', marginBottom: '1rem' }}>
        <div>
          <span>{t('probe.char_count')}: </span>
          <strong id="probe-grapheme-count" style={{ color: graphemeInfo.isValid ? '#10b981' : '#ef4444' }}>
            {graphemeInfo.count}
          </strong> / {maxGraphemes}
        </div>
        <div>
          <span>{t('probe.raw_length')}: </span>
          <span id="probe-raw-length">{rawLength}</span>
        </div>
      </div>

      <button
        id="probe-verify-button"
        onClick={handleVerify}
        disabled={isLoading || !graphemeInfo.isValid}
        style={{
          padding: '8px 16px',
          borderRadius: '8px',
          backgroundColor: 'var(--accent-primary, #6366f1)',
          color: '#ffffff',
          border: 'none',
          fontWeight: 600,
          cursor: isLoading ? 'not-allowed' : 'pointer',
          opacity: isLoading ? 0.7 : 1
        }}
      >
        {isLoading ? 'Verifying...' : t('probe.submit')}
      </button>

      {/* Verification Results */}
      {verificationResult && (
        <div
          id="probe-result-box"
          style={{
            marginTop: '1rem',
            padding: '0.75rem',
            borderRadius: '8px',
            backgroundColor: verificationResult.status === 'PASSED' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
            border: verificationResult.status === 'PASSED' ? '1px solid #10b981' : '1px solid #ef4444'
          }}
        >
          <div style={{ fontWeight: 600, color: verificationResult.status === 'PASSED' ? '#10b981' : '#ef4444', marginBottom: '4px' }}>
            {t('probe.result_title')}: {verificationResult.status}
          </div>
          {verificationResult.code_points && (
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary, #94a3b8)', wordBreak: 'break-all' }}>
              Code Points: {verificationResult.code_points.join(', ')}
            </div>
          )}
          {verificationResult.error && (
            <div style={{ fontSize: '0.85rem', color: '#ef4444' }}>
              {verificationResult.error}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SinhalaInputProbe;
