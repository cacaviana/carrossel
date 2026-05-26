import { ExportRepository } from '$lib/repositories/ExportRepository';
import type { ScoreDTO } from '$lib/dtos/ScoreDTO';

export class ExportService {
  static async buscarScore(pipelineId: string): Promise<ScoreDTO> {
    return ExportRepository.buscarScore(pipelineId);
  }

  static async buscarLegenda(pipelineId: string): Promise<string> {
    return ExportRepository.buscarLegenda(pipelineId);
  }

  static async salvarDrive(pipelineId: string): Promise<{ link: string }> {
    return ExportRepository.salvarDrive(pipelineId);
  }
}
