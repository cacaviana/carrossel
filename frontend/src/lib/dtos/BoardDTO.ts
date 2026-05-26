// src/lib/dtos/BoardDTO.ts

export interface ColumnData {
  id: string;
  name: string;
  order: number;
  color: string | null;
}

export class BoardDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly name: string;
  readonly columns: ColumnData[];
  readonly created_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? data._id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.name = data.name ?? '';
    this.columns = (data.columns ?? []).map((c: any) => ({
      id: c.id ?? '',
      name: c.name ?? '',
      order: c.order ?? 0,
      color: c.color ?? null
    }));
    this.created_at = data.created_at ?? '';
  }

  get columnsSorted(): ColumnData[] {
    return [...this.columns].sort((a, b) => a.order - b.order);
  }

  getColumnById(id: string): ColumnData | undefined {
    return this.columns.find(c => c.id === id);
  }

  getColumnByName(name: string): ColumnData | undefined {
    return this.columns.find(c => c.name === name);
  }

  get canceladoColumnId(): string {
    return this.getColumnByName('Cancelado')?.id ?? '';
  }

  isValid(): boolean {
    return this.id.length > 0 && this.columns.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      tenant_id: this.tenant_id,
      name: this.name,
      columns: this.columns
    };
  }
}
