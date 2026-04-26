// src/lib/dtos/AnuncioDTO.ts
//
// Anuncio pos-pivot (2026-04-23): formato 1080x1350 UNICO (igual post_unico),
// com copy de venda (headline 40 / descricao 125 / cta 30).
// Sem mais 4 dimensoes, sem status parcial.

import { AnuncioCopyDTO } from './AnuncioCopyDTO';

export type AnuncioStatus = 'rascunho' | 'em_andamento' | 'concluido' | 'erro' | 'cancelado';
export type EtapaFunil = 'topo' | 'meio' | 'fundo' | 'avulso';

// Mapeamento de status do backend para frontend (arquitetura backend usa 'gerando'/'completo';
// frontend/UI usa 'em_andamento'/'concluido'). Quando USE_MOCK=true a origem ja vem no padrao frontend.
function normalizeStatus(raw: any): AnuncioStatus {
  const s = String(raw ?? 'em_andamento');
  if (s === 'gerando') return 'em_andamento';
  if (s === 'completo') return 'concluido';
  // 'parcial' legacy -> trata como 'em_andamento' (conservador; nao deveria mais existir)
  if (s === 'parcial') return 'em_andamento';
  if (['rascunho', 'em_andamento', 'concluido', 'erro', 'cancelado'].includes(s)) {
    return s as AnuncioStatus;
  }
  return 'em_andamento';
}

export class AnuncioDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly titulo: string;
  readonly copy: AnuncioCopyDTO;
  readonly image_url: string;
  readonly status: AnuncioStatus;
  readonly etapa_funil: EtapaFunil;
  readonly pipeline_id: string;
  readonly pipeline_funil_id: string;
  readonly drive_folder_link: string;
  readonly criado_por: string;
  readonly created_at: string;
  readonly updated_at: string;
  readonly deleted_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.titulo = data.titulo ?? '';
    // Backend envia headline/descricao/cta em campos flat. Mock envia nested em data.copy.
    const copyRaw = data.copy ?? {
      headline: data.headline ?? '',
      descricao: data.descricao ?? '',
      cta: data.cta ?? ''
    };
    this.copy = new AnuncioCopyDTO(copyRaw);
    this.image_url = data.image_url ?? '';
    this.status = normalizeStatus(data.status);
    this.etapa_funil = data.etapa_funil ?? 'avulso';
    this.pipeline_id = data.pipeline_id ?? '';
    this.pipeline_funil_id = data.pipeline_funil_id ?? '';
    this.drive_folder_link = data.drive_folder_link ?? '';
    this.criado_por = data.criado_por ?? '';
    this.created_at = data.created_at ?? '';
    this.updated_at = data.updated_at ?? '';
    this.deleted_at = data.deleted_at ?? '';
  }

  get isRascunho(): boolean { return this.status === 'rascunho'; }
  get isConcluido(): boolean { return this.status === 'concluido'; }
  get isEmAndamento(): boolean { return this.status === 'em_andamento'; }
  get isErro(): boolean { return this.status === 'erro'; }
  get isCancelado(): boolean { return this.status === 'cancelado'; }
  get isDeletado(): boolean { return this.deleted_at.length > 0; }

  get hasImage(): boolean { return this.image_url.length > 0; }

  get statusLabel(): string {
    const labels: Record<AnuncioStatus, string> = {
      rascunho: 'Rascunho',
      em_andamento: 'Em andamento',
      concluido: 'Concluido',
      erro: 'Erro',
      cancelado: 'Cancelado'
    };
    return labels[this.status];
  }

  get etapaFunilLabel(): string {
    const labels: Record<EtapaFunil, string> = {
      topo: 'Topo',
      meio: 'Meio',
      fundo: 'Fundo',
      avulso: 'Avulso'
    };
    return labels[this.etapa_funil];
  }

  get thumbnailUrl(): string {
    return this.image_url;
  }

  get tituloTruncado(): string {
    return this.titulo.length > 50 ? this.titulo.slice(0, 47) + '...' : this.titulo;
  }

  get driveFolderName(): string {
    const date = this.created_at.slice(0, 10);
    return `${this.titulo} - ${date}`;
  }

  get hasDriveLink(): boolean { return this.drive_folder_link.length > 0; }

  get podeExportar(): boolean {
    return this.isConcluido && this.hasImage;
  }

  get isVindoDoFunil(): boolean {
    return this.pipeline_funil_id.length > 0;
  }

  get criadoEmFormatado(): string {
    if (!this.created_at) return '';
    try {
      const d = new Date(this.created_at);
      return d.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric' });
    } catch { return this.created_at.slice(0, 10); }
  }

  get criadoHa(): string {
    if (!this.created_at) return '';
    try {
      const diff = Date.now() - new Date(this.created_at).getTime();
      const dias = Math.floor(diff / (1000 * 60 * 60 * 24));
      if (dias === 0) return 'Hoje';
      if (dias === 1) return 'Ontem';
      if (dias < 30) return `ha ${dias} dias`;
      const meses = Math.floor(dias / 30);
      if (meses === 1) return 'ha 1 mes';
      return `ha ${meses} meses`;
    } catch { return ''; }
  }

  isValid(): boolean {
    return this.id.length > 0 && this.titulo.length >= 3;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      tenant_id: this.tenant_id,
      titulo: this.titulo,
      copy: this.copy.toPayload(),
      image_url: this.image_url,
      status: this.status,
      etapa_funil: this.etapa_funil,
      pipeline_id: this.pipeline_id,
      pipeline_funil_id: this.pipeline_funil_id,
      drive_folder_link: this.drive_folder_link,
      criado_por: this.criado_por,
      created_at: this.created_at,
      updated_at: this.updated_at,
      deleted_at: this.deleted_at
    };
  }
}
