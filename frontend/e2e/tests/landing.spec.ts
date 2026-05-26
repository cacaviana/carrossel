import { test, expect } from '@playwright/test';

test.describe('Landing Page — Hero Banner', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('headline "Crie conteudos virais" esta visivel', async ({ page }) => {
    const headline = page.locator('h1');
    await expect(headline).toBeVisible();
    await expect(headline).toContainText('Crie conteúdos virais');
  });

  test('subtitulo "em segundos com IA" esta visivel', async ({ page }) => {
    const subtitulo = page.locator('h1 span');
    await expect(subtitulo).toBeVisible();
    await expect(subtitulo).toContainText('em segundos com IA');
  });

  test('paragrafo descritivo esta visivel', async ({ page }) => {
    const subtitle = page.locator('text=Do zero ao post pronto');
    await expect(subtitle).toBeVisible();
  });

  test('botao CTA "Gerar meu carrossel agora" esta visivel', async ({ page }) => {
    const cta = page.locator('a:has-text("Gerar meu carrossel agora")');
    await expect(cta).toBeVisible();
    await expect(cta).toHaveAttribute('href', '/?formato=carrossel');
  });

  test('texto "O que voce quer criar hoje?" esta visivel', async ({ page }) => {
    const label = page.locator('text=O que voce quer criar hoje?');
    await expect(label).toBeVisible();
  });

  test('4 checkmarks (bullet points) aparecem', async ({ page }) => {
    const checks = page.locator('.hero-check');
    await expect(checks).toHaveCount(4);

    // Verifica conteudo de cada checkmark
    await expect(checks.nth(0)).toContainText('Escolha o formato');
    await expect(checks.nth(1)).toContainText('Decida o tema');
    await expect(checks.nth(2)).toContainText('Aprove o texto');
    await expect(checks.nth(3)).toContainText('Gere imagens virais');
  });

  test('cada checkmark tem icone SVG de check', async ({ page }) => {
    const checkIcons = page.locator('.hero-check svg');
    await expect(checkIcons).toHaveCount(4);
  });

  test('clicar CTA navega para /?formato=carrossel', async ({ page }) => {
    const cta = page.locator('a:has-text("Gerar meu carrossel agora")');
    await cta.click();
    await expect(page).toHaveURL('/?formato=carrossel');
  });

  test('social proof mostra contagem de criadores', async ({ page }) => {
    const proof = page.locator('text=criadores');
    await expect(proof).toBeVisible();
  });

  test('tag "IA + Design que converte" esta visivel', async ({ page }) => {
    const tag = page.locator('text=IA + Design que converte');
    await expect(tag).toBeVisible();
  });
});

test.describe('Landing Page — Mobile', () => {
  test.use({ viewport: { width: 375, height: 812 } });

  test('mobile: headline esta visivel e legivel', async ({ page }) => {
    await page.goto('/');
    const headline = page.locator('h1');
    await expect(headline).toBeVisible();
    await expect(headline).toContainText('Crie conteúdos virais');
  });

  test('mobile: CTA esta visivel e acessivel', async ({ page }) => {
    await page.goto('/');
    const cta = page.locator('a:has-text("Gerar meu carrossel agora")');
    await expect(cta).toBeVisible();

    // Verifica tamanho touch-friendly
    const box = await cta.boundingBox();
    expect(box).toBeTruthy();
    expect(box!.height).toBeGreaterThanOrEqual(40);
  });

  test('mobile: checkmarks aparecem (4 itens)', async ({ page }) => {
    await page.goto('/');
    const checks = page.locator('.hero-check');
    await expect(checks).toHaveCount(4);
  });
});
