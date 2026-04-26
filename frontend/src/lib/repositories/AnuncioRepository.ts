// src/lib/repositories/AnuncioRepository.ts
//
// Repository do dominio Anuncio. Branch interno USE_MOCK -> mock store; senao -> API real.
// Pos-pivot (2026-04-23): sem regeneracao por dimensao, sem ZIP. Apenas imagem inteira + Drive.

import { browser } from '$app/environment';
import { AnuncioDTO } from '$lib/dtos/AnuncioDTO';
import type { CriarAnuncioDTO } from '$lib/dtos/CriarAnuncioDTO';
import type { ListarAnunciosFiltroDTO } from '$lib/dtos/ListarAnunciosFiltroDTO';
import type { EditarAnuncioCopyDTO } from '$lib/dtos/EditarAnuncioCopyDTO';
import type { RegerarImagemDTO } from '$lib/dtos/RegerarImagemDTO';
import {
  buscarAnuncioMockPorId,
  filtrarAnunciosMock,
  criarAnuncioMock,
  editarCopyMock,
  excluirAnuncioMock,
  regerarImagemMock,
  salvarDriveMock
} from '$lib/mocks/anuncio.mock';
import { API_BASE } from '$lib/api';
import { getToken } from '$lib/stores/auth.svelte';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function sleep(ms = 300): Promise<void> {
  return new Promise(r => setTimeout(r, ms));
}

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

async function extractError(res: Response, fallback: string): Promise<Error> {
  try {
    const body = await res.json();
    const detail = body?.detail;
    if (typeof detail === 'string') return new Error(detail);
    if (Array.isArray(detail)) return new Error(detail.map((d: any) => d.msg ?? JSON.stringify(d)).join('; '));
  } catch {
    // ignora — cai no fallback
  }
  return new Error(fallback);
}

export class AnuncioRepository {
  static async listar(filtro: ListarAnunciosFiltroDTO): Promise<AnuncioDTO[]> {
    if (USE_MOCK) {
      await sleep();
      return filtrarAnunciosMock(filtro.toPayload()).map(d => new AnuncioDTO(d));
    }
    const qs = filtro.queryString ? `?${filtro.queryString}` : '';
    const res = await fetch(`${API_BASE}/api/anuncios${qs}`, { headers: authHeaders() });
    if (!res.ok) throw await extractError(res, 'Falha ao listar anuncios');
    const body = await res.json();
    const items = Array.isArray(body) ? body : (body.items ?? []);
    return items.map((d: any) => new AnuncioDTO(d));
  }

  static async obterPorId(id: string): Promise<AnuncioDTO> {
    if (USE_MOCK) {
      await sleep();
      const raw = buscarAnuncioMockPorId(id);
      if (!raw) throw new Error('Anuncio nao encontrado');
      return new AnuncioDTO(raw);
    }
    const res = await fetch(`${API_BASE}/api/anuncios/${id}`, { headers: authHeaders() });
    if (!res.ok) throw await extractError(res, 'Anuncio nao encontrado');
    return new AnuncioDTO(await res.json());
  }

  static async criar(dto: CriarAnuncioDTO): Promise<{ anuncio_id: string; pipeline_id: string }> {
    if (USE_MOCK) {
      await sleep(500);
      const novo = criarAnuncioMock(dto.toPayload());
      return { anuncio_id: novo.id, pipeline_id: novo.pipeline_id };
    }
    // Caminho real: POST /api/anuncios cria anuncio + dispara pipeline.
    // Observacao: o fluxo unificado do frontend usa /?formato=anuncio via PipelineService.criar.
    const res = await fetch(`${API_BASE}/api/anuncios`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(dto.toPayload())
    });
    if (!res.ok) throw await extractError(res, 'Falha ao criar anuncio');
    const body = await res.json();
    return { anuncio_id: body.id, pipeline_id: body.pipeline_id };
  }

  static async editarCopy(dto: EditarAnuncioCopyDTO): Promise<AnuncioDTO> {
    if (USE_MOCK) {
      await sleep();
      const atualizado = editarCopyMock(dto.toPayload());
      if (!atualizado) throw new Error('Anuncio nao encontrado');
      return new AnuncioDTO(atualizado);
    }
    const payload = dto.toPayload();
    // Backend PUT /api/anuncios/{id} recebe {titulo, headline, descricao, cta, etapa_funil}
    // sem 'id' no body (id vai na rota).
    const { id, ...bodyPayload } = payload;
    const res = await fetch(`${API_BASE}/api/anuncios/${id}`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify(bodyPayload)
    });
    if (!res.ok) throw await extractError(res, 'Falha ao editar copy');
    return new AnuncioDTO(await res.json());
  }

  static async regerarImagem(dto: RegerarImagemDTO): Promise<{ anuncio_id: string; status: string }> {
    if (USE_MOCK) {
      await sleep(400);
      regerarImagemMock(dto.anuncio_id);
      return { anuncio_id: dto.anuncio_id, status: 'em_andamento' };
    }
    // Pos-pivot: POST /api/anuncios/{id}/regenerar-imagem (sem 'dimensao_id').
    const res = await fetch(`${API_BASE}/api/anuncios/${dto.anuncio_id}/regenerar-imagem`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(dto.toPayload())
    });
    if (!res.ok) throw await extractError(res, 'Falha ao iniciar regeneracao');
    const body = await res.json();
    return {
      anuncio_id: body.anuncio_id ?? body.id ?? dto.anuncio_id,
      status: body.status ?? 'em_andamento'
    };
  }

  static async excluir(id: string): Promise<void> {
    if (USE_MOCK) {
      await sleep();
      const ok = excluirAnuncioMock(id);
      if (!ok) throw new Error('Anuncio nao encontrado');
      return;
    }
    const res = await fetch(`${API_BASE}/api/anuncios/${id}`, {
      method: 'DELETE',
      headers: authHeaders()
    });
    if (!res.ok) throw await extractError(res, 'Falha ao excluir anuncio');
  }

  static async salvarNoDrive(id: string): Promise<{ drive_folder_link: string }> {
    if (USE_MOCK) {
      await sleep(800);
      const link = salvarDriveMock(id);
      if (!link) throw new Error('Anuncio nao encontrado');
      return { drive_folder_link: link };
    }
    // Backend unificou em POST /api/anuncios/{id}/exportar com body {destino: "drive"}.
    const res = await fetch(`${API_BASE}/api/anuncios/${id}/exportar`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ destino: 'drive' })
    });
    if (!res.ok) throw await extractError(res, 'Falha ao salvar no Drive');
    const body = await res.json();
    return { drive_folder_link: body.drive_folder_link ?? '' };
  }
}
