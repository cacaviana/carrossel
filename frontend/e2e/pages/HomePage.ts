import { type Page, type Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class HomePage extends BasePage {
  /* --- Seletores --- */
  readonly heading: Locator;
  readonly btnTextoPronto: Locator;
  readonly btnIdeiaLivre: Locator;
  readonly btnPorDisciplina: Locator;
  readonly textareaTema: Locator;
  readonly btnCriarPipeline: Locator;
  readonly msgErro: Locator;

  constructor(page: Page) {
    super(page);
    this.heading = page.locator('h1');
    this.btnTextoPronto = page.locator('button:has-text("Texto pronto")');
    this.btnIdeiaLivre = page.locator('button:has-text("Ideia livre")');
    this.btnPorDisciplina = page.locator('button:has-text("Por disciplina")');
    this.textareaTema = page.locator('[data-testid="campo-tema"]');
    this.btnCriarPipeline = page.locator('[data-testid="btn-criar-pipeline"]');
    this.msgErro = page.locator('[data-testid="msg-erro"]');
  }

  async navigate(formato?: string) {
    const path = formato ? `/?formato=${formato}` : '/';
    await this.goto(path);
  }

  /* --- Wizard actions --- */

  async selectModoEntrada(modo: 'texto_pronto' | 'ideia' | 'disciplina') {
    const map = {
      texto_pronto: this.btnTextoPronto,
      ideia: this.btnIdeiaLivre,
      disciplina: this.btnPorDisciplina,
    };
    await map[modo].click();
  }

  async fillIdeia(texto: string) {
    await this.selectModoEntrada('ideia');
    await this.textareaTema.fill(texto);
  }

  async selectDisciplina(id: string) {
    await this.selectModoEntrada('disciplina');
    await this.page.locator(`button:has-text("${id}")`).first().click();
  }

  async selectTech(tech: string) {
    await this.page.locator(`button:has-text("${tech}")`).first().click();
  }

  async criarPipeline() {
    await this.btnCriarPipeline.click();
  }

  /* --- Formato labels --- */

  async expectFormato(label: string) {
    await this.expectText(this.heading, label);
  }
}
