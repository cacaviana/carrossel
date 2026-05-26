export type EtapaFunil = 'topo' | 'meio' | 'fundo';

export interface PecaFunil {
  titulo: string;
  etapa_funil: EtapaFunil;
  formato: string;
}

export class BriefingDTO {
  readonly pipeline_id: string;
  readonly briefing_completo: string;
  readonly tema_original: string;
  readonly formato_alvo: string;
  readonly funil_etapa: EtapaFunil | null;
  readonly pecas_funil: PecaFunil[];
  readonly tendencias_usadas: string[];

  constructor(data: Record<string, any>) {
    this.pipeline_id = data.pipeline_id ?? '';
    this.briefing_completo = data.briefing_completo ?? '';
    this.tema_original = data.tema_original ?? '';
    this.formato_alvo = data.formato_alvo ?? '';
    this.funil_etapa = data.funil_etapa ?? null;
    this.pecas_funil = (data.pecas_funil ?? []).map((p: any) => ({
      titulo: p.titulo ?? '',
      etapa_funil: p.etapa_funil ?? 'topo',
      formato: p.formato ?? ''
    }));
    this.tendencias_usadas = data.tendencias_usadas ?? [];
  }

  get temFunil(): boolean {
    return this.pecas_funil.length > 0;
  }

  get totalPecas(): number {
    return this.pecas_funil.length;
  }

  isValid(): boolean {
    return this.pipeline_id.length > 0 && this.briefing_completo.trim().length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      pipeline_id: this.pipeline_id,
      briefing_completo: this.briefing_completo,
      pecas_funil: this.pecas_funil
    };
  }
}
