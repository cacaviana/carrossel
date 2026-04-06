import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { BriefingDTO } from '$lib/dtos/BriefingDTO';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class BriefingRepository {
  static async buscar(pipelineId: string): Promise<BriefingDTO> {
    if (USE_MOCK) {
      const { briefingMock } = await import('$lib/mocks/briefing.mock');
      await new Promise(r => setTimeout(r, 400));
      return new BriefingDTO({ ...briefingMock, pipeline_id: pipelineId });
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/strategist`);
    if (!res.ok) throw new Error('Erro ao carregar briefing');
    const data = await res.json();
    const saida = data.saida ?? {};
    const briefingObj = saida.briefing ?? {};
    const funil = saida.funil ?? [];

    // Montar briefing_completo como texto legivel a partir do JSON estruturado
    const partes: string[] = [];
    if (briefingObj.tema_principal) partes.push(`Tema: ${briefingObj.tema_principal}`);
    if (briefingObj.angulo) partes.push(`Angulo: ${briefingObj.angulo}`);
    if (briefingObj.publico_alvo) partes.push(`Publico-alvo: ${briefingObj.publico_alvo}`);
    if (briefingObj.objetivo) partes.push(`Objetivo: ${briefingObj.objetivo}`);
    if (briefingObj.tom) partes.push(`Tom: ${briefingObj.tom}`);
    if (briefingObj.palavras_chave?.length) partes.push(`Palavras-chave: ${briefingObj.palavras_chave.join(', ')}`);
    if (briefingObj.referencias?.length) partes.push(`Referencias: ${briefingObj.referencias.join(', ')}`);

    return new BriefingDTO({
      pipeline_id: pipelineId,
      briefing_completo: partes.join('\n\n'),
      tema_original: data.entrada?.tema ?? briefingObj.tema_principal ?? '',
      formato_alvo: data.entrada?.formato ?? '',
      pecas_funil: funil,
      tendencias_usadas: briefingObj.referencias ?? [],
    });
  }

  static async aprovar(pipelineId: string, briefing: string, pecasFunil?: any[]): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 600));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/strategist/aprovar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dados_editados: { briefing_completo: briefing, pecas_funil: pecasFunil }, etapa: 'strategist' })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao aprovar briefing');
    }
  }

  static async rejeitar(pipelineId: string, feedback: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 600));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/strategist/rejeitar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao rejeitar briefing');
    }
  }
}
