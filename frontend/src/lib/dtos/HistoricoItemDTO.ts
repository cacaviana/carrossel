export class HistoricoItemDTO {
  readonly id: number;
  readonly pipeline_id: string;
  readonly anuncio_id: string;
  readonly titulo: string;
  readonly formato: string;
  readonly status: string;
  readonly disciplina: string;
  readonly tecnologia_principal: string;
  readonly total_slides: number;
  readonly image_urls: string[];
  readonly final_score: number | null;
  readonly google_drive_link: string;
  readonly created_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? 0;
    this.pipeline_id = data.pipeline_id ?? '';
    this.anuncio_id = data.anuncio_id ?? '';
    this.titulo = data.titulo ?? '';
    this.formato = data.formato ?? '';
    this.status = data.status ?? '';
    this.disciplina = data.disciplina ?? '';
    this.tecnologia_principal = data.tecnologia_principal ?? '';
    this.total_slides = data.total_slides ?? 0;
    this.image_urls = data.image_urls ?? [];
    this.final_score = data.final_score ?? null;
    this.google_drive_link = data.google_drive_link ?? '';
    // Backend padrao: created_at. Mantem compat com mocks antigos via criado_em.
    this.created_at = data.created_at ?? data.criado_em ?? '';
  }

  get temScore(): boolean {
    return this.final_score !== null;
  }

  get temDriveLink(): boolean {
    return this.google_drive_link.length > 0;
  }

  get isPipelineV3(): boolean {
    return this.pipeline_id.length > 0;
  }

  get isAnuncio(): boolean {
    return this.formato === 'anuncio';
  }

  get thumbnailUrl(): string {
    // Anuncio pos-pivot tem apenas 1 imagem 1080x1350. Carrossel pega o primeiro slide.
    return this.image_urls[0] ?? '';
  }

  get detalheRoute(): string {
    if (this.isAnuncio && this.anuncio_id) return `/anuncios/${this.anuncio_id}`;
    if (this.isPipelineV3) return `/pipeline/${this.pipeline_id}`;
    return '';
  }

  get dataFormatada(): string {
    if (!this.created_at) return '';
    try {
      return new Date(this.created_at).toLocaleDateString('pt-BR');
    } catch {
      return this.created_at;
    }
  }

  isValid(): boolean {
    return (this.id > 0 || this.pipeline_id.length > 0 || this.anuncio_id.length > 0) && this.titulo.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      pipeline_id: this.pipeline_id,
      anuncio_id: this.anuncio_id,
      titulo: this.titulo,
      formato: this.formato,
      status: this.status
    };
  }
}
