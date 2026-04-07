import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { HistoricoItemDTO } from '$lib/dtos/HistoricoItemDTO';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

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
    const res = await fetch(`${API_BASE}/api/historico${query}`);
    if (!res.ok) throw new Error('Erro ao carregar historico');
    const data = await res.json();
    const items = Array.isArray(data) ? data : (data.items ?? []);
    return items.map((h: any) => new HistoricoItemDTO(h));
  }

  static async remover(id: number): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }
    const res = await fetch(`${API_BASE}/api/historico/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Erro ao remover item');
  }
}
