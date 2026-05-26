// src/lib/dtos/NotificationDTO.ts

export type NotificationType = 'assigned' | 'mentioned' | 'column_changed';

export class NotificationDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly user_id: string;
  readonly card_id: string;
  readonly type: NotificationType;
  readonly message: string;
  readonly is_read: boolean;
  readonly created_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? data._id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.user_id = data.user_id ?? '';
    this.card_id = data.card_id ?? '';
    this.type = data.type ?? 'assigned';
    this.message = data.message ?? '';
    this.is_read = data.is_read ?? false;
    this.created_at = data.created_at ?? '';
  }

  get typeIcon(): string {
    const icons: Record<NotificationType, string> = {
      assigned: 'user',
      mentioned: 'at',
      column_changed: 'arrow'
    };
    return icons[this.type] ?? 'bell';
  }

  isValid(): boolean {
    return this.id.length > 0 && this.message.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      card_id: this.card_id,
      type: this.type,
      is_read: this.is_read
    };
  }
}
