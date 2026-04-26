// src/lib/dtos/AnuncioCopyDTO.ts
//
// Copy de venda pos-pivot (2026-04-23):
// - headline: max 40 chars (antes 30)
// - descricao: max 125 chars (antes 90)
// - cta: max 30 chars (novo)

export const HEADLINE_MAX = 40;
export const DESCRICAO_MAX = 125;
export const CTA_MAX = 30;

export class AnuncioCopyDTO {
  readonly headline: string;
  readonly descricao: string;
  readonly cta: string;

  constructor(data: Record<string, any>) {
    this.headline = data.headline ?? '';
    this.descricao = data.descricao ?? '';
    this.cta = data.cta ?? '';
  }

  get headlineLength(): number { return this.headline.length; }
  get descricaoLength(): number { return this.descricao.length; }
  get ctaLength(): number { return this.cta.length; }

  get headlineExcedido(): boolean { return this.headlineLength > HEADLINE_MAX; }
  get descricaoExcedido(): boolean { return this.descricaoLength > DESCRICAO_MAX; }
  get ctaExcedido(): boolean { return this.ctaLength > CTA_MAX; }

  get headlineRestante(): number { return HEADLINE_MAX - this.headlineLength; }
  get descricaoRestante(): number { return DESCRICAO_MAX - this.descricaoLength; }
  get ctaRestante(): number { return CTA_MAX - this.ctaLength; }

  get headlineCor(): 'verde' | 'amber' | 'red' {
    return corPorRatio(this.headlineLength / HEADLINE_MAX);
  }

  get descricaoCor(): 'verde' | 'amber' | 'red' {
    return corPorRatio(this.descricaoLength / DESCRICAO_MAX);
  }

  get ctaCor(): 'verde' | 'amber' | 'red' {
    return corPorRatio(this.ctaLength / CTA_MAX);
  }

  get copyTxtPreview(): string {
    return `HEADLINE:\n${this.headline}\n\nDESCRICAO:\n${this.descricao}\n\nCTA:\n${this.cta}\n`;
  }

  isValid(): boolean {
    return this.headlineLength >= 1 && this.headlineLength <= HEADLINE_MAX
      && this.descricaoLength >= 1 && this.descricaoLength <= DESCRICAO_MAX
      && this.ctaLength >= 1 && this.ctaLength <= CTA_MAX;
  }

  toPayload(): Record<string, any> {
    return { headline: this.headline, descricao: this.descricao, cta: this.cta };
  }
}

function corPorRatio(ratio: number): 'verde' | 'amber' | 'red' {
  if (ratio > 1) return 'red';
  if (ratio >= 0.7) return 'amber';
  return 'verde';
}
