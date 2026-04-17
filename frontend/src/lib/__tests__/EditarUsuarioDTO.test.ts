// Testes unitarios - EditarUsuarioDTO

import { describe, it, expect } from 'vitest';
import { EditarUsuarioDTO } from '../dtos/EditarUsuarioDTO';

describe('EditarUsuarioDTO', () => {
  describe('constructor', () => {
    it('cria com campos', () => {
      const dto = new EditarUsuarioDTO({ user_id: 'u1', name: 'Novo', role: 'admin', avatar_url: 'http://img' });
      expect(dto.user_id).toBe('u1');
      expect(dto.name).toBe('Novo');
    });

    it('defaults', () => {
      const dto = new EditarUsuarioDTO({});
      expect(dto.user_id).toBe('');
      expect(dto.role).toBe('viewer');
      expect(dto.avatar_url).toBe('');
    });
  });

  describe('nomeValido', () => {
    it('true para nome >= 2', () => {
      expect(new EditarUsuarioDTO({ name: 'Ab' }).nomeValido).toBe(true);
    });

    it('false para nome curto', () => {
      expect(new EditarUsuarioDTO({ name: 'A' }).nomeValido).toBe(false);
    });
  });

  describe('getUserId', () => {
    it('retorna user_id', () => {
      expect(new EditarUsuarioDTO({ user_id: 'x1' }).getUserId()).toBe('x1');
    });
  });

  describe('isValid', () => {
    it('true quando user_id e nome validos', () => {
      expect(new EditarUsuarioDTO({ user_id: 'u1', name: 'Ab' }).isValid()).toBe(true);
    });

    it('false quando user_id vazio', () => {
      expect(new EditarUsuarioDTO({ name: 'Ab' }).isValid()).toBe(false);
    });

    it('false quando nome invalido', () => {
      expect(new EditarUsuarioDTO({ user_id: 'u1', name: 'A' }).isValid()).toBe(false);
    });
  });

  describe('toPayload', () => {
    it('retorna name, role, avatar_url (sem user_id)', () => {
      const p = new EditarUsuarioDTO({ user_id: 'u1', name: 'N', role: 'admin' }).toPayload();
      expect(p).toHaveProperty('name');
      expect(p).toHaveProperty('role');
      expect(p).toHaveProperty('avatar_url');
      expect(p).not.toHaveProperty('user_id');
    });
  });
});
