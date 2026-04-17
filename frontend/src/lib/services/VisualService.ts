import { VisualRepository } from '$lib/repositories/VisualRepository';
import type { PromptVisualDTO } from '$lib/dtos/PromptVisualDTO';

export class VisualService {
  static async buscar(pipelineId: string): Promise<PromptVisualDTO> {
    return VisualRepository.buscar(pipelineId);
  }

  static async buscarPreferencias(): Promise<any[]> {
    return VisualRepository.buscarPreferencias();
  }

  static async buscarBrandPalette(): Promise<any> {
    return VisualRepository.buscarBrandPalette();
  }

  static async aprovar(pipelineId: string, prompts: any[]): Promise<void> {
    return VisualRepository.aprovar(pipelineId, prompts);
  }

  static async rejeitar(pipelineId: string, feedback: string): Promise<void> {
    return VisualRepository.rejeitar(pipelineId, feedback);
  }

  static async buscarStatus(pipelineId: string): Promise<{ status: string } | null> {
    return VisualRepository.buscarStatus(pipelineId);
  }
}
