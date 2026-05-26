import { type Page, type Locator, expect } from '@playwright/test';

/**
 * BasePage -- helpers compartilhados entre todos os Page Objects.
 * Nunca usar seletores CSS de classe; sempre data-testid ou texto semântico.
 */
export class BasePage {
  readonly page: Page;

  /* Seletores globais reutilizaveis */
  static readonly SEL = {
    /** Mobile header hamburger (layout.svelte) */
    mobileMenuBtn: 'button:has(svg path)',
    sidebarLogo: 'text=Content Factory',
    footer: 'text=v3.0',
  } as const;

  constructor(page: Page) {
    this.page = page;
  }

  /* ---------- Navegacao ---------- */

  async goto(path: string) {
    await this.page.goto(path, { waitUntil: 'networkidle' });
  }

  async waitForLoad() {
    await this.page.waitForLoadState('networkidle');
  }

  /* ---------- Sidebar / Nav ---------- */

  /** Clica no link do sidebar pelo texto exato */
  async navigateVia(label: string) {
    await this.page.locator(`a:has-text("${label}")`).first().click();
    await this.page.waitForLoadState('networkidle');
  }

  /** Abre menu mobile (hamburger) se estivermos em viewport estreita */
  async openMobileMenu() {
    const btn = this.page.locator('button:has(svg)').first();
    if (await btn.isVisible()) {
      await btn.click();
    }
  }

  /* ---------- Assertions helpers ---------- */

  async expectVisible(locator: Locator, timeout = 10_000) {
    await expect(locator).toBeVisible({ timeout });
  }

  async expectText(locator: Locator, text: string | RegExp) {
    await expect(locator).toContainText(text);
  }

  async expectCount(locator: Locator, count: number) {
    await expect(locator).toHaveCount(count);
  }

  async expectURL(pattern: string | RegExp) {
    await expect(this.page).toHaveURL(pattern);
  }

  /** Verifica se elemento tem tamanho touch-friendly (>= minPx) */
  async expectTouchFriendly(locator: Locator, minPx = 40) {
    const box = await locator.boundingBox();
    expect(box).toBeTruthy();
    expect(box!.width).toBeGreaterThanOrEqual(minPx);
    expect(box!.height).toBeGreaterThanOrEqual(minPx);
  }

  /* ---------- Backend health check ---------- */

  /** Retorna true se backend esta respondendo em /health */
  async isBackendUp(): Promise<boolean> {
    try {
      const res = await this.page.request.get('http://localhost:8000/health');
      return res.ok();
    } catch {
      return false;
    }
  }
}
