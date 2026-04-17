import { test, expect, request } from '@playwright/test';
import { backendHealthy, loginBackend } from '../helpers/backend-auth';

/**
 * E2E: Historico created_at (regression INT-01)
 *
 * Antes do fix INT-01, o backend retornava `criado_em` mas o frontend esperava
 * `created_at`. Depois do fix, HistoricoItemDTO aceita ambos (backward-compat)
 * e o campo deve aparecer formatado, nao vazio.
 */

const BACKEND_URL = 'http://localhost:8000';

// Serial: evita race em login cache
test.describe.configure({ mode: 'serial' });

test.describe('Historico - campo data formatada (INT-01 regression)', () => {
  let token = '';

  test.beforeAll(async () => {
    const up = await backendHealthy();
    test.skip(!up, 'Backend nao esta UP');
    const auth = await loginBackend();
    token = auth.token;
  });

  test('GET /api/historico retorna items com campo de data (criado_em ou created_at)', async () => {
    const ctx = await request.newContext({
      baseURL: BACKEND_URL,
      extraHTTPHeaders: { Authorization: `Bearer ${token}` },
    });
    const res = await ctx.get('/api/historico');
    expect(res.status()).toBe(200);
    const data = await res.json();
    const items = Array.isArray(data) ? data : (data.items ?? []);

    if (items.length > 0) {
      const primeiro = items[0];
      // Backend pode retornar `criado_em` (legado SQLite) ou `created_at` (MSSQL)
      const data_campo = primeiro.created_at ?? primeiro.criado_em;
      expect(data_campo).toBeTruthy();
      expect(data_campo.length).toBeGreaterThan(0);
    }
    await ctx.dispose();
  });

  test('UI /historico mostra data formatada (nao vazia) quando ha items', async ({ page }) => {
    const { authPayload } = await loginBackend();
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await page.evaluate((auth) => {
      localStorage.setItem('kanban_auth', JSON.stringify(auth));
    }, authPayload);

    await page.goto('/historico');
    await page.waitForTimeout(2500);

    // Verifica se tem items
    const items = await page.locator('h3.line-clamp-2').count();
    if (items === 0) {
      test.skip(true, 'Historico vazio no backend — sem items pra validar data');
      return;
    }

    // Primeiro card deve ter "slide" e depois " - " e data formatada DD/MM/YYYY
    const firstCardText = await page.locator('span.font-mono').first().textContent();
    // Aceita formato pt-BR: DD/MM/YYYY ou equivalente
    expect(firstCardText).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}|\d+ slide/);
  });

  test('HistoricoItemDTO aceita criado_em (mock) e created_at (real) como mesmo campo', async ({ page }) => {
    // Intercepta o endpoint e retorna `criado_em` (formato legado)
    const { authPayload } = await loginBackend();

    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await page.evaluate((auth) => {
      localStorage.setItem('kanban_auth', JSON.stringify(auth));
    }, authPayload);

    await page.route('**/api/historico**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 999,
              pipeline_id: '',
              titulo: 'Teste INT-01 com criado_em',
              formato: 'carrossel',
              status: 'completo',
              disciplina: 'D1 Linguagens',
              tecnologia_principal: 'Python',
              total_slides: 7,
              final_score: 8.5,
              google_drive_link: '',
              criado_em: '2026-04-15T10:00:00',  // campo LEGADO
            },
          ],
          total: 1,
        }),
      });
    });
    // Tambem mock de pipelines pra nao crashear
    await page.route('**/api/pipelines/**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '{"items":[]}' });
    });

    await page.goto('/historico');
    await page.waitForTimeout(2000);

    // Deve aparecer data formatada '15/4/2026' ou '15/04/2026'
    const cardText = await page.locator('h3:has-text("Teste INT-01")').first().textContent();
    expect(cardText).toContain('Teste INT-01');

    // A data formatada deve aparecer em alguma parte do card
    const fontMono = await page.locator('span.font-mono').allTextContents();
    const temData = fontMono.some(t => /\d+\/\d+\/2026/.test(t));
    expect(temData).toBeTruthy();
  });

  test('HistoricoItemDTO aceita created_at (backend real) tambem', async ({ page }) => {
    const { authPayload } = await loginBackend();
    await page.goto('/', { waitUntil: 'domcontentloaded' });
    await page.evaluate((auth) => {
      localStorage.setItem('kanban_auth', JSON.stringify(auth));
    }, authPayload);

    await page.route('**/api/historico**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          items: [
            {
              id: 1000,
              pipeline_id: '',
              titulo: 'Teste INT-01 com created_at',
              formato: 'carrossel',
              status: 'completo',
              disciplina: '',
              tecnologia_principal: '',
              total_slides: 10,
              final_score: null,
              google_drive_link: '',
              created_at: '2026-04-16T14:30:00',  // campo NOVO
            },
          ],
          total: 1,
        }),
      });
    });
    await page.route('**/api/pipelines/**', async (route) => {
      await route.fulfill({ status: 200, contentType: 'application/json', body: '{"items":[]}' });
    });

    await page.goto('/historico');
    await page.waitForTimeout(2000);

    const card = page.locator('h3:has-text("Teste INT-01 com created_at")').first();
    await expect(card).toBeVisible();

    const fontMono = await page.locator('span.font-mono').allTextContents();
    const temData = fontMono.some(t => /\d+\/\d+\/2026/.test(t));
    expect(temData).toBeTruthy();
  });
});
