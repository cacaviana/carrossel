export interface EditorTexto {
  readonly titulo: string;
  readonly corpo: string;
}

export class EditorSlideDTO {
  readonly slides: string[];
  readonly textos: EditorTexto[];
  readonly tema: string;
  readonly formato: string;
  readonly logoSrc: string;
  readonly bordaCor: string;

  constructor(data: Record<string, any>) {
    this.slides = Array.isArray(data.slides) ? data.slides : [];
    this.textos = Array.isArray(data.textos)
      ? data.textos.map((t: any) => ({ titulo: t.titulo ?? '', corpo: t.corpo ?? '' }))
      : [];
    this.tema = data.tema ?? '';
    this.formato = data.formato ?? 'carrossel';
    this.logoSrc = data.logoSrc ?? '';
    this.bordaCor = data.bordaCor ?? '#3578B0';
  }

  get totalSlides(): number {
    return this.slides.length;
  }

  isValid(): boolean {
    return this.slides.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      slides: this.slides,
      textos: this.textos,
      tema: this.tema,
      formato: this.formato,
    };
  }
}
