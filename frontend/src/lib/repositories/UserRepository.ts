// src/lib/repositories/UserRepository.ts

import { UserDTO } from '$lib/dtos/UserDTO';
import { API_BASE } from '$lib/api';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

export class UserRepository {
  static async listar(): Promise<UserDTO[]> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      const { usersMock } = await import('$lib/mocks/kanban/users.mock');
      return usersMock.map(u => new UserDTO(u));
    }

    const res = await fetch(`${API_BASE}/api/kanban/users`);
    return (await res.json()).map((u: any) => new UserDTO(u));
  }
}
