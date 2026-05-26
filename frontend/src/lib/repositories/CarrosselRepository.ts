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

export interface DesignSystemItem { id: string; name: string }

export class CarrosselRepository {
  static async listarDesignSystems(): Promise<DesignSystemItem[]> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 150));
      return [];
    }
    const res = await fetch(`${API_BASE}/api/drive/design-systems`, { headers: authHeaders() });
    if (!res.ok) return [];
    return res.json();
  }

  static async buscarDesignSystem(id: string): Promise<{ content: string } | null> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 150));
      return { content: '' };
    }
    const res = await fetch(`${API_BASE}/api/drive/design-systems/${id}`, { headers: authHeaders() });
    if (!res.ok) return null;
    return res.json();
  }

  static async gerarImagemSlide(payload: Record<string, any>): Promise<{ image?: string }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 1500));
      return {};
    }
    const res = await fetch(`${API_BASE}/api/gerar-imagem-slide`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao gerar imagem do slide');
    }
    return res.json();
  }

  static async gerarImagens(payload: Record<string, any>): Promise<{ images: string[] }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 2000));
      return { images: [] };
    }
    const res = await fetch(`${API_BASE}/api/gerar-imagem`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao gerar imagens');
    }
    return res.json();
  }

  static async aplicarFotoBatch(payload: { slides: string[]; foto_criador: string }): Promise<{ images: string[] }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 500));
      return { images: payload.slides };
    }
    const res = await fetch(`${API_BASE}/api/aplicar-foto-batch`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Erro ao aplicar foto em batch');
    return res.json();
  }

  static async salvarDrive(payload: Record<string, any>): Promise<{ web_view_link: string }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 800));
      return { web_view_link: 'https://drive.google.com/mock' };
    }
    const res = await fetch(`${API_BASE}/api/google-drive/carrossel`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao salvar no Drive');
    }
    return res.json();
  }
}
