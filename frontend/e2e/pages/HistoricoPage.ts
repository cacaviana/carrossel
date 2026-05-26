import { type Page, type Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class HistoricoPage extends BasePage {
  readonly heading: Locator;
  readonly campoBusca: Locator;
  readonly filtroFormato: Locator;
  readonly filtroStatus: Locator;
  readonly cards: Locator;
  readonly emptyMsg: Locator;
  readonly criarLink: Locator;
  readonly btnLimparFiltros: Locator;
  readonly resultCount: Locator;

  constructor(page: Page) {
    super(page);
    this.heading = page.locator('h1');
    this.campoBusca = page.locator('[data-testid="campo-busca-historico"]');
    this.filtroFormato = page.locator('select').first();
    this.filtroStatus = page.locator('select').nth(1);
    this.cards = page.locator('.grid > div');
    this.emptyMsg = page.locator('text=Nenhum conteudo salvo ainda');
    this.criarLink = page.locator('a:has-text("Criar Conteudo")');
    this.btnLimparFiltros = page.locator('button:has-text("Limpar filtros")');
    this.resultCount = page.locator('p:has-text("resultado")');
  }

  async navigate() {
    await this.goto('/historico');
  }

  async buscar(texto: string) {
    await this.campoBusca.fill(texto);
  }
}
