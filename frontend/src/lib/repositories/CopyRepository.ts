import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { CopyDTO } from '$lib/dtos/CopyDTO';
import { HookDTO } from '$lib/dtos/HookDTO';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class CopyRepository {
  static _mapSaidaToCopy(saida: any, pipelineId: string): CopyDTO {
    const slides = saida.slides ?? saida.sequencia_slides ?? [];
    return new CopyDTO({
      pipeline_id: pipelineId,
      headline: saida.headline ?? '',
      narrativa: saida.narrativa ?? '',
      cta: saida.cta ?? '',
      provider: saida._provider ?? 'anthropic',
      model: saida._model ?? '',
      sequencia_slides: slides.map((s: any, i: number) => ({
        titulo: s.titulo ?? '',
        conteudo: s.corpo ?? s.conteudo ?? '',
        tipo: s.tipo ?? 'content',
        ordem: s.indice ?? s.ordem ?? i,
      })),
    });
  }

  static async buscarCopy(pipelineId: string): Promise<CopyDTO> {
    if (USE_MOCK) {
      const { copyMock } = await import('$lib/mocks/copy.mock');
      await new Promise(r => setTimeout(r, 400));
      return new CopyDTO({ ...copyMock, pipeline_id: pipelineId });
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/copywriter`);
    if (!res.ok) throw new Error('Erro ao carregar copy');
    const data = await res.json();
    const saida = data.saida ?? {};
    return this._mapSaidaToCopy(saida, pipelineId);
  }

  static async buscarVersoes(pipelineId: string): Promise<CopyDTO[]> {
    if (USE_MOCK) {
      const { copyMock } = await import('$lib/mocks/copy.mock');
      await new Promise(r => setTimeout(r, 400));
      return [new CopyDTO({ ...copyMock, pipeline_id: pipelineId })];
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/copywriter`);
    if (!res.ok) throw new Error('Erro ao carregar copy');
    const data = await res.json();
    const saida = data.saida ?? {};
    const versoes = saida._versoes ?? [saida];
    return versoes
      .filter((v: any) => !v._error && !v.raw_text)
      .map((v: any) => this._mapSaidaToCopy(v, pipelineId));
  }

  static async buscarHooks(pipelineId: string): Promise<HookDTO> {
    if (USE_MOCK) {
      const { hooksMock } = await import('$lib/mocks/copy.mock');
      await new Promise(r => setTimeout(r, 300));
      return new HookDTO({ ...hooksMock, pipeline_id: pipelineId });
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/hook_specialist`);
    if (!res.ok) throw new Error('Erro ao carregar hooks');
    const data = await res.json();
    const saida = data.saida ?? {};
    // Backend retorna hooks: [{letra: "A", texto: "..."}, ...], DTO espera hook_a, hook_b, hook_c
    const hooks = saida.hooks ?? [];
    const hookMap: Record<string, string> = {};
    for (const h of hooks) {
      hookMap[h.letra ?? h.opcao ?? ''] = h.texto ?? '';
    }
    return new HookDTO({
      pipeline_id: pipelineId,
      hook_a: hookMap['A'] ?? saida.hook_a ?? '',
      hook_b: hookMap['B'] ?? saida.hook_b ?? '',
      hook_c: hookMap['C'] ?? saida.hook_c ?? '',
      hook_selecionado: saida.hook_selecionado ?? null,
    });
  }

  static async aprovar(pipelineId: string, payload: Record<string, any>): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 600));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/hook_specialist/aprovar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dados_editados: payload, etapa: 'hook_specialist' })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao aprovar copy');
    }
  }

  static async rejeitar(pipelineId: string, feedback: string = ''): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 600));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/hook_specialist/rejeitar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ motivo: feedback || 'Rejeitado pelo usuario' })
    });
    if (!res.ok) throw new Error('Erro ao rejeitar copy');
  }
}
