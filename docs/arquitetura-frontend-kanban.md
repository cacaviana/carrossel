# Arquitetura Frontend — Kanban Pipeline

Documento gerado pelo Agente 04 (Arquiteto IT Valley Frontend).
Base: PRD Kanban Pipeline + Documento de Telas + Estrutura existente do frontend SvelteKit.

---

## 1. Dominios Identificados

| Dominio | Casos de Uso | DTOs |
|---------|-------------|------|
| **Auth** | Login, LoginSSO, Logout, GetUsuarioLogado | AuthDTO, LoginRequestDTO |
| **Board** | CarregarBoard, FiltrarCards | BoardDTO |
| **Card** | ListarCards, CriarCard, EditarCard, MoverParaCancelado, BuscarCard | CardDTO, CriarCardDTO, EditarCardDTO |
| **Comment** | ListarComentarios, CriarComentario, EditarComentario, DeletarComentario | CommentDTO, CriarComentarioDTO |
| **Activity** | ListarAtividades | ActivityDTO |
| **Notification** | ListarNotificacoes, MarcarComoLida, MarcarTodasComoLidas | NotificationDTO |
| **User** | ListarUsuarios, CriarUsuario, EditarUsuario, DesativarUsuario, ReativarUsuario | UserDTO, CriarUsuarioDTO, EditarUsuarioDTO |

---

## 2. Estrutura de Pastas

```
src/lib/
├── components/
│   ├── ui/                          # Ja existentes (Button, Badge, Modal, etc.)
│   ├── kanban/                      # Dominio Kanban (board + cards)
│   │   ├── KanbanBoard.svelte       # Board com 6 colunas
│   │   ├── KanbanColumn.svelte      # 1 coluna com lista de cards
│   │   ├── KanbanCard.svelte        # Card compacto no board
│   │   ├── KanbanFilters.svelte     # Barra de filtros
│   │   ├── CardDetailModal.svelte   # Modal de detalhe (3 abas)
│   │   ├── CardDetailTab.svelte     # Aba Detalhes
│   │   ├── CardCommentsTab.svelte   # Aba Comentarios
│   │   ├── CardActivityTab.svelte   # Aba Atividade
│   │   ├── CardCreateModal.svelte   # Modal de criacao de card
│   │   └── CommentItem.svelte       # 1 comentario na lista
│   ├── auth/                        # Dominio Autenticacao
│   │   ├── LoginForm.svelte         # Formulario email+senha
│   │   └── SSOButtons.svelte        # Botoes Google + Microsoft
│   ├── notification/                # Dominio Notificacoes
│   │   ├── NotificationBell.svelte  # Icone sino + badge
│   │   └── NotificationDropdown.svelte # Dropdown com lista
│   ├── user/                        # Dominio Usuarios
│   │   ├── UserTable.svelte         # Tabela de usuarios
│   │   └── UserFormModal.svelte     # Modal criar/editar usuario
│   └── layout/
│       └── Sidebar.svelte           # Existente (sera alterado)
│
├── dtos/
│   ├── AuthDTO.ts
│   ├── LoginRequestDTO.ts
│   ├── BoardDTO.ts
│   ├── CardDTO.ts
│   ├── CriarCardDTO.ts
│   ├── EditarCardDTO.ts
│   ├── CommentDTO.ts
│   ├── CriarComentarioDTO.ts
│   ├── ActivityDTO.ts
│   ├── NotificationDTO.ts
│   ├── UserDTO.ts
│   ├── CriarUsuarioDTO.ts
│   └── EditarUsuarioDTO.ts
│
├── services/
│   ├── AuthService.ts
│   ├── BoardService.ts
│   ├── CardService.ts
│   ├── CommentService.ts
│   ├── ActivityService.ts
│   ├── NotificationService.ts
│   └── UserService.ts
│
├── repositories/
│   ├── AuthRepository.ts
│   ├── BoardRepository.ts
│   ├── CardRepository.ts
│   ├── CommentRepository.ts
│   ├── ActivityRepository.ts
│   ├── NotificationRepository.ts
│   └── UserRepository.ts
│
├── mocks/
│   ├── auth.mock.ts
│   ├── board.mock.ts
│   ├── cards.mock.ts
│   ├── comments.mock.ts
│   ├── activities.mock.ts
│   ├── notifications.mock.ts
│   └── users.mock.ts
│
├── stores/
│   ├── auth.ts                      # Estado do usuario logado + JWT
│   ├── board.ts                     # Estado do board + cards + filtros
│   └── notifications.ts            # Contador de nao-lidas
│
└── utils/
    └── date.ts                      # formatRelativeDate() — "ha 2 dias"

src/routes/
├── login/
│   └── +page.svelte                 # Tela de Login
├── kanban/
│   ├── +page.svelte                 # Board Kanban
│   └── usuarios/
│       └── +page.svelte             # Gerenciamento de Usuarios (Admin)
└── +layout.svelte                   # Alterado: auth guard + notification bell
```

---

## 3. Rotas

| Rota | Arquivo | Autenticacao | Perfil minimo |
|------|---------|-------------|---------------|
| `/login` | `routes/login/+page.svelte` | Publica | -- |
| `/kanban` | `routes/kanban/+page.svelte` | JWT obrigatorio | Qualquer |
| `/kanban/usuarios` | `routes/kanban/usuarios/+page.svelte` | JWT obrigatorio | Admin |

### Auth Guard

Implementado no `+layout.svelte` raiz. Logica:
1. Se nao existe token no localStorage e rota !== `/login` → redirect `/login`
2. Se existe token e rota === `/login` → redirect `/`
3. Se rota `/kanban/usuarios` e role !== `admin` → redirect `/kanban`

---

## 4. DTOs — Codigo Completo

### AuthDTO.ts

```typescript
// src/lib/dtos/AuthDTO.ts

export type UserRole = 'admin' | 'copywriter' | 'designer' | 'reviewer' | 'viewer';

export class AuthDTO {
  readonly token: string;
  readonly user_id: string;
  readonly tenant_id: string;
  readonly email: string;
  readonly name: string;
  readonly avatar_url: string;
  readonly role: UserRole;

  constructor(data: Record<string, any>) {
    this.token = data.token ?? '';
    this.user_id = data.user_id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.email = data.email ?? '';
    this.name = data.name ?? '';
    this.avatar_url = data.avatar_url ?? '';
    this.role = data.role ?? 'viewer';
  }

  get iniciais(): string {
    return this.name
      .split(' ')
      .map(p => p[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  }

  get isAdmin(): boolean {
    return this.role === 'admin';
  }

  get canEdit(): boolean {
    return this.role !== 'viewer';
  }

  get canComment(): boolean {
    return this.role !== 'viewer';
  }

  get canCreateCard(): boolean {
    return this.role === 'admin' || this.role === 'copywriter';
  }

  get canManageUsers(): boolean {
    return this.role === 'admin';
  }

  get roleLabel(): string {
    const labels: Record<UserRole, string> = {
      admin: 'Admin',
      copywriter: 'Copywriter',
      designer: 'Designer',
      reviewer: 'Reviewer',
      viewer: 'Viewer'
    };
    return labels[this.role];
  }

  isValid(): boolean {
    return this.token.length > 0 && this.user_id.length > 0 && this.email.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      token: this.token,
      user_id: this.user_id,
      tenant_id: this.tenant_id,
      email: this.email,
      name: this.name,
      role: this.role
    };
  }
}
```

### LoginRequestDTO.ts

```typescript
// src/lib/dtos/LoginRequestDTO.ts

export class LoginRequestDTO {
  readonly email: string;
  readonly password: string;

  constructor(data: Record<string, any>) {
    this.email = data.email ?? '';
    this.password = data.password ?? '';
  }

  get emailValido(): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email);
  }

  get senhaForte(): boolean {
    const s = this.password;
    return s.length >= 8
      && /[A-Z]/.test(s)
      && /[0-9]/.test(s)
      && /[^A-Za-z0-9]/.test(s);
  }

  get errosSenha(): string[] {
    const erros: string[] = [];
    if (this.password.length < 8) erros.push('Minimo 8 caracteres');
    if (!/[A-Z]/.test(this.password)) erros.push('1 letra maiuscula');
    if (!/[0-9]/.test(this.password)) erros.push('1 numero');
    if (!/[^A-Za-z0-9]/.test(this.password)) erros.push('1 caractere especial');
    return erros;
  }

  isValid(): boolean {
    return this.emailValido && this.senhaForte;
  }

  toPayload(): Record<string, any> {
    return { email: this.email, password: this.password };
  }
}
```

### BoardDTO.ts

```typescript
// src/lib/dtos/BoardDTO.ts

export interface ColumnData {
  id: string;
  name: string;
  order: number;
  color: string | null;
}

export class BoardDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly name: string;
  readonly columns: ColumnData[];
  readonly created_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? data._id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.name = data.name ?? '';
    this.columns = (data.columns ?? []).map((c: any) => ({
      id: c.id ?? '',
      name: c.name ?? '',
      order: c.order ?? 0,
      color: c.color ?? null
    }));
    this.created_at = data.created_at ?? '';
  }

  get columnsSorted(): ColumnData[] {
    return [...this.columns].sort((a, b) => a.order - b.order);
  }

  getColumnById(id: string): ColumnData | undefined {
    return this.columns.find(c => c.id === id);
  }

  getColumnByName(name: string): ColumnData | undefined {
    return this.columns.find(c => c.name === name);
  }

  get canceladoColumnId(): string {
    return this.getColumnByName('Cancelado')?.id ?? '';
  }

  isValid(): boolean {
    return this.id.length > 0 && this.columns.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      tenant_id: this.tenant_id,
      name: this.name,
      columns: this.columns
    };
  }
}
```

### CardDTO.ts

```typescript
// src/lib/dtos/CardDTO.ts

export type CardPriority = 'alta' | 'media' | 'baixa';

export class CardDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly board_id: string;
  readonly column_id: string;
  readonly title: string;
  readonly copy_text: string;
  readonly disciplina: string;
  readonly tecnologia: string;
  readonly priority: CardPriority;
  readonly assigned_user_ids: string[];
  readonly created_by: string;
  readonly pipeline_id: string;
  readonly drive_link: string;
  readonly drive_folder_name: string;
  readonly pdf_url: string;
  readonly image_urls: string[];
  readonly order_in_column: number;
  readonly comment_count: number;
  readonly created_at: string;
  readonly updated_at: string;
  readonly archived_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? data._id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.board_id = data.board_id ?? '';
    this.column_id = data.column_id ?? '';
    this.title = data.title ?? '';
    this.copy_text = data.copy_text ?? '';
    this.disciplina = data.disciplina ?? '';
    this.tecnologia = data.tecnologia ?? '';
    this.priority = data.priority ?? 'media';
    this.assigned_user_ids = data.assigned_user_ids ?? [];
    this.created_by = data.created_by ?? '';
    this.pipeline_id = data.pipeline_id ?? '';
    this.drive_link = data.drive_link ?? '';
    this.drive_folder_name = data.drive_folder_name ?? '';
    this.pdf_url = data.pdf_url ?? '';
    this.image_urls = data.image_urls ?? [];
    this.order_in_column = data.order_in_column ?? 0;
    this.comment_count = data.comment_count ?? 0;
    this.created_at = data.created_at ?? '';
    this.updated_at = data.updated_at ?? '';
    this.archived_at = data.archived_at ?? '';
  }

  get isArchived(): boolean {
    return this.archived_at.length > 0;
  }

  get hasDriveLink(): boolean {
    return this.drive_link.length > 0;
  }

  get hasPdf(): boolean {
    return this.pdf_url.length > 0;
  }

  get hasImages(): boolean {
    return this.image_urls.length > 0;
  }

  get hasPipeline(): boolean {
    return this.pipeline_id.length > 0;
  }

  get priorityLabel(): string {
    const labels: Record<CardPriority, string> = {
      alta: 'Alta', media: 'Media', baixa: 'Baixa'
    };
    return labels[this.priority];
  }

  get tituloTruncado(): string {
    return this.title.length > 50 ? this.title.slice(0, 47) + '...' : this.title;
  }

  isValid(): boolean {
    return this.id.length > 0 && this.title.length >= 3 && this.board_id.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      board_id: this.board_id,
      column_id: this.column_id,
      title: this.title,
      copy_text: this.copy_text,
      disciplina: this.disciplina,
      tecnologia: this.tecnologia,
      priority: this.priority,
      assigned_user_ids: this.assigned_user_ids,
      pipeline_id: this.pipeline_id,
      drive_link: this.drive_link,
      pdf_url: this.pdf_url,
      image_urls: this.image_urls
    };
  }
}
```

### CriarCardDTO.ts

```typescript
// src/lib/dtos/CriarCardDTO.ts

import type { CardPriority } from '$lib/dtos/CardDTO';

export class CriarCardDTO {
  readonly title: string;
  readonly copy_text: string;
  readonly disciplina: string;
  readonly tecnologia: string;
  readonly priority: CardPriority;
  readonly assigned_user_ids: string[];

  constructor(data: Record<string, any>) {
    this.title = (data.title ?? '').trim();
    this.copy_text = data.copy_text ?? '';
    this.disciplina = data.disciplina ?? '';
    this.tecnologia = data.tecnologia ?? '';
    this.priority = data.priority ?? 'media';
    this.assigned_user_ids = data.assigned_user_ids ?? [];
  }

  isValid(): boolean {
    return this.title.length >= 3;
  }

  toPayload(): Record<string, any> {
    return {
      title: this.title,
      copy_text: this.copy_text,
      disciplina: this.disciplina,
      tecnologia: this.tecnologia,
      priority: this.priority,
      assigned_user_ids: this.assigned_user_ids
    };
  }
}
```

### EditarCardDTO.ts

```typescript
// src/lib/dtos/EditarCardDTO.ts

import type { CardPriority } from '$lib/dtos/CardDTO';

export class EditarCardDTO {
  readonly id: string;
  readonly title: string;
  readonly copy_text: string;
  readonly disciplina: string;
  readonly tecnologia: string;
  readonly priority: CardPriority;
  readonly assigned_user_ids: string[];

  constructor(data: Record<string, any>) {
    this.id = data.id ?? '';
    this.title = (data.title ?? '').trim();
    this.copy_text = data.copy_text ?? '';
    this.disciplina = data.disciplina ?? '';
    this.tecnologia = data.tecnologia ?? '';
    this.priority = data.priority ?? 'media';
    this.assigned_user_ids = data.assigned_user_ids ?? [];
  }

  isValid(): boolean {
    return this.id.length > 0 && this.title.length >= 3;
  }

  toPayload(): Record<string, any> {
    return {
      title: this.title,
      copy_text: this.copy_text,
      disciplina: this.disciplina,
      tecnologia: this.tecnologia,
      priority: this.priority,
      assigned_user_ids: this.assigned_user_ids
    };
  }
}
```

### CommentDTO.ts

```typescript
// src/lib/dtos/CommentDTO.ts

export class CommentDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly card_id: string;
  readonly user_id: string;
  readonly user_name: string;
  readonly user_avatar_url: string;
  readonly text: string;
  readonly created_at: string;
  readonly updated_at: string;
  readonly deleted_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? data._id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.card_id = data.card_id ?? '';
    this.user_id = data.user_id ?? '';
    this.user_name = data.user_name ?? '';
    this.user_avatar_url = data.user_avatar_url ?? '';
    this.text = data.text ?? '';
    this.created_at = data.created_at ?? '';
    this.updated_at = data.updated_at ?? '';
    this.deleted_at = data.deleted_at ?? '';
  }

  get isDeleted(): boolean {
    return this.deleted_at.length > 0;
  }

  get isEdited(): boolean {
    return this.updated_at.length > 0 && this.updated_at !== this.created_at;
  }

  get userIniciais(): string {
    return this.user_name
      .split(' ')
      .map(p => p[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  }

  isOwnedBy(userId: string): boolean {
    return this.user_id === userId;
  }

  isValid(): boolean {
    return this.id.length > 0 && this.text.length > 0 && this.card_id.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      card_id: this.card_id,
      text: this.text
    };
  }
}
```

### CriarComentarioDTO.ts

```typescript
// src/lib/dtos/CriarComentarioDTO.ts

export class CriarComentarioDTO {
  readonly card_id: string;
  readonly text: string;

  constructor(data: Record<string, any>) {
    this.card_id = data.card_id ?? '';
    this.text = (data.text ?? '').trim();
  }

  isValid(): boolean {
    return this.card_id.length > 0 && this.text.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      card_id: this.card_id,
      text: this.text
    };
  }
}
```

### ActivityDTO.ts

```typescript
// src/lib/dtos/ActivityDTO.ts

export type ActivityAction =
  | 'card_created'
  | 'column_changed'
  | 'assignee_changed'
  | 'field_edited'
  | 'comment_added'
  | 'comment_edited'
  | 'comment_deleted'
  | 'image_generated'
  | 'drive_linked'
  | 'pdf_exported';

export class ActivityDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly card_id: string;
  readonly user_id: string;
  readonly user_name: string;
  readonly action: ActivityAction;
  readonly metadata: Record<string, any>;
  readonly created_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? data._id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.card_id = data.card_id ?? '';
    this.user_id = data.user_id ?? '';
    this.user_name = data.user_name ?? '';
    this.action = data.action ?? 'card_created';
    this.metadata = data.metadata ?? {};
    this.created_at = data.created_at ?? '';
  }

  get descricao(): string {
    const nome = this.user_name || 'Sistema';
    const meta = this.metadata;

    const descricoes: Record<ActivityAction, string> = {
      card_created: `${nome} criou o card`,
      column_changed: `${nome} moveu de ${meta.from_column ?? '?'} para ${meta.to_column ?? '?'}`,
      assignee_changed: `${nome} alterou os responsaveis`,
      field_edited: `${nome} editou ${meta.field_name ?? 'um campo'}`,
      comment_added: `${nome} adicionou um comentario`,
      comment_edited: `${nome} editou um comentario`,
      comment_deleted: `${nome} removeu um comentario`,
      image_generated: `${nome} gerou imagens`,
      drive_linked: `${nome} vinculou ao Google Drive`,
      pdf_exported: `${nome} exportou o PDF`
    };

    return descricoes[this.action] ?? `${nome} realizou uma acao`;
  }

  get iconType(): string {
    const icons: Record<ActivityAction, string> = {
      card_created: 'plus',
      column_changed: 'arrow',
      assignee_changed: 'user',
      field_edited: 'pencil',
      comment_added: 'chat',
      comment_edited: 'pencil',
      comment_deleted: 'trash',
      image_generated: 'image',
      drive_linked: 'link',
      pdf_exported: 'document'
    };
    return icons[this.action] ?? 'info';
  }

  isValid(): boolean {
    return this.id.length > 0 && this.card_id.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      card_id: this.card_id,
      action: this.action,
      metadata: this.metadata
    };
  }
}
```

### NotificationDTO.ts

```typescript
// src/lib/dtos/NotificationDTO.ts

export type NotificationType = 'assigned' | 'mentioned' | 'column_changed';

export class NotificationDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly user_id: string;
  readonly card_id: string;
  readonly type: NotificationType;
  readonly message: string;
  readonly is_read: boolean;
  readonly created_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? data._id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.user_id = data.user_id ?? '';
    this.card_id = data.card_id ?? '';
    this.type = data.type ?? 'assigned';
    this.message = data.message ?? '';
    this.is_read = data.is_read ?? false;
    this.created_at = data.created_at ?? '';
  }

  get typeIcon(): string {
    const icons: Record<NotificationType, string> = {
      assigned: 'user',
      mentioned: 'at',
      column_changed: 'arrow'
    };
    return icons[this.type] ?? 'bell';
  }

  isValid(): boolean {
    return this.id.length > 0 && this.message.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      card_id: this.card_id,
      type: this.type,
      is_read: this.is_read
    };
  }
}
```

### UserDTO.ts

```typescript
// src/lib/dtos/UserDTO.ts

import type { UserRole } from '$lib/dtos/AuthDTO';

export class UserDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly email: string;
  readonly name: string;
  readonly avatar_url: string;
  readonly role: UserRole;
  readonly created_at: string;
  readonly deleted_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? data._id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.email = data.email ?? '';
    this.name = data.name ?? '';
    this.avatar_url = data.avatar_url ?? '';
    this.role = data.role ?? 'viewer';
    this.created_at = data.created_at ?? '';
    this.deleted_at = data.deleted_at ?? '';
  }

  get iniciais(): string {
    return this.name
      .split(' ')
      .map(p => p[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  }

  get isActive(): boolean {
    return this.deleted_at.length === 0;
  }

  get roleLabel(): string {
    const labels: Record<UserRole, string> = {
      admin: 'Admin',
      copywriter: 'Copywriter',
      designer: 'Designer',
      reviewer: 'Reviewer',
      viewer: 'Viewer'
    };
    return labels[this.role];
  }

  get roleBadgeColor(): string {
    const colors: Record<UserRole, string> = {
      admin: 'bg-purple/10 text-purple border-purple/20',
      copywriter: 'bg-steel-3/10 text-steel-3 border-steel-3/20',
      designer: 'bg-red/10 text-red border-red/20',
      reviewer: 'bg-amber/10 text-amber border-amber/20',
      viewer: 'bg-teal-5/10 text-teal-6 border-teal-5/20'
    };
    return colors[this.role];
  }

  isValid(): boolean {
    return this.id.length > 0 && this.email.length > 0 && this.name.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      email: this.email,
      name: this.name,
      avatar_url: this.avatar_url,
      role: this.role
    };
  }
}
```

### CriarUsuarioDTO.ts

```typescript
// src/lib/dtos/CriarUsuarioDTO.ts

import type { UserRole } from '$lib/dtos/AuthDTO';

export class CriarUsuarioDTO {
  readonly name: string;
  readonly email: string;
  readonly role: UserRole;
  readonly avatar_url: string;
  readonly password: string;

  constructor(data: Record<string, any>) {
    this.name = (data.name ?? '').trim();
    this.email = (data.email ?? '').trim();
    this.role = data.role ?? 'viewer';
    this.avatar_url = data.avatar_url ?? '';
    this.password = data.password ?? '';
  }

  get emailValido(): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.email);
  }

  isValid(): boolean {
    return this.name.length >= 2 && this.emailValido && this.password.length >= 8;
  }

  toPayload(): Record<string, any> {
    return {
      name: this.name,
      email: this.email,
      role: this.role,
      avatar_url: this.avatar_url,
      password: this.password
    };
  }
}
```

### EditarUsuarioDTO.ts

```typescript
// src/lib/dtos/EditarUsuarioDTO.ts

import type { UserRole } from '$lib/dtos/AuthDTO';

export class EditarUsuarioDTO {
  readonly id: string;
  readonly name: string;
  readonly role: UserRole;
  readonly avatar_url: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? '';
    this.name = (data.name ?? '').trim();
    this.role = data.role ?? 'viewer';
    this.avatar_url = data.avatar_url ?? '';
  }

  isValid(): boolean {
    return this.id.length > 0 && this.name.length >= 2;
  }

  toPayload(): Record<string, any> {
    return {
      name: this.name,
      role: this.role,
      avatar_url: this.avatar_url
    };
  }
}
```

---

## 5. Stores

### auth.ts

```typescript
// src/lib/stores/auth.ts
import { writable, derived } from 'svelte/store';
import { AuthDTO } from '$lib/dtos/AuthDTO';

const TOKEN_KEY = 'kanban_jwt';

function getStoredAuth(): AuthDTO | null {
  if (typeof localStorage === 'undefined') return null;
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) return null;
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return new AuthDTO({ token, ...payload });
  } catch {
    localStorage.removeItem(TOKEN_KEY);
    return null;
  }
}

export const authUser = writable<AuthDTO | null>(getStoredAuth());

export const isAuthenticated = derived(authUser, $u => $u !== null && $u.isValid());
export const userRole = derived(authUser, $u => $u?.role ?? 'viewer');
export const isAdmin = derived(authUser, $u => $u?.isAdmin ?? false);

export function setAuth(auth: AuthDTO): void {
  localStorage.setItem(TOKEN_KEY, auth.token);
  authUser.set(auth);
}

export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  authUser.set(null);
}

export function getToken(): string {
  return localStorage.getItem(TOKEN_KEY) ?? '';
}
```

### board.ts

```typescript
// src/lib/stores/board.ts
import { writable } from 'svelte/store';
import type { BoardDTO } from '$lib/dtos/BoardDTO';
import type { CardDTO } from '$lib/dtos/CardDTO';

export interface BoardFilters {
  busca: string;
  responsavel: string;
  coluna: string[];
  prioridade: string;
}

export const board = writable<BoardDTO | null>(null);
export const cards = writable<CardDTO[]>([]);
export const boardLoading = writable(false);
export const boardError = writable<string | null>(null);
export const boardFilters = writable<BoardFilters>({
  busca: '',
  responsavel: '',
  coluna: [],
  prioridade: ''
});
export const selectedCardId = writable<string | null>(null);
export const showCreateModal = writable(false);
```

### notifications.ts

```typescript
// src/lib/stores/notifications.ts
import { writable, derived } from 'svelte/store';
import type { NotificationDTO } from '$lib/dtos/NotificationDTO';

export const notifications = writable<NotificationDTO[]>([]);
export const notificationsLoading = writable(false);

export const unreadCount = derived(notifications, $n =>
  $n.filter(n => !n.is_read).length
);
```

---

## 6. Services — Codigo Completo

### AuthService.ts

```typescript
// src/lib/services/AuthService.ts
import { AuthRepository } from '$lib/repositories/AuthRepository';
import type { AuthDTO } from '$lib/dtos/AuthDTO';
import type { LoginRequestDTO } from '$lib/dtos/LoginRequestDTO';

export class AuthService {
  static async login(dto: LoginRequestDTO): Promise<AuthDTO> {
    if (!dto.isValid()) throw new Error('Email ou senha invalidos');
    return AuthRepository.login(dto.toPayload());
  }

  static async loginGoogle(): Promise<AuthDTO> {
    return AuthRepository.loginGoogle();
  }

  static async loginMicrosoft(): Promise<AuthDTO> {
    return AuthRepository.loginMicrosoft();
  }

  static async logout(): Promise<void> {
    return AuthRepository.logout();
  }
}
```

### BoardService.ts

```typescript
// src/lib/services/BoardService.ts
import { BoardRepository } from '$lib/repositories/BoardRepository';
import type { BoardDTO } from '$lib/dtos/BoardDTO';

export class BoardService {
  static async carregar(): Promise<BoardDTO> {
    return BoardRepository.carregar();
  }
}
```

### CardService.ts

```typescript
// src/lib/services/CardService.ts
import { CardRepository } from '$lib/repositories/CardRepository';
import type { CardDTO } from '$lib/dtos/CardDTO';
import type { CriarCardDTO } from '$lib/dtos/CriarCardDTO';
import type { EditarCardDTO } from '$lib/dtos/EditarCardDTO';

export class CardService {
  static async listar(boardId: string): Promise<CardDTO[]> {
    if (!boardId) throw new Error('Board ID obrigatorio');
    const cards = await CardRepository.listar(boardId);
    return cards.filter(c => c.isValid());
  }

  static async buscar(id: string): Promise<CardDTO> {
    if (!id) throw new Error('Card ID obrigatorio');
    return CardRepository.buscar(id);
  }

  static async criar(dto: CriarCardDTO): Promise<CardDTO> {
    if (!dto.isValid()) throw new Error('Dados do card invalidos');
    return CardRepository.criar(dto.toPayload());
  }

  static async editar(dto: EditarCardDTO): Promise<CardDTO> {
    if (!dto.isValid()) throw new Error('Dados do card invalidos');
    return CardRepository.editar(dto.toPayload());
  }

  static async moverParaCancelado(cardId: string, canceladoColumnId: string): Promise<CardDTO> {
    if (!cardId || !canceladoColumnId) throw new Error('IDs obrigatorios');
    return CardRepository.moverColuna(cardId, canceladoColumnId);
  }
}
```

### CommentService.ts

```typescript
// src/lib/services/CommentService.ts
import { CommentRepository } from '$lib/repositories/CommentRepository';
import type { CommentDTO } from '$lib/dtos/CommentDTO';
import type { CriarComentarioDTO } from '$lib/dtos/CriarComentarioDTO';

export class CommentService {
  static async listar(cardId: string): Promise<CommentDTO[]> {
    if (!cardId) throw new Error('Card ID obrigatorio');
    const comments = await CommentRepository.listar(cardId);
    return comments.filter(c => c.isValid());
  }

  static async criar(dto: CriarComentarioDTO): Promise<CommentDTO> {
    if (!dto.isValid()) throw new Error('Comentario invalido');
    return CommentRepository.criar(dto.toPayload());
  }

  static async editar(commentId: string, text: string): Promise<CommentDTO> {
    if (!commentId || !text.trim()) throw new Error('Dados invalidos');
    return CommentRepository.editar(commentId, text.trim());
  }

  static async deletar(commentId: string): Promise<void> {
    if (!commentId) throw new Error('Comment ID obrigatorio');
    return CommentRepository.deletar(commentId);
  }
}
```

### ActivityService.ts

```typescript
// src/lib/services/ActivityService.ts
import { ActivityRepository } from '$lib/repositories/ActivityRepository';
import type { ActivityDTO } from '$lib/dtos/ActivityDTO';

export class ActivityService {
  static async listar(cardId: string, page: number = 1): Promise<ActivityDTO[]> {
    if (!cardId) throw new Error('Card ID obrigatorio');
    return ActivityRepository.listar(cardId, page);
  }
}
```

### NotificationService.ts

```typescript
// src/lib/services/NotificationService.ts
import { NotificationRepository } from '$lib/repositories/NotificationRepository';
import type { NotificationDTO } from '$lib/dtos/NotificationDTO';

export class NotificationService {
  static async listar(): Promise<NotificationDTO[]> {
    return NotificationRepository.listar();
  }

  static async marcarComoLida(id: string): Promise<void> {
    if (!id) throw new Error('Notification ID obrigatorio');
    return NotificationRepository.marcarComoLida(id);
  }

  static async marcarTodasComoLidas(): Promise<void> {
    return NotificationRepository.marcarTodasComoLidas();
  }
}
```

### UserService.ts

```typescript
// src/lib/services/UserService.ts
import { UserRepository } from '$lib/repositories/UserRepository';
import type { UserDTO } from '$lib/dtos/UserDTO';
import type { CriarUsuarioDTO } from '$lib/dtos/CriarUsuarioDTO';
import type { EditarUsuarioDTO } from '$lib/dtos/EditarUsuarioDTO';

export class UserService {
  static async listar(): Promise<UserDTO[]> {
    const users = await UserRepository.listar();
    return users.filter(u => u.isValid());
  }

  static async criar(dto: CriarUsuarioDTO): Promise<UserDTO> {
    if (!dto.isValid()) throw new Error('Dados do usuario invalidos');
    return UserRepository.criar(dto.toPayload());
  }

  static async editar(dto: EditarUsuarioDTO): Promise<UserDTO> {
    if (!dto.isValid()) throw new Error('Dados do usuario invalidos');
    return UserRepository.editar(dto.toPayload());
  }

  static async desativar(id: string): Promise<void> {
    if (!id) throw new Error('User ID obrigatorio');
    return UserRepository.desativar(id);
  }

  static async reativar(id: string): Promise<void> {
    if (!id) throw new Error('User ID obrigatorio');
    return UserRepository.reativar(id);
  }
}
```

---

## 7. Repositories — Codigo Completo

### AuthRepository.ts

```typescript
// src/lib/repositories/AuthRepository.ts
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { AuthDTO } from '$lib/dtos/AuthDTO';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class AuthRepository {
  static async login(payload: Record<string, any>): Promise<AuthDTO> {
    if (USE_MOCK) {
      const { authMock, simularDelay } = await import('$lib/mocks/auth.mock');
      await simularDelay(500);
      if (payload.email === 'admin@itvalley.com' && payload.password === 'Admin@123') {
        return new AuthDTO(authMock.admin);
      }
      throw new Error('Email ou senha incorretos');
    }
    const res = await fetch(`${API_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      if (res.status === 401) throw new Error('Email ou senha incorretos');
      if (res.status === 429) throw new Error('Conta bloqueada. Aguarde 1 minuto.');
      throw new Error('Erro de conexao');
    }
    return new AuthDTO(await res.json());
  }

  static async loginGoogle(): Promise<AuthDTO> {
    if (USE_MOCK) {
      const { authMock, simularDelay } = await import('$lib/mocks/auth.mock');
      await simularDelay(800);
      return new AuthDTO(authMock.admin);
    }
    // Em producao: redireciona para OAuth2 consent screen
    window.location.href = `${API_BASE}/api/auth/google`;
    // Nunca chega aqui (redirect). Callback em /api/auth/google/callback
    return new AuthDTO({});
  }

  static async loginMicrosoft(): Promise<AuthDTO> {
    if (USE_MOCK) {
      const { authMock, simularDelay } = await import('$lib/mocks/auth.mock');
      await simularDelay(800);
      return new AuthDTO(authMock.admin);
    }
    window.location.href = `${API_BASE}/api/auth/microsoft`;
    return new AuthDTO({});
  }

  static async logout(): Promise<void> {
    // Logout e local — so limpa o token
  }
}
```

### BoardRepository.ts

```typescript
// src/lib/repositories/BoardRepository.ts
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { BoardDTO } from '$lib/dtos/BoardDTO';
import { getToken } from '$lib/stores/auth';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

export class BoardRepository {
  static async carregar(): Promise<BoardDTO> {
    if (USE_MOCK) {
      const { boardMock, simularDelay } = await import('$lib/mocks/board.mock');
      await simularDelay(400);
      return new BoardDTO(boardMock);
    }
    const res = await fetch(`${API_BASE}/api/kanban/board`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao carregar board');
    return new BoardDTO(await res.json());
  }
}
```

### CardRepository.ts

```typescript
// src/lib/repositories/CardRepository.ts
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { CardDTO } from '$lib/dtos/CardDTO';
import { getToken } from '$lib/stores/auth';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

export class CardRepository {
  static async listar(boardId: string): Promise<CardDTO[]> {
    if (USE_MOCK) {
      const { cardsMock, simularDelay } = await import('$lib/mocks/cards.mock');
      await simularDelay(300);
      return cardsMock.map((c: any) => new CardDTO(c));
    }
    const res = await fetch(`${API_BASE}/api/kanban/boards/${boardId}/cards`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao carregar cards');
    const data = await res.json();
    return data.map((c: any) => new CardDTO(c));
  }

  static async buscar(id: string): Promise<CardDTO> {
    if (USE_MOCK) {
      const { cardsMock, simularDelay } = await import('$lib/mocks/cards.mock');
      await simularDelay(200);
      const found = cardsMock.find((c: any) => c.id === id) ?? cardsMock[0];
      return new CardDTO(found);
    }
    const res = await fetch(`${API_BASE}/api/kanban/cards/${id}`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Card nao encontrado');
    return new CardDTO(await res.json());
  }

  static async criar(payload: Record<string, any>): Promise<CardDTO> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/cards.mock');
      await simularDelay(500);
      return new CardDTO({ ...payload, id: `card-${Date.now()}`, column_id: 'col-copy', created_at: new Date().toISOString() });
    }
    const res = await fetch(`${API_BASE}/api/kanban/cards`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Erro ao criar card');
    return new CardDTO(await res.json());
  }

  static async editar(payload: Record<string, any>): Promise<CardDTO> {
    const { id, ...body } = payload;
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/cards.mock');
      await simularDelay(400);
      return new CardDTO({ ...payload, updated_at: new Date().toISOString() });
    }
    const res = await fetch(`${API_BASE}/api/kanban/cards/${id}`, {
      method: 'PATCH',
      headers: authHeaders(),
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error('Erro ao editar card');
    return new CardDTO(await res.json());
  }

  static async moverColuna(cardId: string, columnId: string): Promise<CardDTO> {
    if (USE_MOCK) {
      const { cardsMock, simularDelay } = await import('$lib/mocks/cards.mock');
      await simularDelay(300);
      const found = cardsMock.find((c: any) => c.id === cardId) ?? cardsMock[0];
      return new CardDTO({ ...found, column_id: columnId });
    }
    const res = await fetch(`${API_BASE}/api/kanban/cards/${cardId}/move`, {
      method: 'PATCH',
      headers: authHeaders(),
      body: JSON.stringify({ column_id: columnId })
    });
    if (!res.ok) throw new Error('Erro ao mover card');
    return new CardDTO(await res.json());
  }
}
```

### CommentRepository.ts

```typescript
// src/lib/repositories/CommentRepository.ts
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { CommentDTO } from '$lib/dtos/CommentDTO';
import { getToken } from '$lib/stores/auth';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

export class CommentRepository {
  static async listar(cardId: string): Promise<CommentDTO[]> {
    if (USE_MOCK) {
      const { commentsMock, simularDelay } = await import('$lib/mocks/comments.mock');
      await simularDelay(300);
      return commentsMock
        .filter((c: any) => c.card_id === cardId)
        .map((c: any) => new CommentDTO(c));
    }
    const res = await fetch(`${API_BASE}/api/kanban/cards/${cardId}/comments`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao carregar comentarios');
    const data = await res.json();
    return data.map((c: any) => new CommentDTO(c));
  }

  static async criar(payload: Record<string, any>): Promise<CommentDTO> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/comments.mock');
      await simularDelay(400);
      return new CommentDTO({
        ...payload,
        id: `comment-${Date.now()}`,
        user_id: 'user-admin',
        user_name: 'Carlos Viana',
        created_at: new Date().toISOString()
      });
    }
    const res = await fetch(`${API_BASE}/api/kanban/cards/${payload.card_id}/comments`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Erro ao criar comentario');
    return new CommentDTO(await res.json());
  }

  static async editar(commentId: string, text: string): Promise<CommentDTO> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/comments.mock');
      await simularDelay(300);
      return new CommentDTO({ id: commentId, text, updated_at: new Date().toISOString() });
    }
    const res = await fetch(`${API_BASE}/api/kanban/comments/${commentId}`, {
      method: 'PATCH',
      headers: authHeaders(),
      body: JSON.stringify({ text })
    });
    if (!res.ok) throw new Error('Erro ao editar comentario');
    return new CommentDTO(await res.json());
  }

  static async deletar(commentId: string): Promise<void> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/comments.mock');
      await simularDelay(300);
      return;
    }
    const res = await fetch(`${API_BASE}/api/kanban/comments/${commentId}`, {
      method: 'DELETE',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao deletar comentario');
  }
}
```

### ActivityRepository.ts

```typescript
// src/lib/repositories/ActivityRepository.ts
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { ActivityDTO } from '$lib/dtos/ActivityDTO';
import { getToken } from '$lib/stores/auth';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

export class ActivityRepository {
  static async listar(cardId: string, page: number = 1): Promise<ActivityDTO[]> {
    if (USE_MOCK) {
      const { activitiesMock, simularDelay } = await import('$lib/mocks/activities.mock');
      await simularDelay(300);
      return activitiesMock
        .filter((a: any) => a.card_id === cardId)
        .map((a: any) => new ActivityDTO(a));
    }
    const res = await fetch(`${API_BASE}/api/kanban/cards/${cardId}/activities?page=${page}`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao carregar atividades');
    const data = await res.json();
    return data.map((a: any) => new ActivityDTO(a));
  }
}
```

### NotificationRepository.ts

```typescript
// src/lib/repositories/NotificationRepository.ts
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { NotificationDTO } from '$lib/dtos/NotificationDTO';
import { getToken } from '$lib/stores/auth';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

export class NotificationRepository {
  static async listar(): Promise<NotificationDTO[]> {
    if (USE_MOCK) {
      const { notificationsMock, simularDelay } = await import('$lib/mocks/notifications.mock');
      await simularDelay(300);
      return notificationsMock.map((n: any) => new NotificationDTO(n));
    }
    const res = await fetch(`${API_BASE}/api/kanban/notifications`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao carregar notificacoes');
    const data = await res.json();
    return data.map((n: any) => new NotificationDTO(n));
  }

  static async marcarComoLida(id: string): Promise<void> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/notifications.mock');
      await simularDelay(200);
      return;
    }
    const res = await fetch(`${API_BASE}/api/kanban/notifications/${id}/read`, {
      method: 'PATCH',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao marcar como lida');
  }

  static async marcarTodasComoLidas(): Promise<void> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/notifications.mock');
      await simularDelay(300);
      return;
    }
    const res = await fetch(`${API_BASE}/api/kanban/notifications/read-all`, {
      method: 'PATCH',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao marcar todas como lidas');
  }
}
```

### UserRepository.ts

```typescript
// src/lib/repositories/UserRepository.ts
import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { UserDTO } from '$lib/dtos/UserDTO';
import { getToken } from '$lib/stores/auth';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

function authHeaders(): Record<string, string> {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getToken()}`
  };
}

export class UserRepository {
  static async listar(): Promise<UserDTO[]> {
    if (USE_MOCK) {
      const { usersMock, simularDelay } = await import('$lib/mocks/users.mock');
      await simularDelay(300);
      return usersMock.map((u: any) => new UserDTO(u));
    }
    const res = await fetch(`${API_BASE}/api/kanban/users`, {
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao carregar usuarios');
    const data = await res.json();
    return data.map((u: any) => new UserDTO(u));
  }

  static async criar(payload: Record<string, any>): Promise<UserDTO> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/users.mock');
      await simularDelay(500);
      return new UserDTO({ ...payload, id: `user-${Date.now()}`, created_at: new Date().toISOString() });
    }
    const res = await fetch(`${API_BASE}/api/kanban/users`, {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Erro ao criar usuario');
    return new UserDTO(await res.json());
  }

  static async editar(payload: Record<string, any>): Promise<UserDTO> {
    const { id, ...body } = payload;
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/users.mock');
      await simularDelay(400);
      return new UserDTO({ ...payload, updated_at: new Date().toISOString() });
    }
    const res = await fetch(`${API_BASE}/api/kanban/users/${id}`, {
      method: 'PATCH',
      headers: authHeaders(),
      body: JSON.stringify(body)
    });
    if (!res.ok) throw new Error('Erro ao editar usuario');
    return new UserDTO(await res.json());
  }

  static async desativar(id: string): Promise<void> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/users.mock');
      await simularDelay(300);
      return;
    }
    const res = await fetch(`${API_BASE}/api/kanban/users/${id}/deactivate`, {
      method: 'PATCH',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao desativar usuario');
  }

  static async reativar(id: string): Promise<void> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/users.mock');
      await simularDelay(300);
      return;
    }
    const res = await fetch(`${API_BASE}/api/kanban/users/${id}/reactivate`, {
      method: 'PATCH',
      headers: authHeaders()
    });
    if (!res.ok) throw new Error('Erro ao reativar usuario');
  }
}
```

---

## 8. Utils

### date.ts

```typescript
// src/lib/utils/date.ts

export function formatRelativeDate(isoDate: string): string {
  if (!isoDate) return '';
  const date = new Date(isoDate);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  const diffH = Math.floor(diffMs / 3600000);
  const diffD = Math.floor(diffMs / 86400000);

  if (diffMin < 1) return 'agora';
  if (diffMin < 60) return `ha ${diffMin} min`;
  if (diffH < 24) return `ha ${diffH}h`;
  if (diffD < 7) return `ha ${diffD} dia${diffD > 1 ? 's' : ''}`;
  if (diffD < 30) return `ha ${Math.floor(diffD / 7)} sem`;
  return date.toLocaleDateString('pt-BR');
}

export function formatAbsoluteDate(isoDate: string): string {
  if (!isoDate) return '';
  return new Date(isoDate).toLocaleString('pt-BR', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit'
  });
}
```

---

## 9. Estrutura das Paginas

### routes/login/+page.svelte

```
Estados: loading, vazio (inicial), erro, sucesso (redirect)
Orquestracao:
  1. Se isAuthenticated → goto('/')
  2. submit → LoginRequestDTO → AuthService.login() → setAuth() → goto('/')
  3. SSO → AuthService.loginGoogle() / loginMicrosoft()
Componentes:
  <LoginForm onSubmit={handleLogin} {loading} {erro} />
  <SSOButtons onGoogle={handleGoogle} onMicrosoft={handleMicrosoft} {loading} />
```

### routes/kanban/+page.svelte

```
Estados: loading, vazio, erro, sucesso, filtro-vazio
Orquestracao:
  1. onMount → BoardService.carregar() → board.set()
  2. onMount → CardService.listar(boardId) → cards.set()
  3. URL query param ?card=X → selectedCardId.set(X)
  4. Filtros via boardFilters store → $derived filtra cards
  5. Drag para Cancelado → CardService.moverParaCancelado() (optimistic update)
  6. Criar card → showCreateModal.set(true)
  7. Refresh → re-fetch board + cards
Componentes:
  <KanbanFilters />
  <KanbanBoard {board} {filteredCards}>
    <KanbanColumn {column} {columnCards}>
      <KanbanCard {card} onOpen={openDetail} onDragCancel={handleCancel} />
    </KanbanColumn>
  </KanbanBoard>
  {#if selectedCardId}
    <CardDetailModal cardId={selectedCardId} onClose={closeDetail} />
  {/if}
  {#if showCreateModal}
    <CardCreateModal onClose={closeCreate} onCreated={handleCreated} />
  {/if}
```

### routes/kanban/usuarios/+page.svelte

```
Estados: loading, vazio, erro, sucesso
Guard: if !isAdmin → goto('/kanban')
Orquestracao:
  1. onMount → UserService.listar() → users
  2. Convidar → abre UserFormModal (mode='create')
  3. Editar → abre UserFormModal (mode='edit', user)
  4. Desativar/Reativar → UserService.desativar/reativar()
Componentes:
  <UserTable {users} onEdit={edit} onToggle={toggleActive} />
  {#if showUserModal}
    <UserFormModal {mode} {user} onSave={handleSave} onClose={closeModal} />
  {/if}
```

---

## 10. Contratos de API — Endpoints Consumidos pelo Frontend

| Metodo | Endpoint | Request Body | Response | Usado por |
|--------|----------|-------------|----------|-----------|
| POST | `/api/auth/login` | `{ email, password }` | `{ token, user_id, tenant_id, email, name, avatar_url, role }` | AuthRepository.login |
| GET | `/api/auth/google` | -- | Redirect OAuth2 | AuthRepository.loginGoogle |
| GET | `/api/auth/microsoft` | -- | Redirect OAuth2 | AuthRepository.loginMicrosoft |
| GET | `/api/kanban/board` | -- | BoardDTO shape | BoardRepository.carregar |
| GET | `/api/kanban/boards/{boardId}/cards` | -- | CardDTO[] | CardRepository.listar |
| GET | `/api/kanban/cards/{id}` | -- | CardDTO | CardRepository.buscar |
| POST | `/api/kanban/cards` | CriarCardDTO.toPayload() | CardDTO | CardRepository.criar |
| PATCH | `/api/kanban/cards/{id}` | EditarCardDTO.toPayload() | CardDTO | CardRepository.editar |
| PATCH | `/api/kanban/cards/{id}/move` | `{ column_id }` | CardDTO | CardRepository.moverColuna |
| GET | `/api/kanban/cards/{cardId}/comments` | -- | CommentDTO[] | CommentRepository.listar |
| POST | `/api/kanban/cards/{cardId}/comments` | `{ text }` | CommentDTO | CommentRepository.criar |
| PATCH | `/api/kanban/comments/{id}` | `{ text }` | CommentDTO | CommentRepository.editar |
| DELETE | `/api/kanban/comments/{id}` | -- | -- | CommentRepository.deletar |
| GET | `/api/kanban/cards/{cardId}/activities?page=N` | -- | ActivityDTO[] | ActivityRepository.listar |
| GET | `/api/kanban/notifications` | -- | NotificationDTO[] | NotificationRepository.listar |
| PATCH | `/api/kanban/notifications/{id}/read` | -- | -- | NotificationRepository.marcarComoLida |
| PATCH | `/api/kanban/notifications/read-all` | -- | -- | NotificationRepository.marcarTodasComoLidas |
| GET | `/api/kanban/users` | -- | UserDTO[] | UserRepository.listar |
| POST | `/api/kanban/users` | CriarUsuarioDTO.toPayload() | UserDTO | UserRepository.criar |
| PATCH | `/api/kanban/users/{id}` | EditarUsuarioDTO.toPayload() | UserDTO | UserRepository.editar |
| PATCH | `/api/kanban/users/{id}/deactivate` | -- | -- | UserRepository.desativar |
| PATCH | `/api/kanban/users/{id}/reactivate` | -- | -- | UserRepository.reativar |

**Nota:** Todos os endpoints (exceto `/api/auth/*`) exigem header `Authorization: Bearer {JWT}`. O backend extrai tenant_id e user_id do token.

---

## 11. Alteracoes no Layout Existente

### +layout.svelte — Auth Guard + Notification Bell

Alteracoes necessarias no `src/routes/+layout.svelte`:

1. Importar `authUser`, `isAuthenticated` do store `auth.ts`
2. Importar `NotificationBell` do dominio notification
3. Adicionar guard: se `!isAuthenticated` e rota !== `/login` → `goto('/login')`
4. Adicionar no header (desktop e mobile): `<NotificationBell />` + avatar do usuario
5. Rota `/login` nao renderiza Sidebar nem header — layout limpo

### Sidebar.svelte — Novos Itens

Adicionar no array `mainItems` (entre Home e Historico):
```typescript
{ href: '/kanban', label: 'Kanban', icon: 'M9 17V7m0 10a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h2a2 2 0 012 2m0 10a2 2 0 002 2h2a2 2 0 002-2M9 7a2 2 0 012-2h2a2 2 0 012 2m0 10V7m0 10a2 2 0 002 2h2a2 2 0 002-2V7a2 2 0 00-2-2h-2a2 2 0 00-2 2' }
```

Adicionar no array `systemItems` (visivel somente para Admin):
```typescript
{ href: '/kanban/usuarios', label: 'Usuarios', icon: 'M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z' }
```

A visibilidade condicional do item "Usuarios" depende do store `isAdmin`.

---

## 12. Design Tokens Necessarios — app.css

Adicionar ao `app.css` existente:

```css
/* === Kanban Board === */
.kanban-board {
  display: flex;
  gap: 1rem;
  overflow-x: auto;
  padding: 1rem 0;
  min-height: calc(100vh - 200px);
}

.kanban-column {
  min-width: 280px;
  max-width: 320px;
  flex-shrink: 0;
  border-radius: 1rem;
  background: var(--color-bg-card);
  padding: 0.75rem;
}

.kanban-card {
  padding: 0.875rem;
  border-radius: 0.75rem;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-default);
  cursor: pointer;
  transition: box-shadow 0.15s, border-color 0.15s;
}

.kanban-card:hover {
  border-color: var(--color-border-active);
  box-shadow: 0 2px 8px rgba(53,120,176,0.1);
}

.kanban-card.dragging {
  opacity: 0.5;
  transform: rotate(2deg);
}

/* === Priority Badges === */
.priority-alta { background: rgba(220,79,79,0.1); color: var(--color-red); border: 1px solid rgba(220,79,79,0.2); }
.priority-media { background: rgba(212,147,10,0.1); color: var(--color-amber); border: 1px solid rgba(212,147,10,0.2); }
.priority-baixa { background: rgba(122,173,166,0.1); color: var(--color-teal-6); border: 1px solid rgba(122,173,166,0.2); }

/* === Column Header Colors === */
.column-copy { border-top: 3px solid var(--color-steel-3); }
.column-design { border-top: 3px solid var(--color-purple); }
.column-revisao { border-top: 3px solid var(--color-amber); }
.column-aprovado { border-top: 3px solid var(--color-green); }
.column-publicado { border-top: 3px solid #1a7a4a; }
.column-cancelado { border-top: 3px solid var(--color-red); }

/* === Activity Timeline === */
.activity-timeline {
  border-left: 2px solid var(--color-border-default);
  padding-left: 1.5rem;
  margin-left: 0.75rem;
}

.activity-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-steel-3);
  position: absolute;
  left: -1.125rem;
  top: 0.5rem;
}

/* === Notification Badge === */
.notification-badge {
  position: absolute;
  top: -4px;
  right: -4px;
  min-width: 18px;
  height: 18px;
  border-radius: 9px;
  background: var(--color-red);
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 4px;
}

/* === Login Page === */
.login-container {
  max-width: 420px;
  margin: 0 auto;
  padding: 2rem;
}

.login-card {
  padding: 2.5rem;
  border-radius: 1.5rem;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-default);
  box-shadow: 0 4px 24px rgba(13,32,51,0.06);
}

/* === Avatar Stack === */
.avatar-stack {
  display: flex;
}

.avatar-stack > * + * {
  margin-left: -8px;
}

.avatar-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid var(--color-bg-card);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6rem;
  font-weight: 600;
  background: var(--color-bg-elevated);
  color: var(--color-text-secondary);
}

/* === Drop Zone === */
.drop-zone-active {
  background: rgba(220,79,79,0.05);
  border: 2px dashed var(--color-red);
  border-radius: 1rem;
}
```

---

## 13. Notas para o Dev Mockado (Agente 06)

### auth.mock.ts
- Exportar `authMock` com objetos para cada role: admin, copywriter, designer, reviewer, viewer
- Token mock pode ser string fixa (nao precisa ser JWT real)
- admin@itvalley.com / Admin@123 para login mock
- Exportar `simularDelay(ms)` como nos outros mocks do projeto

### board.mock.ts
- 1 board com 6 colunas: Copy (col-copy), Design (col-design), Revisao (col-revisao), Aprovado (col-aprovado), Publicado (col-publicado), Cancelado (col-cancelado)
- Cada coluna com id, name, order (0-5), color
- Exportar `boardMock` e `simularDelay`

### cards.mock.ts
- 8-12 cards distribuidos pelas colunas
- Variar: prioridades (alta/media/baixa), disciplinas (NLP, Deep Learning, etc.), com/sem drive_link, com/sem imagens
- Alguns com pipeline_id, outros criados manualmente
- comment_count variado
- assigned_user_ids referenciando IDs dos users mock
- Exportar `cardsMock` e `simularDelay`

### comments.mock.ts
- 5-8 comentarios vinculados a 2-3 cards diferentes via card_id
- Variar autores (user_id + user_name)
- 1 comentario editado (updated_at diferente de created_at)
- Exportar `commentsMock` e `simularDelay`

### activities.mock.ts
- 10-15 atividades de audit log vinculadas a 2-3 cards
- Cobrir todos os action types: card_created, column_changed, field_edited, etc.
- metadata realista (from_column, to_column, field_name, etc.)
- Exportar `activitiesMock` e `simularDelay`

### notifications.mock.ts
- 5-8 notificacoes, mix de lidas e nao-lidas
- Types: assigned, column_changed
- Mensagens realistas em portugues
- Exportar `notificationsMock` e `simularDelay`

### users.mock.ts
- 5 usuarios (1 por role): Carlos (admin), Ana (copywriter), Pedro (designer), Maria (reviewer), Lucas (viewer)
- 1 usuario desativado (deleted_at preenchido)
- Exportar `usersMock` e `simularDelay`

---

## 14. Dev Features — Plano de Entrega

Cada dev feature e 1 caso de uso completo. Ordem recomendada:

| # | Dev Feature | Arquivos | Dependencia |
|---|------------|---------|-------------|
| 1 | Login (email+senha) | AuthDTO, LoginRequestDTO, AuthService, AuthRepository, auth.mock, auth store, LoginForm, SSOButtons, /login page | -- |
| 2 | Auth Guard | Alteracao no +layout.svelte | #1 |
| 3 | CarregarBoard | BoardDTO, BoardService, BoardRepository, board.mock, board store, KanbanBoard, KanbanColumn | #1 |
| 4 | ListarCards | CardDTO, CardService, CardRepository, cards.mock, KanbanCard, KanbanFilters | #3 |
| 5 | CriarCard | CriarCardDTO, CardCreateModal | #4 |
| 6 | DetalheCard | CardDetailModal, CardDetailTab | #4 |
| 7 | EditarCard | EditarCardDTO, alteracao no CardDetailTab | #6 |
| 8 | MoverParaCancelado | Drag-and-drop no KanbanCard + CardService.moverParaCancelado | #4 |
| 9 | ListarComentarios | CommentDTO, CommentService, CommentRepository, comments.mock, CardCommentsTab, CommentItem | #6 |
| 10 | CriarComentario | CriarComentarioDTO, campo no CardCommentsTab | #9 |
| 11 | EditarComentario | Inline edit no CommentItem | #9 |
| 12 | DeletarComentario | Botao no CommentItem | #9 |
| 13 | ListarAtividades | ActivityDTO, ActivityService, ActivityRepository, activities.mock, CardActivityTab | #6 |
| 14 | ListarNotificacoes | NotificationDTO, NotificationService, NotificationRepository, notifications.mock, notifications store, NotificationBell, NotificationDropdown | #2 |
| 15 | MarcarNotificacoesLidas | Acoes no NotificationDropdown | #14 |
| 16 | ListarUsuarios | UserDTO, UserService, UserRepository, users.mock, UserTable, /kanban/usuarios page | #2 |
| 17 | CriarUsuario | CriarUsuarioDTO, UserFormModal | #16 |
| 18 | EditarUsuario | EditarUsuarioDTO, alteracao no UserFormModal | #16 |
| 19 | DesativarReativarUsuario | Botoes no UserTable | #16 |
| 20 | NotificationBell no Header | Alteracao no +layout.svelte | #14 |
| 21 | Sidebar Kanban | Alteracao no Sidebar.svelte | #2 |
| 22 | Deep Links | Query params ?card=X no /kanban | #6 |
| 23 | LoginSSO Google | SSOButtons + AuthRepository.loginGoogle | #1 |
| 24 | LoginSSO Microsoft | SSOButtons + AuthRepository.loginMicrosoft | #1 |

---

## 15. Checklist de Validacao

- [ ] Todo DTO tem: constructor(Record), readonly, isValid(), toPayload()
- [ ] Todo Service usa metodos static, nunca acessa dto.campo
- [ ] Todo Repository alterna mock/real via VITE_USE_MOCK
- [ ] Todo Repository cria o DTO: new XxxDTO(data)
- [ ] Todo mock exporta simularDelay
- [ ] Componentes organizados por dominio (kanban/, auth/, notification/, user/)
- [ ] Import direto, sem barrel exports
- [ ] Stores em src/lib/stores/ (auth, board, notifications)
- [ ] Auth guard no +layout.svelte
- [ ] Design tokens no app.css (kanban-board, kanban-card, priority-*, column-*, etc.)
- [ ] Sidebar atualizada com Kanban e Usuarios
- [ ] NotificationBell no header do layout
- [ ] Deep link /kanban?card=X funciona
- [ ] Filtros via query params
- [ ] Drag-and-drop somente para coluna Cancelado (RN-019)
- [ ] Viewer nao pode editar/mover/comentar (RN-008)
- [ ] Cards cancelados ocultos apos 7 dias, acessiveis via filtro (DT-006)
