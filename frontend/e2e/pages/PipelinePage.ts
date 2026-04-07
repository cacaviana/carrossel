import { type Page, type Locator, expect } from '@playwright/test';
import { BasePage } from './BasePage';

export class PipelinePage extends BasePage {
  readonly heading: Locator;
  readonly btnCancelar: Locator;
  readonly btnVerResultado: Locator;
  readonly etapas: Locator;
  readonly erroMsg: Locator;
  readonly skeleton: Locator;
  readonly notFoundMsg: Locator;

  constructor(page: Page) {
    super(page);
    this.heading = page.locator('h1').first();
    this.btnCancelar = page.locator('[data-testid="btn-cancelar-pipeline"]');
    this.btnVerResultado = page.locator('[data-testid="btn-ver-resultado"]');
    this.etapas = page.locator('.space-y-3 > div');
    this.erroMsg = page.locator('text=Pipeline nao encontrado');
    this.skeleton = page.locator('.animate-pulse, [class*="skeleton"]').first();
    this.notFoundMsg = page.locator('text=Pipeline nao encontrado');
  }

  async navigate(id: string) {
    await this.goto(`/pipeline/${id}`);
  }

  /** Labels das 7 etapas da pipeline */
  static readonly ETAPA_LABELS = [
    'Estrategia',
    'Copywriting',
    'Hooks',
    'Direcao de Arte',
    'Imagens',
    'Brand Gate',
    'Avaliacao Final',
  ];
}
