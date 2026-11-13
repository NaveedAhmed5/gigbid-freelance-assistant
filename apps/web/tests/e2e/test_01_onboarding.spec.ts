import { test, expect } from '@playwright/test';

test.describe('Onboarding & Persona Selection Flow', () => {
  test('User can sign in as reviewer and choose active persona', async ({ page }) => {
    await page.goto('/onboarding');
    await expect(page.locator('h1')).toContainText('Sign In & Persona Onboarding');

    // Fill reviewer credentials
    await page.fill('[data-testid="email-input"]', 'reviewer@gigbid.ai');
    await page.fill('[data-testid="password-input"]', 'reviewer-demo-pass');

    // Select persona
    await page.selectOption('[data-testid="persona-select-onboarding"]', 'ai_ml_engineer');

    // Submit form
    await page.click('[data-testid="onboarding-submit-button"]');

    // Expect navigation to inbox
    await expect(page).toHaveURL(/.*inbox/);
  });
});

