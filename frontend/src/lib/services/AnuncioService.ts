// src/lib/services/AnuncioService.ts
//
// Camada opaca do dominio Anuncio. Nunca acessa dto.campo — usa dto.isValid() /
// dto.toPayload() / metodos publicos.
//
// Pos-pivot (2026-04-23): regenera IMAGEM (nao mais dimensao). Sem ZIP.

import { AnuncioRepository } from '$lib/repositories/AnuncioRepository';
import type { AnuncioDTO } from '$lib/dtos/AnuncioDTO';
import type { CriarAnuncioDTO } from '$lib/dtos/CriarAnuncioDTO';
import type { EditarAnuncioCopyDTO } from '$lib/dtos/EditarAnuncioCopyDTO';
import type { ListarAnunciosFiltroDTO } from '$lib/dtos/ListarAnunciosFiltroDTO';
import type { RegerarImagemDTO } from '$lib/dtos/RegerarImagemDTO';

export class AnuncioService {
  static async listar(filtro: ListarAnunciosFiltroDTO): Promise<AnuncioDTO[]> {
    if (!filtro.isValid()) throw new Error('Filtro invalido');
    const anuncios = await AnuncioRepository.listar(filtro);
    return anuncios.filter(a => a.isValid());
  }

  static async obter(id: string): Promise<AnuncioDTO> {
    if (!id || id.length === 0) throw new Error('ID invalido');
    return AnuncioRepository.obterPorId(id);
  }

  static async criar(dto: CriarAnuncioDTO): Promise<{ anuncio_id: string; pipeline_id: string }> {
    if (!dto.isValid()) throw new Error('Dados de criacao invalidos');
    return AnuncioRepository.criar(dto);
  }

  static async editarCopy(dto: EditarAnuncioCopyDTO): Promise<AnuncioDTO> {
    if (!dto.isValid()) throw new Error('Copy invalida (limites 40/125/30 ou titulo curto)');
    return AnuncioRepository.editarCopy(dto);
  }

  static async regerarImagem(dto: RegerarImagemDTO): Promise<{ anuncio_id: string; status: string }> {
    if (!dto.isValid()) throw new Error('Parametros de regeneracao invalidos');
    return AnuncioRepository.regerarImagem(dto);
  }

  static async excluir(id: string): Promise<void> {
    if (!id || id.length === 0) throw new Error('ID invalido');
    return AnuncioRepository.excluir(id);
  }

  static async salvarNoDrive(id: string): Promise<{ drive_folder_link: string }> {
    if (!id || id.length === 0) throw new Error('ID invalido');
    return AnuncioRepository.salvarNoDrive(id);
  }
}
