import { test, expect } from '@playwright/test';

test.describe('Proposal Studio Approval Flow', () => {
  test('User can inspect proposal and approve submission', async ({ page }) => {
    await page.goto('/studio/job_0001');
    await expect(page.locator('h2')).toContainText('Proposal Studio & Approval Gate');

    // Verify dry-run badge
    await expect(page.locator('text=Dry-Run Validated')).toBeVisible();

    // Click approve button
    await page.click('[data-testid="approve-proposal-button"]');

    // Expect confirmation notification and eventual redirection
    await expect(page.locator('text=Proposal approved and committed')).toBeVisible({ timeout: 5000 });
  });
});
