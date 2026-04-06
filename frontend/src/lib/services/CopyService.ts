import { CopyRepository } from '$lib/repositories/CopyRepository';
import type { CopyDTO } from '$lib/dtos/CopyDTO';
import type { HookDTO } from '$lib/dtos/HookDTO';

export class CopyService {
  static async buscarCopy(pipelineId: string): Promise<CopyDTO> {
    return CopyRepository.buscarCopy(pipelineId);
  }

  static async buscarVersoes(pipelineId: string): Promise<CopyDTO[]> {
    return CopyRepository.buscarVersoes(pipelineId);
  }

  static async buscarHooks(pipelineId: string): Promise<HookDTO> {
    return CopyRepository.buscarHooks(pipelineId);
  }

  static async aprovar(pipelineId: string, payload: Record<string, any>): Promise<void> {
    return CopyRepository.aprovar(pipelineId, payload);
  }

  static async rejeitar(pipelineId: string, feedback: string = ''): Promise<void> {
    return CopyRepository.rejeitar(pipelineId, feedback);
  }
}
