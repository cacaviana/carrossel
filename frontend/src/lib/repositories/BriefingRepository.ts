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
    // Strategist pode retornar {briefing: {...}} ou o JSON direto na saida
    const briefingObj = saida.briefing ?? saida;
    const funil = saida.funil ?? [];

    // Montar briefing_completo como texto legivel a partir do JSON estruturado
    // Resiliente a diferentes chaves que o LLM pode retornar
    const partes: string[] = [];
    const tema = briefingObj.tema_principal ?? briefingObj.tema ?? '';
    const angulo = briefingObj.angulo ?? briefingObj.hook ?? '';
    const publico = briefingObj.publico_alvo ?? briefingObj.publico ?? '';
    const objetivo = briefingObj.objetivo ?? '';
    const tom = briefingObj.tom ?? briefingObj.tom_voz ?? '';
    const linguagem = briefingObj.linguagem ?? '';
    const cta = briefingObj.call_to_action ?? briefingObj.cta ?? '';
    const emocoes = briefingObj.emocoes_despertar ?? briefingObj.emocoes ?? '';
    const visuais = briefingObj.elementos_visuais ?? '';
    const palavras = briefingObj.palavras_chave ?? [];
    const hashtags = briefingObj.hashtags_sugeridas ?? briefingObj.hashtags ?? [];
    const referencias = briefingObj.referencias ?? [];

    if (tema) partes.push(`Tema: ${tema}`);
    if (angulo) partes.push(`Angulo: ${angulo}`);
    if (publico) partes.push(`Publico-alvo: ${publico}`);
    if (objetivo) partes.push(`Objetivo: ${objetivo}`);
    if (tom) partes.push(`Tom: ${tom}`);
    if (linguagem) partes.push(`Linguagem: ${linguagem}`);
    if (cta) partes.push(`CTA: ${cta}`);
    if (emocoes) partes.push(`Emocoes: ${emocoes}`);
    if (visuais) partes.push(`Elementos visuais: ${visuais}`);
    if (palavras.length) partes.push(`Palavras-chave: ${Array.isArray(palavras) ? palavras.join(', ') : palavras}`);
    if (hashtags.length) partes.push(`Hashtags: ${Array.isArray(hashtags) ? hashtags.join(', ') : hashtags}`);
    if (referencias.length) partes.push(`Referencias: ${Array.isArray(referencias) ? referencias.join(', ') : referencias}`);

    // Fallback: se nenhuma parte foi extraida, mostrar JSON formatado
    const textoFinal = partes.length > 0
      ? partes.join('\n\n')
      : JSON.stringify(briefingObj, null, 2);

    return new BriefingDTO({
      pipeline_id: pipelineId,
      briefing_completo: textoFinal,
      tema_original: data.entrada?.tema ?? tema,
      formato_alvo: data.entrada?.formato ?? '',
      pecas_funil: funil,
      tendencias_usadas: referencias,
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
