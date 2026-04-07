import { BriefingRepository } from '$lib/repositories/BriefingRepository';
import type { BriefingDTO } from '$lib/dtos/BriefingDTO';

export class BriefingService {
  static async buscar(pipelineId: string): Promise<BriefingDTO> {
    return BriefingRepository.buscar(pipelineId);
  }

  static async aprovar(pipelineId: string, briefing: string, pecasFunil?: any[]): Promise<void> {
    return BriefingRepository.aprovar(pipelineId, briefing, pecasFunil);
  }

  static async rejeitar(pipelineId: string, feedback: string): Promise<void> {
    return BriefingRepository.rejeitar(pipelineId, feedback);
  }
}
