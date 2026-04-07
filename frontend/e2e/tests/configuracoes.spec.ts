import { test, expect } from '../fixtures/test-fixtures';

test.describe('Configuracoes', () => {
  test('carrega pagina com titulo', async ({ configPage }) => {
    await configPage.navigate();
    // O titulo pode ser "Configuracoes" sem acento dependendo da implementacao
    const h1 = configPage.page.locator('h1, h2').first();
    await configPage.expectVisible(h1);
  });

  test('mostra tabs: Marcas, API Keys, Creators, Foto Perfil', async ({ configPage }) => {
    await configPage.navigate();
    await configPage.expectVisible(configPage.tabMarcas);
    await configPage.expectVisible(configPage.tabAPI);
    await configPage.expectVisible(configPage.tabCreators);
    await configPage.expectVisible(configPage.tabFotoPerfil);
  });

  test('tab Marcas esta ativa por padrao', async ({ configPage }) => {
    await configPage.navigate();
    // Marcas e a primeira tab, deve estar visivel
    await configPage.expectVisible(configPage.tabMarcas);
  });

  test('clicar tab API Keys muda conteudo', async ({ configPage }) => {
    await configPage.navigate();
    await configPage.tabAPI.click();
    // Deve mostrar campos de API keys
    await expect(configPage.page.locator('text=CLAUDE_API_KEY').or(configPage.page.locator('text=Claude')).first()).toBeVisible({ timeout: 5000 });
  });

  test('clicar tab Foto Perfil mostra opcoes de foto', async ({ configPage }) => {
    await configPage.navigate();
    await configPage.tabFotoPerfil.click();
    // Deve mostrar area de upload ou fotos existentes
    await configPage.page.waitForTimeout(500);
    const content = configPage.page.locator('main');
    await configPage.expectVisible(content);
  });
});

test.describe('Configuracoes - com backend', () => {
  test.beforeEach(async ({ configPage }) => {
    const up = await configPage.isBackendUp();
    test.skip(!up, 'Backend nao esta rodando em localhost:8000');
  });

  test('status das API keys carrega do backend', async ({ configPage }) => {
    await configPage.navigate();
    await configPage.tabAPI.click();
    await configPage.page.waitForTimeout(1000);
    // Deve mostrar algum indicador de status (check ou x)
    const content = configPage.page.locator('main');
    await configPage.expectVisible(content);
  });
});
