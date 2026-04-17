import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { BrandDTO } from '$lib/dtos/BrandDTO';
import { getToken } from '$lib/stores/auth.svelte';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

function authHeadersNoContent(): Record<string, string> {
  return { 'Authorization': `Bearer ${getToken()}` };
}

function absolutize(url: string | undefined | null): string {
  if (!url) return '';
  if (url.startsWith('http') || url.startsWith('data:')) return url;
  return `${API_BASE}${url}`;
}

export interface BrandFoto {
  foto: string;
}

export interface BrandAsset {
  nome: string;
  preview: string;
  is_referencia?: boolean;
  pool?: string;
  [key: string]: any;
}

export class BrandRepository {
  /** Lista marcas (resumo — sem assets/foto). */
  static async listar(): Promise<BrandDTO[]> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      return [];
    }
    const res = await fetch(`${API_BASE}/api/brands`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Erro ao carregar marcas');
    const data = await res.json();
    return (data as any[]).map(b => new BrandDTO(b));
  }

  /** Busca uma marca pelo slug — perfil completo. */
  static async buscar(slug: string): Promise<BrandDTO> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      return new BrandDTO({ slug, nome: 'Mock' });
    }
    const res = await fetch(`${API_BASE}/api/brands/${slug}`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Erro ao buscar marca');
    return new BrandDTO(await res.json());
  }

  /** Cria nova marca. */
  static async criar(payload: Record<string, any>): Promise<BrandDTO> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 400));
      return new BrandDTO(payload);
    }
    const res = await fetch(`${API_BASE}/api/brands`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao criar marca');
    }
    return new BrandDTO(await res.json());
  }

  /** Atualiza marca existente. */
  static async atualizar(slug: string, payload: Record<string, any>): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 400));
      return;
    }
    const res = await fetch(`${API_BASE}/api/brands/${slug}`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao salvar marca');
    }
  }

  /** Remove marca. */
  static async remover(slug: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }
    const res = await fetch(`${API_BASE}/api/brands/${slug}`, {
      method: 'DELETE',
      headers: authHeadersNoContent()
    });
    if (!res.ok) throw new Error('Erro ao remover marca');
  }

  /** Clona marca. */
  static async clonar(origemSlug: string, destinoSlug: string, destinoNome: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 400));
      return;
    }
    const res = await fetch(`${API_BASE}/api/brands/${origemSlug}/clonar`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ slug_destino: destinoSlug, nome_destino: destinoNome })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao clonar marca');
    }
  }

  /** Regenera DNA da marca. Retorna { dna, padrao_visual? }. */
  static async regenerarDna(slug: string): Promise<{ dna: any; padrao_visual?: any }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 1500));
      return { dna: {} };
    }
    const res = await fetch(`${API_BASE}/api/brands/${slug}/dna/regenerate`, {
      method: 'POST',
      headers: authHeaders(),
      body: '{}'
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao regenerar DNA');
    }
    return res.json();
  }

  /** Busca foto (logo) da marca. Devolve URL absoluta ou ''. */
  static async buscarFoto(slug: string): Promise<string> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 150));
      return '';
    }
    const res = await fetch(`${API_BASE}/api/brands/${slug}/foto`, { headers: authHeaders() });
    if (!res.ok) return '';
    const data = await res.json();
    return absolutize(data?.foto);
  }

  /** Atualiza foto (logo) da marca. */
  static async salvarFoto(slug: string, foto: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }
    const res = await fetch(`${API_BASE}/api/brands/${slug}/foto`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify({ foto })
    });
    if (!res.ok) throw new Error('Erro ao salvar foto');
  }

  /** Lista assets (avatar + referencias) da marca, com preview absoluto. */
  static async listarAssets(slug: string): Promise<BrandAsset[]> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      return [];
    }
    const res = await fetch(`${API_BASE}/api/brands/${slug}/assets`, { headers: authHeaders() });
    if (!res.ok) return [];
    const data = await res.json();
    const assets = data?.assets ?? [];
    return assets.map((a: any) => ({
      ...a,
      preview: absolutize(a.preview)
    }));
  }

  /** Adiciona asset (avatar, referencia, etc). */
  static async criarAsset(slug: string, payload: { nome: string; imagem: string; pool?: string }): Promise<{ nome: string }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 400));
      return { nome: payload.nome };
    }
    const res = await fetch(`${API_BASE}/api/brands/${slug}/assets`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao criar asset');
    }
    return res.json();
  }

  /** Remove asset. */
  static async removerAsset(slug: string, nomeAsset: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      return;
    }
    const res = await fetch(`${API_BASE}/api/brands/${slug}/assets/${nomeAsset}`, {
      method: 'DELETE',
      headers: authHeadersNoContent()
    });
    if (!res.ok) throw new Error('Erro ao remover asset');
  }

  /** Define (ou limpa) asset de referencia ativa. */
  static async definirReferencia(slug: string, nome: string | null): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      return;
    }
    const res = await fetch(`${API_BASE}/api/brands/${slug}/referencia`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify({ nome })
    });
    if (!res.ok) throw new Error('Erro ao definir referencia');
  }

  /** Analisa N imagens de referencia com IA e sugere brand profile. */
  static async analisarReferencias(payload: { imagens: string[]; nome_marca?: string; descricao?: string }): Promise<any> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 2000));
      return { cores: {}, visual: {} };
    }
    const res = await fetch(`${API_BASE}/api/analisar-referencias`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao analisar referencias');
    }
    return res.json();
  }

  /** Analisa uma imagem individual (DNA visual + brand_profile). */
  static async descreverReferencia(imagem: string): Promise<any> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 1500));
      return {};
    }
    const res = await fetch(`${API_BASE}/api/descrever-referencia`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ imagem })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao analisar imagem');
    }
    return res.json();
  }
}
