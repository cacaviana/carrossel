import { test, expect } from '@playwright/test';
import { loginAndGoHistorico } from '../helpers/auth';

/**
 * E2E: Calendario (/historico?tab=calendario)
 * Pre-condicao: Login como Admin (mock), then navigate to historico
 */

async function loginAndGoCalendario(page: import('@playwright/test').Page) {
  await loginAndGoHistorico(page);
  await page.locator('button:has-text("Calendario")').click();
  await expect(page).toHaveURL(/tab=calendario/);
  await page.waitForTimeout(2000);
}

test.describe('Calendario - Visualizacao', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndGoCalendario(page);
  });

  test('calendario mensal renderiza com nome do mes', async ({ page }) => {
    const meses = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    const mesAtual = meses[new Date().getMonth()];
    await expect(page.locator(`text=${mesAtual}`).first()).toBeVisible();
  });

  test('dias da semana visiveis (Dom, Seg, Ter...)', async ({ page }) => {
    await expect(page.locator('text=Dom').first()).toBeVisible();
    await expect(page.locator('text=Seg').first()).toBeVisible();
    await expect(page.locator('text=Ter').first()).toBeVisible();
  });

  test('legenda de cores visivel (Carrossel, Post unico, YouTube, Capa Reels)', async ({ page }) => {
    await expect(page.locator('text=Carrossel').first()).toBeVisible();
    await expect(page.locator('text=Post unico').first()).toBeVisible();
    await expect(page.locator('text=YouTube').first()).toBeVisible();
    await expect(page.locator('text=Capa Reels').first()).toBeVisible();
  });

  test('botao Hoje visivel', async ({ page }) => {
    await expect(page.locator('button:has-text("Hoje")')).toBeVisible();
  });
});

test.describe('Calendario - Navegacao', () => {
  test.beforeEach(async ({ page }) => {
    await loginAndGoCalendario(page);
  });

  test('seta esquerda navega para mes anterior', async ({ page }) => {
    const meses = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    const mesAnterior = meses[(new Date().getMonth() + 11) % 12];

    const prevBtn = page.locator('button:has(svg path[d="M15 19l-7-7 7-7"])').first();
    await prevBtn.click();
    await page.waitForTimeout(500);
    await expect(page.locator(`text=${mesAnterior}`).first()).toBeVisible();
  });

  test('seta direita navega para proximo mes', async ({ page }) => {
    const meses = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    const proxMes = meses[(new Date().getMonth() + 1) % 12];

    const nextBtn = page.locator('button:has(svg path[d="M9 5l7 7-7 7"])').first();
    await nextBtn.click();
    await page.waitForTimeout(500);
    await expect(page.locator(`text=${proxMes}`).first()).toBeVisible();
  });
});
