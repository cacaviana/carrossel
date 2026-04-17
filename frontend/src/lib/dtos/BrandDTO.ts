/**
 * BrandDTO — representa uma marca (design system) completa.
 *
 * Por causa da natureza extensivel da marca (cores dinamicas, assets variados,
 * dna configuravel), o DTO mantem a estrutura crua em readonly e fornece
 * apenas os campos estaveis como propriedades diretas. O toPayload() devolve
 * a marca completa pronta pro backend.
 */
export class BrandDTO {
  readonly slug: string;
  readonly nome: string;
  readonly estilo: string;
  readonly cores: Record<string, any>;
  readonly fontes: Record<string, any>;
  readonly elementos: Record<string, any>;
  readonly dna: Record<string, any>;
  readonly visual: Record<string, any>;
  readonly comunicacao: Record<string, any>;
  readonly padrao_visual: Record<string, any>;
  readonly modo_geracao: string;
  readonly overrides: Record<string, any>;
  readonly regras_feed: Record<string, any>;
  readonly hack_consistencia: string;
  readonly cor_principal: string;
  readonly cor_fundo: string;
  private readonly _raw: Record<string, any>;

  constructor(data: Record<string, any>) {
    this._raw = { ...data };
    this.slug = data.slug ?? '';
    this.nome = data.nome ?? '';
    this.estilo = data.estilo ?? 'dark_mode_premium';
    this.cores = data.cores ?? {};
    this.fontes = data.fontes ?? {};
    this.elementos = data.elementos ?? {};
    this.dna = data.dna ?? { estilo: '', cores: '', tipografia: '', elementos: '' };
    this.visual = data.visual ?? {};
    this.comunicacao = data.comunicacao ?? {};
    this.padrao_visual = data.padrao_visual ?? {};
    this.modo_geracao = data.modo_geracao ?? 'referencia';
    this.overrides = data.overrides ?? {};
    this.regras_feed = data.regras_feed ?? {};
    this.hack_consistencia = data.hack_consistencia ?? '';
    this.cor_principal = data.cor_principal ?? this.cores?.acento_principal ?? '#A78BFA';
    this.cor_fundo = data.cor_fundo ?? this.cores?.fundo ?? '#0A0A0F';
  }

  isValid(): boolean {
    return this.slug.trim().length > 0 && this.nome.trim().length > 0;
  }

  toPayload(): Record<string, any> {
    return { ...this._raw, slug: this.slug, nome: this.nome };
  }

  /** Devolve a estrutura raw (read-only) para uso em templates ricos. */
  get raw(): Record<string, any> {
    return this._raw;
  }
}
