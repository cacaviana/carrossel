import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { HistoricoItemDTO } from '$lib/dtos/HistoricoItemDTO';
import { getToken } from '$lib/stores/auth.svelte';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

export class HistoricoRepository {
  static async listar(filtros?: Record<string, string>): Promise<HistoricoItemDTO[]> {
    if (USE_MOCK) {
      const { historicoMock } = await import('$lib/mocks/historico.mock');
      await new Promise(r => setTimeout(r, 400));
      return historicoMock.map((h: any) => new HistoricoItemDTO(h));
    }
    const params = new URLSearchParams();
    if (filtros) {
      Object.entries(filtros).forEach(([k, v]) => { if (v) params.set(k, v); });
    }
    const query = params.toString() ? `?${params.toString()}` : '';

    // 1. Historico (exportados pro Drive)
    const histRes = await fetch(`${API_BASE}/api/historico${query}`, { headers: authHeaders() });
    if (!histRes.ok) throw new Error('Erro ao carregar historico');
    const histData = await histRes.json();
    const histItems = Array.isArray(histData) ? histData : (histData.items ?? []);

    // 2. Pipelines (gerados mas nao necessariamente exportados)
    let pipeItems: any[] = [];
    try {
      const pipeRes = await fetch(`${API_BASE}/api/pipelines/`, { headers: authHeaders() });
      if (pipeRes.ok) {
        const pipeData = await pipeRes.json();
        pipeItems = Array.isArray(pipeData) ? pipeData : (pipeData.items ?? []);
      }
    } catch { /* ignore — sem pipelines ainda eh ok */ }

    // Mapear pipelines que nao estao no historico (evita duplicar quando exportado)
    const pipelinesNoHist = new Set(histItems.map((h: any) => h.pipeline_id).filter(Boolean));
    const pipelinesComoHistorico = pipeItems
      .filter((p: any) => !pipelinesNoHist.has(p.id))
      .map((p: any, idx: number) => ({
        id: -(idx + 1), // ID negativo pra nao colidir com historico real
        pipeline_id: p.id,
        titulo: p.tema ?? '(sem titulo)',
        formato: p.formato ?? '',
        status: p.status ?? 'em_andamento',
        disciplina: '',
        tecnologia_principal: '',
        total_slides: 0,
        final_score: null,
        google_drive_link: '',
        created_at: p.created_at ?? '',
      }));

    // Unir: historico (exportado) primeiro, depois pipelines em andamento
    const todos = [...histItems, ...pipelinesComoHistorico];
    return todos.map((h: any) => new HistoricoItemDTO(h));
  }

  static async remover(id: number): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }
    const res = await fetch(`${API_BASE}/api/historico/${id}`, {
      method: 'DELETE',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao remover item');
  }
}
