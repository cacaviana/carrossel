import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { CopyDTO } from '$lib/dtos/CopyDTO';
import { HookDTO } from '$lib/dtos/HookDTO';
import { getToken } from '$lib/stores/auth.svelte';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

/** Extrai string de texto de um valor que pode ser string, dict, ou array de dicts. */
function _str(val: any): string {
  if (typeof val === 'string') return val;
  if (!val) return '';
  // Array de objetos — concatenar textos dos sub-elementos
  if (Array.isArray(val)) {
    return val.map((item: any) => _str(item.texto ?? item.conteudo ?? item)).filter(Boolean).join(' ');
  }
  if (typeof val !== 'object') return '';
  if (typeof val.texto === 'string') return val.texto;
  if (typeof val.conteudo === 'string') return val.conteudo;
  if (typeof val.titulo === 'string') return val.titulo;
  // Array dentro do objeto
  if (Array.isArray(val.conteudo)) return _str(val.conteudo);
  for (const k of Object.keys(val)) {
    const v = val[k];
    if (typeof v === 'string' && v.length > 3) return v;
  }
  return '';
}

/** Extrai titulo e corpo de um slide, independente da estrutura que o LLM retornou. */
function _extractText(s: any): { titulo: string; conteudo: string } {
  // 1. Campos diretos (padrao esperado)
  let titulo = _str(s.titulo) || _str(s.headline) || '';
  let conteudo = _str(s.corpo) || _str(s.conteudo) || _str(s.texto) || _str(s.texto_principal) || _str(s.subtitulo) || '';
  // 2. Fallback: buscar em elementos[] (LLM retorna layout visual com texto dentro)
  if ((!titulo || !conteudo) && Array.isArray(s.elementos)) {
    for (const el of s.elementos) {
      const t = el.tipo ?? '';
      const val = _str(el.texto) || _str(el.conteudo) || _str(el);
      if (!titulo && (t.includes('titulo') || t === 'headline')) titulo = val;
      if (!conteudo && (t.includes('card') || t === 'corpo' || t === 'subtitulo' || t === 'call_to_action' || t === 'descricao')) conteudo = val;
    }
  }
  return { titulo, conteudo };
}

/** Busca array de slides em qualquer nivel da saida do LLM. */
function _findSlides(obj: any): any[] {
  if (!obj || typeof obj !== 'object') return [];
  // Nivel raiz
  if (Array.isArray(obj.slides) && obj.slides.length > 0) return obj.slides;
  if (Array.isArray(obj.sequencia_slides) && obj.sequencia_slides.length > 0) return obj.sequencia_slides;
  if (Array.isArray(obj.carrossel) && obj.carrossel.length > 0) return obj.carrossel;
  if (obj.slide && typeof obj.slide === 'object' && !Array.isArray(obj.slide)) return [obj.slide];
  // Um nivel abaixo (ex: saida.post_unico.slides, saida.carrossel_data.slides)
  for (const key of Object.keys(obj)) {
    const val = obj[key];
    if (Array.isArray(val) && val.length > 0 && val[0]?.titulo) return val;
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

    const primeiro = slides[0] ? _extractText(slides[0]) : { titulo: '', conteudo: '' };
    const headline = saida.headline || primeiro.titulo;
    const narrativa = saida.narrativa || primeiro.conteudo;
    const ultimoSlide = slides[slides.length - 1] ?? {};
    const cta = saida.cta || (ultimoSlide.tipo === 'cta' ? ultimoSlide.texto || ultimoSlide.titulo : '') || '';

    return new CopyDTO({
      pipeline_id: pipelineId,
      headline,
      narrativa,
      cta,
      provider: saida._provider ?? 'anthropic',
      model: saida._model ?? '',
      fallback: saida._fallback ?? false,
      sequencia_slides: slides.map((s: any, i: number) => {
        const { titulo, conteudo } = _extractText(s);
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
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/copywriter`, { headers: authHeaders() });
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
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/copywriter`, { headers: authHeaders() });
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
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/hook_specialist`, { headers: authHeaders() });
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
      headers: authHeaders(),
      body: JSON.stringify({ dados_editados: payload, etapa: 'hook_specialist' })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao aprovar copy');
    }
  }

  /** Aprova a etapa copywriter (AP-2) — usado na tela de revisao de copy. */
  static async aprovarCopywriter(pipelineId: string, payload: Record<string, any>): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 600));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/copywriter/aprovar`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ saida_editada: JSON.stringify(payload) })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao aprovar copywriter');
    }
  }

  static async rejeitar(pipelineId: string, feedback: string = ''): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 600));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/hook_specialist/rejeitar`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ motivo: feedback || 'Rejeitado pelo usuario' })
    });
    if (!res.ok) throw new Error('Erro ao rejeitar copy');
  }

  /** Rejeita a etapa copywriter. */
  static async rejeitarCopywriter(pipelineId: string, feedback: string = ''): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 600));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/copywriter/rejeitar`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ motivo: feedback || 'Rejeitado pelo usuario' })
    });
    if (!res.ok) throw new Error('Erro ao rejeitar copywriter');
  }

  /**
   * Busca status da etapa copywriter (usado pra polling pos-rejeitar).
   * Devolve status simples, sem mapear pra DTO.
   */
  static async buscarStatusCopywriter(pipelineId: string): Promise<{ status: string } | null> {
    if (USE_MOCK) {
      return { status: 'aguardando_aprovacao' };
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/copywriter`, { headers: authHeaders() });
    if (!res.ok) return null;
    const data = await res.json();
    return { status: data?.status ?? '' };
  }
}
