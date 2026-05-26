// src/lib/services/ActivityService.ts

import { ActivityRepository } from '$lib/repositories/ActivityRepository';
import type { ActivityDTO } from '$lib/dtos/ActivityDTO';

export class ActivityService {
  static async listarPorCard(cardId: string): Promise<ActivityDTO[]> {
    const activities = await ActivityRepository.listarPorCard(cardId);
    return activities.filter(a => a.isValid());
  }
}
