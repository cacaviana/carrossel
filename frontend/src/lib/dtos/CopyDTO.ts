export interface SlideItem {
  titulo: string;
  conteudo: string;
  tipo: string;
  ordem: number;
}

export class CopyDTO {
  readonly pipeline_id: string;
  readonly headline: string;
  readonly narrativa: string;
  readonly cta: string;
  readonly provider: string;
  readonly model: string;
  readonly sequencia_slides: SlideItem[];

  constructor(data: Record<string, any>) {
    this.pipeline_id = data.pipeline_id ?? '';
    this.headline = data.headline ?? '';
    this.narrativa = data.narrativa ?? '';
    this.cta = data.cta ?? '';
    this.provider = data.provider ?? '';
    this.model = data.model ?? '';
    this.sequencia_slides = (data.sequencia_slides ?? []).map((s: any, i: number) => ({
      titulo: s.titulo ?? '',
      conteudo: s.conteudo ?? '',
      tipo: s.tipo ?? 'content',
      ordem: s.ordem ?? i
    }));
  }

  get totalSlides(): number {
    return this.sequencia_slides.length;
  }

  isValid(): boolean {
    return (
      this.pipeline_id.length > 0 &&
      this.headline.trim().length > 0 &&
      this.cta.trim().length > 0 &&
      this.sequencia_slides.length > 0
    );
  }

  toPayload(): Record<string, any> {
    return {
      pipeline_id: this.pipeline_id,
      headline: this.headline,
      narrativa: this.narrativa,
      cta: this.cta,
      sequencia_slides: this.sequencia_slides
    };
  }
}
