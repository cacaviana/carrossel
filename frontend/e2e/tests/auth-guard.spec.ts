import { test, expect } from '@playwright/test';
import { cleanLogin, loginAsAdmin, loginAndGoHistorico } from '../helpers/auth';

/**
 * E2E: Auth guard + Navegacao
 */

test.describe('Auth Guard - Acesso sem login', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'commit' });
    await page.evaluate(() => localStorage.removeItem('kanban_auth'));
  });

  test('/ (home) carrega normalmente sem login', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveURL('/');
    await expect(page.locator('body')).toBeVisible();
  });
});

test.describe('Auth Guard - Acesso permitido apos login', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('apos login, /kanban mostra board com colunas', async ({ page }) => {
    await expect(page).toHaveURL(/\/kanban/);
    await expect(page.locator('[role="region"]').first()).toBeVisible({ timeout: 10_000 });
  });

  test('usuario logado que acessa /login e redirecionado', async ({ page }) => {
    await page.goto('/login');
    await page.waitForTimeout(2000);
    await expect(page).not.toHaveURL(/\/login$/);
  });
});

test.describe('Navegacao - Sidebar', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
  });

  test('sidebar tem link Historico clicavel', async ({ page }) => {
    const historicoLink = page.locator('a[href="/historico"]').first();
    await expect(historicoLink).toBeVisible();
    await historicoLink.click();
    await expect(page).toHaveURL(/\/historico/);
  });

  test('sidebar tem link Home clicavel', async ({ page }) => {
    const homeLink = page.locator('a:has-text("Home")').first();
    await expect(homeLink).toBeVisible();
    await homeLink.click();
    await expect(page).toHaveURL('/');
  });

  test('sidebar mostra Content Factory', async ({ page }) => {
    await expect(page.locator('text=Content Factory').first()).toBeVisible();
  });
});
