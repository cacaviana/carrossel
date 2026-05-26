// Testes unitarios - BrandPaletteDTO
// Cobre: constructor com defaults, isValid (regex hex), toPayload, getter cores
// Caso de uso: Atualizar Paleta Cores + Fontes (dominio Marca)

import { describe, it, expect } from 'vitest';
import { BrandPaletteDTO } from '../dtos/BrandPaletteDTO';

describe('BrandPaletteDTO', () => {
  describe('constructor', () => {
    it('cria com campos completos', () => {
      const dto = new BrandPaletteDTO({
        cores: {
          fundo_principal: '#000000',
          destaque_primario: '#A78BFA',
          destaque_secundario: '#6D28D9',
          texto_principal: '#FFFFFF',
          texto_secundario: '#94A3B8',
        },
        fonte: 'Inter',
        elementos_obrigatorios: ['foto', 'logo'],
        estilo: 'minimal',
      });
      expect(dto.fonte).toBe('Inter');
      expect(dto.elementos_obrigatorios).toEqual(['foto', 'logo']);
      expect(dto.estilo).toBe('minimal');
    });

    it('aplica defaults dark mode quando nada passado', () => {
      const dto = new BrandPaletteDTO({});
      expect(dto.fundo_principal).toBe('#0A0A0F');
      expect(dto.destaque_primario).toBe('#A78BFA');
      expect(dto.destaque_secundario).toBe('#6D28D9');
      expect(dto.texto_principal).toBe('#FFFFFF');
      expect(dto.texto_secundario).toBe('#94A3B8');
      expect(dto.fonte).toBe('Outfit');
      expect(dto.estilo).toBe('dark_mode_premium');
      expect(dto.elementos_obrigatorios).toEqual([]);
    });

    it('aceita payload sem envelope cores (flat)', () => {
      const dto = new BrandPaletteDTO({
        fundo_principal: '#FFFFFF',
        destaque_primario: '#FF0000',
        destaque_secundario: '#0000FF',
        texto_principal: '#000000',
        texto_secundario: '#666666',
        fonte: 'Roboto',
        estilo: 'light',
      });
      expect(dto.fundo_principal).toBe('#FFFFFF');
      expect(dto.fonte).toBe('Roboto');
    });
  });

  describe('cores getter', () => {
    it('retorna lista de 5 cores com label/chave/valor', () => {
      const dto = new BrandPaletteDTO({});
      expect(dto.cores).toHaveLength(5);
      expect(dto.cores[0]).toHaveProperty('label');
      expect(dto.cores[0]).toHaveProperty('chave');
      expect(dto.cores[0]).toHaveProperty('valor');
      expect(dto.cores.map((c) => c.chave)).toEqual([
        'fundo_principal',
        'destaque_primario',
        'destaque_secundario',
        'texto_principal',
        'texto_secundario',
      ]);
    });
  });

  describe('isValid', () => {
    it('true para hex 6 digitos + fonte preenchida', () => {
      const dto = new BrandPaletteDTO({});
      expect(dto.isValid()).toBe(true);
    });

    it('false para hex invalido (3 digitos)', () => {
      const dto = new BrandPaletteDTO({
        fundo_principal: '#000',
        destaque_primario: '#A78BFA',
        destaque_secundario: '#6D28D9',
        texto_principal: '#FFFFFF',
        texto_secundario: '#94A3B8',
      });
      expect(dto.isValid()).toBe(false);
    });

    it('false para hex sem hash', () => {
      const dto = new BrandPaletteDTO({
        fundo_principal: '000000',
        destaque_primario: '#A78BFA',
        destaque_secundario: '#6D28D9',
        texto_principal: '#FFFFFF',
        texto_secundario: '#94A3B8',
      });
      expect(dto.isValid()).toBe(false);
    });

    it('false para cor com caractere invalido', () => {
      const dto = new BrandPaletteDTO({
        fundo_principal: '#ZZZZZZ',
        destaque_primario: '#A78BFA',
        destaque_secundario: '#6D28D9',
        texto_principal: '#FFFFFF',
        texto_secundario: '#94A3B8',
      });
      expect(dto.isValid()).toBe(false);
    });

    it('false para fonte vazia', () => {
      const dto = new BrandPaletteDTO({ fonte: '   ' });
      expect(dto.isValid()).toBe(false);
    });

    it('aceita hex minusculo e maiusculo', () => {
      const dto = new BrandPaletteDTO({
        fundo_principal: '#aabbcc',
        destaque_primario: '#A78BFA',
        destaque_secundario: '#6D28D9',
        texto_principal: '#ffffff',
        texto_secundario: '#94a3b8',
      });
      expect(dto.isValid()).toBe(true);
    });
  });

  describe('toPayload', () => {
    it('retorna payload no formato esperado pelo backend', () => {
      const dto = new BrandPaletteDTO({
        fonte: 'Outfit',
        elementos_obrigatorios: ['foto'],
        estilo: 'dark_mode_premium',
      });
      const p = dto.toPayload();
      expect(p).toHaveProperty('cores');
      expect(p).toHaveProperty('fonte', 'Outfit');
      expect(p).toHaveProperty('elementos_obrigatorios', ['foto']);
      expect(p).toHaveProperty('estilo', 'dark_mode_premium');
      expect(p.cores).toHaveProperty('fundo_principal');
      expect(p.cores).toHaveProperty('destaque_primario');
      expect(p.cores).toHaveProperty('texto_secundario');
    });

    it('cores no payload espelham os defaults do DTO', () => {
      const dto = new BrandPaletteDTO({});
      const { cores } = dto.toPayload();
      expect(cores.fundo_principal).toBe('#0A0A0F');
      expect(cores.destaque_primario).toBe('#A78BFA');
    });

    it('nao expoe campos privados alem dos 4 principais', () => {
      const dto = new BrandPaletteDTO({});
      const p = dto.toPayload();
      expect(Object.keys(p).sort()).toEqual(
        ['cores', 'elementos_obrigatorios', 'estilo', 'fonte'].sort()
      );
    });
  });
});
