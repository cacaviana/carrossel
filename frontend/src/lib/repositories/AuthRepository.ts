// src/lib/repositories/AuthRepository.ts

import { AuthDTO } from '$lib/dtos/AuthDTO';
import { UserDTO } from '$lib/dtos/UserDTO';
import { API_BASE } from '$lib/api';
import { getToken } from '$lib/stores/auth.svelte';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

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
    if (res.status === 429) {
      return { success: false, error: 'Muitas tentativas. Aguarde 1 minuto antes de tentar novamente.' };
    }
    if (!res.ok) {
      const body = await res.json().catch(() => ({}));
      return { success: false, error: body.detail ?? 'Email ou senha incorretos.' };
    }
    const data = await res.json();
    return { success: true, data: new AuthDTO(data) };
  }

  static async me(): Promise<AuthDTO> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      const { authMock } = await import('$lib/mocks/kanban/users.mock');
      return new AuthDTO(authMock);
    }

    const res = await fetch(`${API_BASE}/api/auth/me`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Sessao expirada');
    const data = await res.json();
    return new AuthDTO({ ...data, token: getToken() });
  }

  static async listarUsuarios(): Promise<UserDTO[]> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      const { usersMock } = await import('$lib/mocks/kanban/users.mock');
      return usersMock.map(u => new UserDTO(u));
    }

    const res = await fetch(`${API_BASE}/api/auth/users`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao listar usuarios');
    const data = await res.json();
    return data.map((u: any) => new UserDTO(u));
  }

  static async criarUsuario(payload: Record<string, any>): Promise<UserDTO> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 400));
      return new UserDTO({
        id: `usr-${Date.now()}`,
        tenant_id: 'tenant-itvalley',
        ...payload,
        created_at: new Date().toISOString(),
        deleted_at: ''
      });
    }

    const res = await fetch(`${API_BASE}/api/auth/users`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (res.status === 409) throw new Error('Email ja cadastrado');
    if (res.status === 403) throw new Error('Sem permissao');
    if (res.status === 422) {
      const body = await res.json().catch(() => ({}));
      throw new Error(body.detail ?? 'Dados invalidos');
    }
    if (!res.ok) throw new Error('Erro ao criar usuario');
    const data = await res.json();
    return new UserDTO(data);
  }

  static async editarUsuario(userId: string, payload: Record<string, any>): Promise<UserDTO> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      const { usersMock } = await import('$lib/mocks/kanban/users.mock');
      const existing = usersMock.find(u => u.id === userId);
      return new UserDTO({ ...existing, ...payload, id: userId });
    }

    const res = await fetch(`${API_BASE}/api/auth/users/${userId}`, {
      method: 'PATCH',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (res.status === 403) throw new Error('Sem permissao');
    if (!res.ok) throw new Error('Erro ao editar usuario');
    const data = await res.json();
    return new UserDTO(data);
  }

  static async desativarUsuario(userId: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }

    const res = await fetch(`${API_BASE}/api/auth/users/${userId}`, {
      method: 'DELETE',
      headers: authHeaders()
    });
    if (res.status === 403) throw new Error('Sem permissao');
    if (!res.ok) throw new Error('Erro ao desativar usuario');
  }

  static async reativarUsuario(userId: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }

    const res = await fetch(`${API_BASE}/api/auth/users/${userId}/reativar`, {
      method: 'POST',
      headers: authHeaders()
    });
    if (res.status === 403) throw new Error('Sem permissao');
    if (!res.ok) throw new Error('Erro ao reativar usuario');
  }

  static async convidarUsuario(payload: Record<string, any>): Promise<{ invite_token: string; invite_url: string; expires_at: string }> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 400));
      const token = `invite-${Date.now()}`;
      return {
        invite_token: token,
        invite_url: `${window.location.origin}/convite?token=${token}`,
        expires_at: new Date(Date.now() + 48 * 60 * 60 * 1000).toISOString()
      };
    }

    const res = await fetch(`${API_BASE}/api/auth/users/invite`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (res.status === 403) throw new Error('Sem permissao');
    if (!res.ok) throw new Error('Erro ao convidar usuario');
    return await res.json();
  }

  static async aceitarConvite(token: string, password: string): Promise<AuthDTO> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 500));
      return new AuthDTO({
        token: 'mock-jwt-convite',
        user_id: `usr-${Date.now()}`,
        tenant_id: 'tenant-itvalley',
        email: 'convidado@itvalley.com.br',
        name: 'Usuario Convidado',
        avatar_url: '',
        role: 'viewer'
      });
    }

    const res = await fetch(`${API_BASE}/api/auth/users/invite/accept`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, password })
    });
    if (res.status === 410) throw new Error('Convite expirado');
    if (res.status === 409) throw new Error('Convite ja utilizado');
    if (!res.ok) throw new Error('Erro ao aceitar convite');
    const data = await res.json();
    return new AuthDTO(data);
  }
}
