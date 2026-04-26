import { test, expect, request } from '@playwright/test';
import { backendHealthy, loginBackend, loginReal } from '../helpers/backend-auth';

/**
 * E2E: Fluxo do CTA do anuncio.
 *
 * Cobre as 5 mudancas que conectam o input "CTA do anuncio" da home ate
 * o botao renderizado pelo Gemini:
 *   1. Input pre-preenche com brand.cta_anuncio quando troca a marca
 *   2. Depois que o user edita, trocar de marca nao sobrescreve
 *   3. Form envia `cta` no payload do POST /api/pipelines/
 *   4. Backend persiste `[CTA:texto]` no tema do pipeline
 *   5. Modo texto_pronto pre-popula o copywriter com cta + _cta_user=true
 *
 * As suites de UI usam interceptacao de rede (mocks) pra nao depender
 * de brands especificas no Mongo. As de backend batem direto na API.
 */

const BACKEND_URL = 'http://localhost:8000';

test.describe('Anuncio CTA - UI (homepage formato=anuncio)', () => {
  test.beforeEach(async ({ page }) => {
    // Mock /api/brands (lista) e /api/brands/{slug} (detalhe) — independente do Mongo
    await page.route('**/api/brands', async (route) => {
      if (route.request().method() !== 'GET') return route.continue();
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify([
          { slug: 'brand-com-cta', nome: 'Brand Com CTA', cor_principal: '#A78BFA', cor_fundo: '#0A0A0F' },
          { slug: 'brand-sem-cta', nome: 'Brand Sem CTA', cor_principal: '#34D399', cor_fundo: '#0A0A0F' },
        ]),
      });
    });
    await page.route('**/api/brands/brand-com-cta', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          slug: 'brand-com-cta', nome: 'Brand Com CTA',
          cta_anuncio: 'Inscreva-se gratis',
          cores: {}, comunicacao: {}, elementos: {},
        }),
      });
    });
    await page.route('**/api/brands/brand-sem-cta', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          slug: 'brand-sem-cta', nome: 'Brand Sem CTA',
          cta_anuncio: '',
          cores: {}, comunicacao: {}, elementos: {},
        }),
      });
    });
    // Mock foto pra evitar 404
    await page.route('**/api/brands/*/foto', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ foto: '' }) });
    });
    // Login real (mocks de rota nao afetam o backend de auth do localStorage)
    try {
      await loginReal(page);
    } catch {
      // se backend down, segue: testes que exigem auth vao falhar com mensagem clara
    }
  });

  test('formato=anuncio mostra input data-testid="campo-cta-anuncio"', async ({ page }) => {
    await page.goto('/?formato=anuncio', { waitUntil: 'domcontentloaded' });
    const input = page.locator('[data-testid="campo-cta-anuncio"]');
    await expect(input).toBeVisible({ timeout: 10_000 });
  });

  test('selecionar brand com cta_anuncio pre-preenche o input', async ({ page }) => {
    await page.goto('/?formato=anuncio', { waitUntil: 'domcontentloaded' });
    // Espera lista carregar e clica na brand com cta
    const opt = page.locator('button:has-text("Brand Com CTA")').first();
    await expect(opt).toBeVisible({ timeout: 10_000 });
    await opt.click();
    const input = page.locator('[data-testid="campo-cta-anuncio"]');
    await expect(input).toHaveValue('Inscreva-se gratis', { timeout: 5_000 });
  });

  test('depois que user edita, trocar de brand nao sobrescreve', async ({ page }) => {
    await page.goto('/?formato=anuncio', { waitUntil: 'domcontentloaded' });
    await page.locator('button:has-text("Brand Com CTA")').first().click();
    const input = page.locator('[data-testid="campo-cta-anuncio"]');
    await expect(input).toHaveValue('Inscreva-se gratis', { timeout: 5_000 });
    // User digita um valor proprio
    await input.fill('Fale conosco');
    // Troca de brand — nao deve sobrescrever
    await page.locator('button:has-text("Brand Sem CTA")').first().click();
    await expect(input).toHaveValue('Fale conosco');
    // Volta pra brand com cta — tambem nao deve sobrescrever
    await page.locator('button:has-text("Brand Com CTA")').first().click();
    await expect(input).toHaveValue('Fale conosco');
  });

  test('submeter envia o cta digitado no payload do POST /api/pipelines/', async ({ page }) => {
    let payloadEnviado: any = null;
    const fakeId = '00000000-0000-4000-8000-000000000001';
    // Intercepta o POST e responde 201 com UUID valido (evita o backend tentar
    // resolver um ID falso depois do redirect e quebrar a SQL query).
    await page.route('**/api/pipelines/', async (route) => {
      if (route.request().method() !== 'POST') return route.continue();
      payloadEnviado = JSON.parse(route.request().postData() || '{}');
      await route.fulfill({
        status: 201,
        contentType: 'application/json',
        body: JSON.stringify({ id: fakeId, tema: 'x', formato: 'anuncio', status: 'pendente' }),
      });
    });
    // Intercepta o GET subsequente pra evitar que a pagina /pipeline/{id} bate no backend
    await page.route(`**/api/pipelines/${fakeId}`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ id: fakeId, tema: 'x', formato: 'anuncio', status: 'pendente', etapa_atual: 'strategist' }),
      });
    });

    await page.goto('/?formato=anuncio', { waitUntil: 'domcontentloaded' });
    await page.locator('button:has-text("Brand Com CTA")').first().click();
    // Modo ideia + tema valido
    const btnIdeia = page.locator('button:has-text("Ideia livre")').first();
    if (await btnIdeia.isVisible()) await btnIdeia.click();
    await page.locator('[data-testid="campo-tema"]').fill('Pos em IA aplicada para devs experientes');
    // Apaga pre-preenchido e digita CTA proprio
    const cta = page.locator('[data-testid="campo-cta-anuncio"]');
    await cta.fill('Fale conosco');
    await page.locator('[data-testid="btn-criar-pipeline"]').click();
    // Espera o POST ser interceptado
    await expect.poll(() => payloadEnviado, { timeout: 10_000 }).not.toBeNull();
    expect(payloadEnviado.cta).toBe('Fale conosco');
    expect(payloadEnviado.formatos).toContain('anuncio');
  });
});

// Serial: evita stress paralelo no asyncio do uvicorn (Windows tem WinError 64
// quando muitos workers batem em rapido fechamento de socket).
test.describe.configure({ mode: 'serial' });

test.describe('Anuncio CTA - Backend (API direta)', () => {
  let token = '';

  test.beforeAll(async () => {
    const up = await backendHealthy();
    test.skip(!up, 'Backend nao esta UP em localhost:8000');
    const auth = await loginBackend();
    token = auth.token;
  });

  test('POST /api/pipelines/ formato=anuncio + cta -> tema gravado tem [CTA:texto]', async () => {
    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.post('/api/pipelines/', {
      data: {
        tema: 'Tema de teste anuncio E2E',
        formatos: ['anuncio'],
        modo_entrada: 'ideia',
        avatar_mode: 'sem',
        max_slides: 3,
        cta: 'Inscreva-se gratis',
      },
    });
    expect(res.status()).toBe(201);
    const body = await res.json();
    expect(body.id).toBeTruthy();

    // Le o pipeline criado e confere o tema
    const get = await ctx.get(`/api/pipelines/${body.id}`);
    expect(get.ok()).toBeTruthy();
    const pipeline = await get.json();
    expect(pipeline.tema).toContain('[CTA:Inscreva-se gratis]');
    await ctx.dispose();
  });

  test('POST sem cta nao adiciona [CTA:...] ao tema', async () => {
    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.post('/api/pipelines/', {
      data: {
        tema: 'Tema de teste sem cta E2E',
        formatos: ['anuncio'],
        modo_entrada: 'ideia',
        avatar_mode: 'sem',
        max_slides: 3,
      },
    });
    expect(res.status()).toBe(201);
    const { id } = await res.json();
    const get = await ctx.get(`/api/pipelines/${id}`);
    const pipeline = await get.json();
    expect(pipeline.tema).not.toContain('[CTA:');
    await ctx.dispose();
  });

  test('modo texto_pronto + cta -> copywriter pre-populado com cta + _cta_user=true', async () => {
    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.post('/api/pipelines/', {
      data: {
        tema: 'Faca uma consultoria',
        formatos: ['anuncio'],
        modo_entrada: 'texto_pronto',
        avatar_mode: 'sem',
        slides_texto_pronto: [{
          principal: 'Faca uma consultoria',
          alternativo: 'E destrave seu futuro',
          tipo_layout: 'texto',
        }],
        cta: 'Fale conosco',
      },
    });
    expect(res.status()).toBe(201);
    const { id } = await res.json();

    // Le a etapa copywriter — em texto_pronto ja vem aprovada e pre-populada
    const cs = await ctx.get(`/api/pipelines/${id}/etapas/copywriter`);
    expect(cs.ok()).toBeTruthy();
    const stepData = await cs.json();
    const saida = stepData.saida || {};
    expect(saida.cta).toBe('Fale conosco');
    expect(saida._cta_user).toBe(true);
    // headline nao deve carregar o sufixo [CTA:...]
    expect(saida.headline || '').not.toContain('[CTA:');
    await ctx.dispose();
  });
});
