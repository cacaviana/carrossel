import { CopyRepository } from '$lib/repositories/CopyRepository';
import type { CopyDTO } from '$lib/dtos/CopyDTO';

export class CopyService {
  static async buscarCopy(pipelineId: string): Promise<CopyDTO> {
    return CopyRepository.buscarCopy(pipelineId);
  }

  static async buscarVersoes(pipelineId: string): Promise<CopyDTO[]> {
    return CopyRepository.buscarVersoes(pipelineId);
  }

  static async aprovar(pipelineId: string, payload: Record<string, any>): Promise<void> {
    return CopyRepository.aprovar(pipelineId, payload);
  }

  static async aprovarCopywriter(pipelineId: string, payload: Record<string, any>): Promise<void> {
    return CopyRepository.aprovarCopywriter(pipelineId, payload);
  }

  static async rejeitar(pipelineId: string, feedback?: string): Promise<void> {
    return CopyRepository.rejeitar(pipelineId, feedback);
  }

  static async rejeitarCopywriter(pipelineId: string, feedback?: string): Promise<void> {
    return CopyRepository.rejeitarCopywriter(pipelineId, feedback);
  }

  static async buscarStatusCopywriter(pipelineId: string): Promise<{ status: string } | null> {
    return CopyRepository.buscarStatusCopywriter(pipelineId);
  }
}
