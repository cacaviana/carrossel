// Testes unitarios - CreatorEntryDTO
// Cobre casos de uso: Adicionar Creator, Listar Creators, Remover Creator, Salvar Creators Lote
// Escopo do DTO: constructor + defaults, funcaoLabel, isValid, toPayload.

import { describe, it, expect } from 'vitest';
import { CreatorEntryDTO, type FuncaoCriador } from '../dtos/CreatorEntryDTO';

describe('CreatorEntryDTO', () => {
  const valido = {
    id: 'c1',
    nome: 'Carlos Viana',
    funcao: 'THOUGHT_LEADER' as FuncaoCriador,
    plataforma: 'linkedin',
    url: 'https://linkedin.com/in/c',
    ativo: true,
  };

  // ---- Constructor ----
  describe('constructor', () => {
    it('cria com todos os campos', () => {
      const c = new CreatorEntryDTO(valido);
      expect(c.id).toBe('c1');
      expect(c.nome).toBe('Carlos Viana');
      expect(c.funcao).toBe('THOUGHT_LEADER');
      expect(c.plataforma).toBe('linkedin');
      expect(c.url).toBe('https://linkedin.com/in/c');
      expect(c.ativo).toBe(true);
    });

    it('aplica defaults quando campos faltam', () => {
      const c = new CreatorEntryDTO({});
      expect(c.id).toBe('');
      expect(c.nome).toBe('');
      expect(c.funcao).toBe('TECH_SOURCE');
      expect(c.plataforma).toBe('');
      expect(c.url).toBe('');
      expect(c.ativo).toBe(true);
    });

    it('ativo default true mesmo quando passado como false explicitamente nao muda', () => {
      const c = new CreatorEntryDTO({ nome: 'X', funcao: 'EXPLAINER', plataforma: 'yt', ativo: false });
      expect(c.ativo).toBe(false);
    });
  });

  // ---- funcaoLabel (Listar Creators exibe o rotulo amigavel) ----
  describe('funcaoLabel', () => {
    it.each([
      ['TECH_SOURCE', 'Tech Source'],
      ['EXPLAINER', 'Explainer'],
      ['VIRAL_ENGINE', 'Viral Engine'],
      ['THOUGHT_LEADER', 'Thought Leader'],
      ['DINAMICA', 'Dinamica'],
    ] as const)('converte %s -> "%s"', (funcao, esperado) => {
      const c = new CreatorEntryDTO({ funcao });
      expect(c.funcaoLabel).toBe(esperado);
    });

    it('fallback retorna a propria funcao se nao conhecida', () => {
      const c = new CreatorEntryDTO({ funcao: 'ALGO_INESPERADO' as any });
      expect(c.funcaoLabel).toBe('ALGO_INESPERADO');
    });
  });

  // ---- isValid (Adicionar Creator requer campos minimos) ----
  describe('isValid', () => {
    it('true quando nome e plataforma preenchidos', () => {
      const c = new CreatorEntryDTO({ nome: 'X', plataforma: 'yt' });
      expect(c.isValid()).toBe(true);
    });

    it('false quando nome vazio', () => {
      expect(new CreatorEntryDTO({ nome: '', plataforma: 'yt' }).isValid()).toBe(false);
    });

    it('false quando nome so espacos', () => {
      expect(new CreatorEntryDTO({ nome: '   ', plataforma: 'yt' }).isValid()).toBe(false);
    });

    it('false quando plataforma vazia', () => {
      expect(new CreatorEntryDTO({ nome: 'X', plataforma: '' }).isValid()).toBe(false);
    });

    it('false quando plataforma so espacos', () => {
      expect(new CreatorEntryDTO({ nome: 'X', plataforma: '   ' }).isValid()).toBe(false);
    });

    it('true mesmo sem url (url eh opcional)', () => {
      const c = new CreatorEntryDTO({ nome: 'X', plataforma: 'yt', url: '' });
      expect(c.isValid()).toBe(true);
    });
  });

  // ---- toPayload (Salvar Creators Lote serializa para API) ----
  describe('toPayload', () => {
    it('retorna todos os campos esperados pelo backend', () => {
      const c = new CreatorEntryDTO(valido);
      const p = c.toPayload();
      expect(Object.keys(p).sort()).toEqual(['ativo', 'funcao', 'id', 'nome', 'plataforma', 'url']);
    });

    it('preserva valores', () => {
      const c = new CreatorEntryDTO(valido);
      const p = c.toPayload();
      expect(p.nome).toBe('Carlos Viana');
      expect(p.ativo).toBe(true);
      expect(p.funcao).toBe('THOUGHT_LEADER');
    });

    it('serializa creator com defaults', () => {
      const c = new CreatorEntryDTO({});
      const p = c.toPayload();
      expect(p.nome).toBe('');
      expect(p.ativo).toBe(true);
      expect(p.funcao).toBe('TECH_SOURCE');
    });
  });

  // ---- Cenario: Salvar Creators Lote ----
  describe('lote (Salvar Creators Lote)', () => {
    it('mapea lista inteira via toPayload', () => {
      const lista = [
        new CreatorEntryDTO({ nome: 'A', funcao: 'TECH_SOURCE', plataforma: 'yt' }),
        new CreatorEntryDTO({ nome: 'B', funcao: 'EXPLAINER', plataforma: 'tw' }),
        new CreatorEntryDTO({ nome: 'C', funcao: 'VIRAL_ENGINE', plataforma: 'ig' }),
      ];
      const payload = { criadores: lista.map((c) => c.toPayload()) };
      expect(payload.criadores.length).toBe(3);
      expect(payload.criadores[1].nome).toBe('B');
    });

    it('todos isValid antes de salvar (Service deve chamar isValid)', () => {
      const lista = [
        new CreatorEntryDTO({ nome: 'A', funcao: 'TECH_SOURCE', plataforma: 'yt' }),
        new CreatorEntryDTO({ nome: 'B', funcao: 'EXPLAINER', plataforma: 'tw' }),
      ];
      expect(lista.every((c) => c.isValid())).toBe(true);
    });

    it('detecta item invalido dentro do lote', () => {
      const lista = [
        new CreatorEntryDTO({ nome: 'A', funcao: 'TECH_SOURCE', plataforma: 'yt' }),
        new CreatorEntryDTO({ nome: '', funcao: 'EXPLAINER', plataforma: 'tw' }),
      ];
      expect(lista.some((c) => !c.isValid())).toBe(true);
    });
  });

  // ---- Cenario: Remover Creator ----
  describe('remover creator (filtra lote sem ele)', () => {
    it('filtra por id exclui o creator escolhido', () => {
      const lista = [
        new CreatorEntryDTO({ id: 'a', nome: 'A', funcao: 'TECH_SOURCE', plataforma: 'yt' }),
        new CreatorEntryDTO({ id: 'b', nome: 'B', funcao: 'EXPLAINER', plataforma: 'tw' }),
        new CreatorEntryDTO({ id: 'c', nome: 'C', funcao: 'VIRAL_ENGINE', plataforma: 'ig' }),
      ];
      const depois = lista.filter((c) => c.id !== 'b');
      expect(depois.map((c) => c.id)).toEqual(['a', 'c']);
    });
  });
});
