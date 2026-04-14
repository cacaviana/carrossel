// src/lib/services/CardService.ts

import { CardRepository } from '$lib/repositories/CardRepository';
import type { CardDTO } from '$lib/dtos/CardDTO';
import type { CriarCardDTO } from '$lib/dtos/CriarCardDTO';

export class CardService {
  static async listarTodos(): Promise<CardDTO[]> {
    const cards = await CardRepository.listar();
    return cards.filter(c => c.isValid());
  }

  static async buscarPorId(id: string): Promise<CardDTO | null> {
    return CardRepository.buscarPorId(id);
  }

  static async criar(dto: CriarCardDTO): Promise<CardDTO> {
    return CardRepository.criar(dto.toPayload());
  }

  static async moverParaCancelado(cardId: string, canceladoColumnId: string): Promise<CardDTO> {
    return CardRepository.moverParaCancelado(cardId, canceladoColumnId);
  }
}
