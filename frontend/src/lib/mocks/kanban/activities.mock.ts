// src/lib/mocks/kanban/activities.mock.ts
// Timeline de atividades realistas por card

export const activitiesMock = [
  // card-001
  { id: 'act-001', tenant_id: 'tenant-itvalley', card_id: 'card-001', user_id: 'usr-003', user_name: 'Ana Beatriz Silva', action: 'card_created' as const, metadata: {}, created_at: '2026-04-10T09:30:00Z' },
  { id: 'act-002', tenant_id: 'tenant-itvalley', card_id: 'card-001', user_id: 'usr-003', user_name: 'Ana Beatriz Silva', action: 'comment_added' as const, metadata: {}, created_at: '2026-04-10T10:00:00Z' },
  { id: 'act-003', tenant_id: 'tenant-itvalley', card_id: 'card-001', user_id: 'usr-001', user_name: 'Poliana Cardoso', action: 'comment_added' as const, metadata: {}, created_at: '2026-04-10T14:30:00Z' },

  // card-002
  { id: 'act-004', tenant_id: 'tenant-itvalley', card_id: 'card-002', user_id: 'usr-001', user_name: 'Poliana Cardoso', action: 'card_created' as const, metadata: {}, created_at: '2026-04-11T11:00:00Z' },

  // card-003
  { id: 'act-005', tenant_id: 'tenant-itvalley', card_id: 'card-003', user_id: 'usr-003', user_name: 'Ana Beatriz Silva', action: 'card_created' as const, metadata: {}, created_at: '2026-04-08T15:00:00Z' },
  { id: 'act-006', tenant_id: 'tenant-itvalley', card_id: 'card-003', user_id: 'usr-003', user_name: 'Sistema', action: 'column_changed' as const, metadata: { from_column: 'Copy', to_column: 'Diretor de Arte' }, created_at: '2026-04-09T16:00:00Z' },
  { id: 'act-007', tenant_id: 'tenant-itvalley', card_id: 'card-003', user_id: 'usr-001', user_name: 'Poliana Cardoso', action: 'assignee_changed' as const, metadata: { added: 'João Mendes' }, created_at: '2026-04-09T16:05:00Z' },
  { id: 'act-008', tenant_id: 'tenant-itvalley', card_id: 'card-003', user_id: 'usr-002', user_name: 'João Mendes', action: 'image_generated' as const, metadata: {}, created_at: '2026-04-12T10:30:00Z' },

  // card-005
  { id: 'act-009', tenant_id: 'tenant-itvalley', card_id: 'card-005', user_id: 'usr-003', user_name: 'Ana Beatriz Silva', action: 'card_created' as const, metadata: {}, created_at: '2026-04-05T10:00:00Z' },
  { id: 'act-010', tenant_id: 'tenant-itvalley', card_id: 'card-005', user_id: 'usr-003', user_name: 'Sistema', action: 'column_changed' as const, metadata: { from_column: 'Copy', to_column: 'Diretor de Arte' }, created_at: '2026-04-06T09:00:00Z' },
  { id: 'act-011', tenant_id: 'tenant-itvalley', card_id: 'card-005', user_id: 'usr-002', user_name: 'João Mendes', action: 'image_generated' as const, metadata: {}, created_at: '2026-04-07T14:00:00Z' },
  { id: 'act-012', tenant_id: 'tenant-itvalley', card_id: 'card-005', user_id: 'usr-002', user_name: 'Sistema', action: 'column_changed' as const, metadata: { from_column: 'Diretor de Arte', to_column: 'Aprovado' }, created_at: '2026-04-08T10:00:00Z' },
  { id: 'act-013', tenant_id: 'tenant-itvalley', card_id: 'card-005', user_id: 'usr-003', user_name: 'Sistema', action: 'pdf_exported' as const, metadata: {}, created_at: '2026-04-08T10:05:00Z' },
  { id: 'act-014', tenant_id: 'tenant-itvalley', card_id: 'card-005', user_id: 'usr-004', user_name: 'Carlos Viana', action: 'comment_added' as const, metadata: {}, created_at: '2026-04-13T09:00:00Z' },
  { id: 'act-015', tenant_id: 'tenant-itvalley', card_id: 'card-005', user_id: 'usr-003', user_name: 'Ana Beatriz Silva', action: 'field_edited' as const, metadata: { field_name: 'copy_text' }, created_at: '2026-04-13T14:00:00Z' },

  // card-007
  { id: 'act-016', tenant_id: 'tenant-itvalley', card_id: 'card-007', user_id: 'usr-003', user_name: 'Ana Beatriz Silva', action: 'card_created' as const, metadata: {}, created_at: '2026-03-28T11:00:00Z' },
  { id: 'act-017', tenant_id: 'tenant-itvalley', card_id: 'card-007', user_id: 'usr-003', user_name: 'Sistema', action: 'column_changed' as const, metadata: { from_column: 'Copy', to_column: 'Diretor de Arte' }, created_at: '2026-03-29T09:00:00Z' },
  { id: 'act-018', tenant_id: 'tenant-itvalley', card_id: 'card-007', user_id: 'usr-002', user_name: 'Sistema', action: 'column_changed' as const, metadata: { from_column: 'Diretor de Arte', to_column: 'Aprovado' }, created_at: '2026-04-02T10:00:00Z' },
  { id: 'act-019', tenant_id: 'tenant-itvalley', card_id: 'card-007', user_id: 'usr-004', user_name: 'Carlos Viana', action: 'column_changed' as const, metadata: { from_column: 'Diretor de Arte', to_column: 'Aprovado' }, created_at: '2026-04-10T15:00:00Z' },

  // card-008
  { id: 'act-020', tenant_id: 'tenant-itvalley', card_id: 'card-008', user_id: 'usr-001', user_name: 'Poliana Cardoso', action: 'card_created' as const, metadata: {}, created_at: '2026-03-20T09:00:00Z' },
  { id: 'act-021', tenant_id: 'tenant-itvalley', card_id: 'card-008', user_id: 'usr-001', user_name: 'Sistema', action: 'column_changed' as const, metadata: { from_column: 'Copy', to_column: 'Diretor de Arte' }, created_at: '2026-03-21T10:00:00Z' },
  { id: 'act-022', tenant_id: 'tenant-itvalley', card_id: 'card-008', user_id: 'usr-002', user_name: 'Sistema', action: 'column_changed' as const, metadata: { from_column: 'Diretor de Arte', to_column: 'Aprovado' }, created_at: '2026-03-25T14:00:00Z' },
  { id: 'act-023', tenant_id: 'tenant-itvalley', card_id: 'card-008', user_id: 'usr-004', user_name: 'Carlos Viana', action: 'column_changed' as const, metadata: { from_column: 'Diretor de Arte', to_column: 'Aprovado' }, created_at: '2026-03-28T09:00:00Z' },
  { id: 'act-024', tenant_id: 'tenant-itvalley', card_id: 'card-008', user_id: 'usr-001', user_name: 'Sistema', action: 'column_changed' as const, metadata: { from_column: 'Aprovado', to_column: 'Publicado' }, created_at: '2026-04-01T12:00:00Z' },
  { id: 'act-025', tenant_id: 'tenant-itvalley', card_id: 'card-008', user_id: 'usr-001', user_name: 'Poliana Cardoso', action: 'drive_linked' as const, metadata: { drive_folder: 'LangChain Agents - 2026-04-01' }, created_at: '2026-04-01T12:05:00Z' },

  // card-010
  { id: 'act-026', tenant_id: 'tenant-itvalley', card_id: 'card-010', user_id: 'usr-003', user_name: 'Ana Beatriz Silva', action: 'card_created' as const, metadata: {}, created_at: '2026-03-10T10:00:00Z' },
  { id: 'act-027', tenant_id: 'tenant-itvalley', card_id: 'card-010', user_id: 'usr-001', user_name: 'Poliana Cardoso', action: 'column_changed' as const, metadata: { from_column: 'Copy', to_column: 'Cancelado' }, created_at: '2026-03-12T11:00:00Z' },
];
