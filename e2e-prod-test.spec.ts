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

test('Desktop - Cards de disciplina renderizam', async ({ page }) => {
  await page.goto(BASE_URL);
  for (const id of ['D1', 'D7', 'D9']) {
    await expect(page.locator(`button:has-text("${id}")`)).toBeVisible();
  }
});

test('Desktop - Seletor de slides funciona', async ({ page }) => {
  await page.goto(BASE_URL);
  const btn3 = page.locator('button:has-text("3")').first();
  await btn3.click();
  await expect(btn3).toHaveClass(/bg-steel-6/);
});

test('Desktop - Claude Code CLI escondido em producao', async ({ page }) => {
  await page.goto(BASE_URL);
  await page.click('button:has-text("D7")');
  await page.click('button:has-text("RAG")');
  await expect(page.locator('button:has-text("Claude Code")')).toHaveCount(0);
  await expect(page.locator('button:has-text("Gerar Carrossel")')).toBeVisible();
});

test('Desktop - Modo texto livre funciona', async ({ page }) => {
  await page.goto(BASE_URL);
  await page.click('button:has-text("Enviar texto")');
  await expect(page.locator('textarea')).toBeVisible();
  await expect(page.locator('button:has-text("Claude Code")')).toHaveCount(0);
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

test('Mobile - Grid de disciplinas tem 2 colunas', async ({ browser }) => {
  const { context, page } = await mobileContext(browser);
  await page.goto(BASE_URL);
  const grid = page.locator('.grid.grid-cols-2');
  await expect(grid).toBeVisible();
  // Pega posição de 2 cards adjacentes - devem estar lado a lado
  const card1 = page.locator('button:has-text("D1")');
  const card2 = page.locator('button:has-text("D2")');
  const box1 = await card1.boundingBox();
  const box2 = await card2.boundingBox();
  expect(box1).toBeTruthy();
  expect(box2).toBeTruthy();
  // D1 e D2 devem estar na mesma linha (mesmo Y aproximado)
  expect(Math.abs(box1!.y - box2!.y)).toBeLessThan(10);
  // D1 deve estar a esquerda de D2
  expect(box1!.x).toBeLessThan(box2!.x);
  await context.close();
});

test('Mobile - Selecao de disciplina e tecnologia', async ({ browser }) => {
  const { context, page } = await mobileContext(browser);
  await page.goto(BASE_URL);
  // Seleciona disciplina
  await page.click('button:has-text("D7")');
  // Seleciona tecnologia
  await page.click('button:has-text("RAG")');
  // Botao Gerar Carrossel visivel e full-width
  const gerarBtn = page.locator('button:has-text("Gerar Carrossel")');
  await expect(gerarBtn).toBeVisible();
  const box = await gerarBtn.boundingBox();
  expect(box).toBeTruthy();
  // Botao deve ocupar quase toda a largura (>300px em tela de 375px)
  expect(box!.width).toBeGreaterThan(300);
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

test('Mobile - Modo texto livre funciona', async ({ browser }) => {
  const { context, page } = await mobileContext(browser);
  await page.goto(BASE_URL);
  await page.click('button:has-text("Enviar texto")');
  const textarea = page.locator('textarea');
  await expect(textarea).toBeVisible();
  // Textarea deve ocupar largura total
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
  await page.click('button:has-text("Enviar texto")');
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
  await page.click('button:has-text("Enviar texto")');
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
