// src/lib/dtos/ListarAnunciosFiltroDTO.ts

import type { AnuncioStatus, EtapaFunil } from './AnuncioDTO';

export type StatusFiltro = AnuncioStatus | 'todos';
export type EtapaFunilFiltro = EtapaFunil | 'todas';

export class ListarAnunciosFiltroDTO {
  readonly busca: string;
  readonly status: StatusFiltro;
  readonly etapa_funil: EtapaFunilFiltro;
  readonly data_inicio: string;
  readonly data_fim: string;
  readonly incluir_excluidos: boolean;

  constructor(data: Record<string, any>) {
    this.busca = data.busca ?? '';
    // 'parcial' foi removido pos-pivot. Se chegar, rebate pra 'todos'.
    const statusRaw = data.status ?? 'todos';
    this.status = (statusRaw === 'parcial' ? 'todos' : statusRaw) as StatusFiltro;
    this.etapa_funil = data.etapa_funil ?? 'todas';
    this.data_inicio = data.data_inicio ?? '';
    this.data_fim = data.data_fim ?? '';
    this.incluir_excluidos = data.incluir_excluidos ?? false;
  }

  get temFiltroAtivo(): boolean {
    return this.busca !== ''
      || this.status !== 'todos'
      || this.etapa_funil !== 'todas'
      || this.data_inicio !== ''
      || this.data_fim !== ''
      || this.incluir_excluidos;
  }

  get queryString(): string {
    const p = new URLSearchParams();
    if (this.busca) p.set('q', this.busca);
    if (this.status !== 'todos') p.set('status', this.status);
    if (this.etapa_funil !== 'todas') p.set('etapa_funil', this.etapa_funil);
    if (this.data_inicio) p.set('data_inicio', this.data_inicio);
    if (this.data_fim) p.set('data_fim', this.data_fim);
    if (this.incluir_excluidos) p.set('incluir_excluidos', '1');
    return p.toString();
  }

  isValid(): boolean { return true; }

  toPayload(): Record<string, any> {
    return {
      busca: this.busca,
      status: this.status,
      etapa_funil: this.etapa_funil,
      data_inicio: this.data_inicio,
      data_fim: this.data_fim,
      incluir_excluidos: this.incluir_excluidos
    };
  }
}
