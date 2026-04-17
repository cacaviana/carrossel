import { expect } from '@playwright/test';
import type { Page } from '@playwright/test';
import { loginBackend } from './backend-auth';

/**
 * Limpa o estado de auth e garante que estamos na pagina de login
 * com estado limpo (sem sessao anterior).
 */
export async function cleanLogin(page: Page) {
  await page.goto('/', { waitUntil: 'commit' });
  await page.evaluate(() => localStorage.removeItem('kanban_auth'));
  await page.goto('/login', { waitUntil: 'networkidle' });
  await expect(page.locator('#email')).toBeVisible({ timeout: 10_000 });
}

/**
 * Faz login como Admin. Funciona em 2 modos:
 * - MOCK (VITE_USE_MOCK=true): login com qualquer email + Admin@123
 * - REAL (VITE_USE_MOCK=false): usa backend real com usuario de teste
 *
 * Redireciona pra / (home) depois do login e navega pra /historico se necessario.
 */
export async function loginAsAdmin(page: Page) {
  // Tenta login real via API (funciona tanto em mock quanto em real)
  try {
    const { authPayload } = await loginBackend();
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await page.evaluate((auth) => {
      localStorage.setItem('kanban_auth', JSON.stringify(auth));
    }, authPayload);
    // Recarrega pra o onMount do layout pegar auth
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    return;
  } catch {
    // Fallback: login via UI (mock)
  }

  await cleanLogin(page);
  await page.locator('#email').fill('e2e-test@itvalley.com');
  await page.locator('#password').fill('Admin@123');
  await page.locator('button[type="submit"]').click();
  // Aguarda redirecionamento (pode ser /, /kanban ou /historico)
  await expect(page).not.toHaveURL(/\/login$/, { timeout: 10_000 });
}

/**
 * Login + navega para /historico via sidebar.
 */
export async function loginAndGoHistorico(page: Page) {
  await loginAsAdmin(page);
  // Navegar via sidebar (client-side nav preserva Svelte state)
  const historicoLink = page.locator('a[href="/historico"]').first();
  const isVisible = await historicoLink.isVisible({ timeout: 5000 }).catch(() => false);
  if (isVisible) {
    await historicoLink.click();
  } else {
    // fallback direto
    await page.goto('/historico');
  }
  await expect(page).toHaveURL(/\/historico/);
  await expect(page.locator('h1:has-text("Historico")').or(page.locator('h1:has-text("Hist")'))).toBeVisible({ timeout: 10_000 });
}
