import type { PipelineStatus, EtapaPipeline } from './PipelineDTO';

export class PipelineStepDTO {
  readonly id: string;
  readonly pipeline_id: string;
  readonly agente: EtapaPipeline;
  readonly status: PipelineStatus;
  readonly entrada: Record<string, any>;
  readonly saida: Record<string, any>;
  readonly aprovado_por: string;
  readonly approved_at: string;
  readonly duracao_ms: number;
  readonly progresso: { atual: number; total: number; detalhe: string } | null;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? '';
    this.pipeline_id = data.pipeline_id ?? '';
    this.agente = data.agente ?? 'strategist';
    this.status = data.status ?? 'pendente';
    this.entrada = data.entrada ?? {};
    this.saida = data.saida ?? {};
    this.aprovado_por = data.aprovado_por ?? '';
    this.approved_at = data.approved_at ?? '';
    this.duracao_ms = data.duracao_ms ?? 0;
    this.progresso = data.progresso ?? null;
  }

  get agenteLabel(): string {
    const labels: Record<EtapaPipeline, string> = {
      strategist: 'Strategist',
      copywriter: 'Copywriter',
      hook_specialist: 'Hook Specialist',
      art_director: 'Art Director',
      image_generator: 'Image Generator',
      brand_gate: 'Brand Gate',
      content_critic: 'Content Critic'
    };
    return labels[this.agente] ?? this.agente;
  }

  get duracaoFormatada(): string {
    if (this.duracao_ms < 1000) return `${this.duracao_ms}ms`;
    return `${(this.duracao_ms / 1000).toFixed(1)}s`;
  }

  get isPontoAprovacao(): boolean {
    return ['strategist', 'hook_specialist', 'art_director', 'brand_gate'].includes(this.agente);
  }

  get rotaAprovacao(): string | null {
    const rotas: Record<string, string> = {
      strategist: 'briefing',
      hook_specialist: 'copy',
      art_director: 'visual',
      brand_gate: 'imagem'
    };
    return rotas[this.agente] ?? null;
  }

  isValid(): boolean {
    return this.id.length > 0 && this.pipeline_id.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      pipeline_id: this.pipeline_id,
      agente: this.agente,
      status: this.status,
      entrada: this.entrada,
      saida: this.saida
    };
  }
}
