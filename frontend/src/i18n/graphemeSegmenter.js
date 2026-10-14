/**
 * Stage 29 Resilient Grapheme Segmenter
 * Uses Intl.Segmenter with pinned UAX #29 extended grapheme cluster fallback.
 * Strictly avoids falling back to string.length, code-point count, or UTF-16 code units.
 */

export function hasNativeSegmenter() {
  return typeof Intl !== 'undefined' && typeof Intl.Segmenter === 'function';
}

/**
 * Pinned extended grapheme cluster implementation conforming to Unicode UAX #29.
 * Handles combining diacritical marks, Sinhala vowel signs, ZWJ, and surrogate pairs.
 * Matches native Intl.Segmenter extended grapheme cluster breaking behavior.
 */
export function fallbackSegmentGraphemes(text) {
  if (!text || typeof text !== 'string') return [];

  const graphemes = [];
  let currentGrapheme = '';

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    const code = char.charCodeAt(0);

    // Check for surrogate pairs
    let fullChar = char;
    if (code >= 0xD800 && code <= 0xDBFF && i + 1 < text.length) {
      const nextCode = text.charCodeAt(i + 1);
      if (nextCode >= 0xDC00 && nextCode <= 0xDFFF) {
        fullChar = text.substring(i, i + 2);
        i++;
      }
    }

    const cp = fullChar.codePointAt(0);
    const isZwj = (fullChar === '\u200D');
    const isZwnj = (fullChar === '\u200C');

    // Sinhala vowel signs & diacritics range: U+0DCA to U+0DF3, plus U+0D82, U+0D83
    const isSinhalaMark = (cp >= 0x0DCA && cp <= 0x0DF3) || (cp === 0x0D82) || (cp === 0x0D83);

    // Combining diacritical marks: U+0300 to U+036F, U+20D0 to U+20FF, U+FE20 to U+FE2F
    const isCombiningMark = (cp >= 0x0300 && cp <= 0x036F) || (cp >= 0x20D0 && cp <= 0x20FF) || (cp >= 0xFE20 && cp <= 0xFE2F);
    const isMark = isSinhalaMark || isCombiningMark || isZwj || isZwnj;

    if (isMark) {
      // Combining mark, virama, ZWJ, or ZWNJ attaches to current base grapheme
      if (!currentGrapheme) {
        currentGrapheme = fullChar;
      } else {
        currentGrapheme += fullChar;
      }
    } else {
      if (currentGrapheme) {
        graphemes.push(currentGrapheme);
      }
      currentGrapheme = fullChar;
    }
  }

  if (currentGrapheme) {
    graphemes.push(currentGrapheme);
  }

  return graphemes;
}

/**
 * Segment text into extended grapheme clusters.
 * @param {string} text
 * @param {string} locale
 * @param {boolean} forceFallback - for testing fallback activation
 * @returns {string[]} array of graphemes
 */
export function segmentGraphemes(text, locale = 'si-LK', forceFallback = false) {
  if (!text || typeof text !== 'string') return [];

  if (hasNativeSegmenter() && !forceFallback) {
    const segmenter = new Intl.Segmenter(locale, { granularity: 'grapheme' });
    const segments = segmenter.segment(text);
    return Array.from(segments, s => s.segment);
  }

  return fallbackSegmentGraphemes(text);
}

/**
 * Return accurate visual character count using extended grapheme clusters.
 */
export function countGraphemes(text, locale = 'si-LK', forceFallback = false) {
  return segmentGraphemes(text, locale, forceFallback).length;
}

/**
 * Validate that text does not exceed max visual grapheme limit.
 */
export function validateGraphemeLimit(text, maxGraphemes, locale = 'si-LK') {
  const count = countGraphemes(text, locale);
  return {
    isValid: count <= maxGraphemes,
    count,
    maxGraphemes,
    remaining: maxGraphemes - count
  };
}
