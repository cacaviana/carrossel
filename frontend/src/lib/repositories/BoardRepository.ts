// src/lib/repositories/BoardRepository.ts

import { BoardDTO } from '$lib/dtos/BoardDTO';
import { API_BASE } from '$lib/api';
import { getToken } from '$lib/stores/auth.svelte';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

export class BoardRepository {
  static async carregar(): Promise<BoardDTO> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      const { boardMock } = await import('$lib/mocks/kanban/board.mock');
      return new BoardDTO(boardMock);
    }

    const res = await fetch(`${API_BASE}/api/kanban/board`, {
      headers: authHeaders()
    });
    const data = await res.json();
    return new BoardDTO(data);
  }
}
