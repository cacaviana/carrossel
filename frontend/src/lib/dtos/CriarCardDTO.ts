// src/lib/dtos/CriarCardDTO.ts

import type { CardPriority } from '$lib/dtos/CardDTO';

export class CriarCardDTO {
  readonly title: string;
  readonly copy_text: string;
  readonly disciplina: string;
  readonly tecnologia: string;
  readonly priority: CardPriority;
  readonly assigned_user_ids: string[];
  readonly deadline: string;

  constructor(data: Record<string, any>) {
    this.title = (data.title ?? '').trim();
    this.copy_text = data.copy_text ?? '';
    this.disciplina = data.disciplina ?? '';
    this.tecnologia = data.tecnologia ?? '';
    this.priority = data.priority ?? 'media';
    this.assigned_user_ids = data.assigned_user_ids ?? [];
    this.deadline = data.deadline ?? '';
  }

  isValid(): boolean {
    return this.title.length >= 3;
  }

  toPayload(): Record<string, any> {
    return {
      title: this.title,
      copy_text: this.copy_text,
      disciplina: this.disciplina,
      tecnologia: this.tecnologia,
      priority: this.priority,
      assigned_user_ids: this.assigned_user_ids,
      deadline: this.deadline
    };
  }
}
