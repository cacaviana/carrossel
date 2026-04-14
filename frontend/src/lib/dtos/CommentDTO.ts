// src/lib/dtos/CommentDTO.ts

export class CommentDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly card_id: string;
  readonly user_id: string;
  readonly user_name: string;
  readonly user_avatar_url: string;
  readonly text: string;
  readonly created_at: string;
  readonly updated_at: string;
  readonly deleted_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? data._id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.card_id = data.card_id ?? '';
    this.user_id = data.user_id ?? '';
    this.user_name = data.user_name ?? '';
    this.user_avatar_url = data.user_avatar_url ?? '';
    this.text = data.text ?? '';
    this.created_at = data.created_at ?? '';
    this.updated_at = data.updated_at ?? '';
    this.deleted_at = data.deleted_at ?? '';
  }

  get isDeleted(): boolean {
    return this.deleted_at.length > 0;
  }

  get isEdited(): boolean {
    return this.updated_at.length > 0 && this.updated_at !== this.created_at;
  }

  get userIniciais(): string {
    return this.user_name
      .split(' ')
      .map(p => p[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  }

  isOwnedBy(userId: string): boolean {
    return this.user_id === userId;
  }

  isValid(): boolean {
    return this.id.length > 0 && this.text.length > 0 && this.card_id.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      card_id: this.card_id,
      text: this.text
    };
  }
}
