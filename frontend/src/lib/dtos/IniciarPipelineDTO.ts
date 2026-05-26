import type { FormatoConteudo } from './PipelineDTO';

export class IniciarPipelineDTO {
  readonly tema: string;
  readonly formatos: FormatoConteudo[];
  readonly modo_funil: boolean;
  readonly modo_entrada: 'texto' | 'disciplina';
  readonly disciplina: string;
  readonly tecnologia: string;
  readonly tema_custom: string;
  readonly foto_criador_id: string;

  constructor(data: Record<string, any>) {
    this.tema = data.tema ?? '';
    this.formatos = data.formatos ?? [];
    this.modo_funil = data.modo_funil ?? false;
    this.modo_entrada = data.modo_entrada ?? 'texto';
    this.disciplina = data.disciplina ?? '';
    this.tecnologia = data.tecnologia ?? '';
    this.tema_custom = data.tema_custom ?? '';
    this.foto_criador_id = data.foto_criador_id ?? '';
  }

  get temaEfetivo(): string {
    if (this.modo_entrada === 'texto') return this.tema;
    const partes = [this.disciplina, this.tecnologia, this.tema_custom].filter(Boolean);
    return partes.join(' - ');
  }

  isValid(): boolean {
    if (this.formatos.length === 0) return false;
    if (this.modo_entrada === 'texto') return this.tema.trim().length >= 20;
    return this.disciplina.length > 0 && this.tecnologia.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      tema: this.temaEfetivo,
      formatos: this.formatos,
      modo_funil: this.modo_funil,
      foto_criador_id: this.foto_criador_id || undefined
    };
  }
}
