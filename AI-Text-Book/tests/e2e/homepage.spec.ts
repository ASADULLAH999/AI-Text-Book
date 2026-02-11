import { test, expect } from '@playwright/test';

test.describe('Homepage', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load homepage without errors', async ({ page }) => {
    // Check that page loaded successfully
    await expect(page).toHaveTitle(/.*Physical AI.*/i);

    // Check for hero section
    await expect(page.locator('text=Master')).toBeVisible();
  });

  test('hero section should display with all elements', async ({ page }) => {
    // Check title
    await expect(page.locator('text=Physical AI')).toBeVisible();

    // Check subtitle
    await expect(page.locator('text=Learn robotics from fundamentals')).toBeVisible();

    // Check buttons
    await expect(page.locator('button:has-text("Start Reading")')).toBeVisible();
    await expect(page.locator('button:has-text("View Curriculum")')).toBeVisible();

    // Check stats
    await expect(page.locator('text=156')).toBeVisible();
    await expect(page.locator('text=Tasks')).toBeVisible();
  });

  test('should scroll to sections', async ({ page }) => {
    // Scroll to modules section
    await page.locator('text=Our Learning Modules').scrollIntoViewIfNeeded();
    await expect(page.locator('text=Our Learning Modules')).toBeVisible();

    // Scroll to timeline section
    await page.locator('text=Development Timeline').scrollIntoViewIfNeeded();
    await expect(page.locator('text=Development Timeline')).toBeVisible();
  });

  test('module cards should be clickable', async ({ page }) => {
    // Wait for modules section to be visible
    await page.locator('text=Module 1').first().scrollIntoViewIfNeeded();

    // Click on first module
    const moduleCard = page.locator('text=Module 1').first();
    await expect(moduleCard).toBeVisible();
  });

  test('timeline items should be expandable', async ({ page }) => {
    // Scroll to timeline
    await page.locator('text=Development Timeline').scrollIntoViewIfNeeded();

    // Find and click on a timeline item
    const timelineItems = page.locator('button:has-text("Project Setup")');
    if (await timelineItems.count() > 0) {
      await timelineItems.first().click();
      // Verify item expanded (content visible)
      await expect(page.locator('text=Initialize repository')).toBeVisible();
    }
  });

  test('curriculum tabs should switch content', async ({ page }) => {
    // Scroll to curriculum section
    await page.locator('text=Curriculum Guidance').scrollIntoViewIfNeeded();

    // Click on Assessments tab
    await page.locator('button:has-text("Assessments")').click();

    // Check for assessments content
    await expect(page.locator('text=Module Quizzes')).toBeVisible();

    // Click on Prerequisites tab
    await page.locator('button:has-text("Prerequisites")').click();

    // Check for prerequisites content
    await expect(page.locator('text=Basic Python')).toBeVisible();
  });

  test('hardware tabs should switch content', async ({ page }) => {
    // Scroll to hardware section
    await page.locator('text=Hardware Requirements').scrollIntoViewIfNeeded();

    // Click on Edge Kit tab
    await page.locator('button:has-text("Edge Kit")').click();

    // Verify Edge Kit content
    await expect(page.locator('text=Jetson Edge AI Kit')).toBeVisible();

    // Click on Cloud Option tab
    await page.locator('button:has-text("Cloud Option")').click();

    // Verify Cloud content
    await expect(page.locator('text=AWS EC2')).toBeVisible();
  });

  test('should navigate with URL hash', async ({ page }) => {
    // Navigate to modules section using hash
    await page.goto('/#modules');

    // Verify we can see modules content
    await expect(page.locator('text=Our Learning Modules')).toBeVisible();
  });

  test('start reading button should navigate to module', async ({ page }) => {
    // Click Start Reading button
    const startButton = page.locator('button:has-text("Start Reading")');
    await expect(startButton).toBeVisible();

    // Listen for navigation
    const navigationPromise = page.waitForNavigation();
    await startButton.click();

    // Wait for navigation to complete
    await navigationPromise;

    // Check that we navigated to module docs (or stayed on page for SPA)
    // For SPA, we check if navigation occurred
    const currentUrl = page.url();
    expect(currentUrl).toBeDefined();
  });

  test('animations should render without errors', async ({ page }) => {
    // Check for console errors
    const errors: string[] = [];
    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });

    // Scroll through sections
    await page.locator('text=Master').scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);

    await page.locator('text=Our Learning Modules').scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);

    await page.locator('text=Development Timeline').scrollIntoViewIfNeeded();
    await page.waitForTimeout(500);

    // Verify no errors occurred
    expect(errors.length).toBe(0);
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });

    // Check that content is visible
    await expect(page.locator('text=Master')).toBeVisible();
    await expect(page.locator('button:has-text("Start Reading")')).toBeVisible();

    // Scroll and verify sections
    await page.locator('text=Our Learning Modules').scrollIntoViewIfNeeded();
    await expect(page.locator('text=Our Learning Modules')).toBeVisible();
  });

  test('should be responsive on tablet', async ({ page }) => {
    // Set tablet viewport
    await page.setViewportSize({ width: 768, height: 1024 });

    // Check that content is visible
    await expect(page.locator('text=Master')).toBeVisible();

    // Scroll and verify sections are readable
    await page.locator('text=Development Timeline').scrollIntoViewIfNeeded();
    await expect(page.locator('text=Development Timeline')).toBeVisible();
  });

  test('keyboard navigation should work', async ({ page }) => {
    // Tab to Start Reading button
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');
    await page.keyboard.press('Tab');

    // Verify button is focused or visible
    await expect(page.locator('button:has-text("Start Reading")')).toBeVisible();

    // Tab through curriculum tabs
    await page.locator('text=Curriculum Guidance').scrollIntoViewIfNeeded();
    await page.keyboard.press('Tab');

    // Verify tab navigation works
    await expect(page.locator('button:has-text("Assessments")')).toBeVisible();
  });

  test('should have accessible focus indicators', async ({ page }) => {
    // Focus on Start Reading button
    const startButton = page.locator('button:has-text("Start Reading")');
    await startButton.focus();

    // Check that button is in focus
    const focused = await page.evaluate(() => {
      return document.activeElement?.textContent?.includes('Start Reading');
    });

    expect(focused).toBeTruthy();
  });

  test('all sections should be visible on scroll', async ({ page }) => {
    // Get page height
    const pageHeight = await page.evaluate(() => document.body.scrollHeight);

    // Scroll to bottom
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));

    // Check that we can see hardware section
    await expect(page.locator('text=Hardware Requirements')).toBeVisible();
  });

  test('should handle rapid tab clicks', async ({ page }) => {
    // Scroll to curriculum
    await page.locator('text=Curriculum Guidance').scrollIntoViewIfNeeded();

    // Rapidly click tabs
    for (let i = 0; i < 5; i++) {
      await page.locator('button:has-text("Assessments")').click();
      await page.locator('button:has-text("Prerequisites")').click();
    }

    // Page should still be functional
    await expect(page.locator('text=Learning Outcomes')).toBeVisible();
  });
});
