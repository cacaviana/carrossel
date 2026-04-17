// Testes unitarios - CriarCardDTO

import { describe, it, expect } from 'vitest';
import { CriarCardDTO } from '../dtos/CriarCardDTO';

describe('CriarCardDTO', () => {
  describe('constructor', () => {
    it('cria com todos os campos', () => {
      const dto = new CriarCardDTO({
        title: 'Meu Card', copy_text: 'texto', disciplina: 'D1',
        tecnologia: 'Python', priority: 'alta', assigned_user_ids: ['u1'],
        deadline: '2026-12-31',
      });
      expect(dto.title).toBe('Meu Card');
      expect(dto.priority).toBe('alta');
      expect(dto.deadline).toBe('2026-12-31');
    });

    it('aplica defaults e trim no titulo', () => {
      const dto = new CriarCardDTO({ title: '  abc  ' });
      expect(dto.title).toBe('abc');
      expect(dto.priority).toBe('media');
      expect(dto.assigned_user_ids).toEqual([]);
    });
  });

  describe('isValid', () => {
    it('true quando titulo >= 3 chars', () => {
      expect(new CriarCardDTO({ title: 'Abc' }).isValid()).toBe(true);
    });

    it('false quando titulo < 3 chars', () => {
      expect(new CriarCardDTO({ title: 'Ab' }).isValid()).toBe(false);
    });

    it('false quando titulo vazio (apos trim)', () => {
      expect(new CriarCardDTO({ title: '  ' }).isValid()).toBe(false);
    });
  });

  describe('toPayload', () => {
    it('retorna campos esperados', () => {
      const dto = new CriarCardDTO({ title: 'Test', priority: 'baixa' });
      const p = dto.toPayload();
      expect(p.title).toBe('Test');
      expect(p.priority).toBe('baixa');
      expect(p).toHaveProperty('copy_text');
      expect(p).toHaveProperty('deadline');
      expect(p).toHaveProperty('assigned_user_ids');
    });
  });
});
