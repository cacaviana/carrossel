// src/lib/stores/notifications.ts
// Contador de nao-lidas + lista de notificacoes

import type { NotificationDTO } from '$lib/dtos/NotificationDTO';

let notifications = $state<NotificationDTO[]>([]);

export function getNotifications() { return notifications; }
export function setNotifications(n: NotificationDTO[]) { notifications = n; }

export function getUnreadCount(): number {
  return notifications.filter(n => !n.is_read).length;
}

export function markAsRead(id: string) {
  notifications = notifications.map(n =>
    n.id === id ? { ...n, is_read: true } as unknown as NotificationDTO : n
  );
}

export function markAllAsRead() {
  notifications = notifications.map(n =>
    ({ ...n, is_read: true }) as unknown as NotificationDTO
  );
}
