export type HookOpcao = 'A' | 'B' | 'C';

export class HookDTO {
  readonly pipeline_id: string;
  readonly hook_a: string;
  readonly hook_b: string;
  readonly hook_c: string;
  readonly hook_selecionado: HookOpcao | null;

  constructor(data: Record<string, any>) {
    this.pipeline_id = data.pipeline_id ?? '';
    this.hook_a = data.hook_a ?? '';
    this.hook_b = data.hook_b ?? '';
    this.hook_c = data.hook_c ?? '';
    this.hook_selecionado = data.hook_selecionado ?? null;
  }

  get hookEscolhido(): string {
    if (!this.hook_selecionado) return '';
    const map: Record<HookOpcao, string> = {
      A: this.hook_a,
      B: this.hook_b,
      C: this.hook_c
    };
    return map[this.hook_selecionado];
  }

  get hooks(): { opcao: HookOpcao; texto: string }[] {
    return [
      { opcao: 'A', texto: this.hook_a },
      { opcao: 'B', texto: this.hook_b },
      { opcao: 'C', texto: this.hook_c }
    ];
  }

  isValid(): boolean {
    return (
      this.pipeline_id.length > 0 &&
      this.hook_a.length > 0 &&
      this.hook_b.length > 0 &&
      this.hook_c.length > 0 &&
      this.hook_selecionado !== null
    );
  }

  toPayload(): Record<string, any> {
    return {
      pipeline_id: this.pipeline_id,
      hook_selecionado: this.hook_selecionado
    };
  }
}
