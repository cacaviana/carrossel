export class BrandPaletteDTO {
  readonly fundo_principal: string;
  readonly destaque_primario: string;
  readonly destaque_secundario: string;
  readonly texto_principal: string;
  readonly texto_secundario: string;
  readonly fonte: string;
  readonly elementos_obrigatorios: string[];
  readonly estilo: string;

  constructor(data: Record<string, any>) {
    const cores = data.cores ?? data;
    this.fundo_principal = cores.fundo_principal ?? '#0A0A0F';
    this.destaque_primario = cores.destaque_primario ?? '#A78BFA';
    this.destaque_secundario = cores.destaque_secundario ?? '#6D28D9';
    this.texto_principal = cores.texto_principal ?? '#FFFFFF';
    this.texto_secundario = cores.texto_secundario ?? '#94A3B8';
    this.fonte = data.fonte ?? 'Outfit';
    this.elementos_obrigatorios = data.elementos_obrigatorios ?? [];
    this.estilo = data.estilo ?? 'dark_mode_premium';
  }

  get cores(): { label: string; chave: string; valor: string }[] {
    return [
      { label: 'Fundo Principal', chave: 'fundo_principal', valor: this.fundo_principal },
      { label: 'Destaque Primario', chave: 'destaque_primario', valor: this.destaque_primario },
      { label: 'Destaque Secundario', chave: 'destaque_secundario', valor: this.destaque_secundario },
      { label: 'Texto Principal', chave: 'texto_principal', valor: this.texto_principal },
      { label: 'Texto Secundario', chave: 'texto_secundario', valor: this.texto_secundario }
    ];
  }

  isValid(): boolean {
    const hexRegex = /^#[0-9A-Fa-f]{6}$/;
    return (
      hexRegex.test(this.fundo_principal) &&
      hexRegex.test(this.destaque_primario) &&
      hexRegex.test(this.destaque_secundario) &&
      hexRegex.test(this.texto_principal) &&
      hexRegex.test(this.texto_secundario) &&
      this.fonte.trim().length > 0
    );
  }

  toPayload(): Record<string, any> {
    return {
      cores: {
        fundo_principal: this.fundo_principal,
        destaque_primario: this.destaque_primario,
        destaque_secundario: this.destaque_secundario,
        texto_principal: this.texto_principal,
        texto_secundario: this.texto_secundario
      },
      fonte: this.fonte,
      elementos_obrigatorios: this.elementos_obrigatorios,
      estilo: this.estilo
    };
  }
}
