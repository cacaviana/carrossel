export type BrandGateStatus = 'valido' | 'revisao_manual' | 'pendente';

export interface VariacaoImagem {
  variacao_id: string;
  url: string;
  base64: string;
}

export interface SlideImagens {
  slide_index: number;
  titulo: string;
  variacoes: VariacaoImagem[];
  variacao_selecionada: string | null;
  brand_gate_status: BrandGateStatus;
  brand_gate_retries: number;
}

export class ImagemVariacaoDTO {
  readonly pipeline_id: string;
  readonly slides: SlideImagens[];

  constructor(data: Record<string, any>) {
    this.pipeline_id = data.pipeline_id ?? '';
    this.slides = (data.slides ?? []).map((s: any, i: number) => ({
      slide_index: s.slide_index ?? i,
      titulo: s.titulo ?? `Slide ${i + 1}`,
      variacoes: (s.variacoes ?? []).map((v: any) => ({
        variacao_id: v.variacao_id ?? '',
        url: v.url ?? '',
        base64: v.base64 ?? ''
      })),
      variacao_selecionada: s.variacao_selecionada ?? null,
      brand_gate_status: s.brand_gate_status ?? 'pendente',
      brand_gate_retries: s.brand_gate_retries ?? 0
    }));
  }

  get totalSlides(): number {
    return this.slides.length;
  }

  get slidesComRevisaoManual(): SlideImagens[] {
    return this.slides.filter(s => s.brand_gate_status === 'revisao_manual');
  }

  get todosSelecionados(): boolean {
    return this.slides.every(s => s.variacao_selecionada !== null);
  }

  isValid(): boolean {
    return (
      this.pipeline_id.length > 0 &&
      this.slides.length > 0 &&
      this.todosSelecionados
    );
  }

  toPayload(): Record<string, any> {
    return {
      pipeline_id: this.pipeline_id,
      selecoes: this.slides.map(s => ({
        slide_index: s.slide_index,
        variacao_selecionada: s.variacao_selecionada
      }))
    };
  }
}
