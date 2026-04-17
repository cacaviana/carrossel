// Testes unitarios - CriarUsuarioDTO
// Cobre: validacao nome, email, senha forte (RN-021), isValid, toPayload

import { describe, it, expect } from 'vitest';
import { CriarUsuarioDTO } from '../dtos/CriarUsuarioDTO';

describe('CriarUsuarioDTO', () => {
  const valid = { name: 'Test User', email: 'a@b.com', password: 'Abc123!@', role: 'admin' };

  describe('constructor', () => {
    it('cria com campos completos', () => {
      const dto = new CriarUsuarioDTO(valid);
      expect(dto.name).toBe('Test User');
      expect(dto.role).toBe('admin');
    });

    it('default role viewer', () => {
      const dto = new CriarUsuarioDTO({ name: 'A', email: 'a@b.c', password: 'X' });
      expect(dto.role).toBe('viewer');
    });
  });

  describe('nomeValido', () => {
    it('true para nome >= 2 chars', () => {
      expect(new CriarUsuarioDTO({ name: 'Ab' }).nomeValido).toBe(true);
    });

    it('false para nome curto ou espacos', () => {
      expect(new CriarUsuarioDTO({ name: 'A' }).nomeValido).toBe(false);
      expect(new CriarUsuarioDTO({ name: '  ' }).nomeValido).toBe(false);
    });
  });

  describe('emailValido', () => {
    it('true para email valido', () => {
      expect(new CriarUsuarioDTO({ email: 'user@test.com' }).emailValido).toBe(true);
    });

    it('false para email invalido', () => {
      expect(new CriarUsuarioDTO({ email: 'nao' }).emailValido).toBe(false);
    });
  });

  describe('senhaForte (RN-021)', () => {
    it('true para senha forte', () => {
      expect(new CriarUsuarioDTO({ password: 'Abc123!@' }).senhaForte).toBe(true);
    });

    it('false para senha fraca', () => {
      expect(new CriarUsuarioDTO({ password: 'abc' }).senhaForte).toBe(false);
    });
  });

  describe('errosSenha', () => {
    it('vazio para senha forte', () => {
      expect(new CriarUsuarioDTO({ password: 'Abc123!@' }).errosSenha).toEqual([]);
    });

    it('lista erros especificos', () => {
      const erros = new CriarUsuarioDTO({ password: 'abcdefgh' }).errosSenha;
      expect(erros).toContain('1 letra maiuscula');
      expect(erros).toContain('1 numero');
      expect(erros).toContain('1 caractere especial');
    });
  });

  describe('isValid', () => {
    it('true quando nome, email e senha validos', () => {
      expect(new CriarUsuarioDTO(valid).isValid()).toBe(true);
    });

    it('false quando nome invalido', () => {
      expect(new CriarUsuarioDTO({ ...valid, name: 'A' }).isValid()).toBe(false);
    });

    it('false quando email invalido', () => {
      expect(new CriarUsuarioDTO({ ...valid, email: 'nao' }).isValid()).toBe(false);
    });

    it('false quando senha fraca', () => {
      expect(new CriarUsuarioDTO({ ...valid, password: 'fraca' }).isValid()).toBe(false);
    });
  });

  describe('toPayload', () => {
    it('retorna name, email, password, role', () => {
      const p = new CriarUsuarioDTO(valid).toPayload();
      expect(Object.keys(p).sort()).toEqual(['email', 'name', 'password', 'role']);
    });
  });
});
