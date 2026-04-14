# Scripts MongoDB -- Kanban Pipeline

Documento produzido pelo Agente 07 (Arquiteto SQL + MongoDB).
Base: PRD secao 10, Arquitetura Backend DTOs, conexao MongoDB existente.

---

## Decisoes de Arquitetura

### Banco
MongoDB (pymongo sincrono), database `content_factory` -- mesmo ja em uso pelo sistema.
Sem SQL -- todas as entidades do Kanban sao MongoDB.

### Multitenancia
Todo documento tem `tenant_id`. Todo indice comeca com `tenant_id` (exceto TTL e token unique).
O `tenant_id` vem do JWT, nunca do body.

### Collections
7 collections (6 do PRD + 1 para convites):

| # | Collection | Finalidade |
|---|-----------|-----------|
| 1 | `kanban_users` | Usuarios com perfil ACL, soft delete |
| 2 | `kanban_boards` | Boards com colunas como subdocumento |
| 3 | `kanban_cards` | Cards dos carrosseis na pipeline |
| 4 | `kanban_comments` | Comentarios por card |
| 5 | `kanban_activity_log` | Audit log append-only (RN-013) |
| 6 | `kanban_notifications` | Notificacoes por usuario |
| 7 | `kanban_invite_tokens` | Tokens de convite com TTL 48h |

---

## Scripts Executaveis

Todos em `backend/scripts/`. Executar de dentro de `backend/`.

### Ordem de execucao

```
1. python scripts/kanban_setup_collections.py   # Cria 7 collections com JSON Schema
2. python scripts/kanban_setup_indexes.py        # Cria 15 indices otimizados
3. python scripts/kanban_seed_board.py           # Board padrao com 6 colunas
4. python scripts/kanban_seed_admin.py           # Usuario admin inicial
```

Ou tudo de uma vez:
```
python scripts/kanban_run_all.py
```

### Parametros opcionais
```
python scripts/kanban_run_all.py --tenant meu-tenant --email admin@email.com --name "Meu Admin" --password "Senha@123"
```

---

## 1. Collections e Validators

### 1.1 kanban_users
- Campos required: `tenant_id`, `email`, `name`, `password_hash`, `role`, `created_at`
- `role` enum: admin, copywriter, designer, reviewer, viewer
- `deleted_at` para soft delete
- `email` unico por tenant (via indice unique)

### 1.2 kanban_boards
- Campos required: `tenant_id`, `name`, `columns`, `created_at`
- `columns` e array de subdocumentos (id, name, order, color, auto_assign_user_ids)
- Colunas fixas no MVP (RN-020): Copy, Design, Revisao, Aprovado, Publicado, Cancelado

### 1.3 kanban_cards
- Campos required: `tenant_id`, `board_id`, `column_id`, `title`, `priority`, `created_by`, `created_at`
- `priority` enum: alta, media, baixa (default media -- RN-014)
- `assigned_user_ids` array de user_ids
- `pipeline_id` para vincular com pipeline existente
- `drive_link`, `pdf_url`, `image_urls` para artefatos
- `archived_at` para soft delete

### 1.4 kanban_comments
- Campos required: `tenant_id`, `card_id`, `user_id`, `text`, `created_at`
- `parent_comment_id` para threads (pos-MVP)
- `mentions` array de user_ids (pos-MVP)
- `deleted_at` para soft delete

### 1.5 kanban_activity_log
- Campos required: `tenant_id`, `card_id`, `user_id`, `action`, `created_at`
- `action` enum: card_created, column_changed, assignee_changed, field_edited, comment_added, comment_edited, comment_deleted, image_generated, drive_linked, pdf_exported
- `metadata` objeto flexivel por tipo de acao
- **Append-only**: nunca editar nem deletar (RN-013)

### 1.6 kanban_notifications
- Campos required: `tenant_id`, `user_id`, `card_id`, `type`, `message`, `is_read`, `created_at`
- `type` enum: assigned, mentioned, column_changed
- `is_read` boolean para controle de leitura

### 1.7 kanban_invite_tokens
- Campos required: `tenant_id`, `email`, `name`, `role`, `token`, `created_by`, `expires_at`, `used`, `created_at`
- `token` unique (secrets.token_urlsafe(32))
- TTL index em `expires_at` -- MongoDB apaga automaticamente apos 48h
- `used` boolean para marcar token ja consumido

---

## 2. Indices (15 total)

### kanban_users (2 indices)
| Indice | Campos | Tipo | Finalidade |
|--------|--------|------|-----------|
| idx_users_tenant_email_unique | tenant_id + email | unique | Login, busca, evitar duplicata |
| idx_users_tenant_active | tenant_id + deleted_at | normal | Listar usuarios ativos |

### kanban_boards (1 indice)
| Indice | Campos | Tipo | Finalidade |
|--------|--------|------|-----------|
| idx_boards_tenant | tenant_id | normal | Buscar board padrao do tenant |

### kanban_cards (5 indices)
| Indice | Campos | Tipo | Finalidade |
|--------|--------|------|-----------|
| idx_cards_tenant_board_column | tenant_id + board_id + column_id | normal | Query principal: listar cards por coluna |
| idx_cards_tenant_assigned | tenant_id + assigned_user_ids | normal | Filtro por responsavel |
| idx_cards_tenant_board_priority | tenant_id + board_id + priority | normal | Filtro por prioridade |
| idx_cards_tenant_pipeline | tenant_id + pipeline_id | sparse | Integracao pipeline existente |
| idx_cards_tenant_board_archived | tenant_id + board_id + archived_at | normal | Filtro soft delete |

### kanban_comments (1 indice)
| Indice | Campos | Tipo | Finalidade |
|--------|--------|------|-----------|
| idx_comments_tenant_card_date | tenant_id + card_id + created_at ASC | normal | Listar comentarios cronologicamente |

### kanban_activity_log (1 indice)
| Indice | Campos | Tipo | Finalidade |
|--------|--------|------|-----------|
| idx_activity_tenant_card_date | tenant_id + card_id + created_at DESC | normal | Timeline de atividade (mais recente primeiro) |

### kanban_notifications (2 indices)
| Indice | Campos | Tipo | Finalidade |
|--------|--------|------|-----------|
| idx_notifications_tenant_user_read | tenant_id + user_id + is_read | normal | Listar notificacoes filtradas |
| idx_notifications_tenant_user_read_date | tenant_id + user_id + is_read + created_at DESC | normal | Contador de nao-lidas com ordenacao |

### kanban_invite_tokens (3 indices)
| Indice | Campos | Tipo | Finalidade |
|--------|--------|------|-----------|
| idx_invite_token_unique | token | unique | Busca rapida ao aceitar convite |
| idx_invite_ttl | expires_at | TTL (0s) | Expiracao automatica apos 48h |
| idx_invite_tenant_email | tenant_id + email | normal | Verificar convite duplicado |

---

## 3. Seeds

### Board Padrao
6 colunas com IDs fixos:

| ID | Nome | Ordem | Cor |
|----|------|-------|-----|
| col-copy | Copy | 0 | #3B82F6 (blue) |
| col-design | Design | 1 | #8B5CF6 (violet) |
| col-revisao | Revisao | 2 | #F59E0B (amber) |
| col-aprovado | Aprovado | 3 | #10B981 (emerald) |
| col-publicado | Publicado | 4 | #06B6D4 (cyan) |
| col-cancelado | Cancelado | 5 | #EF4444 (red) |

Colunas terminais (RN-007): `col-publicado` e `col-cancelado`.

### Admin Inicial
- Tenant: `itvalley-dev`
- Email: `admin@itvalley.com`
- Senha: `Admin@123` (satisfaz RN-021)
- Role: admin
- **Trocar senha apos primeiro login!**

---

## 4. Dependencias entre Scripts

```
kanban_setup_collections  (nenhuma dependencia)
         |
         v
kanban_setup_indexes      (depende das collections existirem)
         |
         v
kanban_seed_board          (depende de kanban_boards existir)
         |
         v
kanban_seed_admin          (depende de kanban_users existir)
```

Todos dependem de `MONGO_URL` configurado no `.env`.

---

## 5. Observacoes para o Dev Backend

1. **Conexao**: Usa `get_mongo_db()` de `data/connections/mongo_connection.py` -- mesma conexao do sistema existente.
2. **Idempotencia**: Todos os scripts verificam se o recurso ja existe antes de criar. Podem ser re-executados sem efeitos colaterais.
3. **TTL do invite_tokens**: O MongoDB apaga documentos automaticamente quando `expires_at` passa. Nenhum job/cron necessario.
4. **Cards cancelados**: Ocultar apos 7 dias via query filter no repository (`archived_at < now - 7d`), sem job.
5. **Audit log**: Collection append-only. Repository do activity_log NAO deve ter metodos de update/delete.
6. **Validators**: Usam `validationAction: "error"` (padrao). Documentos que violam o schema sao rejeitados.
7. **Sparse index**: `idx_cards_tenant_pipeline` e sparse porque `pipeline_id` e null em cards criados manualmente.
