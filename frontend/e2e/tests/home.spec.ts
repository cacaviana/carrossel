import { test, expect } from '../fixtures/test-fixtures';

test.describe('Home - Content Factory', () => {
  test('carrega home com titulo Carrossel', async ({ homePage }) => {
    await homePage.navigate();
    await homePage.expectFormato('Carrossel');
  });

  test('mostra 3 modos de entrada: texto pronto, ideia livre, por disciplina', async ({ homePage }) => {
    await homePage.navigate();
    await homePage.expectVisible(homePage.btnTextoPronto);
    await homePage.expectVisible(homePage.btnIdeiaLivre);
    await homePage.expectVisible(homePage.btnPorDisciplina);
  });

  test('modo ideia livre: textarea aparece com data-testid campo-tema', async ({ homePage }) => {
    await homePage.navigate();
    await homePage.selectModoEntrada('ideia');
    await homePage.expectVisible(homePage.textareaTema);
  });

  test('wizard: preencher ideia habilita botao criar', async ({ homePage }) => {
    await homePage.navigate();
    await homePage.fillIdeia('Como usar IA generativa para criar conteudo de alta performance');
    await expect(homePage.btnCriarPipeline).toBeEnabled();
  });

  test('wizard: botao criar desabilitado com texto curto', async ({ homePage }) => {
    await homePage.navigate();
    await homePage.selectModoEntrada('ideia');
    await homePage.textareaTema.fill('curto');
    await expect(homePage.btnCriarPipeline).toBeDisabled();
  });

  test('modo disciplina: mostra grid de disciplinas (D1..D9)', async ({ homePage }) => {
    await homePage.navigate();
    await homePage.selectModoEntrada('disciplina');
    await homePage.expectVisible(homePage.page.locator('button:has-text("D1")'));
    await homePage.expectVisible(homePage.page.locator('button:has-text("D7")'));
  });

  test('disciplina: selecionar disciplina mostra tecnologias', async ({ homePage }) => {
    await homePage.navigate();
    await homePage.selectDisciplina('D7');
    // D7 = IA Gen, deve mostrar techs como RAG, Agentes, LangChain
    await expect(homePage.page.locator('text=Tecnologia')).toBeVisible();
  });

  test('modo texto pronto: mostra editor slide-a-slide', async ({ homePage }) => {
    await homePage.navigate();
    await homePage.selectModoEntrada('texto_pronto');
    // Deve mostrar "Capa" e textareas
    await expect(homePage.page.locator('text=Capa')).toBeVisible();
    await expect(homePage.page.locator('textarea').first()).toBeVisible();
  });

  test('texto pronto: botao + Adicionar slide funciona', async ({ homePage }) => {
    await homePage.navigate();
    await homePage.selectModoEntrada('texto_pronto');
    const addBtn = homePage.page.locator('button:has-text("Adicionar slide")');
    await homePage.expectVisible(addBtn);
    await addBtn.click();
    // Agora temos 4 slides (3 iniciais + 1)
    await expect(homePage.page.locator('text=Slide 4')).toBeVisible();
  });

  test('formatos: URL com ?formato=post_unico mostra Post Unico', async ({ homePage }) => {
    await homePage.navigate('post_unico');
    await homePage.expectFormato('Post Unico');
  });

  test('formatos: URL com ?formato=thumbnail_youtube mostra Thumbnail', async ({ homePage }) => {
    await homePage.navigate('thumbnail_youtube');
    await homePage.expectFormato('Thumbnail YouTube');
  });

  test('formatos: URL com ?formato=funil mostra Funil', async ({ homePage }) => {
    await homePage.navigate('funil');
    await homePage.expectFormato('Funil de Conteudo');
    await expect(homePage.page.locator('text=Strategist')).toBeVisible();
  });
});

test.describe('Home - Mobile', () => {
  test.use({ viewport: { width: 375, height: 812 } });

  test('mobile: 3 modos de entrada visiveis', async ({ homePage }) => {
    await homePage.navigate();
    await homePage.expectVisible(homePage.btnTextoPronto);
    await homePage.expectVisible(homePage.btnIdeiaLivre);
    await homePage.expectVisible(homePage.btnPorDisciplina);
  });

  test('mobile: botao criar pipeline tem tamanho touch-friendly', async ({ homePage }) => {
    await homePage.navigate();
    await homePage.fillIdeia('Tema sobre inteligencia artificial e machine learning para testes');
    await homePage.expectTouchFriendly(homePage.btnCriarPipeline, 40);
  });

  test('mobile: textarea ideia livre ocupa largura adequada', async ({ homePage }) => {
    await homePage.navigate();
    await homePage.selectModoEntrada('ideia');
    const box = await homePage.textareaTema.boundingBox();
    expect(box).toBeTruthy();
    expect(box!.width).toBeGreaterThan(300);
  });
});
