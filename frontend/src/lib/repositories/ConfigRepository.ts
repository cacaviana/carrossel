import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { BrandPaletteDTO } from '$lib/dtos/BrandPaletteDTO';
import { CreatorEntryDTO } from '$lib/dtos/CreatorEntryDTO';
import { PlatformRuleDTO } from '$lib/dtos/PlatformRuleDTO';
import { getToken } from '$lib/stores/auth.svelte';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

export class ConfigRepository {
  // --- Brand Palette ---

  static async buscarBrandPalette(): Promise<BrandPaletteDTO> {
    if (USE_MOCK) {
      const { brandPaletteMock } = await import('$lib/mocks/config-brand.mock');
      await new Promise(r => setTimeout(r, 300));
      return new BrandPaletteDTO(brandPaletteMock);
    }
    const res = await fetch(`${API_BASE}/api/config/brand-palette`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Erro ao carregar brand palette');
    return new BrandPaletteDTO(await res.json());
  }

  static async salvarBrandPalette(payload: Record<string, any>): Promise<BrandPaletteDTO> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 500));
      return new BrandPaletteDTO(payload);
    }
    const res = await fetch(`${API_BASE}/api/config/brand-palette`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao salvar brand palette');
    }
    return new BrandPaletteDTO(await res.json());
  }

  // --- Creator Registry ---

  static async buscarCreatorRegistry(): Promise<CreatorEntryDTO[]> {
    if (USE_MOCK) {
      const { creatorsMock } = await import('$lib/mocks/config-creators.mock');
      await new Promise(r => setTimeout(r, 300));
      return creatorsMock.map((c: any) => new CreatorEntryDTO(c));
    }
    const res = await fetch(`${API_BASE}/api/config/creator-registry`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Erro ao carregar creator registry');
    const data = await res.json();
    const items = Array.isArray(data) ? data : (data.criadores ?? []);
    return items.map((c: any) => new CreatorEntryDTO(c));
  }

  static async salvarCreatorRegistry(payload: Record<string, any>[]): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 500));
      return;
    }
    const res = await fetch(`${API_BASE}/api/config/creator-registry`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify({ criadores: payload })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao salvar creator registry');
    }
  }

  // --- Platform Rules ---

  static async buscarPlatformRules(): Promise<PlatformRuleDTO[]> {
    if (USE_MOCK) {
      const { platformRulesMock } = await import('$lib/mocks/config-platform.mock');
      await new Promise(r => setTimeout(r, 300));
      return platformRulesMock.map((p: any) => new PlatformRuleDTO(p));
    }
    const res = await fetch(`${API_BASE}/api/config/platform-rules`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Erro ao carregar platform rules');
    const data = await res.json();
    const items = Array.isArray(data) ? data : (data.regras ?? []);
    return items.map((p: any) => new PlatformRuleDTO(p));
  }

  static async salvarPlatformRules(payload: Record<string, any>[]): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 500));
      return;
    }
    const res = await fetch(`${API_BASE}/api/config/platform-rules`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify({ regras: payload })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao salvar platform rules');
    }
  }

  // --- Plataformas (unificado: rules + brand palette) ---

  static async buscarPlataformas(): Promise<Record<string, any>[]> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return [];
    }
    const res = await fetch(`${API_BASE}/api/config/plataformas`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Erro ao carregar plataformas');
    const data = await res.json();
    return data.plataformas ?? [];
  }

  static async salvarPlataformas(plataformas: Record<string, any>[]): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 500));
      return;
    }
    const res = await fetch(`${API_BASE}/api/config/plataformas`, {
      method: 'PUT',
      headers: authHeaders(),
      body: JSON.stringify({ plataformas })
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      throw new Error(err.detail ?? 'Erro ao salvar plataformas');
    }
  }

  // --- API Keys (legado, mantido) ---

  static async salvarApiKeys(payload: Record<string, any>): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 800));
      return;
    }
    const res = await fetch(`${API_BASE}/api/config`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Erro ao salvar chaves');
  }

  static async buscarApiKeys(): Promise<Record<string, boolean>> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return { claude: false, gemini: false, drive_credentials: false, drive_folder: false };
    }
    const res = await fetch(`${API_BASE}/api/config`, { headers: authHeaders() });
    if (!res.ok) throw new Error('Erro ao carregar status das chaves');
    return res.json();
  }
}
