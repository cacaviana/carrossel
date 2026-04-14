// src/lib/repositories/NotificationRepository.ts

import { NotificationDTO } from '$lib/dtos/NotificationDTO';
import { API_BASE } from '$lib/api';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

let mockNotificationsState: any[] | null = null;

async function getMockNotifications() {
  if (!mockNotificationsState) {
    const { notificationsMock } = await import('$lib/mocks/kanban/notifications.mock');
    mockNotificationsState = [...notificationsMock];
  }
  return mockNotificationsState;
}

export class NotificationRepository {
  static async listar(): Promise<NotificationDTO[]> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      const notifications = await getMockNotifications();
      return notifications
        .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
        .map(n => new NotificationDTO(n));
    }

    const res = await fetch(`${API_BASE}/api/kanban/notifications`);
    return (await res.json()).map((n: any) => new NotificationDTO(n));
  }

  static async marcarComoLida(id: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 100));
      const notifications = await getMockNotifications();
      const notif = notifications.find(n => n.id === id);
      if (notif) notif.is_read = true;
      return;
    }

    await fetch(`${API_BASE}/api/kanban/notifications/${id}/read`, { method: 'PATCH' });
  }

  static async marcarTodasComoLidas(): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      const notifications = await getMockNotifications();
      notifications.forEach(n => n.is_read = true);
      return;
    }

    await fetch(`${API_BASE}/api/kanban/notifications/read-all`, { method: 'PATCH' });
  }
}
