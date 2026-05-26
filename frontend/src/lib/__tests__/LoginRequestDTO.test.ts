// Testes unitarios - LoginRequestDTO
// Cobre: RN-021 senha forte, emailValido, isValid, toPayload, errosSenha

import { describe, it, expect } from 'vitest';
import { LoginRequestDTO } from '../dtos/LoginRequestDTO';

describe('LoginRequestDTO', () => {
  describe('constructor', () => {
    it('cria com campos validos', () => {
      const dto = new LoginRequestDTO({ email: 'a@b.com', password: 'Abc123!@' });
      expect(dto.email).toBe('a@b.com');
      expect(dto.password).toBe('Abc123!@');
    });

    it('defaults para string vazia', () => {
      const dto = new LoginRequestDTO({});
      expect(dto.email).toBe('');
      expect(dto.password).toBe('');
    });
  });

  describe('emailValido', () => {
    it('true para email valido', () => {
      expect(new LoginRequestDTO({ email: 'user@test.com' }).emailValido).toBe(true);
    });

    it('false para email invalido', () => {
      expect(new LoginRequestDTO({ email: 'nao-email' }).emailValido).toBe(false);
      expect(new LoginRequestDTO({ email: '' }).emailValido).toBe(false);
      expect(new LoginRequestDTO({ email: '@test.com' }).emailValido).toBe(false);
    });
  });

  describe('senhaForte (RN-021)', () => {
    it('true para senha que atende todos os criterios', () => {
      expect(new LoginRequestDTO({ password: 'Abc123!@' }).senhaForte).toBe(true);
    });

    it('false para senha curta (<8)', () => {
      expect(new LoginRequestDTO({ password: 'Ab1!' }).senhaForte).toBe(false);
    });

    it('false para senha sem maiuscula', () => {
      expect(new LoginRequestDTO({ password: 'abc12345!' }).senhaForte).toBe(false);
    });

    it('false para senha sem numero', () => {
      expect(new LoginRequestDTO({ password: 'Abcdefgh!' }).senhaForte).toBe(false);
    });

    it('false para senha sem caractere especial', () => {
      expect(new LoginRequestDTO({ password: 'Abcdefg1' }).senhaForte).toBe(false);
    });
  });

  describe('errosSenha', () => {
    it('retorna array vazio para senha forte', () => {
      expect(new LoginRequestDTO({ password: 'Abc123!@' }).errosSenha).toEqual([]);
    });

    it('retorna todos os erros para senha vazia', () => {
      const erros = new LoginRequestDTO({ password: '' }).errosSenha;
      expect(erros.length).toBe(4);
    });

    it('retorna erro especifico para falta de maiuscula', () => {
      const erros = new LoginRequestDTO({ password: 'abc12345!' }).errosSenha;
      expect(erros).toContain('1 letra maiuscula');
    });
  });

  describe('isValid', () => {
    it('true quando email valido E senha forte', () => {
      const dto = new LoginRequestDTO({ email: 'a@b.com', password: 'Abc123!@' });
      expect(dto.isValid()).toBe(true);
    });

    it('false quando email invalido', () => {
      const dto = new LoginRequestDTO({ email: 'invalido', password: 'Abc123!@' });
      expect(dto.isValid()).toBe(false);
    });

    it('false quando senha fraca', () => {
      const dto = new LoginRequestDTO({ email: 'a@b.com', password: 'fraca' });
      expect(dto.isValid()).toBe(false);
    });
  });

  describe('toPayload', () => {
    it('retorna email e password', () => {
      const dto = new LoginRequestDTO({ email: 'a@b.com', password: 'Abc123!@' });
      const p = dto.toPayload();
      expect(p).toEqual({ email: 'a@b.com', password: 'Abc123!@' });
    });
  });
});
