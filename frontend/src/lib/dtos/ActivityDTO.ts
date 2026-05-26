// src/lib/dtos/ActivityDTO.ts

export type ActivityAction =
  | 'card_created'
  | 'column_changed'
  | 'assignee_changed'
  | 'field_edited'
  | 'comment_added'
  | 'comment_edited'
  | 'comment_deleted'
  | 'image_generated'
  | 'drive_linked'
  | 'pdf_exported';

export class ActivityDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly card_id: string;
  readonly user_id: string;
  readonly user_name: string;
  readonly action: ActivityAction;
  readonly metadata: Record<string, any>;
  readonly created_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? data._id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.card_id = data.card_id ?? '';
    this.user_id = data.user_id ?? '';
    this.user_name = data.user_name ?? '';
    this.action = data.action ?? 'card_created';
    this.metadata = data.metadata ?? {};
    this.created_at = data.created_at ?? '';
  }

  get descricao(): string {
    const nome = this.user_name || 'Sistema';
    const meta = this.metadata;

    const descricoes: Record<ActivityAction, string> = {
      card_created: `${nome} criou o card`,
      column_changed: `${nome} moveu de ${meta.from_column ?? '?'} para ${meta.to_column ?? '?'}`,
      assignee_changed: `${nome} alterou os responsaveis`,
      field_edited: `${nome} editou ${meta.field_name ?? 'um campo'}`,
      comment_added: `${nome} adicionou um comentario`,
      comment_edited: `${nome} editou um comentario`,
      comment_deleted: `${nome} removeu um comentario`,
      image_generated: `${nome} gerou imagens`,
      drive_linked: `${nome} vinculou ao Google Drive`,
      pdf_exported: `${nome} exportou o PDF`
    };

    return descricoes[this.action] ?? `${nome} realizou uma acao`;
  }

  get iconType(): string {
    const icons: Record<ActivityAction, string> = {
      card_created: 'plus',
      column_changed: 'arrow',
      assignee_changed: 'user',
      field_edited: 'pencil',
      comment_added: 'chat',
      comment_edited: 'pencil',
      comment_deleted: 'trash',
      image_generated: 'image',
      drive_linked: 'link',
      pdf_exported: 'document'
    };
    return icons[this.action] ?? 'info';
  }

  isValid(): boolean {
    return this.id.length > 0 && this.card_id.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      card_id: this.card_id,
      action: this.action,
      metadata: this.metadata
    };
  }
}
