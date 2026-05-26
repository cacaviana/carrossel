// src/lib/repositories/CardRepository.ts

import { CardDTO } from '$lib/dtos/CardDTO';
import { API_BASE } from '$lib/api';
import { getToken } from '$lib/stores/auth.svelte';

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

// Estado local para mock — permite adicionar e mover cards em memoria
let mockCardsState: any[] | null = null;

async function getMockCards() {
  if (!mockCardsState) {
    const { cardsMock } = await import('$lib/mocks/kanban/cards.mock');
    mockCardsState = [...cardsMock];
  }
  return mockCardsState;
}

export class CardRepository {
  static async listar(): Promise<CardDTO[]> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      const cards = await getMockCards();
      return cards.map(c => new CardDTO(c));
    }

    const res = await fetch(`${API_BASE}/api/kanban/cards`, {
      headers: authHeaders()
    });
    return (await res.json()).map((c: any) => new CardDTO(c));
  }

  static async buscarPorId(id: string): Promise<CardDTO | null> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      const cards = await getMockCards();
      const found = cards.find(c => c.id === id);
      return found ? new CardDTO(found) : null;
    }

    const res = await fetch(`${API_BASE}/api/kanban/cards/${id}`, {
      headers: authHeaders()
    });
    if (!res.ok) return null;
    return new CardDTO(await res.json());
  }

  static async criar(payload: Record<string, any>): Promise<CardDTO> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 400));
      const cards = await getMockCards();
      const newCard = {
        ...payload,
        id: `card-${Date.now()}`,
        tenant_id: 'tenant-itvalley',
        board_id: 'board-001',
        column_id: 'col-copy',
        created_by: 'usr-001',
        pipeline_id: '',
        drive_link: '',
        drive_folder_name: '',
        pdf_url: '',
        image_urls: [],
        order_in_column: cards.filter(c => c.column_id === 'col-copy').length + 1,
        comment_count: 0,
        created_at: new Date().toISOString(),
        updated_at: '',
        archived_at: ''
      };
      cards.unshift(newCard);
      return new CardDTO(newCard);
    }

    const res = await fetch(`${API_BASE}/api/kanban/cards`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    return new CardDTO(await res.json());
  }

  static async moverParaCancelado(cardId: string, canceladoColumnId: string): Promise<CardDTO> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      const cards = await getMockCards();
      const card = cards.find(c => c.id === cardId);
      if (card) {
        card.column_id = canceladoColumnId;
        card.updated_at = new Date().toISOString();
      }
      return new CardDTO(card ?? {});
    }

    const res = await fetch(`${API_BASE}/api/kanban/cards/${cardId}/move`, {
      method: 'PATCH',
      headers: authHeaders(),
      body: JSON.stringify({ column_id: canceladoColumnId })
    });
    return new CardDTO(await res.json());
  }
}
