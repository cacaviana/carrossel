// src/lib/repositories/ActivityRepository.ts

import { ActivityDTO } from '$lib/dtos/ActivityDTO';
import { API_BASE } from '$lib/api';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

export class ActivityRepository {
  static async listarPorCard(cardId: string): Promise<ActivityDTO[]> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 250));
      const { activitiesMock } = await import('$lib/mocks/kanban/activities.mock');
      return activitiesMock
        .filter(a => a.card_id === cardId)
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .map(a => new ActivityDTO(a));
    }

    const res = await fetch(`${API_BASE}/api/kanban/cards/${cardId}/activities`);
    return (await res.json()).map((a: any) => new ActivityDTO(a));
  }
}
