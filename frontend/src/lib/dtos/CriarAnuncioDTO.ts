// src/lib/dtos/CriarAnuncioDTO.ts
//
// Pos-pivot (2026-04-23): adicionou CTA (opcional no modo 'disciplina'/'ideia',
// preenchido pelo usuario no modo 'texto_pronto' ou fallback via brand.cta_anuncio).

import type { EtapaFunil } from './AnuncioDTO';
import { CTA_MAX } from './AnuncioCopyDTO';

export type ModoEntrada = 'texto' | 'disciplina';

export class CriarAnuncioDTO {
  readonly titulo: string;
  readonly tema_ou_briefing: string;
  readonly modo_entrada: ModoEntrada;
  readonly disciplina: string;
  readonly tecnologia: string;
  readonly cta: string;
  readonly etapa_funil: EtapaFunil;
  readonly pipeline_funil_id: string;
  readonly foto_criador_id: string;

  constructor(data: Record<string, any>) {
    this.titulo = (data.titulo ?? '').trim();
    this.tema_ou_briefing = (data.tema_ou_briefing ?? '').trim();
    this.modo_entrada = data.modo_entrada ?? 'texto';
    this.disciplina = data.disciplina ?? '';
    this.tecnologia = data.tecnologia ?? '';
    this.cta = (data.cta ?? '').trim();
    this.etapa_funil = data.etapa_funil ?? 'avulso';
    this.pipeline_funil_id = data.pipeline_funil_id ?? '';
    this.foto_criador_id = data.foto_criador_id ?? '';
  }

  get tituloValido(): boolean { return this.titulo.length >= 3; }
  get temaValido(): boolean { return this.tema_ou_briefing.length >= 20; }
  get ctaValido(): boolean { return this.cta.length === 0 || this.cta.length <= CTA_MAX; }
  get precisaDisciplina(): boolean { return this.modo_entrada === 'disciplina'; }
  get vindoDoFunil(): boolean { return this.pipeline_funil_id.length > 0; }

  isValid(): boolean {
    if (!this.tituloValido) return false;
    if (!this.ctaValido) return false;
    if (this.modo_entrada === 'texto' && !this.temaValido) return false;
    if (this.precisaDisciplina && (this.disciplina === '' || this.tecnologia === '')) return false;
    return true;
  }

  toPayload(): Record<string, any> {
    const payload: Record<string, any> = {
      titulo: this.titulo,
      tema_ou_briefing: this.tema_ou_briefing,
      modo_entrada: this.modo_entrada,
      disciplina: this.disciplina,
      tecnologia: this.tecnologia,
      etapa_funil: this.etapa_funil,
      pipeline_funil_id: this.pipeline_funil_id,
      foto_criador_id: this.foto_criador_id,
      formato: 'anuncio'
    };
    // CTA vai no payload apenas quando preenchido. Vazio = deixa backend usar brand.cta_anuncio
    // ou Copywriter inventar (RN-023).
    if (this.cta.length > 0) payload.cta = this.cta;
    return payload;
  }
}
