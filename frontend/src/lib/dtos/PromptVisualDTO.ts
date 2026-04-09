export interface PromptSlide {
  slide_index: number;
  titulo: string;
  prompt_imagem: string;
  illustration_description: string;
  modelo_sugerido: 'pro' | 'flash';
}

export class PromptVisualDTO {
  readonly pipeline_id: string;
  readonly prompts: PromptSlide[];

  constructor(data: Record<string, any>) {
    this.pipeline_id = data.pipeline_id ?? '';
    this.prompts = (data.prompts ?? []).map((p: any, i: number) => ({
      slide_index: p.slide_index ?? i,
      titulo: p.titulo ?? `Slide ${i + 1}`,
      prompt_imagem: p.prompt_imagem ?? p.prompt ?? '',
      illustration_description: p.illustration_description ?? '',
      modelo_sugerido: p.modelo_sugerido ?? 'flash'
    }));
  }

  get totalSlides(): number {
    return this.prompts.length;
  }

  get promptsPro(): PromptSlide[] {
    return this.prompts.filter(p => p.modelo_sugerido === 'pro');
  }

  isValid(): boolean {
    return (
      this.pipeline_id.length > 0 &&
      this.prompts.length > 0 &&
      this.prompts.every(p => (p.prompt_imagem.trim().length + p.illustration_description.trim().length) >= 10)
    );
  }

  toPayload(): Record<string, any> {
    return {
      pipeline_id: this.pipeline_id,
      prompts: this.prompts.map(p => ({
        slide_index: p.slide_index,
        prompt_imagem: p.prompt_imagem,
        illustration_description: p.illustration_description,
        modelo_sugerido: p.modelo_sugerido
      }))
    };
  }
}
