// Testes unitarios - utils/date.ts

import { describe, it, expect, vi, afterEach } from 'vitest';
import { formatRelativeDate, formatAbsoluteDate } from '../utils/date';

describe('formatRelativeDate', () => {
  afterEach(() => {
    vi.useRealTimers();
  });

  it('retorna string vazia para input vazio', () => {
    expect(formatRelativeDate('')).toBe('');
  });

  it('retorna "agora" para menos de 1 min atras', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-06-15T12:00:30Z'));
    expect(formatRelativeDate('2026-06-15T12:00:00Z')).toBe('agora');
  });

  it('retorna minutos', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-06-15T12:05:00Z'));
    expect(formatRelativeDate('2026-06-15T12:00:00Z')).toBe('ha 5 min');
  });

  it('retorna horas', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-06-15T15:00:00Z'));
    expect(formatRelativeDate('2026-06-15T12:00:00Z')).toBe('ha 3h');
  });

  it('retorna dias (singular)', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-06-16T12:00:00Z'));
    expect(formatRelativeDate('2026-06-15T12:00:00Z')).toBe('ha 1 dia');
  });

  it('retorna dias (plural)', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-06-18T12:00:00Z'));
    expect(formatRelativeDate('2026-06-15T12:00:00Z')).toBe('ha 3 dias');
  });

  it('retorna semanas', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-06-29T12:00:00Z'));
    expect(formatRelativeDate('2026-06-15T12:00:00Z')).toBe('ha 2 sem');
  });

  it('retorna data formatada para > 30 dias', () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2026-08-15T12:00:00Z'));
    const result = formatRelativeDate('2026-06-15T12:00:00Z');
    // Deve retornar data pt-BR
    expect(result).toMatch(/\d{2}\/\d{2}\/\d{4}/);
  });
});

describe('formatAbsoluteDate', () => {
  it('retorna string vazia para input vazio', () => {
    expect(formatAbsoluteDate('')).toBe('');
  });

  it('retorna data formatada pt-BR com hora', () => {
    const result = formatAbsoluteDate('2026-01-15T14:30:00Z');
    // Deve conter dia, mes, ano
    expect(result).toMatch(/15/);
    expect(result).toMatch(/01/);
    expect(result).toMatch(/2026/);
  });
});
