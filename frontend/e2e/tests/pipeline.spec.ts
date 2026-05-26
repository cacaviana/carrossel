import { test, expect } from '../fixtures/test-fixtures';

test.describe('Pipeline', () => {
  test('pipeline com ID inexistente mostra mensagem de erro', async ({ pipelinePage }) => {
    await pipelinePage.navigate('00000000-0000-0000-0000-000000000000');
    await pipelinePage.page.waitForTimeout(3000);
    // Deve mostrar "Pipeline nao encontrado" ou skeleton+erro
    const notFound = await pipelinePage.notFoundMsg.isVisible().catch(() => false);
    const erroVisible = await pipelinePage.page.locator('text=Ir para Home').isVisible().catch(() => false);
    const skeleton = await pipelinePage.skeleton.isVisible().catch(() => false);
    expect(notFound || erroVisible || skeleton).toBeTruthy();
  });

  test('pagina pipeline tem titulo no head', async ({ pipelinePage }) => {
    await pipelinePage.navigate('test');
    await expect(pipelinePage.page).toHaveTitle(/Pipeline/);
  });
});

test.describe('Pipeline - com backend', () => {
  test.beforeEach(async ({ pipelinePage }) => {
    const up = await pipelinePage.isBackendUp();
    test.skip(!up, 'Backend nao esta rodando em localhost:8000');
  });

  test('criar pipeline via home e acompanhar', async ({ homePage, pipelinePage }) => {
    await homePage.navigate();
    await homePage.fillIdeia('Como usar RAG para melhorar respostas de chatbots corporativos');
    await homePage.criarPipeline();

    // Deve redirecionar para /pipeline/[id]
    await homePage.expectURL(/\/pipeline\//);

    // Deve mostrar o tema na pagina
    await expect(homePage.page.locator('text=RAG')).toBeVisible({ timeout: 10_000 });
  });

  test('pipeline mostra 7 etapas no wizard', async ({ homePage, pipelinePage }) => {
    await homePage.navigate();
    await homePage.fillIdeia('Feature engineering para modelos de ML em producao com Python');
    await homePage.criarPipeline();
    await homePage.expectURL(/\/pipeline\//);

    // Verifica que as 7 etapas existem
    for (const label of ['Estrategia', 'Copywriting', 'Hooks', 'Direcao de Arte', 'Imagens', 'Brand Gate', 'Avaliacao Final']) {
      await expect(homePage.page.locator(`text=${label}`).first()).toBeVisible({ timeout: 10_000 });
    }
  });

  test('botao cancelar pipeline esta visivel', async ({ homePage }) => {
    await homePage.navigate();
    await homePage.fillIdeia('Deploy de modelos com Docker e Kubernetes para MLOps avancado');
    await homePage.criarPipeline();
    await homePage.expectURL(/\/pipeline\//);

    const btnCancelar = homePage.page.locator('[data-testid="btn-cancelar-pipeline"]');
    await expect(btnCancelar).toBeVisible({ timeout: 10_000 });
  });
});
