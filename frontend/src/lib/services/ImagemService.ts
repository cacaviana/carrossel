import { ImagemRepository } from '$lib/repositories/ImagemRepository';
import type { ImagemVariacaoDTO } from '$lib/dtos/ImagemVariacaoDTO';

export class ImagemService {
  static async buscar(pipelineId: string): Promise<ImagemVariacaoDTO> {
    return ImagemRepository.buscar(pipelineId);
  }

  static async aprovar(pipelineId: string, selecoes: any[]): Promise<void> {
    return ImagemRepository.aprovar(pipelineId, selecoes);
  }

  static async rejeitar(pipelineId: string): Promise<void> {
    return ImagemRepository.rejeitar(pipelineId);
  }

  static async regerar(pipelineId: string, slideIndex: number, variacaoId: string): Promise<void> {
    return ImagemRepository.regerar(pipelineId, slideIndex, variacaoId);
  }
}
