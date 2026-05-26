// src/lib/dtos/EditarAnuncioCopyDTO.ts
//
// Pos-pivot (2026-04-23): edicao dos 3 campos de copy (headline / descricao / cta)
// + titulo + etapa_funil. Limites novos: 40 / 125 / 30.

import type { EtapaFunil } from './AnuncioDTO';
import { HEADLINE_MAX, DESCRICAO_MAX, CTA_MAX } from './AnuncioCopyDTO';

export class EditarAnuncioCopyDTO {
  readonly id: string;
  readonly titulo: string;
  readonly headline: string;
  readonly descricao: string;
  readonly cta: string;
  readonly etapa_funil: EtapaFunil;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? '';
    this.titulo = (data.titulo ?? '').trim();
    this.headline = data.headline ?? '';
    this.descricao = data.descricao ?? '';
    this.cta = data.cta ?? '';
    this.etapa_funil = data.etapa_funil ?? 'avulso';
  }

  get tituloValido(): boolean { return this.titulo.length >= 3; }
  get headlineValido(): boolean { return this.headline.length >= 1 && this.headline.length <= HEADLINE_MAX; }
  get descricaoValido(): boolean { return this.descricao.length >= 1 && this.descricao.length <= DESCRICAO_MAX; }
  get ctaValido(): boolean { return this.cta.length >= 1 && this.cta.length <= CTA_MAX; }

  isValid(): boolean {
    return this.id.length > 0
      && this.tituloValido
      && this.headlineValido
      && this.descricaoValido
      && this.ctaValido;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      titulo: this.titulo,
      headline: this.headline,
      descricao: this.descricao,
      cta: this.cta,
      etapa_funil: this.etapa_funil
    };
  }
}
