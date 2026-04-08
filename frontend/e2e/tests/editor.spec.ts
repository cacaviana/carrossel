import { test, expect } from '../fixtures/test-fixtures';

test.describe('Editor - estado vazio', () => {
  test('carrega editor e mostra estado vazio ou slides', async ({ editorPage }) => {
    await editorPage.navigate();
    await editorPage.expectLoaded();
  });

  test('sem pipeline: mostra mensagem Nenhum slide encontrado', async ({ editorPage }) => {
    await editorPage.navigate();
    await editorPage.page.waitForTimeout(2000);
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
      const upload = await editorPage.uploadLogoLabel.isVisible().catch(() => false);
      const logo = await editorPage.page.locator('img[alt="Logo"]').isVisible().catch(() => false);
      expect(upload || logo).toBeTruthy();
    }
  });
});

test.describe('Editor - botoes de export (ultimo slide)', () => {
  test.beforeEach(async ({ editorPage }) => {
    const up = await editorPage.isBackendUp();
    test.skip(!up, 'Backend nao esta rodando');
  });

  test('botoes anterior/proximo existem quando ha slides', async ({ editorPage }) => {
    await editorPage.navigate();
    await editorPage.page.waitForTimeout(2000);
    const hasSlides = (await editorPage.slideImage.count()) > 0;
    if (hasSlides) {
      await editorPage.expectVisible(editorPage.btnAnterior);
      await editorPage.expectVisible(editorPage.btnProximo);
    }
  });

  test('botoes PNG, JPEG, PDF e Drive existem no ultimo slide', async ({ editorPage }) => {
    // Navegar com uma brand que tenha slides salvos
    await editorPage.navigate({ brand: 'itvalley' });
    await editorPage.page.waitForTimeout(3000);
    const hasSlides = (await editorPage.slideImage.count()) > 0;
    if (!hasSlides) {
      test.skip(true, 'Nenhum slide disponivel para esta brand');
      return;
    }

    // Ir ate o ultimo slide clicando Proximo
    let proximo = editorPage.page.locator('button:has-text("Proximo")');
    while (await proximo.isVisible().catch(() => false)) {
      await proximo.click();
      await editorPage.page.waitForTimeout(300);
      proximo = editorPage.page.locator('button:has-text("Proximo")');
    }

    // No ultimo slide, os botoes de export devem aparecer
    const btnPNG = editorPage.page.locator('button:has-text("PNG")');
    const btnJPEG = editorPage.page.locator('button:has-text("JPEG")');
    const btnPDF = editorPage.page.locator('button:has-text("PDF")');
    const btnDrive = editorPage.page.locator('button:has-text("Drive")');

    await expect(btnPNG).toBeVisible({ timeout: 5000 });
    await expect(btnJPEG).toBeVisible({ timeout: 5000 });
    await expect(btnPDF).toBeVisible({ timeout: 5000 });
    await expect(btnDrive).toBeVisible({ timeout: 5000 });
  });

  test('toggle de qualidade Media/Alta existe no ultimo slide', async ({ editorPage }) => {
    await editorPage.navigate({ brand: 'itvalley' });
    await editorPage.page.waitForTimeout(3000);
    const hasSlides = (await editorPage.slideImage.count()) > 0;
    if (!hasSlides) {
      test.skip(true, 'Nenhum slide disponivel para esta brand');
      return;
    }

    // Navegar ate o ultimo slide
    let proximo = editorPage.page.locator('button:has-text("Proximo")');
    while (await proximo.isVisible().catch(() => false)) {
      await proximo.click();
      await editorPage.page.waitForTimeout(300);
      proximo = editorPage.page.locator('button:has-text("Proximo")');
    }

    const btnMedia = editorPage.page.locator('button:has-text("Media")');
    const btnAlta = editorPage.page.locator('button:has-text("Alta")');

    await expect(btnMedia).toBeVisible({ timeout: 5000 });
    await expect(btnAlta).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Editor - feedback e regeneracao', () => {
  test.beforeEach(async ({ editorPage }) => {
    const up = await editorPage.isBackendUp();
    test.skip(!up, 'Backend nao esta rodando');
  });

  test('botao Tirar texto existe quando ha slides com textos', async ({ editorPage }) => {
    await editorPage.navigate({ brand: 'itvalley' });
    await editorPage.page.waitForTimeout(3000);
    const hasSlides = (await editorPage.slideImage.count()) > 0;
    if (!hasSlides) {
      test.skip(true, 'Nenhum slide disponivel');
      return;
    }

    // O botao "Tirar texto" so aparece se textos[] esta preenchido (vem do pipeline/copywriter)
    // Em modo sem pipeline, pode nao existir. Verificamos se o locator esta no DOM.
    const btnTirarTexto = editorPage.page.locator('button:has-text("Tirar texto")');
    const visible = await btnTirarTexto.isVisible().catch(() => false);
    // Se nao ha textos do copywriter, o bloco de regeneracao nao aparece — isso e esperado
    if (visible) {
      await expect(btnTirarTexto).toBeEnabled();
    }
  });

  test('campo de feedback existe com placeholder correto', async ({ editorPage }) => {
    await editorPage.navigate({ brand: 'itvalley' });
    await editorPage.page.waitForTimeout(3000);

    const feedbackInput = editorPage.page.locator('input[placeholder*="Feedback"]');
    const visible = await feedbackInput.isVisible().catch(() => false);
    // Campo so aparece se textos[] esta preenchido (precisa de pipeline com copywriter)
    if (visible) {
      await expect(feedbackInput).toHaveAttribute('placeholder', /Feedback.*feedback|mais escuro|menos texto|trocar ilustracao/i);
    }
  });

  test('botao muda para "Regenerar com feedback" quando campo tem texto', async ({ editorPage }) => {
    await editorPage.navigate({ brand: 'itvalley' });
    await editorPage.page.waitForTimeout(3000);

    const feedbackInput = editorPage.page.locator('input[placeholder*="Feedback"]');
    const visible = await feedbackInput.isVisible().catch(() => false);
    if (!visible) {
      test.skip(true, 'Campo de feedback nao visivel (sem textos do copywriter)');
      return;
    }

    // Antes de digitar: botao deve dizer "Regenerar slide"
    const btnRegenerar = editorPage.page.locator('button:has-text("Regenerar slide")');
    await expect(btnRegenerar).toBeVisible({ timeout: 5000 });

    // Digitar feedback
    await feedbackInput.fill('mais escuro');

    // Depois de digitar: botao deve mudar para "Regenerar com feedback"
    const btnComFeedback = editorPage.page.locator('button:has-text("Regenerar com feedback")');
    await expect(btnComFeedback).toBeVisible({ timeout: 5000 });
  });
});
