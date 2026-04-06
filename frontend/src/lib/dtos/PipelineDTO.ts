export type PipelineStatus = 'pendente' | 'executando' | 'em_execucao' | 'aguardando_aprovacao' | 'aprovado' | 'rejeitado' | 'completo' | 'erro' | 'cancelado';
export type FormatoConteudo = 'carrossel' | 'post_unico' | 'thumbnail_youtube';
export type EtapaPipeline = 'strategist' | 'copywriter' | 'hook_specialist' | 'art_director' | 'image_generator' | 'brand_gate' | 'content_critic';

export class PipelineDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly tema: string;
  readonly formato: FormatoConteudo;
  readonly status: PipelineStatus;
  readonly etapa_atual: EtapaPipeline;
  readonly modo_funil: boolean;
  readonly brand_slug: string;
  readonly created_at: string;
  readonly updated_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.tema = data.tema ?? '';
    this.formato = data.formato ?? 'carrossel';
    this.status = data.status ?? 'pendente';
    this.etapa_atual = data.etapa_atual ?? 'strategist';
    this.modo_funil = data.modo_funil ?? false;
    this.brand_slug = data.brand_slug ?? '';
    this.created_at = data.created_at ?? '';
    this.updated_at = data.updated_at ?? '';
  }

  get etapaIndex(): number {
    const etapas: EtapaPipeline[] = [
      'strategist', 'copywriter', 'hook_specialist',
      'art_director', 'image_generator', 'brand_gate', 'content_critic'
    ];
    return etapas.indexOf(this.etapa_atual);
  }

  get etapaLabel(): string {
    const labels: Record<EtapaPipeline, string> = {
      strategist: 'Strategist',
      copywriter: 'Copywriter',
      hook_specialist: 'Hook Specialist',
      art_director: 'Art Director',
      image_generator: 'Image Generator',
      brand_gate: 'Brand Gate',
      content_critic: 'Content Critic'
    };
    return labels[this.etapa_atual] ?? this.etapa_atual;
  }

  get isAguardandoAprovacao(): boolean {
    return this.status === 'aguardando_aprovacao';
  }

  get isCompleto(): boolean {
    return this.status === 'completo' || (this.etapa_atual === 'content_critic' && this.status === 'aprovado');
  }

  get formatoLabel(): string {
    const labels: Record<FormatoConteudo, string> = {
      carrossel: 'Carrossel',
      post_unico: 'Post Unico',
      thumbnail_youtube: 'Thumbnail YouTube'
    };
    return labels[this.formato] ?? this.formato;
  }

  isValid(): boolean {
    return this.id.length > 0 && this.tema.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      tenant_id: this.tenant_id,
      tema: this.tema,
      formato: this.formato,
      status: this.status,
      etapa_atual: this.etapa_atual,
      modo_funil: this.modo_funil
    };
  }
}
