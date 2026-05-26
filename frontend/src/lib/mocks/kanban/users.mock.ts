// src/lib/mocks/kanban/users.mock.ts
// Dados falsos realistas de usuarios do sistema Kanban

export const usersMock = [
  {
    id: 'usr-001',
    tenant_id: 'tenant-itvalley',
    email: 'poliana@itvalley.com.br',
    name: 'Poliana Cardoso',
    avatar_url: '',
    role: 'admin' as const,
    created_at: '2025-11-10T14:00:00Z',
    deleted_at: ''
  },
  {
    id: 'usr-002',
    tenant_id: 'tenant-itvalley',
    email: 'joao@itvalley.com.br',
    name: 'João Mendes',
    avatar_url: '',
    role: 'designer' as const,
    created_at: '2025-12-01T09:00:00Z',
    deleted_at: ''
  },
  {
    id: 'usr-003',
    tenant_id: 'tenant-itvalley',
    email: 'ana@itvalley.com.br',
    name: 'Ana Beatriz Silva',
    avatar_url: '',
    role: 'copywriter' as const,
    created_at: '2025-12-15T10:30:00Z',
    deleted_at: ''
  },
  {
    id: 'usr-004',
    tenant_id: 'tenant-itvalley',
    email: 'carlos@itvalley.com.br',
    name: 'Carlos Viana',
    avatar_url: '',
    role: 'reviewer' as const,
    created_at: '2026-01-05T08:00:00Z',
    deleted_at: ''
  },
  {
    id: 'usr-005',
    tenant_id: 'tenant-itvalley',
    email: 'maria@itvalley.com.br',
    name: 'Maria Fernanda Costa',
    avatar_url: '',
    role: 'viewer' as const,
    created_at: '2026-02-20T16:00:00Z',
    deleted_at: ''
  }
];

export const authMock = {
  token: 'mock-jwt-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9',
  user_id: 'usr-001',
  tenant_id: 'tenant-itvalley',
  email: 'poliana@itvalley.com.br',
  name: 'Poliana Cardoso',
  avatar_url: '',
  role: 'admin' as const
};

export function loginMock(email: string, password: string) {
  if (password !== 'Admin@123') {
    return { success: false, error: 'Email ou senha incorretos. Verifique e tente novamente.' };
  }

  const user = usersMock.find(u => u.email === email);
  const match = user ?? usersMock[0];

  return {
    success: true,
    data: {
      token: 'mock-jwt-eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9',
      user_id: match.id,
      tenant_id: match.tenant_id,
      email: match.email,
      name: match.name,
      avatar_url: match.avatar_url,
      role: match.role
    }
  };
}
