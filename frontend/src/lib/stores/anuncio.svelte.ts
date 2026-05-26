// src/lib/stores/anuncio.svelte.ts
// Estado reativo: filtros da lista + regeneracao em andamento (por anuncio_id).
//
// Pos-pivot (2026-04-23): regeneracao e por IMAGEM INTEIRA (nao mais por dimensao).
// Guardamos apenas um Set de anuncio_ids em processo de regeneracao.

import { ListarAnunciosFiltroDTO } from '$lib/dtos/ListarAnunciosFiltroDTO';

let filtro = $state(new ListarAnunciosFiltroDTO({}));
let imagensRegenerando = $state<Set<string>>(new Set());

export function getFiltro(): ListarAnunciosFiltroDTO {
  return filtro;
}

export function setFiltro(novo: ListarAnunciosFiltroDTO): void {
  filtro = novo;
}

export function resetFiltros(): void {
  filtro = new ListarAnunciosFiltroDTO({});
}

export function marcarImagemRegenerando(anuncioId: string): void {
  const novo = new Set(imagensRegenerando);
  novo.add(anuncioId);
  imagensRegenerando = novo;
}

export function marcarImagemRegenerada(anuncioId: string): void {
  if (!imagensRegenerando.has(anuncioId)) return;
  const novo = new Set(imagensRegenerando);
  novo.delete(anuncioId);
  imagensRegenerando = novo;
}

export function estaRegerandoImagem(anuncioId: string): boolean {
  return imagensRegenerando.has(anuncioId);
}
