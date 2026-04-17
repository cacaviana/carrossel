// Testes unitarios - AgenteDTO
// Cobre casos de uso: Obter Prompt Agente, Listar Skills (via Listar Agentes)
// Escopo do DTO: constructor + defaults, isLLM/isSkill, isValid, toPayload.

import { describe, it, expect } from 'vitest';
import { AgenteDTO, type TipoAgente } from '../dtos/AgenteDTO';

describe('AgenteDTO', () => {
  const agenteLLM = {
    slug: 'strategist',
    nome: 'Strategist',
    descricao: 'Gera briefing',
    tipo: 'llm' as TipoAgente,
    conteudo: '# System prompt\nVoce e um strategist...',
  };

  const skill = {
    slug: 'brand_overlay',
    nome: 'Brand Overlay',
    descricao: 'Aplica foto + logo via Pillow',
    tipo: 'skill' as TipoAgente,
    conteudo: 'Aplica foto + logo via Pillow',
  };

  // ---- Constructor ----
  describe('constructor', () => {
    it('cria agente LLM com campos completos', () => {
      const a = new AgenteDTO(agenteLLM);
      expect(a.slug).toBe('strategist');
      expect(a.nome).toBe('Strategist');
      expect(a.tipo).toBe('llm');
      expect(a.conteudo).toContain('System prompt');
    });

    it('cria skill com tipo skill', () => {
      const s = new AgenteDTO(skill);
      expect(s.tipo).toBe('skill');
    });

    it('aplica defaults quando campos faltam', () => {
      const a = new AgenteDTO({});
      expect(a.slug).toBe('');
      expect(a.nome).toBe('');
      expect(a.descricao).toBe('');
      expect(a.tipo).toBe('llm');
      expect(a.conteudo).toBe('');
    });
  });

  // ---- isLLM / isSkill ----
  describe('isLLM / isSkill', () => {
    it('isLLM true para tipo llm', () => {
      const a = new AgenteDTO(agenteLLM);
      expect(a.isLLM).toBe(true);
      expect(a.isSkill).toBe(false);
    });

    it('isSkill true para tipo skill', () => {
      const s = new AgenteDTO(skill);
      expect(s.isSkill).toBe(true);
      expect(s.isLLM).toBe(false);
    });

    it('default tipo llm considera como LLM', () => {
      const a = new AgenteDTO({});
      expect(a.isLLM).toBe(true);
    });
  });

  // ---- isValid (Obter Prompt Agente precisa slug + nome) ----
  describe('isValid', () => {
    it('true quando slug e nome preenchidos', () => {
      const a = new AgenteDTO({ slug: 'x', nome: 'X' });
      expect(a.isValid()).toBe(true);
    });

    it('false quando slug vazio', () => {
      const a = new AgenteDTO({ slug: '', nome: 'X' });
      expect(a.isValid()).toBe(false);
    });

    it('false quando nome vazio', () => {
      const a = new AgenteDTO({ slug: 'x', nome: '' });
      expect(a.isValid()).toBe(false);
    });
  });

  // ---- toPayload ----
  describe('toPayload', () => {
    it('retorna todos os campos esperados', () => {
      const a = new AgenteDTO(agenteLLM);
      const p = a.toPayload();
      expect(Object.keys(p).sort()).toEqual(['conteudo', 'descricao', 'nome', 'slug', 'tipo']);
    });

    it('preserva conteudo do prompt', () => {
      const a = new AgenteDTO(agenteLLM);
      const p = a.toPayload();
      expect(p.conteudo).toBe(agenteLLM.conteudo);
    });
  });

  // ---- Cenario: Listar Agentes/Skills separadamente ----
  describe('cenario: Listar Skills', () => {
    it('filtra skills a partir da lista', () => {
      const lista = [
        new AgenteDTO({ slug: 'strategist', nome: 'S', tipo: 'llm' }),
        new AgenteDTO({ slug: 'brand_overlay', nome: 'BO', tipo: 'skill' }),
        new AgenteDTO({ slug: 'trend_scanner', nome: 'TS', tipo: 'skill' }),
      ];
      const skills = lista.filter((x) => x.isSkill);
      expect(skills.map((s) => s.slug).sort()).toEqual(['brand_overlay', 'trend_scanner']);
    });

    it('filtra LLMs a partir da lista', () => {
      const lista = [
        new AgenteDTO({ slug: 'strategist', nome: 'S', tipo: 'llm' }),
        new AgenteDTO({ slug: 'copywriter', nome: 'C', tipo: 'llm' }),
        new AgenteDTO({ slug: 'brand_overlay', nome: 'BO', tipo: 'skill' }),
      ];
      const llms = lista.filter((x) => x.isLLM);
      expect(llms.length).toBe(2);
    });
  });

  // ---- Cenario: Obter Prompt Agente ----
  describe('cenario: Obter Prompt Agente', () => {
    it('conteudo eh usado como system prompt', () => {
      const a = new AgenteDTO({
        slug: 's', nome: 'S', tipo: 'llm',
        conteudo: '# Strategist\nSeu trabalho...',
      });
      expect(a.isValid()).toBe(true);
      expect(a.conteudo.startsWith('# Strategist')).toBe(true);
    });
  });
});
