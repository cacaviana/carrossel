import { AgenteRepository } from '$lib/repositories/AgenteRepository';
import type { AgenteDTO } from '$lib/dtos/AgenteDTO';

export class AgenteService {
  static async listar(): Promise<AgenteDTO[]> {
    const agentes = await AgenteRepository.listar();
    return agentes.filter(a => a.isValid());
  }

  static async listarLLM(): Promise<AgenteDTO[]> {
    const agentes = await AgenteRepository.listarLLM();
    return agentes.filter(a => a.isValid());
  }

  static async listarSkills(): Promise<AgenteDTO[]> {
    const agentes = await AgenteRepository.listarSkills();
    return agentes.filter(a => a.isValid());
  }
}
