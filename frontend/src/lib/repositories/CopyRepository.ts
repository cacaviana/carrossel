import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { CopyDTO } from '$lib/dtos/CopyDTO';
import { HookDTO } from '$lib/dtos/HookDTO';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

/** Busca array de slides em qualquer nivel da saida do LLM. */
function _findSlides(obj: any): any[] {
  if (!obj || typeof obj !== 'object') return [];
  // Nivel raiz
  if (Array.isArray(obj.slides) && obj.slides.length > 0) return obj.slides;
  if (Array.isArray(obj.sequencia_slides) && obj.sequencia_slides.length > 0) return obj.sequencia_slides;
  if (obj.slide && typeof obj.slide === 'object' && !Array.isArray(obj.slide)) return [obj.slide];
  // Um nivel abaixo (ex: saida.carrossel.slides, saida.post_unico.slides)
  for (const key of Object.keys(obj)) {
    const val = obj[key];
    if (val && typeof val === 'object' && !Array.isArray(val)) {
      if (Array.isArray(val.slides) && val.slides.length > 0) return val.slides;
      if (val.slide && typeof val.slide === 'object') return [val.slide];
    }
  }
  return [];
}

export class CopyRepository {
  static _mapSaidaToCopy(saida: any, pipelineId: string): CopyDTO {
    // LLM retorna em formatos variados — buscar slides em qualquer estrutura
    const slides = _findSlides(saida);

    // headline/narrativa/cta podem estar no nivel raiz, no slide, ou em elementos[]
    const primeiroSlide = slides[0] ?? {};
    let headline = saida.headline || primeiroSlide.titulo || primeiroSlide.headline || '';
    let narrativa = saida.narrativa || primeiroSlide.subtitulo || primeiroSlide.narrativa || '';
    // Fallback: buscar em elementos[] do slide
    if ((!headline || !narrativa) && Array.isArray(primeiroSlide.elementos)) {
      for (const el of primeiroSlide.elementos) {
        if (!headline && (el.tipo === 'titulo_principal' || el.tipo === 'titulo')) headline = el.texto || el.conteudo || '';
        if (!narrativa && (el.tipo === 'card_principal' || el.tipo === 'subtitulo' || el.tipo === 'credibilidade_footer')) narrativa = el.texto || el.conteudo || '';
      }
    }
    const ultimoSlide = slides[slides.length - 1] ?? {};
    const cta = saida.cta || (ultimoSlide.tipo === 'cta' ? ultimoSlide.texto || ultimoSlide.titulo : '') || '';

    return new CopyDTO({
      pipeline_id: pipelineId,
      headline,
      narrativa,
      cta,
      provider: saida._provider ?? 'anthropic',
      model: saida._model ?? '',
      sequencia_slides: slides.map((s: any, i: number) => {
        let titulo = s.titulo ?? '';
        let conteudo = s.corpo ?? s.conteudo ?? s.texto ?? s.texto_principal ?? s.subtitulo ?? '';
        if ((!titulo || !conteudo) && Array.isArray(s.elementos)) {
          for (const el of s.elementos) {
            if (!titulo && (el.tipo === 'titulo_principal' || el.tipo === 'titulo')) titulo = el.texto || el.conteudo || '';
            if (!conteudo && (el.tipo === 'card_principal' || el.tipo === 'corpo')) conteudo = el.texto || el.conteudo || '';
          }
        }
        return {
          titulo,
          conteudo,
          tipo: s.tipo ?? 'content',
          ordem: s.indice ?? s.ordem ?? i,
        };
      }),
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
      hookMap[h.letra ?? h.id ?? h.opcao ?? ''] = h.texto ?? '';
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
