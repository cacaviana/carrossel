import { type Page, type Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class EditorPage extends BasePage {
  readonly heading: Locator;
  readonly slideImage: Locator;
  readonly btnAnterior: Locator;
  readonly btnProximo: Locator;
  readonly btnBaixarPDF: Locator;
  readonly btnRegenerar: Locator;
  readonly emptyMsg: Locator;
  readonly loadingMsg: Locator;
  readonly uploadLogoLabel: Locator;

  constructor(page: Page) {
    super(page);
    this.heading = page.locator('h1');
    this.slideImage = page.locator('img[alt^="Slide"]');
    this.btnAnterior = page.locator('button:has-text("Anterior")');
    this.btnProximo = page.locator('button:has-text("Proximo")');
    this.btnBaixarPDF = page.locator('button:has-text("Baixar PDF")');
    this.btnRegenerar = page.locator('button:has-text("Regenerar todos")');
    this.emptyMsg = page.locator('text=Nenhum slide encontrado');
    this.loadingMsg = page.locator('text=Carregando slides');
    this.uploadLogoLabel = page.locator('text=Upload logo');
  }

  async navigate(params?: { pipeline?: string; brand?: string }) {
    const qs = new URLSearchParams();
    if (params?.pipeline) qs.set('pipeline', params.pipeline);
    if (params?.brand) qs.set('brand', params.brand);
    const path = qs.toString() ? `/editor?${qs}` : '/editor';
    await this.goto(path);
  }

  async expectLoaded() {
    // Either shows slides, empty message, or loading
    const hasSlides = await this.heading.isVisible().catch(() => false);
    const isEmpty = await this.emptyMsg.isVisible().catch(() => false);
    expect(hasSlides || isEmpty).toBeTruthy();
  }
}
