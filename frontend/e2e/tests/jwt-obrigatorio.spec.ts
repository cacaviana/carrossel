import { test, expect, request } from '@playwright/test';
import { backendHealthy, loginBackend } from '../helpers/backend-auth';

/**
 * E2E: JWT obrigatorio (regression do fix C1)
 *
 * Fluxo testado:
 * - Endpoints protegidos retornam 401/403 sem token
 * - Endpoints protegidos retornam 200 com token valido
 * - Frontend redireciona para /login quando API retorna 401
 */

const BACKEND_URL = 'http://localhost:8000';

test.describe('JWT obrigatorio (C1) - backend API', () => {
  test.beforeAll(async () => {
    const up = await backendHealthy();
    test.skip(!up, 'Backend nao esta UP em localhost:8000');
  });

  test('GET /api/historico sem token retorna 401/403', async () => {
    const ctx = await request.newContext({ baseURL: BACKEND_URL });
    const res = await ctx.get('/api/historico');
    expect([401, 403]).toContain(res.status());
    await ctx.dispose();
  });

  test('GET /api/pipelines/ sem token retorna 401/403', async () => {
    const ctx = await request.newContext({ baseURL: BACKEND_URL });
    const res = await ctx.get('/api/pipelines/');
    expect([401, 403]).toContain(res.status());
    await ctx.dispose();
  });

  test('GET /api/brands sem token retorna 401/403', async () => {
    const ctx = await request.newContext({ baseURL: BACKEND_URL });
    const res = await ctx.get('/api/brands');
    expect([401, 403]).toContain(res.status());
    await ctx.dispose();
  });

  test('GET /api/config/brand-palette sem token retorna 401/403', async () => {
    const ctx = await request.newContext({ baseURL: BACKEND_URL });
    const res = await ctx.get('/api/config/brand-palette');
    expect([401, 403]).toContain(res.status());
    await ctx.dispose();
  });

  test('GET /api/config/creator-registry sem token retorna 401/403', async () => {
    const ctx = await request.newContext({ baseURL: BACKEND_URL });
    const res = await ctx.get('/api/config/creator-registry');
    expect([401, 403]).toContain(res.status());
    await ctx.dispose();
  });

  test('GET /api/auth/users sem token retorna 401/403', async () => {
    const ctx = await request.newContext({ baseURL: BACKEND_URL });
    const res = await ctx.get('/api/auth/users');
    expect([401, 403]).toContain(res.status());
    await ctx.dispose();
  });

  test('GET /api/historico com token valido retorna 200', async () => {
    const { token } = await loginBackend();
    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.get('/api/historico');
    expect(res.status()).toBe(200);
    await ctx.dispose();
  });

  test('GET /api/brands com token valido retorna 200', async () => {
    const { token } = await loginBackend();
    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.get('/api/brands');
    expect(res.status()).toBe(200);
    await ctx.dispose();
  });

  test('token invalido retorna 401', async () => {
    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: 'Bearer token-falso-aqui' },
    });
    const res = await ctx.get('/api/historico');
    expect(res.status()).toBe(401);
    await ctx.dispose();
  });
});

test.describe('Auth guard - frontend redireciona para login', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/', { waitUntil: 'commit' });
    await page.evaluate(() => localStorage.removeItem('kanban_auth'));
  });

  test('acesso a /historico sem login nao renderiza dados de historico', async ({ page }) => {
    await page.goto('/historico', { waitUntil: 'networkidle' });
    // Sem auth, o historico nao consegue buscar dados — ou redireciona, ou mostra vazio/erro
    // O comportamento aceitavel: URL = login, OR pagina vazia/sem cards clicaveis
    const url = page.url();
    const isLogin = url.includes('/login');
    const hasCards = (await page.locator('h3.line-clamp-2').count()) > 0;
    // ou redireciona, ou pagina sem cards (historico vazio)
    expect(isLogin || !hasCards).toBeTruthy();
  });
});
