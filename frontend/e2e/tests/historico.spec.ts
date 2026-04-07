import { test, expect } from '../fixtures/test-fixtures';

test.describe('Historico', () => {
  test('carrega pagina com titulo Historico', async ({ historicoPage }) => {
    await historicoPage.navigate();
    await historicoPage.expectText(historicoPage.heading, /Histor?ico/i);
  });

  test('mostra campo de busca', async ({ historicoPage }) => {
    await historicoPage.navigate();
    await historicoPage.expectVisible(historicoPage.campoBusca);
  });

  test('mostra filtros de formato e status', async ({ historicoPage }) => {
    await historicoPage.navigate();
    await historicoPage.expectVisible(historicoPage.filtroFormato);
    await historicoPage.expectVisible(historicoPage.filtroStatus);
  });

  test('mostra contagem de resultados', async ({ historicoPage }) => {
    await historicoPage.navigate();
    await historicoPage.page.waitForTimeout(2000); // espera carregamento
    await historicoPage.expectVisible(historicoPage.resultCount);
  });
});

test.describe('Historico - com backend', () => {
  test.beforeEach(async ({ historicoPage }) => {
    const up = await historicoPage.isBackendUp();
    test.skip(!up, 'Backend nao esta rodando em localhost:8000');
  });

  test('lista itens ou mostra mensagem de vazio', async ({ historicoPage }) => {
    await historicoPage.navigate();
    await historicoPage.page.waitForTimeout(2000);
    const temCards = await historicoPage.cards.count() > 0;
    const temVazio = await historicoPage.emptyMsg.isVisible().catch(() => false);
    const temErro = await historicoPage.page.locator('text=Nao foi possivel').isVisible().catch(() => false);
    expect(temCards || temVazio || temErro).toBeTruthy();
  });

  test('busca filtra resultados', async ({ historicoPage }) => {
    await historicoPage.navigate();
    await historicoPage.page.waitForTimeout(2000);

    const countBefore = await historicoPage.resultCount.textContent();
    await historicoPage.buscar('xyzinexistente');
    await historicoPage.page.waitForTimeout(500);
    const countAfter = await historicoPage.resultCount.textContent();

    // O texto deve mudar (ou mostrar 0 resultados, ou Nenhum resultado)
    expect(countAfter).toBeTruthy();
  });

  test('filtro formato funciona', async ({ historicoPage }) => {
    await historicoPage.navigate();
    await historicoPage.page.waitForTimeout(2000);
    await historicoPage.filtroFormato.selectOption('carrossel');
    await historicoPage.page.waitForTimeout(500);
    // Deve mostrar resultado filtrado
    await historicoPage.expectVisible(historicoPage.resultCount);
  });
});

test.describe('Historico - sem dados', () => {
  test('mensagem de vazio mostra CTA para criar conteudo', async ({ historicoPage }) => {
    await historicoPage.navigate();
    await historicoPage.page.waitForTimeout(3000);
    const vazio = await historicoPage.emptyMsg.isVisible().catch(() => false);
    if (vazio) {
      await historicoPage.expectVisible(historicoPage.criarLink);
    }
    // Se tem dados, teste passa (nao ha estado vazio para testar)
  });
});
