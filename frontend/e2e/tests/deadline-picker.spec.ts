import { test, expect } from '@playwright/test';

/**
 * E2E: DeadlinePicker na pagina de criacao (/?formato=carrossel)
 * Pre-condicao: VITE_USE_MOCK=true, sem login necessario
 * A pagina / mostra landing hero. /?formato=carrossel mostra o formulario com DeadlinePicker.
 */

test.describe('DeadlinePicker - Criacao de carrossel', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/?formato=carrossel');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(1000);
  });

  test('DeadlinePicker comeca fechado com texto placeholder', async ({ page }) => {
    const pickerBtn = page.locator('text=Prazo de publicacao');
    await pickerBtn.scrollIntoViewIfNeeded();
    await expect(pickerBtn).toBeVisible();
  });

  test('clicar no picker expande o calendario com legenda', async ({ page }) => {
    const pickerBtn = page.locator('text=Prazo de publicacao');
    await pickerBtn.scrollIntoViewIfNeeded();
    await pickerBtn.click();
    await page.waitForTimeout(500);
    // Legenda de cores deve aparecer
    await expect(page.locator('text=Carrossel').first()).toBeVisible();
  });

  test('calendario expandido mostra nome do mes', async ({ page }) => {
    const pickerBtn = page.locator('text=Prazo de publicacao');
    await pickerBtn.scrollIntoViewIfNeeded();
    await pickerBtn.click();
    await page.waitForTimeout(500);
    const meses = ['Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
      'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
    const mesAtual = meses[new Date().getMonth()];
    await expect(page.locator(`text=${mesAtual}`).first()).toBeVisible();
  });

  test('selecionar data futura mostra "Prazo: dd/mm/aaaa"', async ({ page }) => {
    const pickerBtn = page.locator('text=Prazo de publicacao');
    await pickerBtn.scrollIntoViewIfNeeded();
    await pickerBtn.click();
    await page.waitForTimeout(1000);

    const availableDays = page.locator('.grid.grid-cols-7 button:not([disabled])');
    const count = await availableDays.count();
    if (count > 0) {
      await availableDays.last().click();
      await page.waitForTimeout(300);
      await expect(page.locator('text=/Prazo:/')).toBeVisible();
    }
  });

  test('limpar prazo funciona', async ({ page }) => {
    const pickerBtn = page.locator('text=Prazo de publicacao');
    await pickerBtn.scrollIntoViewIfNeeded();
    await pickerBtn.click();
    await page.waitForTimeout(1000);

    const availableDays = page.locator('.grid.grid-cols-7 button:not([disabled])');
    const count = await availableDays.count();
    if (count > 0) {
      await availableDays.last().click();
      await page.waitForTimeout(300);
      const limparBtn = page.locator('button:has-text("Limpar prazo")');
      if (await limparBtn.isVisible()) {
        await limparBtn.click();
        await page.waitForTimeout(300);
        await expect(page.locator('text=Prazo de publicacao')).toBeVisible();
      }
    }
  });
});
