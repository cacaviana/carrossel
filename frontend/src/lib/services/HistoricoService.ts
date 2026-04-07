import { HistoricoRepository } from '$lib/repositories/HistoricoRepository';
import type { HistoricoItemDTO } from '$lib/dtos/HistoricoItemDTO';

export class HistoricoService {
  static async listar(): Promise<HistoricoItemDTO[]> {
    const items = await HistoricoRepository.listar();
    return items.filter(item => item.isValid());
  }

  static async remover(id: number): Promise<void> {
    return HistoricoRepository.remover(id);
  }
}
