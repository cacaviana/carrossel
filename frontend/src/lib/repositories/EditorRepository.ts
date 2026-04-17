import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { getToken } from '$lib/stores/auth.svelte';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

export class EditorRepository {
  static async carregarCopywriter(pipelineId: string): Promise<any> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return { slides: [] };
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/copywriter`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Erro ao carregar copywriter');
    return res.json();
  }

  static async carregarPipeline(pipelineId: string): Promise<any> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      return { tema: 'Mock Pipeline', formato: 'carrossel' };
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Erro ao carregar pipeline');
    return res.json();
  }

  static async carregarImagens(pipelineId: string): Promise<any> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 400));
      return { saida: { imagens: [] } };
    }
    // Tentar etapa image_generator primeiro
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/etapas/image_generator`, { headers: authHeaders() });
    if (res.ok) {
      const data = await res.json();
      const saida = data.saida ?? data;
      const imgs = saida?.imagens || saida?.resultados || [];
      if (imgs.length > 0 && imgs.some((i: any) => i.image_path || i.image_base64 || i.image_url)) {
        return data;
      }
    }
    // Fallback: listar imagens direto do disco
    const diskRes = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/imagens`, { headers: authHeaders() });
    if (!diskRes.ok) throw new Error('Erro ao carregar imagens');
    return { saida: await diskRes.json() };
  }

  static async carregarBrand(slug: string): Promise<any> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      return { cores: { acento_principal: '#3578B0' } };
    }
    const res = await fetch(`${API_BASE}/api/brands/${slug}`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Erro ao carregar marca');
    return res.json();
  }

  static async carregarFoto(slug: string): Promise<string> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      return '';
    }
    const res = await fetch(`${API_BASE}/api/brands/${slug}/foto`, { headers: authHeaders() });
    if (!res.ok) return '';
    const data = await res.json();
    if (!data.foto) return '';
    return data.foto.startsWith('http') || data.foto.startsWith('data:')
      ? data.foto
      : `${API_BASE}${data.foto}`;
  }

  static async carregarEditorSlides(brand: string): Promise<string[]> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 400));
      return [];
    }
    const res = await fetch(`${API_BASE}/api/editor/slides/${brand}`, { headers: authHeaders() });
    if (!res.ok) return [];
    const data = await res.json();
    return (data.imagens || []).map((i: any) =>
      i.image_base64.startsWith('data:') ? i.image_base64 : `data:image/png;base64,${i.image_base64}`
    );
  }

  static async salvarFoto(slug: string, foto: string): Promise<void> {
    if (USE_MOCK) return;
    await fetch(`${API_BASE}/api/brands/${slug}/foto`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify({ foto }),
    });
  }

  static async gerarImagem(payload: {
    slides: any[];
    brand_slug: string;
    formato: string;
    skip_validation?: boolean;
  }): Promise<{ images: string[] }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 1000));
      return { images: [] };
    }
    const controller = new AbortController();
    setTimeout(() => controller.abort(), 120_000);
    const res = await fetch(`${API_BASE}/api/gerar-imagem`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    if (!res.ok) throw new Error('Erro ao gerar imagem');
    return res.json();
  }

  static async corrigirTexto(payload: {
    image: string;
    slide: any;
    brand_slug: string;
    instrucao?: string;
  }): Promise<{ image?: string; tentativas?: number; aviso?: string }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 1000));
      return { image: payload.image, tentativas: 1 };
    }
    const controller = new AbortController();
    setTimeout(() => controller.abort(), 120_000);
    const res = await fetch(`${API_BASE}/api/editor/corrigir-texto`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    if (!res.ok) throw new Error('Erro ao corrigir texto');
    return res.json();
  }

  static async corrigirAvatar(payload: {
    imagem: string;
    brand_slug: string;
    pipeline_id?: string;
    slide_index?: number;
  }): Promise<{ image?: string; tentativas?: number; aviso?: string; detail?: string }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 1000));
      return { image: payload.imagem, tentativas: 1 };
    }
    const controller = new AbortController();
    setTimeout(() => controller.abort(), 120_000);
    const res = await fetch(`${API_BASE}/api/corrigir-avatar`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload),
      signal: controller.signal
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao corrigir avatar');
    }
    return res.json();
  }

  static async ajustarImagem(payload: {
    imagem: string;
    feedback: string;
    brand_slug: string;
  }): Promise<{ image?: string; ajustado?: boolean }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 1000));
      return { image: payload.imagem, ajustado: true };
    }
    const controller = new AbortController();
    setTimeout(() => controller.abort(), 120_000);
    const res = await fetch(`${API_BASE}/api/editor/ajustar-imagem`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
    if (!res.ok) throw new Error('Erro ao ajustar imagem');
    return res.json();
  }

  static async salvarDrive(payload: {
    title: string;
    pdf_base64: string;
    images_base64: string[];
    pipeline_id?: string;
  }): Promise<{ web_view_link: string }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 800));
      return { web_view_link: 'https://drive.google.com/mock' };
    }
    const res = await fetch(`${API_BASE}/api/google-drive/carrossel`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({
        ...payload,
        disciplina: null,
        tecnologia_principal: null,
        tipo_carrossel: 'texto',
        legenda_linkedin: null,
      }),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail || 'Erro ao salvar no Drive');
    }
    return res.json();
  }
}
