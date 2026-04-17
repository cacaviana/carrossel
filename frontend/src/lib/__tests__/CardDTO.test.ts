// Testes unitarios - CardDTO
// Cobre: constructor, isValid, toPayload, getters derivados (isOverdue, isDueSoon, deadlineLabel, etc)

import { describe, it, expect, vi, afterEach } from 'vitest';
import { CardDTO } from '../dtos/CardDTO';

describe('CardDTO', () => {
  // ---- Constructor ----
  describe('constructor', () => {
    it('cria com todos os campos', () => {
      const card = new CardDTO({
        id: 'c1', tenant_id: 't1', board_id: 'b1', column_id: 'col1',
        title: 'Meu Card', priority: 'alta', formato: 'post_unico',
        assigned_user_ids: ['u1'], deadline: '2026-12-31',
      });
      expect(card.id).toBe('c1');
      expect(card.priority).toBe('alta');
      expect(card.formato).toBe('post_unico');
      expect(card.assigned_user_ids).toEqual(['u1']);
      expect(card.deadline).toBe('2026-12-31');
    });

    it('aplica defaults quando campos faltam', () => {
      const card = new CardDTO({});
      expect(card.id).toBe('');
      expect(card.priority).toBe('media');
      expect(card.formato).toBe('carrossel');
      expect(card.assigned_user_ids).toEqual([]);
      expect(card.image_urls).toEqual([]);
      expect(card.order_in_column).toBe(0);
      expect(card.comment_count).toBe(0);
    });

    it('aceita _id como fallback para id', () => {
      const card = new CardDTO({ _id: 'mongo-id' });
      expect(card.id).toBe('mongo-id');
    });
  });

  // ---- isValid ----
  describe('isValid', () => {
    it('true quando id, title>=3, board_id preenchidos', () => {
      const card = new CardDTO({ id: 'c1', title: 'Abc', board_id: 'b1' });
      expect(card.isValid()).toBe(true);
    });

    it('false quando id vazio', () => {
      const card = new CardDTO({ title: 'Abc', board_id: 'b1' });
      expect(card.isValid()).toBe(false);
    });

    it('false quando title < 3 chars', () => {
      const card = new CardDTO({ id: 'c1', title: 'Ab', board_id: 'b1' });
      expect(card.isValid()).toBe(false);
    });

    it('false quando board_id vazio', () => {
      const card = new CardDTO({ id: 'c1', title: 'Abc' });
      expect(card.isValid()).toBe(false);
    });
  });

  // ---- toPayload ----
  describe('toPayload', () => {
    it('retorna so os campos esperados', () => {
      const card = new CardDTO({ id: 'c1', board_id: 'b1', title: 'Test', tenant_id: 't1' });
      const payload = card.toPayload();
      expect(payload.id).toBe('c1');
      expect(payload.board_id).toBe('b1');
      expect(payload.title).toBe('Test');
      // campos nao incluidos no payload
      expect(payload).not.toHaveProperty('tenant_id');
      expect(payload).not.toHaveProperty('created_at');
      expect(payload).not.toHaveProperty('updated_at');
      expect(payload).not.toHaveProperty('archived_at');
      expect(payload).not.toHaveProperty('order_in_column');
      expect(payload).not.toHaveProperty('comment_count');
      expect(payload).not.toHaveProperty('created_by');
    });
  });

  // ---- Getters derivados ----
  describe('getters booleanos', () => {
    it('isArchived: true quando archived_at preenchido', () => {
      expect(new CardDTO({ archived_at: '2025-01-01' }).isArchived).toBe(true);
      expect(new CardDTO({}).isArchived).toBe(false);
    });

    it('hasDriveLink, hasPdf, hasImages, hasPipeline', () => {
      const full = new CardDTO({
        drive_link: 'http://x', pdf_url: 'http://pdf',
        image_urls: ['img1'], pipeline_id: 'p1',
      });
      expect(full.hasDriveLink).toBe(true);
      expect(full.hasPdf).toBe(true);
      expect(full.hasImages).toBe(true);
      expect(full.hasPipeline).toBe(true);

      const empty = new CardDTO({});
      expect(empty.hasDriveLink).toBe(false);
      expect(empty.hasPdf).toBe(false);
      expect(empty.hasImages).toBe(false);
      expect(empty.hasPipeline).toBe(false);
    });
  });

  describe('deadline getters', () => {
    afterEach(() => {
      vi.useRealTimers();
    });

    it('hasDeadline: false quando vazio', () => {
      expect(new CardDTO({}).hasDeadline).toBe(false);
    });

    it('hasDeadline: true quando preenchido', () => {
      expect(new CardDTO({ deadline: '2026-12-31' }).hasDeadline).toBe(true);
    });

    it('isOverdue: true quando deadline no passado', () => {
      vi.useFakeTimers();
      vi.setSystemTime(new Date('2026-06-15T12:00:00Z'));
      const card = new CardDTO({ deadline: '2026-06-14' });
      expect(card.isOverdue).toBe(true);
      vi.useRealTimers();
    });

    it('isOverdue: false quando deadline no futuro', () => {
      vi.useFakeTimers();
      vi.setSystemTime(new Date('2026-06-15T12:00:00Z'));
      const card = new CardDTO({ deadline: '2026-06-20' });
      expect(card.isOverdue).toBe(false);
      vi.useRealTimers();
    });

    it('isOverdue: false quando sem deadline', () => {
      expect(new CardDTO({}).isOverdue).toBe(false);
    });

    it('isDueSoon: true quando falta menos de 2 dias', () => {
      vi.useFakeTimers();
      vi.setSystemTime(new Date('2026-06-15T12:00:00Z'));
      const card = new CardDTO({ deadline: '2026-06-16T12:00:00Z' });
      expect(card.isDueSoon).toBe(true);
      vi.useRealTimers();
    });

    it('isDueSoon: false quando falta mais de 2 dias', () => {
      vi.useFakeTimers();
      vi.setSystemTime(new Date('2026-06-15T12:00:00Z'));
      const card = new CardDTO({ deadline: '2026-06-20' });
      expect(card.isDueSoon).toBe(false);
      vi.useRealTimers();
    });

    it('isDueSoon: false quando ja esta overdue', () => {
      vi.useFakeTimers();
      vi.setSystemTime(new Date('2026-06-15T12:00:00Z'));
      const card = new CardDTO({ deadline: '2026-06-10' });
      expect(card.isDueSoon).toBe(false);
      vi.useRealTimers();
    });

    it('deadlineLabel formata dd/mm', () => {
      const card = new CardDTO({ deadline: '2026-06-15T12:00:00Z' });
      const label = card.deadlineLabel;
      // Deve ser formato dd/mm (2 digitos cada)
      expect(label).toMatch(/\d{2}\/\d{2}/);
      expect(label).toMatch(/06/);
    });

    it('deadlineLabel vazio sem deadline', () => {
      expect(new CardDTO({}).deadlineLabel).toBe('');
    });
  });

  describe('priorityLabel', () => {
    it('retorna label correto', () => {
      expect(new CardDTO({ priority: 'alta' }).priorityLabel).toBe('Alta');
      expect(new CardDTO({ priority: 'media' }).priorityLabel).toBe('Media');
      expect(new CardDTO({ priority: 'baixa' }).priorityLabel).toBe('Baixa');
    });
  });

  describe('tituloTruncado', () => {
    it('nao trunca titulo curto', () => {
      expect(new CardDTO({ title: 'Curto' }).tituloTruncado).toBe('Curto');
    });

    it('trunca titulo longo com ...', () => {
      const long = 'A'.repeat(60);
      const card = new CardDTO({ title: long });
      expect(card.tituloTruncado.length).toBe(50);
      expect(card.tituloTruncado.endsWith('...')).toBe(true);
    });
  });
});
