import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { AgenteDTO } from '$lib/dtos/AgenteDTO';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class AgenteRepository {
  static async listar(): Promise<AgenteDTO[]> {
    if (USE_MOCK) {
      const { agentesMock, skillsMock } = await import('$lib/mocks/agente.mock');
      await new Promise(r => setTimeout(r, 300));
      return [...agentesMock, ...skillsMock].map((a: any) => new AgenteDTO(a));
    }
    const res = await fetch(`${API_BASE}/api/agentes`);
    if (!res.ok) throw new Error('Erro ao carregar agentes');
    const data = await res.json();
    const items = Array.isArray(data)
      ? data
      : [...(data.agentes_llm ?? []), ...(data.skills_deterministicas ?? [])];
    return items.map((a: any) => new AgenteDTO(a));
  }

  static async listarLLM(): Promise<AgenteDTO[]> {
    if (USE_MOCK) {
      const { agentesMock } = await import('$lib/mocks/agente.mock');
      await new Promise(r => setTimeout(r, 200));
      return agentesMock.map((a: any) => new AgenteDTO(a));
    }
    const all = await this.listar();
    return all.filter(a => a.isLLM);
  }

  static async listarSkills(): Promise<AgenteDTO[]> {
    if (USE_MOCK) {
      const { skillsMock } = await import('$lib/mocks/agente.mock');
      await new Promise(r => setTimeout(r, 200));
      return skillsMock.map((a: any) => new AgenteDTO(a));
    }
    const all = await this.listar();
    return all.filter(a => a.isSkill);
  }

  static async buscar(slug: string): Promise<AgenteDTO> {
    if (USE_MOCK) {
      const { agentesMock, skillsMock } = await import('$lib/mocks/agente.mock');
      await new Promise(r => setTimeout(r, 200));
      const found = [...agentesMock, ...skillsMock].find((a: any) => a.slug === slug);
      if (!found) throw new Error('Agente nao encontrado');
      return new AgenteDTO(found);
    }
    const res = await fetch(`${API_BASE}/api/agentes/${slug}`);
    if (!res.ok) throw new Error('Agente nao encontrado');
    return new AgenteDTO(await res.json());
  }
}
