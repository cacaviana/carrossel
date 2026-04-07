import { PipelineRepository } from '$lib/repositories/PipelineRepository';
import type { PipelineDTO } from '$lib/dtos/PipelineDTO';
import type { PipelineStepDTO } from '$lib/dtos/PipelineStepDTO';

export class PipelineService {
  static async criar(payload: Record<string, any>): Promise<PipelineDTO> {
    return PipelineRepository.criar(payload);
  }

  static async buscar(id: string): Promise<PipelineDTO> {
    return PipelineRepository.buscar(id);
  }

  static async listarSteps(pipelineId: string): Promise<PipelineStepDTO[]> {
    return PipelineRepository.listarSteps(pipelineId);
  }

  static async cancelar(id: string): Promise<void> {
    return PipelineRepository.cancelar(id);
  }

  static async executar(id: string): Promise<void> {
    return PipelineRepository.executar(id);
  }

  static async retomar(id: string): Promise<void> {
    return PipelineRepository.retomar(id);
  }
}
