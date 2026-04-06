import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { PromptVisualDTO } from '$lib/dtos/PromptVisualDTO';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class VisualRepository {
  static async buscar(pipelineId: string): Promise<PromptVisualDTO> {
    if (USE_MOCK) {
      const { promptVisualMock } = await import('$lib/mocks/visual.mock');
      await new Promise(r => setTimeout(r, 400));
      return new PromptVisualDTO({ ...promptVisualMock, pipeline_id: pipelineId });
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/art_director`);
    if (!res.ok) throw new Error('Erro ao carregar prompts visuais');
    const data = await res.json();
    const saida = data.saida ?? {};
    // Backend retorna prompt/tipo_slide, DTO espera prompt_imagem/titulo/modelo_sugerido
    const prompts = (saida.prompts ?? []).map((p: any, i: number) => ({
      slide_index: p.slide_index ?? i,
      titulo: p.titulo ?? p.tipo_slide ?? `Slide ${(p.slide_index ?? i) + 1}`,
      prompt_imagem: p.prompt_imagem ?? p.prompt ?? '',
      modelo_sugerido: p.modelo_sugerido ??
        (p.slide_index === 1 || p.tipo_slide === 'capa' || p.tipo_slide === 'cta' || p.tipo_slide === 'codigo' ? 'pro' : 'flash'),
    }));
    return new PromptVisualDTO({ pipeline_id: pipelineId, prompts });
  }

  static async buscarPreferencias(): Promise<any[]> {
    if (USE_MOCK) {
      const { preferenciasVisuaisMock } = await import('$lib/mocks/visual.mock');
      await new Promise(r => setTimeout(r, 200));
      return preferenciasVisuaisMock;
    }
    const res = await fetch(`${API_BASE}/api/visual-preferences`);
    if (!res.ok) return [];
    return res.json();
  }

  static async buscarBrandPalette(): Promise<any> {
    if (USE_MOCK) {
      const { brandPaletteMock } = await import('$lib/mocks/visual.mock');
      await new Promise(r => setTimeout(r, 150));
      return brandPaletteMock;
    }
    const res = await fetch(`${API_BASE}/api/config/brand-palette`);
    if (!res.ok) throw new Error('Erro ao carregar brand palette');
    return res.json();
  }

  static async aprovar(pipelineId: string, prompts: any[]): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 600));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/art_director/aprovar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dados_editados: { prompts }, etapa: 'art_director' })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao aprovar prompts visuais');
    }
  }

  static async rejeitar(pipelineId: string, feedback: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 600));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/art_director/rejeitar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback })
    });
    if (!res.ok) throw new Error('Erro ao rejeitar prompts visuais');
  }
}
