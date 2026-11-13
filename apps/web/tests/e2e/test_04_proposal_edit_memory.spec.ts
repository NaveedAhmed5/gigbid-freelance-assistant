import { test, expect } from '@playwright/test';

test.describe('Proposal Studio Edit & Style Memory Flow', () => {
  test('User can edit proposal text and promote changes to style memory', async ({ page }) => {
    await page.goto('/studio/job_0001');

    const editor = page.locator('[data-testid="proposal-editor-textarea"]');
    await expect(editor).toBeVisible();

    // Edit text
    await editor.fill('Hi team — customized proposal text specifically tailored for enterprise scalability.');

    // Approve the edited draft
    await page.click('[data-testid="approve-proposal-button"]');

    // Confirm submission
    await expect(page.locator('text=Proposal approved and committed')).toBeVisible({ timeout: 5000 });
  });
});

