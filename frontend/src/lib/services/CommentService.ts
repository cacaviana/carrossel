// src/lib/services/CommentService.ts

import { CommentRepository } from '$lib/repositories/CommentRepository';
import type { CommentDTO } from '$lib/dtos/CommentDTO';

export class CommentService {
  static async listarPorCard(cardId: string): Promise<CommentDTO[]> {
    const comments = await CommentRepository.listarPorCard(cardId);
    return comments.filter(c => c.isValid());
  }

  static async criar(cardId: string, text: string): Promise<CommentDTO> {
    return CommentRepository.criar(cardId, text);
  }

  static async deletar(commentId: string): Promise<void> {
    return CommentRepository.deletar(commentId);
  }
}
