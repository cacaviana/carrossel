import { type Page, type Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class AgentesPage extends BasePage {
  readonly heading: Locator;
  readonly tabLLM: Locator;
  readonly tabSkills: Locator;
  readonly agenteCards: Locator;
  readonly detalheNome: Locator;
  readonly detalheConteudo: Locator;
  readonly pipelineVisual: Locator;
  readonly pipelineEtapas: Locator;
  readonly spinner: Locator;
  readonly erroMsg: Locator;

  constructor(page: Page) {
    super(page);
    this.heading = page.locator('text=Agentes e Skills');
    this.tabLLM = page.locator('button:has-text("Agentes LLM")');
    this.tabSkills = page.locator('button:has-text("Skills")');
    this.agenteCards = page.locator('.space-y-2 > button');
    this.detalheNome = page.locator('h2').first();
    this.detalheConteudo = page.locator('pre');
    this.pipelineVisual = page.locator('text=Pipeline Visual');
    this.pipelineEtapas = page.locator('.flex.items-center.gap-2 .rounded-full');
    this.spinner = page.locator('[class*="animate-spin"]');
    this.erroMsg = page.locator('text=Erro ao carregar agentes');
  }

  async navigate() {
    await this.goto('/agentes');
  }

  async selectTab(tab: 'llm' | 'skills') {
    if (tab === 'llm') await this.tabLLM.click();
    else await this.tabSkills.click();
  }

  async selectAgente(index: number) {
    await this.agenteCards.nth(index).click();
  }
}
