// src/lib/dtos/RegerarImagemDTO.ts
//
// Pos-pivot (2026-04-23): substitui RegerarDimensaoDTO.
// Regenera a UNICA imagem do anuncio (1080x1350), opcionalmente com feedback livre
// pro Art Director.

export const FEEDBACK_MAX = 500;

export class RegerarImagemDTO {
  readonly anuncio_id: string;
  readonly feedback_livre: string;
  readonly manter_prompt_base: boolean;

  constructor(data: Record<string, any>) {
    this.anuncio_id = data.anuncio_id ?? '';
    this.feedback_livre = (data.feedback_livre ?? '').trim();
    this.manter_prompt_base = data.manter_prompt_base ?? true;
  }

  get feedbackLength(): number { return this.feedback_livre.length; }
  get feedbackDentroLimite(): boolean { return this.feedback_livre.length <= FEEDBACK_MAX; }

  isValid(): boolean {
    return this.anuncio_id.length > 0 && this.feedbackDentroLimite;
  }

  toPayload(): Record<string, any> {
    const payload: Record<string, any> = {
      manter_prompt_base: this.manter_prompt_base
    };
    if (this.feedback_livre.length > 0) payload.feedback_livre = this.feedback_livre;
    return payload;
  }
}
