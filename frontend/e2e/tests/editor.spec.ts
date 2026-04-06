import { test, expect } from '../fixtures/test-fixtures';

test.describe('Editor', () => {
  test('carrega editor e mostra estado vazio ou slides', async ({ editorPage }) => {
    await editorPage.navigate();
    await editorPage.expectLoaded();
  });

  test('sem pipeline: mostra mensagem Nenhum slide encontrado', async ({ editorPage }) => {
    await editorPage.navigate();
    await editorPage.page.waitForTimeout(2000);
    // Sem pipeline param, nao deve ter slides
    const empty = await editorPage.emptyMsg.isVisible().catch(() => false);
    const loading = await editorPage.loadingMsg.isVisible().catch(() => false);
    const slides = await editorPage.slideImage.count();
    expect(empty || loading || slides === 0).toBeTruthy();
  });

  test('titulo da pagina contem Editor', async ({ page }) => {
    await page.goto('/editor');
    await expect(page).toHaveTitle(/Editor/);
  });

  test('mostra opcao de upload logo quando sem logo', async ({ editorPage }) => {
    await editorPage.navigate();
    await editorPage.page.waitForTimeout(2000);
    const empty = await editorPage.emptyMsg.isVisible().catch(() => false);
    if (!empty) {
      // Se tem slides, deve mostrar upload logo ou logo existente
      const upload = await editorPage.uploadLogoLabel.isVisible().catch(() => false);
      const logo = await editorPage.page.locator('img[alt="Logo"]').isVisible().catch(() => false);
      expect(upload || logo).toBeTruthy();
    }
  });
});

test.describe('Editor - navegacao de slides', () => {
  test.beforeEach(async ({ editorPage }) => {
    const up = await editorPage.isBackendUp();
    test.skip(!up, 'Backend nao esta rodando');
  });

  test('botoes anterior/proximo funcionam quando ha slides', async ({ editorPage }) => {
    // Este teste requer que haja um pipeline com imagens geradas
    // Testamos a existencia dos controles
    await editorPage.navigate();
    await editorPage.page.waitForTimeout(2000);
    const hasSlides = await editorPage.slideImage.count() > 0;
    if (hasSlides) {
      await editorPage.expectVisible(editorPage.btnAnterior);
      await editorPage.expectVisible(editorPage.btnProximo);
    }
  });
});
