import { test, expect } from '../fixtures/test-fixtures';

test.describe('Texto Pronto - tipo_layout select', () => {
  test('select de tipo_layout aparece ao clicar Texto pronto', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectModoEntrada('texto_pronto');
    const select = homePage.page.locator('[data-testid="select-tipo-layout-0"]');
    await expect(select).toBeVisible();
  });

  test('tipo_layout tem valor padrao "texto"', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectModoEntrada('texto_pronto');
    const select = homePage.page.locator('[data-testid="select-tipo-layout-0"]');
    await expect(select).toHaveValue('texto');
  });

  test('todos os 4 valores de layout estao disponiveis (Texto, Lista, Comparativo, Dados)', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectModoEntrada('texto_pronto');
    const select = homePage.page.locator('[data-testid="select-tipo-layout-0"]');
    const options = select.locator('option');
    await expect(options).toHaveCount(4);
    await expect(options.nth(0)).toHaveText('Texto');
    await expect(options.nth(1)).toHaveText('Lista');
    await expect(options.nth(2)).toHaveText('Comparativo');
    await expect(options.nth(3)).toHaveText('Dados');
  });

  test('mudar tipo_layout de um slide altera o valor do select', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectModoEntrada('texto_pronto');
    const select = homePage.page.locator('[data-testid="select-tipo-layout-0"]');
    await select.selectOption('lista');
    await expect(select).toHaveValue('lista');
  });

  test('cada slide tem seu proprio select de tipo_layout', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectModoEntrada('texto_pronto');
    // 3 slides iniciais por padrao
    const select0 = homePage.page.locator('[data-testid="select-tipo-layout-0"]');
    const select1 = homePage.page.locator('[data-testid="select-tipo-layout-1"]');
    const select2 = homePage.page.locator('[data-testid="select-tipo-layout-2"]');
    await expect(select0).toBeVisible();
    await expect(select1).toBeVisible();
    await expect(select2).toBeVisible();
  });

  test('slides independentes: mudar layout de um nao afeta outro', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectModoEntrada('texto_pronto');
    const select0 = homePage.page.locator('[data-testid="select-tipo-layout-0"]');
    const select1 = homePage.page.locator('[data-testid="select-tipo-layout-1"]');
    await select0.selectOption('comparativo');
    await select1.selectOption('dados');
    await expect(select0).toHaveValue('comparativo');
    await expect(select1).toHaveValue('dados');
  });

  test('adicionar slide cria novo select de tipo_layout com valor padrao', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectModoEntrada('texto_pronto');
    const addBtn = homePage.page.locator('button:has-text("Adicionar slide")');
    await addBtn.click();
    const select3 = homePage.page.locator('[data-testid="select-tipo-layout-3"]');
    await expect(select3).toBeVisible();
    await expect(select3).toHaveValue('texto');
  });
});

test.describe('Galeria test-slides', () => {
  test('GET /api/test-slides retorna HTML com galeria', async ({ page }) => {
    const response = await page.request.get('http://localhost:8000/api/test-slides');
    // A rota pode retornar 404 se a pasta test_slides nao existir no ambiente
    if (response.ok()) {
      const body = await response.text();
      expect(body).toContain('Test Slides');
      expect(body).toContain('<html');
    } else {
      // 404 e aceitavel se a pasta nao existe neste ambiente
      expect(response.status()).toBe(404);
    }
  });
});
