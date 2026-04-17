import { test, expect } from '@playwright/test';
import { cleanLogin } from '../helpers/auth';

/**
 * E2E: Login (/login)
 * Pre-condicao: VITE_USE_MOCK=true
 * Mock aceita qualquer email + senha "Admin@123"
 * Login redireciona para /kanban
 */

test.describe('Login - Formulario', () => {
  test.beforeEach(async ({ page }) => {
    await cleanLogin(page);
  });

  test('pagina carrega com formulario email + senha', async ({ page }) => {
    await expect(page.locator('#email')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();
  });

  test('titulo da pagina contem Login', async ({ page }) => {
    await expect(page).toHaveTitle(/Login/);
  });

  test('botoes SSO (Google e Microsoft) visiveis', async ({ page }) => {
    await expect(page.locator('button:has-text("Google")')).toBeVisible();
    await expect(page.locator('button:has-text("Microsoft")')).toBeVisible();
  });

  test('botao entrar desabilitado sem preencher campos', async ({ page }) => {
    await expect(page.locator('button[type="submit"]')).toBeDisabled();
  });

  test('botao entrar desabilitado com senha fraca', async ({ page }) => {
    await page.locator('#email').fill('test@itvalley.com.br');
    await page.locator('#password').fill('123');
    await page.locator('#password').focus();
    await expect(page.locator('button[type="submit"]')).toBeDisabled();
  });

  test('validacao visual de senha: mostra erros para senha fraca', async ({ page }) => {
    await page.locator('#password').focus();
    await page.locator('#password').fill('abc');
    await expect(page.locator('text=Minimo 8 caracteres')).toBeVisible();
    await expect(page.locator('text=1 letra maiuscula')).toBeVisible();
    await expect(page.locator('text=1 numero')).toBeVisible();
    await expect(page.locator('text=1 caractere especial')).toBeVisible();
  });

  test('validacao: erros desaparecem conforme senha fica forte', async ({ page }) => {
    await page.locator('#password').focus();
    await page.locator('#password').fill('Admin@123');
    await expect(page.locator('text=Minimo 8 caracteres')).not.toBeVisible();
    await expect(page.locator('text=1 letra maiuscula')).not.toBeVisible();
  });

  test('mostrar/ocultar senha funciona', async ({ page }) => {
    await page.locator('#password').fill('Admin@123');
    await expect(page.locator('#password')).toHaveAttribute('type', 'password');
    const toggleBtn = page.locator('#password ~ button');
    await toggleBtn.click();
    await expect(page.locator('#password')).toHaveAttribute('type', 'text');
    await toggleBtn.click();
    await expect(page.locator('#password')).toHaveAttribute('type', 'password');
  });
});

test.describe('Login - Happy path', () => {
  test.beforeEach(async ({ page }) => {
    await cleanLogin(page);
  });

  test('login com email + senha valida redireciona para /kanban', async ({ page }) => {
    await page.locator('#email').fill('poliana@itvalley.com.br');
    await page.locator('#password').fill('Admin@123');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/\/kanban/, { timeout: 10_000 });
  });

  test('login com email qualquer + Admin@123 funciona (mock)', async ({ page }) => {
    await page.locator('#email').fill('qualquer@teste.com');
    await page.locator('#password').fill('Admin@123');
    await page.locator('button[type="submit"]').click();
    await expect(page).toHaveURL(/\/kanban/, { timeout: 10_000 });
  });

  test('login com senha errada mostra mensagem de erro', async ({ page }) => {
    await page.locator('#email').fill('test@teste.com');
    await page.locator('#password').fill('Errada@123');
    await page.locator('button[type="submit"]').click();
    await expect(page.locator('text=Email ou senha incorretos')).toBeVisible({ timeout: 5_000 });
  });
});
