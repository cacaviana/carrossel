import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { PipelineDTO } from '$lib/dtos/PipelineDTO';
import { PipelineStepDTO } from '$lib/dtos/PipelineStepDTO';
import { getToken } from '$lib/stores/auth.svelte';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

export class PipelineRepository {
  static async criar(payload: Record<string, any>): Promise<PipelineDTO> {
    if (USE_MOCK) {
      const { pipelinesMock, simularDelay } = await import('$lib/mocks/pipeline.mock');
      await simularDelay(800);
      return new PipelineDTO({ ...pipelinesMock[0], id: `pip-${Date.now()}` });
    }
    const res = await fetch(`${API_BASE}/api/pipelines/`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      const detail = err.detail;
      const msg = typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: any) => d.msg ?? JSON.stringify(d)).join('; ')
          : 'Erro ao criar pipeline';
      throw new Error(msg);
    }
    return new PipelineDTO(await res.json());
  }

  static async buscar(id: string): Promise<PipelineDTO> {
    if (USE_MOCK) {
      const { pipelinesMock, simularDelay } = await import('$lib/mocks/pipeline.mock');
      await simularDelay(300);
      const found = pipelinesMock.find(p => p.id === id) ?? pipelinesMock[0];
      return new PipelineDTO({ ...found, id });
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${id}`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Pipeline nao encontrado');
    return new PipelineDTO(await res.json());
  }

  static async listarSteps(pipelineId: string): Promise<PipelineStepDTO[]> {
    if (USE_MOCK) {
      const { pipelineStepsMock, simularDelay } = await import('$lib/mocks/pipeline.mock');
      await simularDelay(200);
      const steps = pipelineStepsMock[pipelineId] ?? pipelineStepsMock['pip-001'];
      return steps.map((s: any) => new PipelineStepDTO({ ...s, pipeline_id: pipelineId }));
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Erro ao carregar etapas');
    const data = await res.json();
    return (data.etapas ?? []).map((s: any) => new PipelineStepDTO(s));
  }

  static async executar(id: string): Promise<void> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/pipeline.mock');
      await simularDelay(500);
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${id}/executar`, {
      method: 'POST',
      headers: authHeaders()
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao executar proxima etapa');
    }
  }

  static async cancelar(id: string): Promise<void> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/pipeline.mock');
      await simularDelay(500);
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${id}/cancelar`, {
      method: 'POST',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao cancelar pipeline');
  }

  static async retomar(id: string): Promise<void> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/pipeline.mock');
      await simularDelay(500);
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${id}/retomar`, {
      method: 'POST',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao retomar pipeline');
  }

  /**
   * Aprova etapa generica — usado para auto-aprovar etapas que nao tem
   * tela de revisao propria (ex: image_generator). Envia payload vazio.
   */
  static async aprovarEtapa(pipelineId: string, agente: string): Promise<void> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/pipeline.mock');
      await simularDelay(300);
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/${agente}/aprovar`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({})
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? `Erro ao aprovar etapa ${agente}`);
    }
  }
}
