# Stage 29 UI Rendering & Font Shaping Report

**Component:** Component 3 — AI/NLP-Based Language Simplification  
**Scope:** Real-Browser Chromium Rendering & Glyph Shaping Verification  
**Evaluation Browser:** Chrome/155.0.8059.41  
**Status:** COMPLETE (VERIFIED)  
**Date:** 2026-10-14  

---

## 1. Executive Summary

This report records the real-browser verification of Sinhala font loading, computed CSS typography, complex ligature shaping, and responsive layout across desktop (1280px), mobile (375px), and 200% zoom viewports.
The verification was executed directly in a genuine headless Chromium browser session via Chrome DevTools Protocol (CDP).

---

## 2. Font Loading & CSS Resolution

| Verification Check | Target / Expected | Observed Result | Status |
|---|---|---|---|
| Font Availability Check | `document.fonts.check('16px "Noto Sans Sinhala"')` | `True` | PASSED |
| Network TTF Resolution | `GET /fonts/NotoSansSinhala-Regular.ttf` | HTTP 200 (TrueType binary loaded) | PASSED |
| Computed Font Family | Includes `"Noto Sans Sinhala"` | Verified on all Sinhala DOM nodes | PASSED |
| Fallback Stack | `"Noto Sans Sinhala", "Nirmala UI", sans-serif` | Declared and verified in CSS | PASSED |

---

## 3. Canonical Probe Rendering & Complex Shaping

The five canonical Sinhala text probes and the interactive input probe were evaluated in the live DOM:

| Probe ID | Text Value | Computed Font Family | Font Size | Line Height | Bounding Box (px) | Disposition |
|---|---|---|---|---|---|---|
| `probe-1` | `ආයුබෝවන්` | `"Noto Sans Sinhala", "Nirmala UI", sans-serif` | `20px` | `33px` | `600.0x33.0` | PASSED |
| `probe-2` | `ක්‍ෂීරපායී සතුන්ගේ ව්‍යුහය` | `"Noto Sans Sinhala", "Nirmala UI", sans-serif` | `20px` | `33px` | `600.0x33.0` | PASSED |
| `probe-3` | `ශ්‍රී ලංකා ප්‍රජාතාන්ත්‍රික සමාජවාදී ජනරජය` | `"Noto Sans Sinhala", "Nirmala UI", sans-serif` | `20px` | `33px` | `600.0x33.0` | PASSED |
| `probe-4` | `Grade 1: සිංහල කියවීම (Reading - Level 1)` | `"Noto Sans Sinhala", "Nirmala UI", sans-serif` | `20px` | `33px` | `600.0x33.0` | PASSED |
| `probe-5` | `පිටුව 123 (අංක: 45)` | `"Noto Sans Sinhala", "Nirmala UI", sans-serif` | `20px` | `33px` | `600.0x33.0` | PASSED |
| `sinhala-input` | `අම්මා සහ තාත්තා` | `"Noto Sans Sinhala", "Nirmala UI", sans-serif` | `16px` | `25.6px` | `600.0x43.6` | PASSED |

### Complex Ligature Shaping Observations
1. **Bandi Akuru (`ක්‍ෂීරපායී`, Probe 2):** The sequence `ක` + `්` + `ZWJ` + `ෂ` shaped correctly into a single visual Bandi akuru ligature glyph without splitting or rendering orphan virama characters.
2. **Yansaya (`ව්‍යුහය`, Probe 2):** The sequence `ව` + `්` + `ZWJ` + `ය` shaped cleanly with the subjoined Yansaya loop.
3. **Rakaransaya (`ශ්‍රී`, Probe 3):** The sequence `ශ` + `්` + `ZWJ` + `ර` shaped cleanly into the combined Sri ligature.
4. **No Replacement Characters:** Zero instances of `\uFFFD` or blank tofu boxes observed across all evaluated elements.

---

## 4. Viewport & Responsive Layout Verification

| Viewport Profile | Width x Height | Layout Metrics | Tofu / Text Collision | Status |
|---|---|---|---|---|
| Desktop Default | 1280 x 800 px | Normal container flex, 1.65 line-height | None | PASSED |
| Mobile Emulation | 375 x 667 px | `scrollWidth = 375px`, `clientWidth = 375px` | None (Horizontal overflow: False) | PASSED |
| 200% Zoom Emulation | 1280 x 800 (Scale 2.0) | High-DPI subpixel glyph rasterization | None | PASSED |

Captured visual screenshots have been archived in `docs/screenshots/stage29/`:
- `desktop_1280.png`
- `mobile_375.png`
- `zoom_200.png`

---

## 5. Architectural Invariants & Governance

- **Child Delivery Exclusions:** None of these probes are approved for child delivery (`approved_for_child_delivery: false`).
- **Linguistic Processing:** Pure rendering verification only. No Stage 30 text normalization or simplification was applied.
- **Verification Disposition:** Real-browser rendering gate is **PASSED**.
