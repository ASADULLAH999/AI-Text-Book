/**
 * E2E Tests — Mode Switching (User Story 3)
 * T079 [US3] — Validates mode switching UI, persistence, and boundaries.
 *
 * Tests:
 *  - Three mode buttons render correctly
 *  - Active mode has correct aria-pressed state
 *  - Clicking a mode button updates the active mode
 *  - Mode badge reflects the active mode
 *  - General Knowledge disclaimer banner shows/hides correctly
 *  - Mode persists across component interactions (sessionStorage)
 *  - Book-Only is the default mode on new session
 */

import { test, expect, Page } from '@playwright/test';

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000';

async function openPage(page: Page): Promise<void> {
  await page.goto(BASE_URL);
  // Ensure ChatPanel is visible (not collapsed)
  const expandBtn = page.locator('[aria-label="Expand chat"]');
  if (await expandBtn.isVisible()) {
    await expandBtn.click();
  }
}

// ---------------------------------------------------------------------------
// Mode selector rendering
// ---------------------------------------------------------------------------

test.describe('ModeSelector — rendering', () => {
  test('renders all three mode buttons', async ({ page }) => {
    await openPage(page);
    await expect(page.getByTestId('mode-btn-book_only')).toBeVisible();
    await expect(page.getByTestId('mode-btn-selected_text')).toBeVisible();
    await expect(page.getByTestId('mode-btn-general_knowledge')).toBeVisible();
  });

  test('Book Only button has correct label', async ({ page }) => {
    await openPage(page);
    await expect(page.getByTestId('mode-btn-book_only')).toContainText('Book Only');
  });

  test('Selected Text button has correct label', async ({ page }) => {
    await openPage(page);
    await expect(page.getByTestId('mode-btn-selected_text')).toContainText('Selected Text');
  });

  test('General Knowledge button has correct label', async ({ page }) => {
    await openPage(page);
    await expect(page.getByTestId('mode-btn-general_knowledge')).toContainText('General Knowledge');
  });
});

// ---------------------------------------------------------------------------
// Default mode — T075
// ---------------------------------------------------------------------------

test.describe('Default mode — Book Only (T075)', () => {
  test('Book Only is active by default', async ({ page }) => {
    // Clear sessionStorage to simulate new session
    await page.addInitScript(() => sessionStorage.clear());
    await openPage(page);

    const bookBtn = page.getByTestId('mode-btn-book_only');
    await expect(bookBtn).toHaveAttribute('aria-pressed', 'true');
  });

  test('mode badge shows Book Only by default', async ({ page }) => {
    await page.addInitScript(() => sessionStorage.clear());
    await openPage(page);

    const badge = page.getByTestId('mode-badge');
    await expect(badge).toContainText('Book Only');
  });
});

// ---------------------------------------------------------------------------
// Mode switching — T069
// ---------------------------------------------------------------------------

test.describe('Mode switching (T069)', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => sessionStorage.clear());
  });

  test('clicking Selected Text makes it active', async ({ page }) => {
    await openPage(page);
    await page.getByTestId('mode-btn-selected_text').click();

    await expect(page.getByTestId('mode-btn-selected_text')).toHaveAttribute(
      'aria-pressed',
      'true'
    );
    await expect(page.getByTestId('mode-btn-book_only')).toHaveAttribute('aria-pressed', 'false');
  });

  test('clicking General Knowledge makes it active', async ({ page }) => {
    await openPage(page);
    await page.getByTestId('mode-btn-general_knowledge').click();

    await expect(page.getByTestId('mode-btn-general_knowledge')).toHaveAttribute(
      'aria-pressed',
      'true'
    );
  });

  test('switching back to Book Only works', async ({ page }) => {
    await openPage(page);
    await page.getByTestId('mode-btn-general_knowledge').click();
    await page.getByTestId('mode-btn-book_only').click();

    await expect(page.getByTestId('mode-btn-book_only')).toHaveAttribute('aria-pressed', 'true');
    await expect(page.getByTestId('mode-btn-general_knowledge')).toHaveAttribute(
      'aria-pressed',
      'false'
    );
  });

  test('only one mode is active at a time', async ({ page }) => {
    await openPage(page);
    await page.getByTestId('mode-btn-selected_text').click();

    const activeButtons = page
      .locator('[role="group"] button[aria-pressed="true"]');
    await expect(activeButtons).toHaveCount(1);
  });
});

// ---------------------------------------------------------------------------
// Mode badge — T073
// ---------------------------------------------------------------------------

test.describe('Mode badge (T073)', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => sessionStorage.clear());
  });

  test('badge updates when mode changes to Selected Text', async ({ page }) => {
    await openPage(page);
    await page.getByTestId('mode-btn-selected_text').click();

    const badge = page.getByTestId('mode-badge');
    await expect(badge).toContainText('Selected Text');
  });

  test('badge updates when mode changes to General Knowledge', async ({ page }) => {
    await openPage(page);
    await page.getByTestId('mode-btn-general_knowledge').click();

    const badge = page.getByTestId('mode-badge');
    await expect(badge).toContainText('General Knowledge');
  });

  test('badge returns to Book Only after switching back', async ({ page }) => {
    await openPage(page);
    await page.getByTestId('mode-btn-general_knowledge').click();
    await page.getByTestId('mode-btn-book_only').click();

    const badge = page.getByTestId('mode-badge');
    await expect(badge).toContainText('Book Only');
  });
});

// ---------------------------------------------------------------------------
// General Knowledge disclaimer banner — T074
// ---------------------------------------------------------------------------

test.describe('General Knowledge disclaimer banner (T074)', () => {
  test.beforeEach(async ({ page }) => {
    await page.addInitScript(() => sessionStorage.clear());
  });

  test('disclaimer NOT visible in Book Only mode', async ({ page }) => {
    await openPage(page);
    await expect(page.getByTestId('gk-disclaimer')).not.toBeVisible();
  });

  test('disclaimer NOT visible in Selected Text mode', async ({ page }) => {
    await openPage(page);
    await page.getByTestId('mode-btn-selected_text').click();
    await expect(page.getByTestId('gk-disclaimer')).not.toBeVisible();
  });

  test('disclaimer IS visible when General Knowledge mode is active', async ({ page }) => {
    await openPage(page);
    await page.getByTestId('mode-btn-general_knowledge').click();
    await expect(page.getByTestId('gk-disclaimer')).toBeVisible();
  });

  test('disclaimer disappears when switching away from General Knowledge', async ({ page }) => {
    await openPage(page);
    await page.getByTestId('mode-btn-general_knowledge').click();
    await expect(page.getByTestId('gk-disclaimer')).toBeVisible();

    await page.getByTestId('mode-btn-book_only').click();
    await expect(page.getByTestId('gk-disclaimer')).not.toBeVisible();
  });

  test('disclaimer contains expected warning text', async ({ page }) => {
    await openPage(page);
    await page.getByTestId('mode-btn-general_knowledge').click();

    const banner = page.getByTestId('gk-disclaimer');
    await expect(banner).toContainText('General Knowledge mode');
  });
});

// ---------------------------------------------------------------------------
// sessionStorage persistence — T070
// ---------------------------------------------------------------------------

test.describe('Mode persistence in sessionStorage (T070)', () => {
  test('mode persists across page interactions within session', async ({ page }) => {
    await page.addInitScript(() => sessionStorage.clear());
    await openPage(page);

    // Switch to General Knowledge
    await page.getByTestId('mode-btn-general_knowledge').click();

    // Reload the page (same session = sessionStorage still present)
    await page.reload();

    // Ensure ChatPanel is expanded
    const expandBtn = page.locator('[aria-label="Expand chat"]');
    if (await expandBtn.isVisible()) {
      await expandBtn.click();
    }

    await expect(page.getByTestId('mode-btn-general_knowledge')).toHaveAttribute(
      'aria-pressed',
      'true'
    );
  });

  test('new session (cleared sessionStorage) starts with Book Only', async ({ page }) => {
    // Set GK mode in sessionStorage, then clear it before navigation
    await page.addInitScript(() => {
      sessionStorage.setItem('chatbot_mode', 'general_knowledge');
      // Immediately clear to simulate new session
      sessionStorage.clear();
    });
    await openPage(page);

    await expect(page.getByTestId('mode-btn-book_only')).toHaveAttribute('aria-pressed', 'true');
  });
});

// ---------------------------------------------------------------------------
// Accessibility
// ---------------------------------------------------------------------------

test.describe('Mode selector accessibility', () => {
  test('mode selector group has aria-label', async ({ page }) => {
    await openPage(page);
    const group = page.locator('[role="group"][aria-label="Answering mode"]');
    await expect(group).toBeVisible();
  });

  test('each mode button has a title tooltip', async ({ page }) => {
    await openPage(page);
    const bookBtn = page.getByTestId('mode-btn-book_only');
    const title = await bookBtn.getAttribute('title');
    expect(title).toBeTruthy();
  });

  test('mode badge has aria-label', async ({ page }) => {
    await page.addInitScript(() => sessionStorage.clear());
    await openPage(page);

    const badge = page.getByTestId('mode-badge');
    const ariaLabel = await badge.getAttribute('aria-label');
    expect(ariaLabel).toContain('Current mode');
  });
});
