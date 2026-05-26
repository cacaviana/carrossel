import { type Page, type Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class ConfigPage extends BasePage {
  readonly heading: Locator;
  readonly tabMarcas: Locator;
  readonly tabAPI: Locator;
  readonly tabCreators: Locator;
  readonly tabFotoPerfil: Locator;

  constructor(page: Page) {
    super(page);
    this.heading = page.locator('text=Configurações').first().or(page.locator('text=Configuracoes').first());
    this.tabMarcas = page.locator('button:has-text("Marcas")');
    this.tabAPI = page.locator('button:has-text("API Keys")');
    this.tabCreators = page.locator('button:has-text("Creators")');
    this.tabFotoPerfil = page.locator('button:has-text("Foto Perfil")');
  }

  async navigate() {
    await this.goto('/configuracoes');
  }
}
