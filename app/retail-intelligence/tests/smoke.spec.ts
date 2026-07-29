import { test, expect } from '@playwright/test';

test('smoke test - executive overview loads', async ({ page }) => {
  await page.goto('/');

  await expect(page.getByRole('heading', { name: 'Retail Intelligence' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Executive Overview' })).toBeVisible();
  await expect(page.getByText('Customers Requiring Action')).toBeVisible();
});

test('smoke test - customer 360 route loads', async ({ page }) => {
  await page.goto('/customer/CUST-0007');

  await expect(page.getByRole('heading', { name: 'Customer 360' })).toBeVisible();
  await expect(page.getByText('Sources to Customer 360 to churn prediction.')).toBeVisible();
});

test('smoke test - retention copilot route loads', async ({ page }) => {
  await page.goto('/copilot/CUST-0007');

  await expect(page.getByRole('heading', { name: 'Retention Copilot' })).toBeVisible();
  await expect(page.getByText('Customer 360 + ML Prediction + Business Knowledge to Next-Best Action.')).toBeVisible();
});
