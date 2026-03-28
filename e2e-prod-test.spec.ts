import { test, expect } from '@playwright/test';

const BASE_URL = 'https://app-carrossel-frontend.azurewebsites.net';
const BACKEND_URL = 'https://app-carrossel-backend.azurewebsites.net';

// --- Desktop tests ---

test('Home page loads', async ({ page }) => {
  await page.goto(BASE_URL);
  await expect(page.locator('h2')).toContainText('Criar Carrossel LinkedIn');
});

test('Backend health check', async ({ request }) => {
  const res = await request.get(`${BACKEND_URL}/health`);
  expect(res.ok()).toBeTruthy();
  const data = await res.json();
  expect(data.status).toBe('ok');
});

test('Navigation works', async ({ page }) => {
  await page.goto(BASE_URL);
  await page.click('nav >> text=Config');
  await expect(page).toHaveURL(/configuracoes/);
  await expect(page.locator('h2')).toContainText('Configurações');
});

test('Discipline cards render', async ({ page }) => {
  await page.goto(BASE_URL);
  const cards = page.locator('button:has-text("D1")');
  await expect(cards).toBeVisible();
});

test('Slide count selector works', async ({ page }) => {
  await page.goto(BASE_URL);
  // Default is 10 (Completo), click 3 and verify the button becomes active
  const btn3 = page.locator('button:has-text("3")').first();
  await btn3.click();
  await expect(btn3).toHaveClass(/bg-steel-6/);
});

test('Claude Code CLI button is hidden in production', async ({ page }) => {
  await page.goto(BASE_URL);
  // Click a discipline
  await page.click('button:has-text("D7")');
  // Select a tech
  await page.click('button:has-text("RAG")');
  // Should NOT see Claude Code button
  await expect(page.locator('button:has-text("Claude Code")')).toHaveCount(0);
  // Should see Gerar Carrossel button
  await expect(page.locator('button:has-text("Gerar Carrossel")')).toBeVisible();
});

test('Backend API config endpoint', async ({ request }) => {
  const res = await request.get(`${BACKEND_URL}/api/config`);
  expect(res.ok()).toBeTruthy();
  const data = await res.json();
  expect(data).toHaveProperty('gemini_api_key_set');
});

// --- Mobile tests ---

test('Mobile - Home page loads', async ({ browser }) => {
  const context = await browser.newContext({
    viewport: { width: 375, height: 812 },
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'
  });
  const page = await context.newPage();
  await page.goto(BASE_URL);
  await expect(page.locator('h2')).toContainText('Criar Carrossel LinkedIn');
  // Hamburger menu should be visible
  await expect(page.locator('button[aria-label="Menu"]')).toBeVisible();
  // Desktop nav should be hidden
  await expect(page.locator('nav.hidden')).toBeHidden();
  await context.close();
});

test('Mobile - Hamburger menu opens', async ({ browser }) => {
  const context = await browser.newContext({
    viewport: { width: 375, height: 812 },
  });
  const page = await context.newPage();
  await page.goto(BASE_URL);
  await page.click('button[aria-label="Menu"]');
  // After clicking hamburger, mobile nav links should appear
  // Wait for the nav to expand and click Config link
  const configLink = page.locator('a[href="/configuracoes"]').last();
  await expect(configLink).toBeVisible({ timeout: 10000 });
  await context.close();
});

test('Mobile - Discipline grid shows 2 columns', async ({ browser }) => {
  const context = await browser.newContext({
    viewport: { width: 375, height: 812 },
  });
  const page = await context.newPage();
  await page.goto(BASE_URL);
  const grid = page.locator('.grid.grid-cols-2');
  await expect(grid).toBeVisible();
  await context.close();
});
