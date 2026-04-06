export type FuncaoCriador = 'TECH_SOURCE' | 'EXPLAINER' | 'VIRAL_ENGINE' | 'THOUGHT_LEADER' | 'DINAMICA';

export class CreatorEntryDTO {
  readonly id: string;
  readonly nome: string;
  readonly funcao: FuncaoCriador;
  readonly plataforma: string;
  readonly url: string;
  readonly ativo: boolean;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? '';
    this.nome = data.nome ?? '';
    this.funcao = data.funcao ?? 'TECH_SOURCE';
    this.plataforma = data.plataforma ?? '';
    this.url = data.url ?? '';
    this.ativo = data.ativo ?? true;
  }

  get funcaoLabel(): string {
    const labels: Record<FuncaoCriador, string> = {
      TECH_SOURCE: 'Tech Source',
      EXPLAINER: 'Explainer',
      VIRAL_ENGINE: 'Viral Engine',
      THOUGHT_LEADER: 'Thought Leader',
      DINAMICA: 'Dinamica'
    };
    return labels[this.funcao] ?? this.funcao;
  }

  isValid(): boolean {
    return (
      this.nome.trim().length > 0 &&
      this.plataforma.trim().length > 0
    );
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      nome: this.nome,
      funcao: this.funcao,
      plataforma: this.plataforma,
      url: this.url,
      ativo: this.ativo
    };
  }
}
