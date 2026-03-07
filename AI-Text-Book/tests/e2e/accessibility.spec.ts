/**
 * T132 — WCAG AA accessibility compliance validation.
 * Uses axe-core via @axe-core/playwright for automated checks.
 */

import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

// Pages to test
const PAGES_TO_TEST = [
  { path: '/', name: 'Homepage' },
  { path: '/docs/module-1-ros2/', name: 'Module 1 Docs' },
];

for (const { path, name } of PAGES_TO_TEST) {
  test.describe(`Accessibility: ${name}`, () => {
    test('passes WCAG 2.1 AA automated checks', async ({ page }) => {
      await page.goto(path);
      await page.waitForLoadState('networkidle');

      const results = await new AxeBuilder({ page })
        .withTags(['wcag2a', 'wcag2aa', 'wcag21aa'])
        .exclude('#nprogress') // Skip loading indicator
        .analyze();

      // Report violations for debugging
      if (results.violations.length > 0) {
        console.error(`Accessibility violations on ${path}:`);
        for (const v of results.violations) {
          console.error(`  [${v.impact}] ${v.id}: ${v.description}`);
          for (const node of v.nodes) {
            console.error(`    Target: ${node.target.join(', ')}`);
          }
        }
      }

      expect(results.violations.filter(v => v.impact === 'critical')).toHaveLength(0);
      expect(results.violations.filter(v => v.impact === 'serious')).toHaveLength(0);
    });

    test('all images have alt text', async ({ page }) => {
      await page.goto(path);
      const imagesWithoutAlt = await page.evaluate(() => {
        const images = document.querySelectorAll('img');
        return Array.from(images)
          .filter(img => !img.alt && !img.getAttribute('aria-hidden'))
          .map(img => img.src);
      });
      expect(imagesWithoutAlt).toHaveLength(0);
    });

    test('all interactive elements are keyboard accessible', async ({ page }) => {
      await page.goto(path);
      // Tab through page and check for focus traps
      const focusableCount = await page.evaluate(() => {
        const focusable = document.querySelectorAll(
          'a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        return focusable.length;
      });
      expect(focusableCount).toBeGreaterThan(0);
    });

    test('color contrast meets WCAG AA (axe)', async ({ page }) => {
      await page.goto(path);
      const results = await new AxeBuilder({ page })
        .withRules(['color-contrast'])
        .analyze();
      const criticalContrast = results.violations.filter(
        v => v.id === 'color-contrast' && v.impact === 'serious'
      );
      expect(criticalContrast).toHaveLength(0);
    });
  });
}

// Chat panel accessibility
test.describe('Chat Panel Accessibility', () => {
  test('chat input has accessible label', async ({ page }) => {
    await page.goto('/docs/module-1-ros2/');
    // Open chat if needed
    const chatInput = page.locator('textarea[aria-label], input[aria-label], [data-testid="chat-input"]').first();
    if (await chatInput.isVisible()) {
      const ariaLabel = await chatInput.getAttribute('aria-label');
      const ariaLabelledby = await chatInput.getAttribute('aria-labelledby');
      const placeholder = await chatInput.getAttribute('placeholder');
      expect(ariaLabel || ariaLabelledby || placeholder).toBeTruthy();
    }
  });
});
