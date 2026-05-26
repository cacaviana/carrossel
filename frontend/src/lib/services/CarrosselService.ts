import { CarrosselRepository, type DesignSystemItem } from '$lib/repositories/CarrosselRepository';

/**
 * CarrosselService — orquestra operacoes do fluxo de carrossel legado
 * (design systems, gerar imagens, aplicar foto, salvar drive).
 *
 * Service e opaco: nao conhece campos do payload, delega ao Repository.
 */
export class CarrosselService {
  static async listarDesignSystems(): Promise<DesignSystemItem[]> {
    return CarrosselRepository.listarDesignSystems();
  }

  static async buscarDesignSystem(id: string): Promise<{ content: string } | null> {
    if (!id) return null;
    return CarrosselRepository.buscarDesignSystem(id);
  }

  static async gerarImagemSlide(payload: Record<string, any>): Promise<{ image?: string }> {
    return CarrosselRepository.gerarImagemSlide(payload);
  }

  static async gerarImagens(payload: Record<string, any>): Promise<{ images: string[] }> {
    return CarrosselRepository.gerarImagens(payload);
  }

  static async aplicarFotoBatch(payload: { slides: string[]; foto_criador: string }): Promise<{ images: string[] }> {
    return CarrosselRepository.aplicarFotoBatch(payload);
  }

  static async salvarDrive(payload: Record<string, any>): Promise<{ web_view_link: string }> {
    return CarrosselRepository.salvarDrive(payload);
  }
}
