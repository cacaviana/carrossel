// src/lib/mocks/kanban/notifications.mock.ts
// Notificacoes falsas realistas para o usuario logado (Poliana)

export const notificationsMock = [
  {
    id: 'ntf-001',
    tenant_id: 'tenant-itvalley',
    user_id: 'usr-001',
    card_id: 'card-005',
    type: 'column_changed' as const,
    message: 'Card "Data Drift: Como Detectar e Corrigir" moveu para Aprovado',
    is_read: false,
    created_at: '2026-04-13T09:00:00Z'
  },
  {
    id: 'ntf-002',
    tenant_id: 'tenant-itvalley',
    user_id: 'usr-001',
    card_id: 'card-001',
    type: 'assigned' as const,
    message: 'Ana Beatriz atribuiu voce ao card "5 Erros Fatais em Feature Engineering"',
    is_read: false,
    created_at: '2026-04-10T14:00:00Z'
  },
  {
    id: 'ntf-003',
    tenant_id: 'tenant-itvalley',
    user_id: 'usr-001',
    card_id: 'card-007',
    type: 'column_changed' as const,
    message: 'Card "XGBoost vs Random Forest" moveu para Aprovado',
    is_read: false,
    created_at: '2026-04-10T15:00:00Z'
  },
  {
    id: 'ntf-004',
    tenant_id: 'tenant-itvalley',
    user_id: 'usr-001',
    card_id: 'card-003',
    type: 'column_changed' as const,
    message: 'Card "Transfer Learning na Pratica com PyTorch" moveu para Diretor de Arte',
    is_read: true,
    created_at: '2026-04-09T16:00:00Z'
  },
  {
    id: 'ntf-005',
    tenant_id: 'tenant-itvalley',
    user_id: 'usr-001',
    card_id: 'card-008',
    type: 'column_changed' as const,
    message: 'Card "LangChain Agents: Guia Definitivo" moveu para Publicado',
    is_read: true,
    created_at: '2026-04-01T12:00:00Z'
  },
  {
    id: 'ntf-006',
    tenant_id: 'tenant-itvalley',
    user_id: 'usr-001',
    card_id: 'card-002',
    type: 'assigned' as const,
    message: 'Voce foi atribuido ao card "RAG vs Fine-Tuning: Qual Escolher?"',
    is_read: true,
    created_at: '2026-04-11T11:05:00Z'
  }
];
