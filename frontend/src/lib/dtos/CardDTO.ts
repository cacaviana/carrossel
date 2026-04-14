// src/lib/dtos/CardDTO.ts

export type CardPriority = 'alta' | 'media' | 'baixa';
export type CardFormato = 'carrossel' | 'post_unico' | 'thumbnail_youtube' | 'capa_reels';

export class CardDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly board_id: string;
  readonly column_id: string;
  readonly title: string;
  readonly copy_text: string;
  readonly disciplina: string;
  readonly tecnologia: string;
  readonly priority: CardPriority;
  readonly formato: CardFormato;
  readonly assigned_user_ids: string[];
  readonly created_by: string;
  readonly pipeline_id: string;
  readonly drive_link: string;
  readonly drive_folder_name: string;
  readonly pdf_url: string;
  readonly image_urls: string[];
  readonly order_in_column: number;
  readonly comment_count: number;
  readonly deadline: string;
  readonly created_at: string;
  readonly updated_at: string;
  readonly archived_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? data._id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.board_id = data.board_id ?? '';
    this.column_id = data.column_id ?? '';
    this.title = data.title ?? '';
    this.copy_text = data.copy_text ?? '';
    this.disciplina = data.disciplina ?? '';
    this.tecnologia = data.tecnologia ?? '';
    this.priority = data.priority ?? 'media';
    this.formato = data.formato ?? 'carrossel';
    this.assigned_user_ids = data.assigned_user_ids ?? [];
    this.created_by = data.created_by ?? '';
    this.pipeline_id = data.pipeline_id ?? '';
    this.drive_link = data.drive_link ?? '';
    this.drive_folder_name = data.drive_folder_name ?? '';
    this.pdf_url = data.pdf_url ?? '';
    this.image_urls = data.image_urls ?? [];
    this.order_in_column = data.order_in_column ?? 0;
    this.comment_count = data.comment_count ?? 0;
    this.deadline = data.deadline ?? '';
    this.created_at = data.created_at ?? '';
    this.updated_at = data.updated_at ?? '';
    this.archived_at = data.archived_at ?? '';
  }

  get isArchived(): boolean {
    return this.archived_at.length > 0;
  }

  get hasDriveLink(): boolean {
    return this.drive_link.length > 0;
  }

  get hasPdf(): boolean {
    return this.pdf_url.length > 0;
  }

  get hasImages(): boolean {
    return this.image_urls.length > 0;
  }

  get hasPipeline(): boolean {
    return this.pipeline_id.length > 0;
  }

  get hasDeadline(): boolean {
    return this.deadline.length > 0;
  }

  get isOverdue(): boolean {
    if (!this.hasDeadline) return false;
    return new Date(this.deadline) < new Date();
  }

  get isDueSoon(): boolean {
    if (!this.hasDeadline || this.isOverdue) return false;
    const diff = new Date(this.deadline).getTime() - Date.now();
    return diff < 2 * 24 * 60 * 60 * 1000; // 2 dias
  }

  get deadlineLabel(): string {
    if (!this.hasDeadline) return '';
    const d = new Date(this.deadline);
    return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
  }

  get priorityLabel(): string {
    const labels: Record<CardPriority, string> = {
      alta: 'Alta', media: 'Media', baixa: 'Baixa'
    };
    return labels[this.priority];
  }

  get tituloTruncado(): string {
    return this.title.length > 50 ? this.title.slice(0, 47) + '...' : this.title;
  }

  isValid(): boolean {
    return this.id.length > 0 && this.title.length >= 3 && this.board_id.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      board_id: this.board_id,
      column_id: this.column_id,
      title: this.title,
      copy_text: this.copy_text,
      disciplina: this.disciplina,
      tecnologia: this.tecnologia,
      priority: this.priority,
      assigned_user_ids: this.assigned_user_ids,
      pipeline_id: this.pipeline_id,
      drive_link: this.drive_link,
      pdf_url: this.pdf_url,
      image_urls: this.image_urls,
      deadline: this.deadline
    };
  }
}
