import { test, expect } from '@playwright/test';

test.describe('Proposal Studio Rejection Flow', () => {
  test('User can reject draft with feedback reason', async ({ page }) => {
    await page.goto('/studio/job_0001');

    // Click reject button to trigger modal
    await page.click('[data-testid="reject-proposal-button"]');

    // Enter feedback reason
    await page.fill('[data-testid="reject-reason-input"]', 'Need more emphasis on distributed cloud architecture.');

    // Confirm rejection
    await page.click('[data-testid="confirm-reject-button"]');

    // Verify rejection confirmation message
    await expect(page.locator('text=Draft rejected: Need more emphasis')).toBeVisible({ timeout: 5000 });
  });
});
