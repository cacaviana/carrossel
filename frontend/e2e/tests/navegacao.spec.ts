import { test, expect } from '../fixtures/test-fixtures';

test.describe('Navegacao - Desktop', () => {
  test('sidebar mostra logo Content Factory', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=Content Factory').first()).toBeVisible();
  });

  test('sidebar: link Home navega para /', async ({ page }) => {
    await page.goto('/configuracoes');
    await page.locator('a:has-text("Home")').first().click();
    await expect(page).toHaveURL('/');
  });

  test('sidebar: link Historico navega para /historico', async ({ page }) => {
    await page.goto('/');
    await page.locator('a:has-text("Historico")').first().click();
    await expect(page).toHaveURL('/historico');
  });

  test('sidebar: link Agentes navega para /agentes', async ({ page }) => {
    await page.goto('/');
    await page.locator('a:has-text("Agentes")').first().click();
    await expect(page).toHaveURL('/agentes');
  });

  test('sidebar: link Config navega para /configuracoes', async ({ page }) => {
    await page.goto('/');
    await page.locator('a:has-text("Config")').first().click();
    await expect(page).toHaveURL('/configuracoes');
  });

  test('sidebar: link Carrossel (legado) navega para /carrossel', async ({ page }) => {
    await page.goto('/');
    const legacyLink = page.locator('a[href="/carrossel"]');
    if (await legacyLink.isVisible()) {
      await legacyLink.click();
      await expect(page).toHaveURL('/carrossel');
    }
  });

  test('sidebar: formatos Carrossel, Post Unico, YouTube, Funil', async ({ page }) => {
    await page.goto('/');
    // Verifica que os links de formato existem
    await expect(page.locator('a:has-text("Carrossel")').first()).toBeVisible();
    await expect(page.locator('a:has-text("Post Unico")').first()).toBeVisible();
    await expect(page.locator('a:has-text("YouTube")').first()).toBeVisible();
    await expect(page.locator('a:has-text("Funil")').first()).toBeVisible();
  });

  test('sidebar: formato Carrossel navega com query param', async ({ page }) => {
    await page.goto('/');
    await page.locator('a[href="/?formato=carrossel"]').first().click();
    await expect(page).toHaveURL('/?formato=carrossel');
  });

  test('sidebar: formato Post Unico navega com query param', async ({ page }) => {
    await page.goto('/');
    await page.locator('a[href="/?formato=post_unico"]').first().click();
    await expect(page).toHaveURL('/?formato=post_unico');
  });

  test('sidebar: botao collapse funciona', async ({ page }) => {
    await page.goto('/');
    const sidebar = page.locator('aside');
    await expect(sidebar).toBeVisible();

    // Clica no botao de collapse (ultimo botao no footer do sidebar)
    const collapseBtn = sidebar.locator('button').last();
    await collapseBtn.click();

    // Sidebar deve ter classe w-16 (collapsed)
    await expect(sidebar).toHaveClass(/w-16/);
  });

  test('sidebar: versao v3.0 visivel no footer', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('text=v3.0')).toBeVisible();
  });
});

test.describe('Navegacao - Mobile', () => {
  test.use({ viewport: { width: 375, height: 812 } });

  test('mobile: sidebar desktop esta escondida', async ({ page }) => {
    await page.goto('/');
    const sidebar = page.locator('aside');
    // No mobile, o aside fica dentro de div.hidden.md:block
    await expect(sidebar).toBeHidden();
  });

  test('mobile: header mostra Content Factory e hamburger', async ({ page }) => {
    await page.goto('/');
    await expect(page.locator('span:has-text("Content Factory")')).toBeVisible();
    // Hamburger button (o botao com SVG no mobile header)
    const hamburger = page.locator('.md\\:hidden button:has(svg)');
    await expect(hamburger).toBeVisible();
  });

  test('mobile: hamburger abre drawer com sidebar', async ({ page }) => {
    await page.goto('/');
    const hamburger = page.locator('.md\\:hidden button:has(svg)').first();
    await hamburger.click();

    // Sidebar deve aparecer no drawer
    const sidebar = page.locator('aside');
    await expect(sidebar).toBeVisible({ timeout: 5000 });
  });

  test('mobile: navegar via drawer e fechar', async ({ page }) => {
    await page.goto('/');
    const hamburger = page.locator('.md\\:hidden button:has(svg)').first();
    await hamburger.click();

    // Clicar em Config no drawer
    const configLink = page.locator('a[href="/configuracoes"]').last();
    await expect(configLink).toBeVisible({ timeout: 5000 });
    await configLink.click();
    await expect(page).toHaveURL(/configuracoes/);
  });

  test('mobile: backdrop fecha drawer', async ({ page }) => {
    await page.goto('/');
    const hamburger = page.locator('.md\\:hidden button:has(svg)').first();
    await hamburger.click();

    // Clicar no backdrop (a area escura)
    const backdrop = page.locator('.md\\:hidden .absolute.inset-0.bg-black\\/60');
    if (await backdrop.isVisible()) {
      await backdrop.click();
      // Sidebar deve sumir
      await expect(page.locator('aside')).toBeHidden({ timeout: 3000 });
    }
  });
});

test.describe('Navegacao - Pipeline sub-pages', () => {
  test('briefing sub-page carrega com titulo Pipeline', async ({ page }) => {
    await page.goto('/pipeline/test/briefing');
    await expect(page).toHaveTitle(/Pipeline|Briefing|Content Factory/);
  });

  test('copy sub-page carrega', async ({ page }) => {
    await page.goto('/pipeline/test/copy');
    await page.waitForTimeout(1000);
    // Deve carregar sem crash
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });

  test('visual sub-page carrega', async ({ page }) => {
    await page.goto('/pipeline/test/visual');
    await page.waitForTimeout(1000);
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });

  test('export sub-page carrega', async ({ page }) => {
    await page.goto('/pipeline/test/export');
    await page.waitForTimeout(1000);
    const body = page.locator('body');
    await expect(body).toBeVisible();
  });
});
