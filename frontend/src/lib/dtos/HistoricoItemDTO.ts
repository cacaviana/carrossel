export class HistoricoItemDTO {
  readonly id: number;
  readonly pipeline_id: string;
  readonly titulo: string;
  readonly formato: string;
  readonly status: string;
  readonly disciplina: string;
  readonly tecnologia_principal: string;
  readonly total_slides: number;
  readonly final_score: number | null;
  readonly google_drive_link: string;
  readonly criado_em: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? 0;
    this.pipeline_id = data.pipeline_id ?? '';
    this.titulo = data.titulo ?? '';
    this.formato = data.formato ?? '';
    this.status = data.status ?? '';
    this.disciplina = data.disciplina ?? '';
    this.tecnologia_principal = data.tecnologia_principal ?? '';
    this.total_slides = data.total_slides ?? 0;
    this.final_score = data.final_score ?? null;
    this.google_drive_link = data.google_drive_link ?? '';
    this.criado_em = data.criado_em ?? '';
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

  get dataFormatada(): string {
    if (!this.criado_em) return '';
    try {
      return new Date(this.criado_em).toLocaleDateString('pt-BR');
    } catch {
      return this.criado_em;
    }
  }

  isValid(): boolean {
    return (this.id > 0 || this.pipeline_id.length > 0) && this.titulo.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      pipeline_id: this.pipeline_id,
      titulo: this.titulo,
      formato: this.formato,
      status: this.status
    };
  }
}
