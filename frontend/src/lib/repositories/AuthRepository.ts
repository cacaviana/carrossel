// src/lib/repositories/AuthRepository.ts

import { AuthDTO } from '$lib/dtos/AuthDTO';
import { API_BASE } from '$lib/api';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

export class AuthRepository {
  static async login(email: string, password: string): Promise<{ success: boolean; data?: AuthDTO; error?: string }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 500));
      const { loginMock } = await import('$lib/mocks/kanban/users.mock');
      const result = loginMock(email, password);
      if (result.success && result.data) {
        return { success: true, data: new AuthDTO(result.data) };
      }
      return { success: false, error: result.error };
    }

    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      return { success: false, error: body.detail ?? 'Email ou senha incorretos.' };
    }
    const data = await res.json();
    return { success: true, data: new AuthDTO(data) };
  }
}
