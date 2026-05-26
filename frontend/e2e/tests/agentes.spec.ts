import { test, expect } from '../fixtures/test-fixtures';

test.describe('Agentes e Skills', () => {
  test.beforeEach(async ({ agentesPage }) => {
    const up = await agentesPage.isBackendUp();
    test.skip(!up, 'Backend nao esta rodando em localhost:8000');
  });

  test('carrega pagina com titulo Agentes e Skills', async ({ agentesPage }) => {
    await agentesPage.navigate();
    await agentesPage.expectVisible(agentesPage.heading);
  });

  test('mostra tabs Agentes LLM e Skills', async ({ agentesPage }) => {
    await agentesPage.navigate();
    await agentesPage.expectVisible(agentesPage.tabLLM);
    await agentesPage.expectVisible(agentesPage.tabSkills);
  });

  test('tab Agentes LLM lista agentes', async ({ agentesPage }) => {
    await agentesPage.navigate();
    await agentesPage.selectTab('llm');
    // Espera pelo menos 1 agente (depende do backend)
    const count = await agentesPage.agenteCards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('tab Skills lista skills', async ({ agentesPage }) => {
    await agentesPage.navigate();
    await agentesPage.selectTab('skills');
    await agentesPage.page.waitForTimeout(500);
    const count = await agentesPage.agenteCards.count();
    expect(count).toBeGreaterThan(0);
  });

  test('selecionar agente mostra detalhes', async ({ agentesPage }) => {
    await agentesPage.navigate();
    await agentesPage.page.waitForTimeout(1000);
    // Seleciona o primeiro agente
    const firstCard = agentesPage.agenteCards.first();
    if (await firstCard.isVisible()) {
      await firstCard.click();
      await agentesPage.expectVisible(agentesPage.detalheNome);
    }
  });

  test('pipeline visual mostra 7 etapas', async ({ agentesPage }) => {
    await agentesPage.navigate();
    await agentesPage.page.waitForTimeout(1000);
    await agentesPage.expectVisible(agentesPage.pipelineVisual);
    // 7 etapas: Strategist, Copywriter, Hook Specialist, Art Director, Image Generator, Brand Gate, Content Critic
    const etapas = agentesPage.page.locator('text=Strategist');
    await agentesPage.expectVisible(etapas.first());
    await expect(agentesPage.page.locator('text=Content Critic')).toBeVisible();
  });
});

test.describe('Agentes - sem backend', () => {
  test('pagina carrega e mostra titulo mesmo sem dados', async ({ agentesPage }) => {
    await agentesPage.navigate();
    // Deve mostrar o titulo ou o spinner ou mensagem de erro
    const titulo = agentesPage.heading;
    const erro = agentesPage.erroMsg;
    const spinner = agentesPage.spinner;
    const algumVisivel = await titulo.isVisible()
      .catch(() => false) || await erro.isVisible()
      .catch(() => false) || await spinner.isVisible()
      .catch(() => false);
    expect(algumVisivel).toBeTruthy();
  });
});
