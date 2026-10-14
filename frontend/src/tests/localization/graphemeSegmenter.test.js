import { test, describe } from 'node:test';
import assert from 'node:assert/strict';
import {
  hasNativeSegmenter,
  segmentGraphemes,
  countGraphemes,
  validateGraphemeLimit,
  fallbackSegmentGraphemes
} from '../../i18n/graphemeSegmenter.js';

describe('Grapheme Segmenter Tests', () => {
  test('detects native Intl.Segmenter', () => {
    assert.equal(hasNativeSegmenter(), typeof Intl !== 'undefined' && typeof Intl.Segmenter === 'function');
  });

  test('correctly counts Sinhala Bandi akuru (ksha) as grapheme clusters (2 in UAX #29 vs 4 UTF-16 code units)', () => {
    const ksha = 'ක්‍ෂ'; // 4 UTF-16 code units (ක + ් + ZWJ + ෂ)
    assert.equal(ksha.length, 4);
    assert.equal(countGraphemes(ksha), 2);
  });

  test('correctly counts Sinhala word (amma) as 3 visual characters', () => {
    const word = 'අම්මා'; // 5 UTF-16 code units
    assert.equal(word.length, 5);
    assert.equal(countGraphemes(word), 3);
  });

  test('count equivalence between native segmenter and fallback implementation', () => {
    const testCases = [
      'ක්‍ෂ',
      'ශ්‍රී ලංකා',
      'ව්‍යවස්ථාව',
      'කෞතුකාගාරය',
      'Grade 1: කියවීම',
      'පිටුව 123 (අංක: 45)',
      'සතුටුයි 😊🎉',
      'Hello World',
      'සිංහල 🌟'
    ];

    for (const tc of testCases) {
      const nativeCount = countGraphemes(tc, 'si-LK', false);
      const fallbackCount = countGraphemes(tc, 'si-LK', true);
      assert.equal(
        fallbackCount,
        nativeCount,
        `Count mismatch for '${tc}': fallback=${fallbackCount}, native=${nativeCount}`
      );
    }
  });

  test('emoji and mixed script grapheme limits', () => {
    const textWithEmoji = 'සිංහල 🌟';
    const limitResult = validateGraphemeLimit(textWithEmoji, 10);
    assert.equal(limitResult.isValid, true);
    assert.equal(limitResult.count, 5); // 'සිං' + 'හ' + 'ල' + ' ' + '🌟'
  });
});
