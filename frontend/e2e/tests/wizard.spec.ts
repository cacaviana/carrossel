import { test, expect } from '../fixtures/test-fixtures';

test.describe('Wizard — Carrossel', () => {
  test('navegar para /?formato=carrossel mostra titulo "Carrossel"', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.expectFormato('Carrossel');
  });

  test('3 modos de entrada existem: Texto pronto, Ideia livre, Por disciplina', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.expectVisible(homePage.btnTextoPronto);
    await homePage.expectVisible(homePage.btnIdeiaLivre);
    await homePage.expectVisible(homePage.btnPorDisciplina);
  });

  test('modo Ideia livre: preencher textarea com texto >= 20 chars habilita botao', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectModoEntrada('ideia');
    await homePage.textareaTema.fill('5 erros que todo dev comete no primeiro projeto');
    await expect(homePage.btnCriarPipeline).toBeEnabled();
  });

  test('modo Ideia livre: texto curto (< 20 chars) mantem botao desabilitado', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectModoEntrada('ideia');
    await homePage.textareaTema.fill('curto');
    await expect(homePage.btnCriarPipeline).toBeDisabled();
  });

  test('modo Ideia livre: textarea tem data-testid="campo-tema"', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectModoEntrada('ideia');
    await homePage.expectVisible(homePage.textareaTema);
  });

  test('modo Texto pronto: mostra editor slide-a-slide com "Capa"', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectModoEntrada('texto_pronto');
    await expect(homePage.page.locator('text=Capa')).toBeVisible();
    await expect(homePage.page.locator('textarea').first()).toBeVisible();
  });

  test('modo Texto pronto: botao "+ Adicionar slide" adiciona slide', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectModoEntrada('texto_pronto');
    const addBtn = homePage.page.locator('button:has-text("Adicionar slide")');
    await homePage.expectVisible(addBtn);
    await addBtn.click();
    // 3 iniciais + 1 adicionado = 4
    await expect(homePage.page.locator('text=Slide 4')).toBeVisible();
  });

  test('modo Disciplina: grid de disciplinas D1..D9 aparece', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectModoEntrada('disciplina');
    await homePage.expectVisible(homePage.page.locator('button:has-text("D1")'));
    await homePage.expectVisible(homePage.page.locator('button:has-text("D9")'));
  });

  test('modo Disciplina: selecionar disciplina D7 mostra tecnologias', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.selectDisciplina('D7');
    await expect(homePage.page.locator('text=Tecnologia')).toBeVisible();
  });

  test('dimensao 1080 x 1350 aparece no wizard carrossel', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await expect(homePage.page.locator('text=1080 x 1350')).toBeVisible();
  });

  test('avatar opcoes: "Avatar na capa", "Avatar livre", "Sem avatar"', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await expect(homePage.page.locator('button:has-text("Avatar na capa")')).toBeVisible();
    await expect(homePage.page.locator('button:has-text("Avatar livre")')).toBeVisible();
    await expect(homePage.page.locator('button:has-text("Sem avatar")')).toBeVisible();
  });

  test('botao criar tem data-testid="btn-criar-pipeline"', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.expectVisible(homePage.btnCriarPipeline);
  });
});

test.describe('Wizard — Post Unico', () => {
  test('navegar para /?formato=post_unico mostra titulo "Post Unico"', async ({ homePage }) => {
    await homePage.navigate('post_unico');
    await homePage.expectFormato('Post Unico');
  });

  test('avatar marcado "Com avatar" por default', async ({ homePage }) => {
    await homePage.navigate('post_unico');
    // Post unico default = "sim" que mostra "Com avatar"
    const btnAtivo = homePage.page.locator('button:has-text("Com avatar")');
    await homePage.expectVisible(btnAtivo);
    // Botao ativo tem classe bg-purple (selecionado)
    await expect(btnAtivo).toHaveClass(/bg-purple/);
  });

  test('dimensao 1080 x 1080 aparece', async ({ homePage }) => {
    await homePage.navigate('post_unico');
    await expect(homePage.page.locator('text=1080 x 1080')).toBeVisible();
  });

  test('modo Texto pronto: mostra apenas 1 slide (sem "+ Adicionar slide")', async ({ homePage }) => {
    await homePage.navigate('post_unico');
    await homePage.selectModoEntrada('texto_pronto');
    // Slide unico: nao deve ter botao "Adicionar slide"
    const addBtn = homePage.page.locator('button:has-text("Adicionar slide")');
    await expect(addBtn).toBeHidden();
    // Deve mostrar "Texto da imagem" em vez de "Capa"
    await expect(homePage.page.locator('text=Texto da imagem')).toBeVisible();
  });
});

test.describe('Wizard — Thumbnail YouTube', () => {
  test('navegar para /?formato=thumbnail_youtube mostra titulo "Thumbnail YouTube"', async ({ homePage }) => {
    await homePage.navigate('thumbnail_youtube');
    await homePage.expectFormato('Thumbnail YouTube');
  });

  test('dimensao 1280 x 720 aparece', async ({ homePage }) => {
    await homePage.navigate('thumbnail_youtube');
    await expect(homePage.page.locator('text=1280 x 720')).toBeVisible();
  });

  test('avatar com unica opcao "Com avatar"', async ({ homePage }) => {
    await homePage.navigate('thumbnail_youtube');
    const btnAvatar = homePage.page.locator('button:has-text("Com avatar")');
    await homePage.expectVisible(btnAvatar);
    // Nao deve ter "Sem avatar" para thumbnail
    const btnSem = homePage.page.locator('button:has-text("Sem avatar")');
    await expect(btnSem).toBeHidden();
  });
});

test.describe('Wizard — Capa Reels', () => {
  test('navegar para /?formato=capa_reels mostra titulo "Capa Reels"', async ({ homePage }) => {
    await homePage.navigate('capa_reels');
    await homePage.expectFormato('Capa Reels');
  });

  test('dimensao 1080 x 1920 aparece', async ({ homePage }) => {
    await homePage.navigate('capa_reels');
    await expect(homePage.page.locator('text=1080 x 1920')).toBeVisible();
  });
});

test.describe('Wizard — Funil', () => {
  test('navegar para /?formato=funil mostra "Funil de Conteudo"', async ({ homePage }) => {
    await homePage.navigate('funil');
    await homePage.expectFormato('Funil de Conteudo');
  });

  test('funil mostra Strategist na pagina', async ({ homePage }) => {
    await homePage.navigate('funil');
    await expect(homePage.page.locator('text=Strategist')).toBeVisible();
  });
});

test.describe('Wizard — Link Voltar', () => {
  test('botao "Voltar" no wizard volta para landing page', async ({ page }) => {
    await page.goto('/?formato=carrossel');
    const voltar = page.locator('a:has-text("Voltar")');
    await expect(voltar).toBeVisible();
    await expect(voltar).toHaveAttribute('href', '/');
  });
});
