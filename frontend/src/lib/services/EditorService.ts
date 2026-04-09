import { EditorRepository } from '$lib/repositories/EditorRepository';

export class EditorService {
  static async carregarCopywriter(pipelineId: string): Promise<any> {
    return EditorRepository.carregarCopywriter(pipelineId);
  }

  static async carregarPipeline(pipelineId: string): Promise<any> {
    return EditorRepository.carregarPipeline(pipelineId);
  }

  static async carregarImagens(pipelineId: string): Promise<any> {
    return EditorRepository.carregarImagens(pipelineId);
  }

  static async carregarBrand(slug: string): Promise<any> {
    return EditorRepository.carregarBrand(slug);
  }

  static async carregarFoto(slug: string): Promise<string> {
    return EditorRepository.carregarFoto(slug);
  }

  static async carregarEditorSlides(brand: string): Promise<string[]> {
    return EditorRepository.carregarEditorSlides(brand);
  }

  static async salvarFoto(slug: string, foto: string): Promise<void> {
    return EditorRepository.salvarFoto(slug, foto);
  }

  static async gerarImagem(payload: {
    slides: any[];
    brand_slug: string;
    formato: string;
    skip_validation?: boolean;
  }): Promise<{ images: string[] }> {
    return EditorRepository.gerarImagem(payload);
  }

  static async corrigirTexto(payload: {
    image: string;
    slide: any;
    brand_slug: string;
    instrucao?: string;
  }): Promise<{ image?: string; tentativas?: number; aviso?: string }> {
    return EditorRepository.corrigirTexto(payload);
  }

  static async ajustarImagem(payload: {
    imagem: string;
    feedback: string;
    brand_slug: string;
  }): Promise<{ image?: string; ajustado?: boolean }> {
    return EditorRepository.ajustarImagem(payload);
  }

  static async salvarDrive(payload: {
    title: string;
    pdf_base64: string;
    images_base64: string[];
  }): Promise<{ web_view_link: string }> {
    return EditorRepository.salvarDrive(payload);
  }
}
