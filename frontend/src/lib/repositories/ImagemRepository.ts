import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { ImagemVariacaoDTO } from '$lib/dtos/ImagemVariacaoDTO';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class ImagemRepository {
  static async buscar(pipelineId: string): Promise<ImagemVariacaoDTO> {
    if (USE_MOCK) {
      const { getImagemVariacoesComPlaceholders } = await import('$lib/mocks/imagem.mock');
      await new Promise(r => setTimeout(r, 600));
      const data = getImagemVariacoesComPlaceholders();
      return new ImagemVariacaoDTO({ ...data, pipeline_id: pipelineId });
    }
    // Buscar do image_generator (novo formato: versoes de backgrounds + slides renderizados)
    const igRes = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/image_generator`);
    if (!igRes.ok) throw new Error('Erro ao carregar imagens');
    const igData = await igRes.json();
    const saida = igData.saida ?? {};

    // Novo formato: versoes[{background_estilo, slides[{slide_index, titulo, image_base64}]}]
    const versoes = saida.versoes ?? [];
    // Fallback para formato antigo
    const resultados = versoes.length > 0
      ? [] // Usar versoes
      : (saida.resultados ?? saida.imagens ?? saida.slides ?? []);

    const slideMap = new Map<number, any>();

    if (versoes.length > 0) {
      // Novo formato: cada versao é um background diferente, cada slide dentro tem image_base64
      for (const [vi, versao] of versoes.entries()) {
        for (const slide of versao.slides ?? []) {
          const si = slide.slide_index ?? 0;
          if (!slideMap.has(si)) {
            slideMap.set(si, {
              slide_index: si,
              titulo: slide.titulo ?? `Slide ${si}`,
              variacoes: [],
              brand_gate_status: 'valido',
              brand_gate_retries: 0,
            });
          }
          slideMap.get(si)!.variacoes.push({
            variacao_id: `bg${vi + 1}-slide${si}`,
            url: '',
            base64: slide.image_base64 ?? '',
          });
        }
      }
    } else {
      // Formato: resultados[{slide_index, variacao, image_url?, image_base64?}]
      for (const r of resultados) {
        const si = r.slide_index ?? 0;
        if (!slideMap.has(si)) {
          slideMap.set(si, {
            slide_index: si,
            titulo: r.titulo ?? `Slide ${si}`,
            variacoes: [],
            brand_gate_status: 'pendente',
            brand_gate_retries: 0,
          });
        }
        const slide = slideMap.get(si)!;
        // Preferir URL sobre base64
        const imgUrl = r.image_url ? (r.image_url.startsWith('http') ? r.image_url : `${API_BASE}${r.image_url}`) : '';
        slide.variacoes.push({
          variacao_id: `${si}-${r.variacao ?? slide.variacoes.length + 1}`,
          url: imgUrl,
          base64: imgUrl ? '' : (r.image_base64 ?? ''),
        });
        if (r.validacao?.valido === true) slide.brand_gate_status = 'valido';
        else if (r.validacao?.valido === false) slide.brand_gate_status = 'revisao_manual';
      }
    }
    return new ImagemVariacaoDTO({
      pipeline_id: pipelineId,
      slides: Array.from(slideMap.values()),
    });
  }

  static async aprovar(pipelineId: string, selecoes: any[]): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 600));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/brand_gate/aprovar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dados_editados: { selecoes }, etapa: 'brand_gate' })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao aprovar imagens');
    }
  }

  static async rejeitar(pipelineId: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 600));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/brand_gate/rejeitar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback: 'Todas as imagens rejeitadas pelo usuario' })
    });
    if (!res.ok) throw new Error('Erro ao rejeitar imagens');
  }

  static async regerar(pipelineId: string, slideIndex: number, variacaoId: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 1000));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/image_generator/aprovar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dados_editados: { regerar: true, slide_index: slideIndex, variacao_id: variacaoId }, etapa: 'image_generator' })
    });
    if (!res.ok) throw new Error('Erro ao regerar imagem');
  }
}
