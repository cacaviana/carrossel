// src/lib/services/NotificationService.ts

import { NotificationRepository } from '$lib/repositories/NotificationRepository';
import type { NotificationDTO } from '$lib/dtos/NotificationDTO';

export class NotificationService {
  static async listar(): Promise<NotificationDTO[]> {
    const notifications = await NotificationRepository.listar();
    return notifications.filter(n => n.isValid());
  }

  static async marcarComoLida(id: string): Promise<void> {
    return NotificationRepository.marcarComoLida(id);
  }

  static async marcarTodasComoLidas(): Promise<void> {
    return NotificationRepository.marcarTodasComoLidas();
  }
}
