# Stage 29 — Sinhala Font Selection, Licensing, and Provenance Record

**Component:** Component 3 — Language Simplification MVP  
**Stage:** Stage 29 (Sinhala Database, UI and Font Support)  
**Font Family:** Noto Sans Sinhala  
**Licence:** SIL Open Font License 1.1 (OFL-1.1)  
**Redistribution Status:** ALLOWED  

---

## 1. Font Provenance Registry Details

```json
{
  "font_family": "Noto Sans Sinhala",
  "font_style": "normal",
  "font_weight": "400",
  "source_url": "https://raw.githubusercontent.com/googlefonts/noto-fonts/main/hinted/ttf/NotoSansSinhala/NotoSansSinhala-Regular.ttf",
  "upstream_filename": "NotoSansSinhala-Regular.ttf",
  "local_path": "frontend/public/fonts/NotoSansSinhala-Regular.ttf",
  "retrieved_timestamp": "2026-10-14T10:45:00Z",
  "licence_identifier": "OFL-1.1",
  "licence_source_url": "https://raw.githubusercontent.com/googlefonts/noto-fonts/main/LICENSE",
  "licence_local_path": "frontend/public/fonts/OFL.txt",
  "licence_file_sha256": "0dab92d0544f7b233403f14b84a663bdbfa746982eda629e7f4f9ffe1b036feb",
  "font_binary_sha256": "a966549310b2d3046ba25bbeef11985428ff9356fa656fd6118bc90fb82df031",
  "redistribution_allowed": true,
  "is_original_binary": true,
  "subsetting_tool": null,
  "fallback_stack": [
    "Noto Sans Sinhala",
    "Nirmala UI",
    "sans-serif"
  ],
  "verified_by": "infrastructure_team"
}
```

### Auditable Font Governance Evidence:
- **Commit-Pinned Upstream Source:** `googlefonts/noto-fonts` (main repository, commit `9cb517a6a7c36a495914fa060934d402be4b6118`)
- **Downloaded Filename & Version:** `NotoSansSinhala-Regular.ttf` (Version 2.004)
- **Font Binary SHA-256:** `a966549310b2d3046ba25bbeef11985428ff9356fa656fd6118bc90fb82df031`
- **OFL.txt Licence SHA-256:** `0dab92d0544f7b233403f14b84a663bdbfa746982eda629e7f4f9ffe1b036feb`
- **Redistribution Decision:** Permitted without royalty under SIL Open Font License, Version 1.1 (Sections 1 and 2).
- **Modification / Subsetting Status:** Untouched full binary (no glyph modification, re-encoding, or subsetting applied).

---

## 2. Font Loading & Fallback Stack

The font is declared locally via `@font-face` in `frontend/src/styles/fonts.css` and applied to `:lang(si)` and `:lang(si-LK)` in `frontend/src/styles/language.css`:

```css
@font-face {
  font-family: 'Noto Sans Sinhala';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/fonts/NotoSansSinhala-Regular.ttf') format('truetype');
}

:lang(si), :lang(si-LK) {
  font-family: 'Noto Sans Sinhala', 'Nirmala UI', sans-serif;
  line-height: 1.65;
}
```

### Fallback Evaluation:
- **Windows:** System font `Nirmala UI` (`C:\Windows\Fonts\Nirmala.ttc`) is present and acts as the native fallback if web font loading is offline or disabled.
- **Android / Linux / macOS:** Standard `sans-serif` and system Sinhala fonts provide readable fallback rendering.

---

## 3. Automated and Real-Browser Verification

- **Automated Registry Verification:** `test_font_registry_integrity.py` confirms that the local font binary and license file match the exact SHA-256 hashes recorded in `data/sinhala_foundation/registry/font_registry.json`.
- **Browser Loading Verification:** Playwright integration gate verifies HTTP status 200 on `/fonts/NotoSansSinhala-Regular.ttf`, resolution of `document.fonts.ready`, and `document.fonts.check("16px 'Noto Sans Sinhala'")`.
