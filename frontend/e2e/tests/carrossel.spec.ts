import { test, expect } from '../fixtures/test-fixtures';

test.describe('Carrossel (legado) - sem dados', () => {
  test('mostra mensagem Nenhum carrossel gerado', async ({ carrosselPage }) => {
    await carrosselPage.navigate();
    await carrosselPage.expectEmpty();
  });

  test('CTA Criar carrossel leva para home', async ({ carrosselPage }) => {
    await carrosselPage.navigate();
    await carrosselPage.expectVisible(carrosselPage.criarLink);
    await carrosselPage.criarLink.click();
    await carrosselPage.expectURL('/');
  });
});

test.describe('Carrossel - preview (se houver dados em store)', () => {
  test('pagina carrega sem erros JavaScript', async ({ page }) => {
    const errors: string[] = [];
    page.on('pageerror', (err) => errors.push(err.message));
    await page.goto('/carrossel');
    await page.waitForTimeout(1000);
    // Filtra erros que nao sao do nosso codigo
    const criticalErrors = errors.filter(e => !e.includes('fetch') && !e.includes('network'));
    expect(criticalErrors).toHaveLength(0);
  });

  test('titulo da pagina contem Carrossel', async ({ page }) => {
    await page.goto('/carrossel');
    await expect(page).toHaveTitle(/Carrossel/);
  });
});
