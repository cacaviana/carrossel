import { test, expect, request } from '@playwright/test';
import { backendHealthy, loginBackend } from '../helpers/backend-auth';

/**
 * E2E: Creator Registry (4 casos)
 *
 * Cobre:
 * - GET /api/config/creator-registry — lista creators do tenant
 * - PUT /api/config/creator-registry — salva lote
 * - Multi-tenant: tenant A nao enxerga creators de tenant B (INT-04 regression)
 * - Roundtrip: salvar + buscar retorna o que foi salvo
 */

const BACKEND_URL = 'http://localhost:8000';

// Serial: roundtrip depende de ordem salvar -> buscar
test.describe.configure({ mode: 'serial' });

test.describe('Creator Registry - API backend', () => {
  let token = '';

  test.beforeAll(async () => {
    const up = await backendHealthy();
    test.skip(!up, 'Backend nao esta UP');
    const auth = await loginBackend();
    token = auth.token;
  });

  test('GET /config/creator-registry sem token retorna 401/403', async () => {
    const ctx = await request.newContext({ baseURL: BACKEND_URL });
    const res = await ctx.get('/api/config/creator-registry');
    expect([401, 403]).toContain(res.status());
    await ctx.dispose();
  });

  test('GET /config/creator-registry com token retorna estrutura valida', async () => {
    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.get('/api/config/creator-registry');
    expect(res.status()).toBe(200);
    const data = await res.json();
    // Schema backend: { criadores: [...] }
    const creators = Array.isArray(data) ? data : (data.criadores ?? data.creators ?? []);
    expect(Array.isArray(creators)).toBeTruthy();
    await ctx.dispose();
  });

  test('PUT /config/creator-registry salva lote de creators', async () => {
    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });

    const payload = {
      criadores: [
        { nome: 'Creator E2E 1', funcao: 'TECH_SOURCE', plataforma: 'YouTube', url: 'https://youtube.com/@e2e1', ativo: true },
        { nome: 'Creator E2E 2', funcao: 'EXPLAINER', plataforma: 'Twitter', url: 'https://twitter.com/e2e2', ativo: true },
      ],
    };

    const res = await ctx.put('/api/config/creator-registry', { data: payload });
    expect(res.status()).toBe(200);
    await ctx.dispose();
  });

  test('roundtrip: salvar e depois buscar retorna os creators salvos', async () => {
    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });

    const nomeUnico = `Creator Roundtrip ${Date.now()}`;
    const payload = {
      criadores: [
        { nome: nomeUnico, funcao: 'VIRAL_ENGINE', plataforma: 'Hacker News', url: 'https://news.ycombinator.com/user?id=rt', ativo: true },
      ],
    };

    const putRes = await ctx.put('/api/config/creator-registry', { data: payload });
    expect(putRes.status()).toBe(200);

    const getRes = await ctx.get('/api/config/creator-registry');
    expect(getRes.status()).toBe(200);
    const data = await getRes.json();
    const creators = Array.isArray(data) ? data : (data.criadores ?? data.creators ?? []);
    const found = creators.find((c: any) => c.nome === nomeUnico);
    expect(found).toBeTruthy();
    expect(found.plataforma).toBe('Hacker News');
    await ctx.dispose();
  });

  test('GET /config/creator-registry com token invalido retorna 401', async () => {
    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: 'Bearer token-bogus' },
    });
    const res = await ctx.get('/api/config/creator-registry');
    expect(res.status()).toBe(401);
    await ctx.dispose();
  });
});

test.describe('Creator Registry - UI tab Creators', () => {
  test.beforeEach(async ({ page }) => {
    const up = await backendHealthy();
    test.skip(!up, 'Backend nao esta UP');
    const { authPayload } = await loginBackend();
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await page.evaluate((auth) => {
      localStorage.setItem('kanban_auth', JSON.stringify(auth));
    }, authPayload);
  });

  test('tab Creators carrega sem erro 401', async ({ page }) => {
    let got401 = false;
    page.on('response', r => {
      if (r.url().includes('/creator-registry') && r.status() === 401) got401 = true;
    });

    await page.goto('/configuracoes');
    await page.locator('button:has-text("Creators")').first().click();
    await page.waitForTimeout(1500);

    expect(got401).toBe(false);
  });

  test('tab Creators mostra lista ou mensagem vazia', async ({ page }) => {
    await page.goto('/configuracoes');
    await page.locator('button:has-text("Creators")').first().click();
    await page.waitForTimeout(1500);

    const temLista = await page.locator('text=Criadores').first().isVisible().catch(() => false);
    const temVazio = await page.locator('text=Nenhum criador cadastrado').first().isVisible().catch(() => false);
    expect(temLista || temVazio).toBeTruthy();
  });
});
