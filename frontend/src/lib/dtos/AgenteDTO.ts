export type TipoAgente = 'llm' | 'skill';

export class AgenteDTO {
  readonly slug: string;
  readonly nome: string;
  readonly descricao: string;
  readonly tipo: TipoAgente;
  readonly conteudo: string;

  constructor(data: Record<string, any>) {
    this.slug = data.slug ?? '';
    this.nome = data.nome ?? '';
    this.descricao = data.descricao ?? '';
    this.tipo = data.tipo ?? 'llm';
    this.conteudo = data.conteudo ?? '';
  }

  get isLLM(): boolean {
    return this.tipo === 'llm';
  }

  get isSkill(): boolean {
    return this.tipo === 'skill';
  }

  isValid(): boolean {
    return this.slug.length > 0 && this.nome.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      slug: this.slug,
      nome: this.nome,
      descricao: this.descricao,
      tipo: this.tipo,
      conteudo: this.conteudo
    };
  }
}
