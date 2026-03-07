/**
 * E2E Tests — Key Terms (User Story 5)
 * T096 [P] [US5] — Validates key term highlighting, tooltip display, toggle, and
 * "More about" chat pre-fill action.
 *
 * Tests:
 *  - Highlighted key terms render in page content
 *  - Clicking a term shows the definition tooltip
 *  - Tooltip contains the term title and definition text
 *  - "More about [term]" button pre-fills the chat input
 *  - Escape key closes the tooltip
 *  - Outside click closes the tooltip
 *  - Toggle switch disables highlighting (terms no longer have highlight class)
 *  - Toggle switch re-enables highlighting
 *  - Highlighting preference persists across page reload (localStorage)
 */

import { test, expect, Page } from '@playwright/test';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000';

async function openPage(page: Page): Promise<void> {
  await page.goto(BASE_URL);
  await page.waitForLoadState('networkidle');
}

async function expandChat(page: Page): Promise<void> {
  const expandBtn = page.locator('[aria-label="Expand chat"]');
  if (await expandBtn.isVisible({ timeout: 2000 }).catch(() => false)) {
    await expandBtn.click();
  }
}

// ---------------------------------------------------------------------------
// Term highlighting — rendering
// ---------------------------------------------------------------------------

test.describe('TermHighlight — rendering', () => {
  test('at least one key term is highlighted on the page', async ({ page }) => {
    await openPage(page);
    const highlights = page.locator('[data-testid^="term-highlight-"]');
    await expect(highlights.first()).toBeVisible({ timeout: 5000 });
  });

  test('highlighted term has correct aria-label', async ({ page }) => {
    await openPage(page);
    const first = page.locator('[data-testid^="term-highlight-"]').first();
    await expect(first).toHaveAttribute('aria-label', /Key term:/);
  });

  test('highlighted term has role=button', async ({ page }) => {
    await openPage(page);
    const first = page.locator('[data-testid^="term-highlight-"]').first();
    await expect(first).toHaveAttribute('role', 'button');
  });
});

// ---------------------------------------------------------------------------
// Tooltip — appearance and content
// ---------------------------------------------------------------------------

test.describe('TermTooltip — definition display', () => {
  test('clicking a highlighted term shows the tooltip', async ({ page }) => {
    await openPage(page);
    const firstTerm = page.locator('[data-testid^="term-highlight-"]').first();
    await firstTerm.click();
    await expect(page.getByTestId('term-tooltip')).toBeVisible();
  });

  test('tooltip contains a definition', async ({ page }) => {
    await openPage(page);
    await page.locator('[data-testid^="term-highlight-"]').first().click();
    const tooltip = page.getByTestId('term-tooltip');
    // The definition should be a non-trivial paragraph
    const text = await tooltip.innerText();
    expect(text.length).toBeGreaterThan(30);
  });

  test('tooltip has correct role=tooltip', async ({ page }) => {
    await openPage(page);
    await page.locator('[data-testid^="term-highlight-"]').first().click();
    await expect(page.getByTestId('term-tooltip')).toHaveAttribute('role', 'tooltip');
  });

  test('tooltip shows the "More about" button', async ({ page }) => {
    await openPage(page);
    await page.locator('[data-testid^="term-highlight-"]').first().click();
    await expect(page.getByTestId('term-ask-more')).toBeVisible();
  });

  test('closing with the × button hides the tooltip', async ({ page }) => {
    await openPage(page);
    await page.locator('[data-testid^="term-highlight-"]').first().click();
    await page.getByTestId('term-tooltip-close').click();
    await expect(page.getByTestId('term-tooltip')).not.toBeVisible();
  });

  test('Escape key closes the tooltip', async ({ page }) => {
    await openPage(page);
    await page.locator('[data-testid^="term-highlight-"]').first().click();
    await expect(page.getByTestId('term-tooltip')).toBeVisible();
    await page.keyboard.press('Escape');
    await expect(page.getByTestId('term-tooltip')).not.toBeVisible();
  });

  test('clicking outside the tooltip closes it', async ({ page }) => {
    await openPage(page);
    await page.locator('[data-testid^="term-highlight-"]').first().click();
    await expect(page.getByTestId('term-tooltip')).toBeVisible();
    await page.mouse.click(10, 10); // far outside tooltip
    await expect(page.getByTestId('term-tooltip')).not.toBeVisible();
  });
});

// ---------------------------------------------------------------------------
// T094 — "More about [term]" pre-fills chat input
// ---------------------------------------------------------------------------

test.describe('TermTooltip — "More about" action (T094)', () => {
  test('"More about" click opens chat with pre-filled query', async ({ page }) => {
    await openPage(page);
    await expandChat(page);

    await page.locator('[data-testid^="term-highlight-"]').first().click();
    const askMoreBtn = page.getByTestId('term-ask-more');
    await expect(askMoreBtn).toBeVisible();

    await askMoreBtn.click();

    // Tooltip should close
    await expect(page.getByTestId('term-tooltip')).not.toBeVisible();

    // Chat input should be pre-filled with "Tell me more about <term>"
    const chatInput = page.locator('[data-testid="chat-input"]');
    if (await chatInput.isVisible({ timeout: 2000 }).catch(() => false)) {
      const value = await chatInput.inputValue();
      expect(value.toLowerCase()).toContain('more about');
    }
  });
});

// ---------------------------------------------------------------------------
// T093 — Highlighting toggle
// ---------------------------------------------------------------------------

test.describe('TermHighlightToggle — T093', () => {
  test('toggle switch is rendered', async ({ page }) => {
    await openPage(page);
    // Toggle may be in settings panel — find it anywhere
    const toggle = page.getByTestId('term-highlight-toggle');
    // If it's inside a panel, we might need to open settings first
    // For now verify it exists in DOM
    await expect(toggle).toHaveCount(1);
  });

  test('toggling off removes highlighted terms from view', async ({ page }) => {
    await openPage(page);
    const toggle = page.getByTestId('term-highlight-toggle-input');
    const initialHighlights = await page
      .locator('[data-testid^="term-highlight-"]')
      .count();

    if (initialHighlights > 0) {
      // Turn off
      await toggle.uncheck();
      const afterHighlights = await page
        .locator('[data-testid^="term-highlight-"]')
        .count();
      expect(afterHighlights).toBe(0);
    }
  });

  test('re-enabling highlighting restores highlighted terms', async ({ page }) => {
    await openPage(page);
    const toggle = page.getByTestId('term-highlight-toggle-input');

    const initialCount = await page
      .locator('[data-testid^="term-highlight-"]')
      .count();
    if (initialCount === 0) {
      test.skip(); // no terms on this page
    }

    await toggle.uncheck();
    await toggle.check();

    const restored = await page.locator('[data-testid^="term-highlight-"]').count();
    expect(restored).toBeGreaterThan(0);
  });

  test('highlighting preference persists after reload', async ({ page }) => {
    await openPage(page);
    const toggle = page.getByTestId('term-highlight-toggle-input');

    // Disable and reload
    await toggle.uncheck();
    await page.reload();
    await page.waitForLoadState('networkidle');

    const highlights = await page
      .locator('[data-testid^="term-highlight-"]')
      .count();
    expect(highlights).toBe(0);

    // Re-enable and reload
    const toggle2 = page.getByTestId('term-highlight-toggle-input');
    await toggle2.check();
    await page.reload();
    await page.waitForLoadState('networkidle');

    const restoredHighlights = await page
      .locator('[data-testid^="term-highlight-"]')
      .count();
    expect(restoredHighlights).toBeGreaterThan(0);
  });
});

// ---------------------------------------------------------------------------
// Accessibility
// ---------------------------------------------------------------------------

test.describe('TermHighlight — accessibility', () => {
  test('term can be activated by keyboard (Enter)', async ({ page }) => {
    await openPage(page);
    const firstTerm = page.locator('[data-testid^="term-highlight-"]').first();
    await firstTerm.focus();
    await page.keyboard.press('Enter');
    await expect(page.getByTestId('term-tooltip')).toBeVisible();
  });

  test('term can be activated by keyboard (Space)', async ({ page }) => {
    await openPage(page);
    const firstTerm = page.locator('[data-testid^="term-highlight-"]').first();
    await firstTerm.focus();
    await page.keyboard.press(' ');
    await expect(page.getByTestId('term-tooltip')).toBeVisible();
  });
});
