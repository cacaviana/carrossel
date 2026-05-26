import { ConfigRepository } from '$lib/repositories/ConfigRepository';
import type { BrandPaletteDTO } from '$lib/dtos/BrandPaletteDTO';
import type { CreatorEntryDTO } from '$lib/dtos/CreatorEntryDTO';
import type { PlatformRuleDTO } from '$lib/dtos/PlatformRuleDTO';

export class ConfigService {
  static async buscarBrandPalette(): Promise<BrandPaletteDTO> {
    return ConfigRepository.buscarBrandPalette();
  }

  static async salvarBrandPalette(dto: BrandPaletteDTO): Promise<BrandPaletteDTO> {
    if (!dto.isValid()) throw new Error('Dados da brand palette invalidos. Verifique os campos.');
    return ConfigRepository.salvarBrandPalette(dto.toPayload());
  }

  static async buscarCreatorRegistry(): Promise<CreatorEntryDTO[]> {
    return ConfigRepository.buscarCreatorRegistry();
  }

  static async salvarCreatorRegistry(dtos: CreatorEntryDTO[]): Promise<void> {
    const invalidos = dtos.filter(d => !d.isValid());
    if (invalidos.length > 0) throw new Error(`${invalidos.length} criador(es) com dados invalidos.`);
    return ConfigRepository.salvarCreatorRegistry(dtos.map(d => d.toPayload()));
  }

  static async buscarPlatformRules(): Promise<PlatformRuleDTO[]> {
    return ConfigRepository.buscarPlatformRules();
  }

  static async salvarPlatformRules(dtos: PlatformRuleDTO[]): Promise<void> {
    const invalidos = dtos.filter(d => !d.isValid());
    if (invalidos.length > 0) throw new Error(`${invalidos.length} regra(s) com dados invalidos.`);
    return ConfigRepository.salvarPlatformRules(dtos.map(d => d.toPayload()));
  }

  static async salvarApiKeys(payload: Record<string, any>): Promise<void> {
    return ConfigRepository.salvarApiKeys(payload);
  }

  static async buscarApiKeys(): Promise<Record<string, boolean>> {
    return ConfigRepository.buscarApiKeys();
  }
}
