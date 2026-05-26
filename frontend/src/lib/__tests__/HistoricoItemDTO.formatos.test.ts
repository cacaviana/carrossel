// Testes unitarios - HistoricoItemDTO x 3 formatos (PostUnico, Reels, Thumbnail)
// Complementa HistoricoItemDTO.test.ts estendendo parametrizacao aos novos formatos.
// Valida: o DTO e polimorfico — aceita post_unico, capa_reels, thumbnail_youtube.

import { describe, it, expect } from 'vitest';
import { HistoricoItemDTO } from '../dtos/HistoricoItemDTO';

const FORMATOS: Array<[string, number]> = [
  ['post_unico', 1],
  ['capa_reels', 1],
  ['thumbnail_youtube', 1],
];

describe('HistoricoItemDTO — 3 formatos (PostUnico, Reels, Thumbnail)', () => {
  describe.each(FORMATOS)('formato=%s', (formato, total_slides) => {
    it('guarda formato e total_slides', () => {
      const dto = new HistoricoItemDTO({
        id: 1, pipeline_id: 'p1', titulo: `Item ${formato}`,
        formato, total_slides,
      });
      expect(dto.formato).toBe(formato);
      expect(dto.total_slides).toBe(total_slides);
    });

    it('isValid() aceita DTO valido para o formato', () => {
      const dto = new HistoricoItemDTO({
        id: 1, titulo: `x ${formato}`, formato,
      });
      expect(dto.isValid()).toBe(true);
    });

    it('isValid() rejeita DTO sem titulo', () => {
      const dto = new HistoricoItemDTO({ id: 1, formato });
      expect(dto.isValid()).toBe(false);
    });

    it('toPayload() contem o formato', () => {
      const dto = new HistoricoItemDTO({
        id: 1, pipeline_id: 'p1', titulo: 'x', formato, status: 'completo',
      });
      const payload = dto.toPayload();
      expect(payload.formato).toBe(formato);
      expect(payload.id).toBe(1);
      expect(payload.pipeline_id).toBe('p1');
      expect(payload.status).toBe('completo');
    });

    it('temScore false quando score nao vem do backend', () => {
      const dto = new HistoricoItemDTO({ id: 1, titulo: 'x', formato });
      expect(dto.temScore).toBe(false);
    });

    it('temDriveLink true quando drive_link preenchido', () => {
      const dto = new HistoricoItemDTO({
        id: 1, titulo: 'x', formato,
        google_drive_link: `https://drive.google.com/x-${formato}`,
      });
      expect(dto.temDriveLink).toBe(true);
    });
  });

  // Cenario adicional: uma lista mista retornada por GET /api/historico
  describe('lista mista (Listar PostsUnicos, CapasReels, Thumbnails)', () => {
    it('cria N items com formatos diferentes sem colisao de estado', () => {
      const raw = [
        { id: 1, titulo: 'Post 1', formato: 'post_unico', total_slides: 1 },
        { id: 2, titulo: 'Reels 1', formato: 'capa_reels', total_slides: 1 },
        { id: 3, titulo: 'Thumb 1', formato: 'thumbnail_youtube', total_slides: 1 },
      ];
      const dtos = raw.map((d) => new HistoricoItemDTO(d));
      expect(dtos.map((x) => x.formato)).toEqual([
        'post_unico', 'capa_reels', 'thumbnail_youtube',
      ]);
      expect(dtos.every((x) => x.isValid())).toBe(true);
    });
  });
});
