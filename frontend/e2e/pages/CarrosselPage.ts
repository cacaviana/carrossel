import { type Page, type Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class CarrosselPage extends BasePage {
  readonly emptyMsg: Locator;
  readonly criarLink: Locator;
  readonly slideTitle: Locator;
  readonly btnEditar: Locator;
  readonly btnImagens: Locator;
  readonly btnPDF: Locator;
  readonly btnDrive: Locator;
  readonly btnAnterior: Locator;
  readonly btnProximo: Locator;

  constructor(page: Page) {
    super(page);
    this.emptyMsg = page.locator('text=Nenhum carrossel gerado');
    this.criarLink = page.locator('a:has-text("Criar carrossel")');
    this.slideTitle = page.locator('h2').first();
    this.btnEditar = page.locator('button:has-text("Editar")');
    this.btnImagens = page.locator('button:has-text("Imagens")');
    this.btnPDF = page.locator('button:has-text("PDF")');
    this.btnDrive = page.locator('button:has-text("Drive")');
    this.btnAnterior = page.locator('button:has-text("Anterior")');
    this.btnProximo = page.locator('button:has-text("Proximo"), button:has-text("Próximo")');
  }

  async navigate() {
    await this.goto('/carrossel');
  }

  async expectEmpty() {
    await this.expectVisible(this.emptyMsg);
    await this.expectVisible(this.criarLink);
  }

  async expectHasSlides() {
    await this.expectVisible(this.slideTitle);
  }
}
