export class PlatformRuleDTO {
  readonly plataforma: string;
  readonly max_caracteres_titulo: number;
  readonly max_caracteres_corpo: number;
  readonly max_hashtags: number;
  readonly formatos_suportados: string[];
  readonly specs: Record<string, string>;

  constructor(data: Record<string, any>) {
    this.plataforma = data.plataforma ?? '';
    this.max_caracteres_titulo = data.max_caracteres_titulo ?? 0;
    this.max_caracteres_corpo = data.max_caracteres_corpo ?? 0;
    this.max_hashtags = data.max_hashtags ?? 0;
    this.formatos_suportados = data.formatos_suportados ?? [];
    this.specs = data.specs ?? {};
  }

  get plataformaLabel(): string {
    const labels: Record<string, string> = {
      linkedin: 'LinkedIn',
      instagram: 'Instagram',
      youtube: 'YouTube',
      facebook: 'Facebook',
      meta_ads: 'Meta Ads'
    };
    return labels[this.plataforma] ?? this.plataforma;
  }

  isValid(): boolean {
    return (
      this.plataforma.trim().length > 0 &&
      this.max_caracteres_titulo > 0 &&
      this.max_caracteres_corpo > 0
    );
  }

  toPayload(): Record<string, any> {
    return {
      plataforma: this.plataforma,
      max_caracteres_titulo: this.max_caracteres_titulo,
      max_caracteres_corpo: this.max_caracteres_corpo,
      max_hashtags: this.max_hashtags,
      formatos_suportados: this.formatos_suportados,
      specs: this.specs
    };
  }
}
