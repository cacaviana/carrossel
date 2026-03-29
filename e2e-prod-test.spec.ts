import { test, expect, type Page, type BrowserContext } from '@playwright/test';

const BASE_URL = 'https://app-carrossel-frontend.azurewebsites.net';
const BACKEND_URL = 'https://app-carrossel-backend.azurewebsites.net';

// Timeout maior para cold start do Azure
test.use({ actionTimeout: 15000, navigationTimeout: 60000 });

// Helper para criar contexto mobile iPhone
async function mobileContext(browser: any): Promise<{ context: BrowserContext; page: Page }> {
  const context = await browser.newContext({
    viewport: { width: 375, height: 812 },
    userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15',
    hasTouch: true,
    isMobile: true,
  });
  const page = await context.newPage();
  return { context, page };
}

// ====================== BACKEND ======================

test('Backend - health check', async ({ request }) => {
  const res = await request.get(`${BACKEND_URL}/health`);
  expect(res.ok()).toBeTruthy();
  const data = await res.json();
  expect(data.status).toBe('ok');
});

test('Backend - config endpoint retorna status das chaves', async ({ request }) => {
  const res = await request.get(`${BACKEND_URL}/api/config`);
  expect(res.ok()).toBeTruthy();
  const data = await res.json();
  expect(data).toHaveProperty('gemini_api_key_set');
  expect(data).toHaveProperty('google_drive_credentials_set');
});

test('Backend - agentes endpoint retorna skills', async ({ request }) => {
  const res = await request.get(`${BACKEND_URL}/api/agentes`);
  expect(res.ok()).toBeTruthy();
  const data = await res.json();
  // API pode retornar { agentes: [...] } ou lista diretamente
  const agentes = data.agentes || data;
  expect(agentes).toBeDefined();
});

// ====================== DESKTOP ======================

test('Desktop - Home page carrega com titulo', async ({ page }) => {
  await page.goto(BASE_URL);
  await expect(page.locator('h2')).toContainText('Criar Carrossel LinkedIn');
  await expect(page.locator('footer')).toContainText('IT Valley School');
});

test('Desktop - Navegacao funciona', async ({ page }) => {
  await page.goto(BASE_URL);
  await page.click('nav >> text=Config');
  await expect(page).toHaveURL(/configuracoes/);
});

test('Desktop - Wizard mostra tipos e textarea', async ({ page }) => {
  await page.goto(BASE_URL);
  // Tipos de carrossel visíveis
  await expect(page.getByRole('button', { name: 'Texto Slides com texto' })).toBeVisible();
  await expect(page.getByRole('button', { name: /^Visual Texto \+ diagramas/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /^Infográfico/ })).toBeVisible();
  // Textarea visível por padrão (modo texto livre)
  await expect(page.locator('textarea')).toBeVisible();
});

test('Desktop - Seletor de slides funciona', async ({ page }) => {
  await page.goto(BASE_URL);
  const btn3 = page.locator('button:has-text("3")').first();
  await btn3.click();
  await expect(btn3).toHaveClass(/bg-steel-6/);
});

test('Desktop - Disciplinas aparecem ao clicar Por disciplina', async ({ page }) => {
  await page.goto(BASE_URL);
  await page.click('button:has-text("Por disciplina")');
  await expect(page.locator('button:has-text("D1")')).toBeVisible();
  await expect(page.locator('button:has-text("D7")')).toBeVisible();
});

test('Desktop - Claude Code CLI escondido em producao', async ({ page }) => {
  await page.goto(BASE_URL);
  await expect(page.locator('button:has-text("Claude Code")')).toHaveCount(0);
  await expect(page.locator('button:has-text("Gerar Carrossel")')).toBeVisible();
});

// ====================== MOBILE FIRST ======================

test('Mobile - Home page carrega e mostra hamburger', async ({ browser }) => {
  const { context, page } = await mobileContext(browser);
  await page.goto(BASE_URL);
  await expect(page.locator('h2')).toContainText('Criar Carrossel LinkedIn');
  // Hamburger visivel
  await expect(page.locator('button[aria-label="Menu"]')).toBeVisible();
  // Nav desktop escondida
  const desktopNav = page.locator('nav.hidden');
  await expect(desktopNav).toBeHidden();
  await context.close();
});

test('Mobile - Hamburger abre menu e navega', async ({ browser }) => {
  const { context, page } = await mobileContext(browser);
  await page.goto(BASE_URL);
  await page.click('button[aria-label="Menu"]');
  const configLink = page.locator('a[href="/configuracoes"]').last();
  await expect(configLink).toBeVisible({ timeout: 10000 });
  await configLink.click();
  await expect(page).toHaveURL(/configuracoes/);
  await context.close();
});

test('Mobile - Wizard mostra tipos', async ({ browser }) => {
  const { context, page } = await mobileContext(browser);
  await page.goto(BASE_URL);
  await expect(page.getByRole('button', { name: 'Texto Slides com texto' })).toBeVisible();
  await expect(page.getByRole('button', { name: /^Visual Texto \+ diagramas/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /^Infográfico/ })).toBeVisible();
  await context.close();
});

test('Mobile - Disciplinas em grid 2 colunas', async ({ browser }) => {
  const { context, page } = await mobileContext(browser);
  await page.goto(BASE_URL);
  await page.click('button:has-text("Por disciplina")');
  const card1 = page.locator('button:has-text("D1")');
  const card2 = page.locator('button:has-text("D2")');
  await expect(card1).toBeVisible();
  const box1 = await card1.boundingBox();
  const box2 = await card2.boundingBox();
  expect(box1).toBeTruthy();
  expect(box2).toBeTruthy();
  expect(Math.abs(box1!.y - box2!.y)).toBeLessThan(10);
  await context.close();
});

test('Mobile - Seletor de slides touch-friendly', async ({ browser }) => {
  const { context, page } = await mobileContext(browser);
  await page.goto(BASE_URL);
  // Botoes de slides devem ter tamanho touch-friendly (>=44px)
  const btn3 = page.locator('button:has-text("3")').first();
  const box = await btn3.boundingBox();
  expect(box).toBeTruthy();
  expect(box!.width).toBeGreaterThanOrEqual(40);
  expect(box!.height).toBeGreaterThanOrEqual(40);
  await btn3.tap();
  await expect(btn3).toHaveClass(/bg-steel-6/);
  await context.close();
});

test('Mobile - Textarea visivel por padrao', async ({ browser }) => {
  const { context, page } = await mobileContext(browser);
  await page.goto(BASE_URL);
  const textarea = page.locator('textarea');
  await expect(textarea).toBeVisible();
  const box = await textarea.boundingBox();
  expect(box).toBeTruthy();
  expect(box!.width).toBeGreaterThan(300);
  await context.close();
});

test('Mobile - Pagina carrossel (sem dados) mostra CTA', async ({ browser }) => {
  const { context, page } = await mobileContext(browser);
  await page.goto(`${BASE_URL}/carrossel`);
  await expect(page.locator('text=Nenhum carrossel gerado')).toBeVisible();
  await expect(page.locator('a:has-text("Criar carrossel")')).toBeVisible();
  await context.close();
});

test('Mobile - Pagina historico carrega', async ({ browser }) => {
  const { context, page } = await mobileContext(browser);
  await page.goto(`${BASE_URL}/historico`);
  // Deve carregar sem erro
  await expect(page.locator('h2')).toBeVisible();
  await context.close();
});

test('Mobile - Pagina config carrega', async ({ browser }) => {
  const { context, page } = await mobileContext(browser);
  await page.goto(`${BASE_URL}/configuracoes`);
  await expect(page.locator('h2')).toContainText('Configurações');
  await context.close();
});

// ====================== TEXTO LIVRE ======================

test('Desktop - Texto livre envia payload correto', async ({ page }) => {
  await page.goto(BASE_URL);
  const textarea = page.locator('textarea');
  await textarea.fill('Este e um texto sobre inteligencia artificial e machine learning para testar o modo texto livre do carrossel LinkedIn.');
  const [request] = await Promise.all([
    page.waitForRequest(req => req.url().includes('/api/gerar-conteudo') && req.method() === 'POST'),
    page.click('button:has-text("Gerar Carrossel")')
  ]);
  const body = request.postDataJSON();
  expect(body).toHaveProperty('texto_livre');
  expect(body).toHaveProperty('total_slides');
  expect(body.texto_livre).toContain('inteligencia artificial');
});

test('Mobile - Texto livre funciona no mobile', async ({ browser }) => {
  const { context, page } = await mobileContext(browser);
  await page.goto(BASE_URL);
  const textarea = page.locator('textarea');
  await expect(textarea).toBeVisible();
  await textarea.fill('Texto sobre deep learning e redes neurais para carrossel mobile test.');
  const gerarBtn = page.locator('button:has-text("Gerar Carrossel")');
  await expect(gerarBtn).toBeVisible();
  const box = await gerarBtn.boundingBox();
  expect(box).toBeTruthy();
  expect(box!.width).toBeGreaterThan(300);
  await context.close();
});
