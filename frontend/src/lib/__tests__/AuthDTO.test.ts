// Testes unitarios - AuthDTO
// Cobre: constructor, getters ACL, isValid, toPayload

import { describe, it, expect } from 'vitest';
import { AuthDTO } from '../dtos/AuthDTO';

describe('AuthDTO', () => {
  describe('constructor', () => {
    it('cria com campos validos', () => {
      const dto = new AuthDTO({
        token: 'jwt-tok', user_id: 'u1', tenant_id: 't1',
        email: 'a@b.com', name: 'Carlos Viana', role: 'admin',
      });
      expect(dto.token).toBe('jwt-tok');
      expect(dto.role).toBe('admin');
    });

    it('defaults para viewer e strings vazias', () => {
      const dto = new AuthDTO({});
      expect(dto.role).toBe('viewer');
      expect(dto.token).toBe('');
      expect(dto.avatar_url).toBe('');
    });
  });

  describe('iniciais', () => {
    it('retorna iniciais do nome', () => {
      expect(new AuthDTO({ name: 'Carlos Viana' }).iniciais).toBe('CV');
    });

    it('retorna 1 letra para nome simples', () => {
      expect(new AuthDTO({ name: 'Admin' }).iniciais).toBe('A');
    });

    it('maximo 2 iniciais', () => {
      expect(new AuthDTO({ name: 'Jose Carlos Viana' }).iniciais).toBe('JC');
    });
  });

  describe('getters ACL', () => {
    it('admin: isAdmin true, canEdit true, canComment true, canCreateCard true, canManageUsers true', () => {
      const admin = new AuthDTO({ role: 'admin' });
      expect(admin.isAdmin).toBe(true);
      expect(admin.canEdit).toBe(true);
      expect(admin.canComment).toBe(true);
      expect(admin.canCreateCard).toBe(true);
      expect(admin.canManageUsers).toBe(true);
    });

    it('viewer: tudo false exceto canEdit/canComment que sao false', () => {
      const viewer = new AuthDTO({ role: 'viewer' });
      expect(viewer.isAdmin).toBe(false);
      expect(viewer.canEdit).toBe(false);
      expect(viewer.canComment).toBe(false);
      expect(viewer.canCreateCard).toBe(false);
      expect(viewer.canManageUsers).toBe(false);
    });

    it('copywriter: canCreateCard true', () => {
      const cw = new AuthDTO({ role: 'copywriter' });
      expect(cw.canCreateCard).toBe(true);
      expect(cw.canEdit).toBe(true);
      expect(cw.canManageUsers).toBe(false);
    });

    it('designer: canEdit true, canCreateCard false', () => {
      const d = new AuthDTO({ role: 'designer' });
      expect(d.canEdit).toBe(true);
      expect(d.canCreateCard).toBe(false);
    });
  });

  describe('roleLabel', () => {
    it('retorna labels corretos', () => {
      expect(new AuthDTO({ role: 'admin' }).roleLabel).toBe('Admin');
      expect(new AuthDTO({ role: 'copywriter' }).roleLabel).toBe('Copywriter');
      expect(new AuthDTO({ role: 'designer' }).roleLabel).toBe('Designer');
      expect(new AuthDTO({ role: 'reviewer' }).roleLabel).toBe('Reviewer');
      expect(new AuthDTO({ role: 'viewer' }).roleLabel).toBe('Viewer');
    });
  });

  describe('isValid', () => {
    it('true quando token, user_id e email preenchidos', () => {
      const dto = new AuthDTO({ token: 'tok', user_id: 'u1', email: 'a@b.c' });
      expect(dto.isValid()).toBe(true);
    });

    it('false quando token vazio', () => {
      expect(new AuthDTO({ user_id: 'u1', email: 'a@b.c' }).isValid()).toBe(false);
    });
  });

  describe('toPayload', () => {
    it('retorna campos esperados sem avatar_url', () => {
      const dto = new AuthDTO({ token: 'tok', user_id: 'u1', tenant_id: 't1', email: 'a@b.c', name: 'N', role: 'admin' });
      const p = dto.toPayload();
      expect(p).toHaveProperty('token');
      expect(p).toHaveProperty('role');
      expect(p).not.toHaveProperty('avatar_url');
    });
  });
});
