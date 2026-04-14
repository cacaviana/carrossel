// src/lib/stores/kanban.ts
// Estado do board + cards + filtros

import type { BoardDTO } from '$lib/dtos/BoardDTO';
import type { CardDTO } from '$lib/dtos/CardDTO';
import type { UserDTO } from '$lib/dtos/UserDTO';

// Board
let board = $state<BoardDTO | null>(null);
let cards = $state<CardDTO[]>([]);
let users = $state<UserDTO[]>([]);

// Filtros
let searchQuery = $state('');
let filterResponsavel = $state('');
let filterPrioridade = $state('');
let filterColuna = $state('');

// Loading / erro
let loading = $state(false);
let erro = $state('');

export function getBoard() { return board; }
export function setBoard(b: BoardDTO) { board = b; }

export function getCards() { return cards; }
export function setCards(c: CardDTO[]) { cards = c; }

export function getUsers() { return users; }
export function setUsers(u: UserDTO[]) { users = u; }

export function getSearchQuery() { return searchQuery; }
export function setSearchQuery(q: string) { searchQuery = q; }

export function getFilterResponsavel() { return filterResponsavel; }
export function setFilterResponsavel(r: string) { filterResponsavel = r; }

export function getFilterPrioridade() { return filterPrioridade; }
export function setFilterPrioridade(p: string) { filterPrioridade = p; }

export function getFilterColuna() { return filterColuna; }
export function setFilterColuna(c: string) { filterColuna = c; }

export function getLoading() { return loading; }
export function setLoading(l: boolean) { loading = l; }

export function getErro() { return erro; }
export function setErro(e: string) { erro = e; }

export function clearFilters() {
  searchQuery = '';
  filterResponsavel = '';
  filterPrioridade = '';
  filterColuna = '';
}

export function hasActiveFilters(): boolean {
  return searchQuery.length > 0 || filterResponsavel.length > 0 || filterPrioridade.length > 0 || filterColuna.length > 0;
}

export function getFilteredCards(): CardDTO[] {
  let filtered = cards;

  if (searchQuery) {
    const q = searchQuery.toLowerCase();
    filtered = filtered.filter(c => c.title.toLowerCase().includes(q));
  }

  if (filterResponsavel) {
    filtered = filtered.filter(c => c.assigned_user_ids.includes(filterResponsavel));
  }

  if (filterPrioridade) {
    filtered = filtered.filter(c => c.priority === filterPrioridade);
  }

  if (filterColuna) {
    filtered = filtered.filter(c => c.column_id === filterColuna);
  }

  return filtered;
}

export function getCardsByColumn(columnId: string): CardDTO[] {
  return getFilteredCards()
    .filter(c => c.column_id === columnId)
    .sort((a, b) => a.order_in_column - b.order_in_column);
}
