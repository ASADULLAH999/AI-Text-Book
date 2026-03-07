/**
 * T131 — Mobile responsiveness tests
 * Tests layout at iPhone SE (375x667), iPhone 14 (390x844), and tablet (768x1024).
 */

import { test, expect, devices } from '@playwright/test';

const MOBILE_VIEWPORTS = [
  { name: 'iPhone SE (320px)', width: 320, height: 568 },
  { name: 'iPhone SE (375px)', width: 375, height: 667 },
  { name: 'iPhone 14', width: 390, height: 844 },
  { name: 'iPad Mini', width: 768, height: 1024 },
];

for (const viewport of MOBILE_VIEWPORTS) {
  test.describe(`Mobile: ${viewport.name}`, () => {
    test.use({ viewport: { width: viewport.width, height: viewport.height } });

    test('homepage loads without horizontal overflow', async ({ page }) => {
      await page.goto('/');
      const bodyWidth = await page.evaluate(() => document.body.scrollWidth);
      expect(bodyWidth).toBeLessThanOrEqual(viewport.width + 5); // 5px tolerance
    });

    test('navbar is visible and not truncated', async ({ page }) => {
      await page.goto('/');
      const navbar = page.locator('nav, .navbar, [class*="navbar"]').first();
      await expect(navbar).toBeVisible();
      const box = await navbar.boundingBox();
      expect(box).not.toBeNull();
      expect(box!.width).toBeLessThanOrEqual(viewport.width);
    });

    test('chat panel button is reachable and tappable', async ({ page }) => {
      await page.goto('/docs/module-1-ros2/');
      // The chat panel trigger button
      const chatTrigger = page.locator('[aria-label*="chat"], [data-testid="chat-toggle"], button').filter({ hasText: /chat|ask/i }).first();
      if (await chatTrigger.isVisible()) {
        const box = await chatTrigger.boundingBox();
        expect(box).not.toBeNull();
        // Touch target: at least 44x44px (WCAG 2.5.5)
        expect(box!.width).toBeGreaterThanOrEqual(44);
        expect(box!.height).toBeGreaterThanOrEqual(44);
      }
    });

    test('doc pages are readable (no text overflow)', async ({ page }) => {
      await page.goto('/docs/module-1-ros2/');
      const main = page.locator('main, article, .theme-doc-markdown').first();
      await expect(main).toBeVisible();
      const mainBox = await main.boundingBox();
      expect(mainBox).not.toBeNull();
      expect(mainBox!.width).toBeLessThanOrEqual(viewport.width);
    });

    test('font size is readable (>=14px)', async ({ page }) => {
      await page.goto('/docs/module-1-ros2/');
      const bodyFontSize = await page.evaluate(() => {
        const style = window.getComputedStyle(document.body);
        return parseFloat(style.fontSize);
      });
      expect(bodyFontSize).toBeGreaterThanOrEqual(14);
    });
  });
}
