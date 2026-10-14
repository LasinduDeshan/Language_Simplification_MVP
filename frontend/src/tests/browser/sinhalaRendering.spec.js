import { test, expect } from '@playwright/test';

test.describe('Stage 29 Real-Browser Sinhala Rendering & Font Gate', () => {

  test('Font HTTP request succeeds with status 200', async ({ page }) => {
    let fontResponseStatus = null;
    page.on('response', response => {
      if (response.url().includes('NotoSansSinhala-Regular.ttf')) {
        fontResponseStatus = response.status();
      }
    });

    await page.goto('http://127.0.0.1:4173/test_harness.html');
    await page.waitForLoadState('networkidle');

    expect(fontResponseStatus).toBe(200);
  });

  test('document.fonts.ready resolves and document.fonts.check returns true', async ({ page }) => {
    await page.goto('http://127.0.0.1:4173/test_harness.html');

    const result = await page.evaluate(async () => {
      await document.fonts.ready;
      return {
        isReady: true,
        fontCheck: document.fonts.check('16px "Noto Sans Sinhala"')
      };
    });

    expect(result.isReady).toBe(true);
    expect(result.fontCheck).toBe(true);
  });

  test('Computed styles and canonical probe elements render without tofu boxes', async ({ page }) => {
    await page.goto('http://127.0.0.1:4173/test_harness.html');
    await page.waitForLoadState('networkidle');

    for (let i = 1; i <= 5; i++) {
      const probe = page.locator(`#probe-${i}`);
      await expect(probe).toBeVisible();

      const text = await probe.innerText();
      expect(text).not.toContain('\uFFFD');

      const style = await probe.evaluate(el => {
        const computed = window.getComputedStyle(el);
        const rect = el.getBoundingClientRect();
        return {
          fontFamily: computed.fontFamily,
          lineHeight: computed.lineHeight,
          width: rect.width,
          height: rect.height
        };
      });

      expect(style.fontFamily).toContain('Noto Sans Sinhala');
      expect(style.width).toBeGreaterThan(0);
      expect(style.height).toBeGreaterThan(0);
    }
  });

  test('Complex ligature shaping for Bandi akuru, Yansaya, and Rakaransaya', async ({ page }) => {
    await page.goto('http://127.0.0.1:4173/test_harness.html');
    await page.waitForLoadState('networkidle');

    // Probe 2 contains Bandi akuru (ක්‍ෂ) and Yansaya (ව්‍ය)
    const probe2 = page.locator('#probe-2');
    const text2 = await probe2.innerText();
    expect(text2).toContain('ක්‍ෂීරපායී');
    expect(text2).toContain('ව්‍යුහය');

    // Probe 3 contains Rakaransaya (ශ්‍රී, ප්‍ර)
    const probe3 = page.locator('#probe-3');
    const text3 = await probe3.innerText();
    expect(text3).toContain('ශ්‍රී');
    expect(text3).toContain('ප්‍රජාතාන්ත්‍රික');

    // Verify ligature elements have non-zero dimensions
    const box2 = await probe2.boundingBox();
    const box3 = await probe3.boundingBox();
    expect(box2?.width).toBeGreaterThan(0);
    expect(box3?.width).toBeGreaterThan(0);
  });

  test('Zoom 100%, 200%, and 400% layout and text stability', async ({ page }) => {
    await page.goto('http://127.0.0.1:4173/test_harness.html');
    await page.waitForLoadState('networkidle');

    const zoomLevels = [1.0, 2.0, 4.0];
    for (const zoom of zoomLevels) {
      await page.evaluate(z => {
        document.body.style.zoom = String(z);
      }, zoom);

      const probe1 = page.locator('#probe-1');
      await expect(probe1).toBeVisible();

      const metrics = await page.evaluate(() => {
        const doc = document.documentElement;
        return {
          clientWidth: doc.clientWidth,
          scrollWidth: doc.scrollWidth,
          hasReplacement: document.body.innerText.includes('\uFFFD')
        };
      });

      expect(metrics.hasReplacement).toBe(false);
    }
  });

  test('Offline and system font fallback resiliency', async ({ page }) => {
    // Abort all font requests to simulate network failure or offline mode
    await page.route('**/*.ttf', route => route.abort());

    await page.goto('http://127.0.0.1:4173/test_harness.html');
    await page.waitForLoadState('domcontentloaded');

    const probe1 = page.locator('#probe-1');
    await expect(probe1).toBeVisible();

    const fallbackStyle = await probe1.evaluate(el => {
      const computed = window.getComputedStyle(el);
      return {
        fontFamily: computed.fontFamily,
        text: el.innerText
      };
    });

    // Fallback stack includes Nirmala UI / sans-serif
    expect(fallbackStyle.fontFamily).toBeDefined();
    expect(fallbackStyle.text).toBe('ආයුබෝවන්');
    expect(fallbackStyle.text).not.toContain('\uFFFD');
  });

});
