import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { ScoreDTO } from '$lib/dtos/ScoreDTO';
import { getToken } from '$lib/stores/auth.svelte';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

export class ExportRepository {
  static async buscarScore(pipelineId: string): Promise<ScoreDTO> {
    if (USE_MOCK) {
      const { scoreMock } = await import('$lib/mocks/score.mock');
      await new Promise(r => setTimeout(r, 500));
      return new ScoreDTO({ ...scoreMock, pipeline_id: pipelineId });
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/content_critic`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Erro ao carregar score');
    const data = await res.json();
    const saida = data.saida ?? {};
    return new ScoreDTO({ ...saida, pipeline_id: pipelineId });
  }

  static async buscarLegenda(pipelineId: string): Promise<string> {
    if (USE_MOCK) {
      const { legendaLinkedinMock } = await import('$lib/mocks/score.mock');
      await new Promise(r => setTimeout(r, 200));
      return legendaLinkedinMock;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/content_critic`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Erro ao carregar legenda');
    const data = await res.json();
    return data.saida?.legenda ?? '';
  }

  static async salvarDrive(pipelineId: string): Promise<{ link: string }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 2000));
      return { link: 'https://drive.google.com/drive/folders/example-mock' };
    }
    const res = await fetch(`${API_BASE}/api/google-drive/carrossel`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ pipeline_id: pipelineId })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao salvar no Drive');
    }
    return res.json();
  }
}
