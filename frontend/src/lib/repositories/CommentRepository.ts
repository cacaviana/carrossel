// src/lib/repositories/CommentRepository.ts

import { CommentDTO } from '$lib/dtos/CommentDTO';
import { API_BASE } from '$lib/api';
import { getToken } from '$lib/stores/auth.svelte';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

let mockCommentsState: any[] | null = null;

async function getMockComments() {
  if (!mockCommentsState) {
    const { commentsMock } = await import('$lib/mocks/kanban/comments.mock');
    mockCommentsState = [...commentsMock];
  }
  return mockCommentsState;
}

export class CommentRepository {
  static async listarPorCard(cardId: string): Promise<CommentDTO[]> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 250));
      const comments = await getMockComments();
      return comments
        .filter(c => c.card_id === cardId && !c.deleted_at)
        .map(c => new CommentDTO(c));
    }

    const res = await fetch(`${API_BASE}/api/kanban/cards/${cardId}/comments`, {
      headers: authHeaders()
    });
    return (await res.json()).map((c: any) => new CommentDTO(c));
  }

  static async criar(cardId: string, text: string): Promise<CommentDTO> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      const comments = await getMockComments();
      const newComment = {
        id: `cmt-${Date.now()}`,
        tenant_id: 'tenant-itvalley',
        card_id: cardId,
        user_id: 'usr-001',
        user_name: 'Poliana Cardoso',
        user_avatar_url: '',
        text,
        created_at: new Date().toISOString(),
        updated_at: '',
        deleted_at: ''
      };
      comments.push(newComment);
      return new CommentDTO(newComment);
    }

    const res = await fetch(`${API_BASE}/api/kanban/cards/${cardId}/comments`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ text })
    });
    return new CommentDTO(await res.json());
  }

  static async deletar(commentId: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      const comments = await getMockComments();
      const comment = comments.find(c => c.id === commentId);
      if (comment) comment.deleted_at = new Date().toISOString();
      return;
    }

    await fetch(`${API_BASE}/api/kanban/comments/${commentId}`, {
      method: 'DELETE',
      headers: authHeaders()
    });
  }
}
