// src/lib/mocks/kanban/board.mock.ts
// Board padrao com 6 colunas fixas do MVP

export const boardMock = {
  id: 'board-001',
  tenant_id: 'tenant-itvalley',
  name: 'Pipeline de Carrosseis',
  columns: [
    { id: 'col-copy', name: 'Copy', order: 1, color: '#3B82F6' },
    { id: 'col-design', name: 'Diretor de Arte', order: 2, color: '#8B5CF6' },
    { id: 'col-aprovado', name: 'Aprovado', order: 3, color: '#10B981' },
    { id: 'col-publicado', name: 'Publicado', order: 4, color: '#06B6D4' },
    { id: 'col-cancelado', name: 'Cancelado', order: 5, color: '#EF4444' }
  ],
  created_at: '2025-11-10T14:00:00Z'
};
