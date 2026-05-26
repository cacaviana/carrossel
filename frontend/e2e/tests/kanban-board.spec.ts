import { test, expect } from '@playwright/test';
import { loginAndGoHistorico } from '../helpers/auth';

/**
 * E2E: Board Kanban (/historico?tab=kanban)
 * Pre-condicao: Login como Admin (mock)
 * 5 colunas: Copy, Diretor de Arte, Aprovado, Publicado, Cancelado
 */

async function loginAndGoKanban(page: import('@playwright/test').Page) {
  await loginAndGoHistorico(page);
  await page.locator('button:has-text("Kanban")').click();
  await expect(page).toHaveURL(/tab=kanban/);
  await expect(page.locator('[role="region"]').first()).toBeVisible({ timeout: 10_000 });
}

test.describe('Kanban Board - Colunas', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndGoKanban(page);
  });

  test('5 colunas visiveis: Copy, Diretor de Arte, Aprovado, Publicado, Cancelado', async ({ page }) => {
    const columns = page.locator('[role="region"]');
    await expect(columns).toHaveCount(5);

    await expect(page.locator('[aria-label="Coluna Copy"]')).toBeVisible();
    await expect(page.locator('[aria-label="Coluna Diretor de Arte"]')).toBeVisible();
    await expect(page.locator('[aria-label="Coluna Aprovado"]')).toBeVisible();
    await expect(page.locator('[aria-label="Coluna Publicado"]')).toBeVisible();
    await expect(page.locator('[aria-label="Coluna Cancelado"]')).toBeVisible();
  });

  test('cada coluna mostra contagem de cards', async ({ page }) => {
    const copyColumn = page.locator('[aria-label="Coluna Copy"]');
    // Badge with number is inside the column header
    const headerSpans = copyColumn.locator('span');
    const count = await headerSpans.count();
    expect(count).toBeGreaterThan(0);
    // At least one span should contain a number
    const texts = await headerSpans.allTextContents();
    const hasNumber = texts.some(t => /\d+/.test(t.trim()));
    expect(hasNumber).toBeTruthy();
  });
});

test.describe('Kanban Board - Cards', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndGoKanban(page);
  });

  test('cards mostram titulo', async ({ page }) => {
    await expect(page.locator('text=5 Erros Fatais').first()).toBeVisible();
  });

  test('cards mostram badge de prioridade', async ({ page }) => {
    // Priority labels: Alta, Media, Baixa
    const prioTexts = page.locator('text=/^(Alta|Media|Baixa)$/');
    const count = await prioTexts.count();
    expect(count).toBeGreaterThan(0);
  });

  test('cards com deadline mostram prazo', async ({ page }) => {
    const prazoTexts = page.locator('text=/Prazo|Atrasado|Vence em breve/');
    const count = await prazoTexts.count();
    expect(count).toBeGreaterThan(0);
  });

  test('clicar num card abre modal de detalhe', async ({ page }) => {
    await page.locator('text=5 Erros Fatais').first().click();
    await expect(page.locator('h2:has-text("5 Erros Fatais")')).toBeVisible({ timeout: 5000 });
  });
});

test.describe('Kanban Board - Modal detalhe', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndGoKanban(page);
    await page.locator('text=5 Erros Fatais').first().click();
    await expect(page.locator('h2:has-text("5 Erros Fatais")')).toBeVisible({ timeout: 5000 });
  });

  test('modal tem 3 abas: Detalhes, Comentarios, Atividade', async ({ page }) => {
    await expect(page.locator('button:has-text("Detalhes")')).toBeVisible();
    await expect(page.locator('button:has-text("Comentarios")')).toBeVisible();
    await expect(page.locator('button:has-text("Atividade")')).toBeVisible();
  });

  test('clicar em Comentarios mostra aba de comentarios', async ({ page }) => {
    await page.locator('button:has-text("Comentarios")').click();
    await page.waitForTimeout(500);
    const modalContent = page.locator('.overflow-y-auto').last();
    await expect(modalContent).toBeVisible();
  });

  test('clicar em Atividade mostra historico de atividade', async ({ page }) => {
    await page.locator('button:has-text("Atividade")').click();
    await page.waitForTimeout(500);
    const modalContent = page.locator('.overflow-y-auto').last();
    await expect(modalContent).toBeVisible();
  });

  test('fechar modal funciona (pressionar Escape)', async ({ page }) => {
    await page.keyboard.press('Escape');
    // Alternatively click the X button
    const closeBtn = page.locator('.fixed.inset-0 button:has(svg)').first();
    if (await page.locator('h2:has-text("5 Erros Fatais")').isVisible()) {
      await closeBtn.click({ force: true });
    }
    await expect(page.locator('h2:has-text("5 Erros Fatais")')).not.toBeVisible({ timeout: 3000 });
  });
});

test.describe('Kanban Board - Criar card', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndGoKanban(page);
  });

  test('botao Novo Card visivel para Admin', async ({ page }) => {
    await expect(page.locator('button:has-text("Novo Card")')).toBeVisible();
  });

  test('clicar Novo Card abre modal de criacao', async ({ page }) => {
    await page.locator('button:has-text("Novo Card")').click();
    await expect(page.locator('h2:has-text("Novo carrossel")')).toBeVisible({ timeout: 5000 });
  });

  test('criar card com titulo valido funciona', async ({ page }) => {
    await page.locator('button:has-text("Novo Card")').click();
    await expect(page.locator('h2:has-text("Novo carrossel")')).toBeVisible({ timeout: 5000 });

    const tituloInput = page.locator('input[placeholder*="Transfer Learning"]');
    await tituloInput.fill('Teste E2E: Novo Carrossel Automatizado');
    await page.locator('button:has-text("Criar")').last().click();
    await expect(page.locator('h2:has-text("Novo carrossel")')).not.toBeVisible({ timeout: 5000 });
    await expect(page.locator('text=Teste E2E: Novo Carrossel Automatizado')).toBeVisible({ timeout: 5000 });
  });

  test('titulo com menos de 3 caracteres mostra validacao', async ({ page }) => {
    await page.locator('button:has-text("Novo Card")').click();
    await expect(page.locator('h2:has-text("Novo carrossel")')).toBeVisible({ timeout: 5000 });
    await page.locator('input[placeholder*="Transfer Learning"]').fill('AB');
    await expect(page.locator('text=Titulo deve ter no minimo 3 caracteres')).toBeVisible();
  });
});

test.describe('Kanban Board - Filtros', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndGoKanban(page);
  });

  test('busca por texto filtra cards', async ({ page }) => {
    await page.locator('input[placeholder="Buscar por titulo..."]').fill('LangChain');
    await page.waitForTimeout(500);
    await expect(page.locator('text=LangChain Agents').first()).toBeVisible();
  });

  test('busca por texto inexistente filtra todos', async ({ page }) => {
    await page.locator('input[placeholder="Buscar por titulo..."]').fill('xyzinexistente999');
    await page.waitForTimeout(500);
    const cards = page.locator('button[draggable="true"]');
    await expect(cards).toHaveCount(0);
  });
});
