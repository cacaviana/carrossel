// src/lib/mocks/kanban/comments.mock.ts
// Comentarios contextuais e realistas por card

export const commentsMock = [
  // card-001: Feature Engineering
  {
    id: 'cmt-001',
    tenant_id: 'tenant-itvalley',
    card_id: 'card-001',
    user_id: 'usr-003',
    user_name: 'Ana Beatriz Silva',
    user_avatar_url: '',
    text: 'Rascunho do copy pronto. Foquei nos erros mais comuns que vejo em projetos reais: leakage, encoding errado, e falta de normalizacao.',
    created_at: '2026-04-10T10:00:00Z',
    updated_at: '',
    deleted_at: ''
  },
  {
    id: 'cmt-002',
    tenant_id: 'tenant-itvalley',
    card_id: 'card-001',
    user_id: 'usr-001',
    user_name: 'Poliana Cardoso',
    user_avatar_url: '',
    text: 'Ficou otimo! Sugiro adicionar um slide sobre multicolinearidade, e um erro que muita gente ignora.',
    created_at: '2026-04-10T14:30:00Z',
    updated_at: '',
    deleted_at: ''
  },
  // card-003: Transfer Learning
  {
    id: 'cmt-003',
    tenant_id: 'tenant-itvalley',
    card_id: 'card-003',
    user_id: 'usr-002',
    user_name: 'João Mendes',
    user_avatar_url: '',
    text: 'Gerando as imagens agora. Vou usar o estilo dark mode premium com destaque em gradiente azul/roxo pro codigo.',
    created_at: '2026-04-12T10:30:00Z',
    updated_at: '',
    deleted_at: ''
  },
  {
    id: 'cmt-004',
    tenant_id: 'tenant-itvalley',
    card_id: 'card-003',
    user_id: 'usr-003',
    user_name: 'Ana Beatriz Silva',
    user_avatar_url: '',
    text: 'O slide 3 com o diagrama de camadas ficou confuso. Pode simplificar? Talvez usar setas ao inves de caixas sobrepostas.',
    created_at: '2026-04-12T11:15:00Z',
    updated_at: '',
    deleted_at: ''
  },
  {
    id: 'cmt-005',
    tenant_id: 'tenant-itvalley',
    card_id: 'card-003',
    user_id: 'usr-002',
    user_name: 'João Mendes',
    user_avatar_url: '',
    text: 'Feito! Simplifiquei o diagrama. Da uma olhada na versao nova.',
    created_at: '2026-04-12T14:00:00Z',
    updated_at: '',
    deleted_at: ''
  },
  // card-005: Data Drift
  {
    id: 'cmt-006',
    tenant_id: 'tenant-itvalley',
    card_id: 'card-005',
    user_id: 'usr-004',
    user_name: 'Carlos Viana',
    user_avatar_url: '',
    text: 'Revisando o conteudo. O slide sobre PSI (Population Stability Index) precisa de mais contexto pra quem nao conhece.',
    created_at: '2026-04-13T09:00:00Z',
    updated_at: '',
    deleted_at: ''
  },
  {
    id: 'cmt-007',
    tenant_id: 'tenant-itvalley',
    card_id: 'card-005',
    user_id: 'usr-003',
    user_name: 'Ana Beatriz Silva',
    user_avatar_url: '',
    text: 'Adicionei uma explicacao curta no slide 4. Veja se ficou claro agora.',
    created_at: '2026-04-13T10:30:00Z',
    updated_at: '',
    deleted_at: ''
  },
  {
    id: 'cmt-008',
    tenant_id: 'tenant-itvalley',
    card_id: 'card-005',
    user_id: 'usr-004',
    user_name: 'Carlos Viana',
    user_avatar_url: '',
    text: 'Melhor! Mas o CTA final ta fraco. Algo como "Implemente monitoramento ANTES de perder dinheiro" seria mais impactante.',
    created_at: '2026-04-13T11:00:00Z',
    updated_at: '',
    deleted_at: ''
  },
  {
    id: 'cmt-009',
    tenant_id: 'tenant-itvalley',
    card_id: 'card-005',
    user_id: 'usr-001',
    user_name: 'Poliana Cardoso',
    user_avatar_url: '',
    text: 'Concordo com o Carlos. CTA precisa de urgencia. Ajusta e manda pra aprovacao.',
    created_at: '2026-04-13T11:30:00Z',
    updated_at: '',
    deleted_at: ''
  },
  {
    id: 'cmt-010',
    tenant_id: 'tenant-itvalley',
    card_id: 'card-005',
    user_id: 'usr-003',
    user_name: 'Ana Beatriz Silva',
    user_avatar_url: '',
    text: 'Pronto, CTA atualizado. Ficou: "Seu modelo esta degradando agora. Implemente monitoramento antes que custe caro."',
    created_at: '2026-04-13T14:00:00Z',
    updated_at: '',
    deleted_at: ''
  },
  // card-010: Cancelado
  {
    id: 'cmt-011',
    tenant_id: 'tenant-itvalley',
    card_id: 'card-010',
    user_id: 'usr-001',
    user_name: 'Poliana Cardoso',
    user_avatar_url: '',
    text: 'Cancelando este card. Ja cobrimos Apache NiFi no carrossel de ETL do mes passado.',
    created_at: '2026-03-12T11:00:00Z',
    updated_at: '',
    deleted_at: ''
  }
];
