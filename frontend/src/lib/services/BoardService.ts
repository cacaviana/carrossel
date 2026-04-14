// src/lib/services/BoardService.ts

import { BoardRepository } from '$lib/repositories/BoardRepository';
import type { BoardDTO } from '$lib/dtos/BoardDTO';

export class BoardService {
  static async carregar(): Promise<BoardDTO> {
    return BoardRepository.carregar();
  }
}
