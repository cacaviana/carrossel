import { BrandRepository, type BrandAsset } from '$lib/repositories/BrandRepository';
import { BrandDTO } from '$lib/dtos/BrandDTO';

/**
 * BrandService — camada opaca. Nao conhece campos de payload,
 * apenas orquestra DTOs e Repository.
 */
export class BrandService {
  static async listar(): Promise<BrandDTO[]> {
    return BrandRepository.listar();
  }

  static async buscar(slug: string): Promise<BrandDTO> {
    return BrandRepository.buscar(slug);
  }

  static async criar(dto: BrandDTO): Promise<BrandDTO> {
    if (!dto.isValid()) throw new Error('Dados da marca invalidos');
    return BrandRepository.criar(dto.toPayload());
  }

  /** Atualiza marca com payload custom (permite edicao parcial em campos nao tipados). */
  static async atualizar(slug: string, payload: Record<string, any>): Promise<void> {
    if (!slug) throw new Error('Slug obrigatorio');
    return BrandRepository.atualizar(slug, payload);
  }

  static async remover(slug: string): Promise<void> {
    return BrandRepository.remover(slug);
  }

  static async clonar(origemSlug: string, destinoSlug: string, destinoNome: string): Promise<void> {
    if (!origemSlug || !destinoSlug || !destinoNome) throw new Error('Dados de clonagem invalidos');
    return BrandRepository.clonar(origemSlug, destinoSlug, destinoNome);
  }

  static async regenerarDna(slug: string): Promise<{ dna: any; padrao_visual?: any }> {
    return BrandRepository.regenerarDna(slug);
  }

  static async buscarFoto(slug: string): Promise<string> {
    return BrandRepository.buscarFoto(slug);
  }

  static async salvarFoto(slug: string, foto: string): Promise<void> {
    return BrandRepository.salvarFoto(slug, foto);
  }

  static async listarAssets(slug: string): Promise<BrandAsset[]> {
    return BrandRepository.listarAssets(slug);
  }

  static async criarAsset(slug: string, payload: { nome: string; imagem: string; pool?: string }): Promise<{ nome: string }> {
    return BrandRepository.criarAsset(slug, payload);
  }

  static async removerAsset(slug: string, nomeAsset: string): Promise<void> {
    return BrandRepository.removerAsset(slug, nomeAsset);
  }

  static async definirReferencia(slug: string, nome: string | null): Promise<void> {
    return BrandRepository.definirReferencia(slug, nome);
  }

  static async analisarReferencias(payload: { imagens: string[]; nome_marca?: string; descricao?: string }): Promise<any> {
    return BrandRepository.analisarReferencias(payload);
  }

  static async descreverReferencia(imagem: string): Promise<any> {
    return BrandRepository.descreverReferencia(imagem);
  }
}
