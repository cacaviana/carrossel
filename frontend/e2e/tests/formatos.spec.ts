import { test, expect } from '../fixtures/test-fixtures';

test.describe('Formatos - Dimensoes e labels por formato', () => {
  test('Post Unico mostra dimensao 1080 x 1080', async ({ homePage }) => {
    await homePage.navigate('post_unico');
    await homePage.expectFormato('Post Unico');
    await expect(homePage.page.locator('text=1080 x 1080')).toBeVisible();
  });

  test('Thumbnail YouTube mostra dimensao 1280 x 720', async ({ homePage }) => {
    await homePage.navigate('thumbnail_youtube');
    await homePage.expectFormato('Thumbnail YouTube');
    await expect(homePage.page.locator('text=1280 x 720')).toBeVisible();
  });

  test('Capa Reels mostra dimensao 1080 x 1920', async ({ homePage }) => {
    await homePage.navigate('capa_reels');
    await homePage.expectFormato('Capa Reels');
    await expect(homePage.page.locator('text=1080 x 1920')).toBeVisible();
  });

  test('Carrossel continua mostrando 1080 x 1350', async ({ homePage }) => {
    await homePage.navigate('carrossel');
    await homePage.expectFormato('Carrossel');
    await expect(homePage.page.locator('text=1080 x 1350')).toBeVisible();
  });
});

test.describe('Formatos - Sidebar links (desktop)', () => {
  test.beforeEach(async ({ page }, testInfo) => {
    test.skip(testInfo.project.name === 'Mobile', 'Sidebar not visible on mobile without hamburger');
  });

  test('sidebar: link Reels existe e esta ativo (nao disabled)', async ({ page }) => {
    await page.goto('/');
    const reelsLink = page.locator('a[href="/?formato=capa_reels"]');
    await expect(reelsLink).toBeVisible();
    await expect(reelsLink).toHaveAttribute('href', '/?formato=capa_reels');
    // Confirma que e um <a> (link ativo), nao um <div> (disabled)
    await expect(reelsLink).toBeEnabled();
  });

  test('sidebar: todos os 4 formatos principais tem links ativos', async ({ page }) => {
    await page.goto('/');

    const formatos = [
      { href: '/?formato=carrossel', label: 'Carrossel' },
      { href: '/?formato=post_unico', label: 'Post Unico' },
      { href: '/?formato=thumbnail_youtube', label: 'YouTube' },
      { href: '/?formato=capa_reels', label: 'Reels' },
    ];

    for (const fmt of formatos) {
      const link = page.locator(`a[href="${fmt.href}"]`);
      await expect(link, `Link ${fmt.label} deve estar visivel`).toBeVisible();
    }
  });

  test('sidebar: clicar Reels navega e mostra Capa Reels', async ({ homePage }) => {
    await homePage.goto('/');
    await homePage.page.locator('a[href="/?formato=capa_reels"]').first().click();
    await homePage.expectURL(/formato=capa_reels/);
    await homePage.expectFormato('Capa Reels');
  });

  test('sidebar: clicar Post Unico navega e mostra Post Unico', async ({ homePage }) => {
    await homePage.goto('/');
    await homePage.page.locator('a[href="/?formato=post_unico"]').first().click();
    await homePage.expectURL(/formato=post_unico/);
    await homePage.expectFormato('Post Unico');
  });

  test('sidebar: clicar YouTube navega e mostra Thumbnail YouTube', async ({ homePage }) => {
    await homePage.goto('/');
    await homePage.page.locator('a[href="/?formato=thumbnail_youtube"]').first().click();
    await homePage.expectURL(/formato=thumbnail_youtube/);
    await homePage.expectFormato('Thumbnail YouTube');
  });
});
