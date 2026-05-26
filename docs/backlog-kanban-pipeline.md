# Backlog Kanban Pipeline -- Divisao por Dominios e Dev Features

Documento produzido pelo Agente 08 (P.O. / Product Owner).
Base: PRD, Telas, Arquitetura Backend, Arquitetura Frontend, Design, Scripts MongoDB.

---

## 1. MAPA DE DOMINIOS E DEPENDENCIAS

```
Dominios identificados:
  Auth         (base -- sem dependencias)
  Board        (depende de: Auth)
  Card         (depende de: Auth, Board)
  Comment      (depende de: Auth, Card)
  Activity     (depende de: Auth, Card)
  Notification (depende de: Auth, Card)
  Pipeline     (depende de: Auth, Card, Board)

Ordem de implementacao:
  Nivel 0 (infra):             Base Backend + Base Frontend
  Nivel 1 (sem dependencia):   Auth
  Nivel 2 (depende do Auth):   Board
  Nivel 3 (depende do Board):  Card
  Nivel 4 (depende do Card):   Comment, Activity, Notification (paralelo)
  Nivel 5 (depende de tudo):   Pipeline Integration
```

---

## 2. PACOTE BASE -- Backend (obrigatorio primeiro)

**Pode comecar apos:** nada (e o primeiro)

**O que o dev CRIA:**

| Arquivo | Descricao |
|---------|-----------|
| `middleware/auth.py` | CurrentUser, create_access_token, verify_password, hash_password, get_current_user, require_role |
| `data/connections/mongo_connection.py` | get_mongo_db() -- se nao existir, adaptar para Kanban collections |
| `scripts/kanban_setup_collections.py` | Cria 7 collections com JSON Schema validation |
| `scripts/kanban_setup_indexes.py` | Cria 15 indices otimizados |
| `scripts/kanban_seed_board.py` | Board padrao com 6 colunas fixas (IDs fixos) |
| `scripts/kanban_seed_admin.py` | Usuario admin inicial (admin@itvalley.com / Admin@123) |
| `scripts/kanban_run_all.py` | Executa os 4 scripts acima em sequencia |

**Dependencias de pacote:** python-jose, passlib[bcrypt], httpx (SSO), pydantic[email-validator]

**Criterio de pronto:**
- `python scripts/kanban_run_all.py` executa sem erro
- 7 collections criadas com validators no MongoDB
- 15 indices criados
- 1 board padrao com 6 colunas inserido
- 1 usuario admin inserido
- `middleware/auth.py` importavel, `create_access_token()` gera JWT valido, `verify_password()` funciona com bcrypt

---

## 3. PACOTE BASE -- Frontend (obrigatorio primeiro)

**Pode comecar apos:** nada (paralelo ao Base Backend)

**O que o dev CRIA:**

| Arquivo | Descricao |
|---------|-----------|
| `src/lib/dtos/AuthDTO.ts` | readonly, constructor, isValid, toPayload, helpers (iniciais, isAdmin, canEdit, etc.) |
| `src/lib/dtos/LoginRequestDTO.ts` | readonly, constructor, isValid (emailValido + senhaForte), toPayload, errosSenha |
| `src/lib/stores/auth.ts` | Estado do usuario logado, JWT no localStorage, logout |
| `src/lib/stores/notifications.ts` | Contador de nao-lidas (store reativo) |
| `src/lib/utils/date.ts` | formatRelativeDate() -- "ha 2 dias", "ha 5 min" |
| `src/lib/mocks/auth.mock.ts` | Dados mock de login (token fake, usuarios com roles variados) |
| `src/lib/mocks/users.mock.ts` | Lista de usuarios mock com roles variados |
| Tokens CSS no `app.css` | 6 variaveis de cor para colunas Kanban (--color-col-copy, etc.) |

**O que o dev ALTERA:**

| Arquivo | Alteracao |
|---------|----------|
| `src/routes/+layout.svelte` | Auth guard: redireciona para /login se sem token, redireciona para / se logado em /login |

**Criterio de pronto:**
- AuthDTO e LoginRequestDTO com testes de isValid()
- Store auth.ts funciona (login mock, logout limpa localStorage)
- Auth guard redireciona corretamente
- Tokens CSS adicionados ao app.css
- formatRelativeDate() funciona com datas variadas

---

## 4. PACOTES DE DESENVOLVIMENTO

---

### PACOTE BACK-1 -- Dominio: Auth

**Pode comecar apos:** Pacote Base Backend

**Casos de uso (dev features):**

#### Dev Feature B1.1: Login (email+senha)

**O que o dev CRIA:**
- `dtos/auth/base.py` -- UsuarioBase
- `dtos/auth/login/request.py` -- LoginRequest (email, password)
- `dtos/auth/login/response.py` -- LoginResponse (access_token, token_type, user_id, tenant_id, role, name, email)
- `factories/auth_factory.py` -- AuthFactory.validate_login(), AuthFactory.create_user_doc()
- `mappers/auth_mapper.py` -- to_login_response(), to_usuario_response()
- `services/auth_service.py` -- login()
- `routers/auth.py` -- POST /api/auth/login
- `data/repositories/mongo/auth_repository.py` -- find_by_email(), insert_user()

**Dependencias:** middleware/auth.py pronto (Pacote Base)
**Criterio de pronto:** POST /api/auth/login com email+senha retorna LoginResponse com JWT valido (status 200). Login com credenciais erradas retorna 401. Rate limit de 5 tentativas/minuto retorna 429.

---

#### Dev Feature B1.2: Me (usuario logado)

**O que o dev CRIA:**
- `dtos/auth/me/response.py` -- MeResponse

**O que o dev ADICIONA:**
- `services/auth_service.py` -- me()
- `routers/auth.py` -- GET /api/auth/me
- `data/repositories/mongo/auth_repository.py` -- find_by_id()

**Dependencias:** B1.1 (Login)
**Criterio de pronto:** GET /api/auth/me com JWT valido retorna dados do usuario logado. Sem JWT retorna 401.

---

#### Dev Feature B1.3: Criar usuario (Admin)

**O que o dev CRIA:**
- `dtos/auth/criar_usuario/request.py` -- CriarUsuarioRequest (name, email, password, role, avatar_url) com validators (senha forte RN-021, role valido, nome min 2)
- `dtos/auth/criar_usuario/response.py` -- UsuarioResponse

**O que o dev ADICIONA:**
- `factories/auth_factory.py` -- create_user_doc() com hash_password
- `services/auth_service.py` -- criar_usuario()
- `routers/auth.py` -- POST /api/auth/users (require_role("admin"))
- `data/repositories/mongo/auth_repository.py` -- email_exists()

**Dependencias:** B1.1 (Login)
**Criterio de pronto:** POST /api/auth/users com JWT de Admin cria usuario. Retorna 201 + UsuarioResponse. Email duplicado retorna 409. Role nao-admin retorna 403. Senha fraca retorna 422.

---

#### Dev Feature B1.4: Listar usuarios

**O que o dev CRIA:**
- `dtos/auth/listar_usuarios/response.py` -- ListarUsuariosResponse (lista de UsuarioResponse)

**O que o dev ADICIONA:**
- `services/auth_service.py` -- listar_usuarios()
- `routers/auth.py` -- GET /api/auth/users
- `data/repositories/mongo/auth_repository.py` -- find_all_by_tenant()

**Dependencias:** B1.3 (Criar usuario)
**Criterio de pronto:** GET /api/auth/users retorna lista de usuarios do tenant. Filtra por tenant_id do JWT. Exclui usuarios com deleted_at preenchido.

---

#### Dev Feature B1.5: Convidar usuario + Aceitar convite

**O que o dev CRIA:**
- `dtos/auth/convidar_usuario/request.py` -- ConvidarUsuarioRequest (email, name, role)
- `dtos/auth/convidar_usuario/response.py` -- ConviteResponse (invite_token, email, role, expires_at, invite_url)
- `dtos/auth/aceitar_convite/request.py` -- AceitarConviteRequest (token, password) com validator senha forte
- `data/repositories/mongo/invite_repository.py` -- insert_invite(), find_by_token(), mark_used()

**O que o dev ADICIONA:**
- `factories/auth_factory.py` -- create_invite_doc()
- `services/auth_service.py` -- convidar_usuario(), aceitar_convite()
- `routers/auth.py` -- POST /api/auth/users/invite (require_role("admin")), POST /api/auth/users/invite/accept (publico)

**Dependencias:** B1.3 (Criar usuario)
**Criterio de pronto:** Admin gera invite token. Token valido permite criar usuario com senha definida pelo convidado. Token expirado (48h) retorna 410. Token ja usado retorna 409.

---

#### Dev Feature B1.6: Atualizar + Desativar + Reativar usuario

**O que o dev CRIA:**
- `dtos/auth/atualizar_usuario/request.py` -- AtualizarUsuarioRequest (name, role, avatar_url -- todos opcionais)

**O que o dev ADICIONA:**
- `services/auth_service.py` -- atualizar_usuario(), desativar_usuario(), reativar_usuario()
- `routers/auth.py` -- PATCH /api/auth/users/{user_id}, DELETE /api/auth/users/{user_id}, POST /api/auth/users/{user_id}/reativar
- `data/repositories/mongo/auth_repository.py` -- update_user(), soft_delete(), reactivate()
- `mappers/auth_mapper.py` -- to_usuario_response() (se ainda nao existir)

**Dependencias:** B1.4 (Listar usuarios)
**Criterio de pronto:** Admin edita nome/role/avatar de usuario. Admin desativa usuario (soft delete). Admin reativa usuario desativado. Role nao-admin retorna 403.

---

#### Dev Feature B1.7: SSO Google + Microsoft

**O que o dev CRIA:**
- `dtos/auth/login_google/request.py` -- LoginGoogleRequest (code, redirect_uri)
- `dtos/auth/login_microsoft/request.py` -- LoginMicrosoftRequest (code, redirect_uri)

**O que o dev ADICIONA:**
- `services/auth_service.py` -- login_google(), login_microsoft()
- `routers/auth.py` -- POST /api/auth/google, POST /api/auth/microsoft
- `factories/auth_factory.py` -- create_user_from_sso() (cria usuario se nao existir)

**Dependencias:** B1.1 (Login)
**Criterio de pronto:** Authorization code do Google/Microsoft e trocado por userinfo, JWT gerado. Se usuario nao existe, e criado com role "viewer" por padrao. Requer GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, MICROSOFT_CLIENT_ID, MICROSOFT_CLIENT_SECRET no .env.

**Observacao:** SSO pode ser implementado por ultimo dentro do Auth -- nao bloqueia os demais dominios.

---

### PACOTE FRONT-1 -- Dominio: Auth

**Pode comecar apos:** Pacote Base Frontend

**Casos de uso (dev features):**

#### Dev Feature F1.1: Tela de Login (email+senha)

**O que o dev CRIA:**
- `src/lib/components/auth/LoginForm.svelte` -- formulario email+senha com validacao (errosSenha), toggle mostrar senha, loading state
- `src/lib/repositories/AuthRepository.ts` -- login() com mock/real via VITE_USE_MOCK
- `src/lib/services/AuthService.ts` -- login() (static, camada opaca)
- `src/routes/login/+page.svelte` -- tela completa de login

**O que o dev ADICIONA:**
- `src/lib/stores/auth.ts` -- setAuth(), clearAuth(), isAuthenticated derived

**Dependencias:** Pacote Base Frontend (AuthDTO, LoginRequestDTO, store auth, auth guard)
**Criterio de pronto:** Formulario de login funciona com VITE_USE_MOCK=true. Valida email e senha forte no frontend. Exibe erros de validacao. Loading spinner no botao. Redireciona para / apos login mock. Campo senha com toggle mostrar/ocultar.

**O que os outros devs estao fazendo:** Backend esta implementando POST /api/auth/login (B1.1). Frontend deve trabalhar com mock ate o backend estar pronto.

---

#### Dev Feature F1.2: Botoes SSO (Google + Microsoft)

**O que o dev CRIA:**
- `src/lib/components/auth/SSOButtons.svelte` -- 2 botoes com icones SVG, loading state

**O que o dev ADICIONA:**
- `src/lib/repositories/AuthRepository.ts` -- loginGoogle(), loginMicrosoft()
- `src/lib/services/AuthService.ts` -- loginGoogle(), loginMicrosoft()
- `src/routes/login/+page.svelte` -- integrar SSOButtons abaixo do formulario com separador "ou"

**Dependencias:** F1.1 (Login email+senha)
**Criterio de pronto:** Botoes SSO visiveis na tela de login. Clique inicia fluxo OAuth2 (mock redireciona e simula callback). Layout conforme design (separador "ou continue com" entre form e SSO).

---

#### Dev Feature F1.3: Tela de Gerenciamento de Usuarios

**O que o dev CRIA:**
- `src/lib/dtos/UserDTO.ts` -- readonly, constructor, isValid, toPayload
- `src/lib/dtos/CriarUsuarioDTO.ts` -- readonly, constructor, isValid (senha forte), toPayload
- `src/lib/dtos/EditarUsuarioDTO.ts` -- readonly, constructor, isValid, toPayload
- `src/lib/components/user/UserTable.svelte` -- tabela com avatar, nome, email, role badge, status, acoes
- `src/lib/components/user/UserFormModal.svelte` -- modal criar/editar usuario
- `src/lib/repositories/UserRepository.ts` -- listar(), criar(), editar(), desativar(), reativar() com mock/real
- `src/lib/services/UserService.ts` -- metodos static
- `src/routes/kanban/usuarios/+page.svelte` -- tela completa

**O que o dev ADICIONA:**
- `src/lib/components/layout/Sidebar.svelte` -- item "Usuarios" na secao Sistema (visivel so para Admin)

**Dependencias:** F1.1 (Login, auth guard com role check)
**Criterio de pronto:** Tela lista usuarios mock. Modal cria usuario com validacao. Modal edita usuario. Desativar/reativar funciona com mock. Rota /kanban/usuarios acessivel somente para Admin (redirect para /kanban se nao-admin). Badge de role com cor por perfil. VITE_USE_MOCK=true.

**O que os outros devs estao fazendo:** Backend esta implementando CRUD de usuarios (B1.3-B1.6). Frontend deve trabalhar com mock.

---

### PACOTE BACK-2 -- Dominio: Board

**Pode comecar apos:** PACOTE BACK-1 (Auth completo)

**Casos de uso (dev features):**

#### Dev Feature B2.1: Buscar Board Padrao

**O que o dev CRIA:**
- `dtos/kanban_board/base.py` -- BoardBase, ColunaBase
- `dtos/kanban_board/buscar_board/response.py` -- BoardResponse (id, tenant_id, name, columns, created_at)
- `factories/kanban_board_factory.py` -- KanbanBoardFactory (se necessario)
- `mappers/kanban_board_mapper.py` -- to_board_response()
- `services/kanban_board_service.py` -- buscar_board_padrao()
- `routers/kanban_board.py` -- GET /api/kanban/boards/default
- `data/repositories/mongo/kanban_board_repository.py` -- find_default_by_tenant()

**Dependencias:** middleware/auth.py (Pacote Base)
**Criterio de pronto:** GET /api/kanban/boards/default com JWT valido retorna BoardResponse com 6 colunas fixas. Filtra por tenant_id do JWT. Retorna 404 se nenhum board existir para o tenant.

---

### PACOTE FRONT-2 -- Dominio: Board (estrutura visual)

**Pode comecar apos:** PACOTE FRONT-1 (Auth)

**Casos de uso (dev features):**

#### Dev Feature F2.1: Board Kanban (estrutura visual + filtros)

**O que o dev CRIA:**
- `src/lib/dtos/BoardDTO.ts` -- readonly, constructor, isValid, toPayload, columnsSorted, canceladoColumnId
- `src/lib/components/kanban/KanbanBoard.svelte` -- board com 6 colunas, scroll horizontal
- `src/lib/components/kanban/KanbanColumn.svelte` -- 1 coluna com header colorido (4px border-top), nome, contagem, lista de cards
- `src/lib/components/kanban/KanbanFilters.svelte` -- barra de filtros (busca, responsavel, coluna, prioridade, limpar)
- `src/lib/repositories/BoardRepository.ts` -- buscarPadrao() com mock/real
- `src/lib/services/BoardService.ts` -- buscarPadrao() static
- `src/lib/stores/board.ts` -- estado do board + cards + filtros
- `src/lib/mocks/board.mock.ts` -- board mock com 6 colunas
- `src/routes/kanban/+page.svelte` -- tela completa do board

**O que o dev ADICIONA:**
- `src/lib/components/layout/Sidebar.svelte` -- item "Kanban" na secao Principal (entre Home e Historico)

**Dependencias:** F1.1 (Login, auth guard)
**Criterio de pronto:** Rota /kanban exibe board com 6 colunas coloridas (vazias). Filtros funcionam (sem cards ainda, mas estrutura pronta). Skeleton loading visivel ao carregar. Estado vazio com mensagem "Nenhum carrossel em producao". Sidebar com link Kanban. Scroll horizontal funciona no mobile. VITE_USE_MOCK=true.

**O que os outros devs estao fazendo:** Backend esta implementando GET /api/kanban/boards/default (B2.1). Frontend usa mock.

---

### PACOTE BACK-3 -- Dominio: Card

**Pode comecar apos:** PACOTE BACK-2 (Board)

**Casos de uso (dev features):**

#### Dev Feature B3.1: Criar Card

**O que o dev CRIA:**
- `dtos/kanban_card/base.py` -- CardBase
- `dtos/kanban_card/criar_card/request.py` -- CriarCardRequest (title, copy_text, disciplina, tecnologia, priority, assigned_user_ids)
- `dtos/kanban_card/criar_card/response.py` -- CardResponse
- `factories/kanban_card_factory.py` -- KanbanCardFactory.create_card_doc() (seta column_id = col-copy, board_id do padrao, created_by do JWT)
- `mappers/kanban_card_mapper.py` -- to_card_response()
- `services/kanban_card_service.py` -- criar_card()
- `routers/kanban_card.py` -- POST /api/kanban/cards (require_role("admin", "copywriter"))
- `data/repositories/mongo/kanban_card_repository.py` -- insert_card()

**O que o dev ADICIONA:**
- `factories/kanban_activity_factory.py` -- create_card_created_log()
- `data/repositories/mongo/kanban_activity_repository.py` -- insert_activity()

**Dependencias:** B2.1 (Board -- precisa do board_id e column_id do board padrao)
**Criterio de pronto:** POST /api/kanban/cards cria card na coluna "Copy" do board padrao. Retorna 201 + CardResponse. Registra "card_created" no audit log. Valida titulo min 3 chars. Role viewer/designer/reviewer retorna 403.

---

#### Dev Feature B3.2: Listar Cards (com filtros)

**O que o dev CRIA:**
- `dtos/kanban_card/listar_cards/request.py` -- ListarCardsFiltros (query params: board_id, column_id, priority, assigned_user_id, search, page, per_page)
- `dtos/kanban_card/listar_cards/response.py` -- ListarCardsResponse (items, total, page, per_page)

**O que o dev ADICIONA:**
- `services/kanban_card_service.py` -- listar_cards()
- `routers/kanban_card.py` -- GET /api/kanban/cards
- `data/repositories/mongo/kanban_card_repository.py` -- find_by_filters() com paginacao

**Dependencias:** B3.1 (Criar Card)
**Criterio de pronto:** GET /api/kanban/cards retorna cards do tenant com filtros opcionais. Exclui cards com archived_at preenchido (exceto se filtro explicito). Cards cancelados ha mais de 7 dias ocultos por padrao. Busca por titulo (regex case-insensitive).

---

#### Dev Feature B3.3: Buscar Card (detalhe)

**O que o dev CRIA:**
- `dtos/kanban_card/buscar_card/response.py` -- CardDetalheResponse (inclui comment_count)

**O que o dev ADICIONA:**
- `services/kanban_card_service.py` -- buscar_card()
- `routers/kanban_card.py` -- GET /api/kanban/cards/{card_id}
- `data/repositories/mongo/kanban_card_repository.py` -- find_by_id()

**Dependencias:** B3.1 (Criar Card)
**Criterio de pronto:** GET /api/kanban/cards/{card_id} retorna CardDetalheResponse. Card de outro tenant retorna 404. Card inexistente retorna 404.

---

#### Dev Feature B3.4: Atualizar Card

**O que o dev CRIA:**
- `dtos/kanban_card/atualizar_card/request.py` -- AtualizarCardRequest (title, copy_text, disciplina, tecnologia, priority -- todos opcionais)
- `dtos/kanban_card/atualizar_card/response.py` -- CardResponse (reutiliza)

**O que o dev ADICIONA:**
- `services/kanban_card_service.py` -- atualizar_card()
- `routers/kanban_card.py` -- PATCH /api/kanban/cards/{card_id}
- `data/repositories/mongo/kanban_card_repository.py` -- update_card()
- `factories/kanban_activity_factory.py` -- create_field_edited_log()

**Dependencias:** B3.3 (Buscar Card)
**Criterio de pronto:** PATCH /api/kanban/cards/{card_id} atualiza campos. Retorna CardResponse atualizado. Registra "field_edited" no audit log com old_value/new_value. Viewer retorna 403.

---

#### Dev Feature B3.5: Mover Card (entre colunas)

**O que o dev CRIA:**
- `dtos/kanban_card/mover_card/request.py` -- MoverCardRequest (target_column_id)
- `dtos/kanban_card/mover_card/response.py` -- CardResponse (reutiliza)

**O que o dev ADICIONA:**
- `services/kanban_card_service.py` -- mover_card()
- `routers/kanban_card.py` -- POST /api/kanban/cards/{card_id}/mover
- `data/repositories/mongo/kanban_card_repository.py` -- update_column()
- `factories/kanban_activity_factory.py` -- create_column_changed_log()
- `factories/kanban_notification_factory.py` -- create_column_changed_notification()
- `data/repositories/mongo/kanban_notification_repository.py` -- insert_notification()

**Regras de negocio (na Factory):**
- Movimentacao manual so para coluna Cancelado (RN-019). Outras movimentacoes sao via pipeline (dev feature separada).
- Colunas terminais (Publicado, Cancelado) nao podem mover para frente (RN-007).
- Viewer nao pode mover (RN-008).

**Dependencias:** B3.3 (Buscar Card)
**Criterio de pronto:** POST /api/kanban/cards/{card_id}/mover com target_column_id valido move o card. Registra "column_changed" no audit log. Gera notificacao para responsaveis do card. Mover para coluna nao-Cancelado manualmente retorna 403 (exceto chamadas internas da pipeline). Mover de Publicado retorna 422.

---

#### Dev Feature B3.6: Atribuir Responsaveis

**O que o dev CRIA:**
- `dtos/kanban_card/atribuir_responsaveis/request.py` -- AtribuirResponsaveisRequest (user_ids: list)
- `dtos/kanban_card/atribuir_responsaveis/response.py` -- CardResponse (reutiliza)

**O que o dev ADICIONA:**
- `services/kanban_card_service.py` -- atribuir_responsaveis()
- `routers/kanban_card.py` -- PATCH /api/kanban/cards/{card_id}/responsaveis (require_role("admin"))
- `data/repositories/mongo/kanban_card_repository.py` -- update_assigned_users()
- `factories/kanban_activity_factory.py` -- create_assignee_changed_log()
- `factories/kanban_notification_factory.py` -- create_assigned_notification()

**Dependencias:** B3.3 (Buscar Card)
**Criterio de pronto:** Admin atribui responsaveis a card. Registra "assignee_changed" no audit log. Gera notificacao "assigned" para novos responsaveis. Nao-admin retorna 403.

---

### PACOTE FRONT-3 -- Dominio: Card

**Pode comecar apos:** PACOTE FRONT-2 (Board visual)

**Casos de uso (dev features):**

#### Dev Feature F3.1: Cards no Board (listagem visual)

**O que o dev CRIA:**
- `src/lib/dtos/CardDTO.ts` -- readonly, constructor, isValid, toPayload, helpers (priorityLabel, isArchived, etc.)
- `src/lib/components/kanban/KanbanCard.svelte` -- card compacto (titulo, badge prioridade, avatares, disciplina, comentarios, data)
- `src/lib/repositories/CardRepository.ts` -- listar() com mock/real
- `src/lib/services/CardService.ts` -- listar() static
- `src/lib/mocks/cards.mock.ts` -- 8-12 cards realistas distribuidos nas 6 colunas

**O que o dev ADICIONA:**
- `src/lib/stores/board.ts` -- cardsByColumn derived, filteredCards derived
- `src/lib/components/kanban/KanbanColumn.svelte` -- renderizar KanbanCards dentro da coluna

**Dependencias:** F2.1 (Board visual)
**Criterio de pronto:** Board exibe cards mock nas colunas corretas. Badge de prioridade com cor certa. Avatares empilhados. Disciplina como tag. Data relativa. Filtros de busca/responsavel/prioridade funcionam sobre os cards mock. VITE_USE_MOCK=true.

**O que os outros devs estao fazendo:** Backend implementa CRUD de Cards (B3.1-B3.6). Frontend usa mock.

---

#### Dev Feature F3.2: Criar Card (modal)

**O que o dev CRIA:**
- `src/lib/dtos/CriarCardDTO.ts` -- readonly, constructor, isValid (titulo min 3), toPayload
- `src/lib/components/kanban/CardCreateModal.svelte` -- modal com formulario (titulo, copy, disciplina, tecnologia, prioridade, responsaveis)

**O que o dev ADICIONA:**
- `src/lib/repositories/CardRepository.ts` -- criar()
- `src/lib/services/CardService.ts` -- criar()
- `src/routes/kanban/+page.svelte` -- botao "Novo Card" abre CardCreateModal
- `src/lib/stores/board.ts` -- addCard()

**Dependencias:** F3.1 (Cards no Board)
**Criterio de pronto:** Botao "Novo Card" abre modal. Formulario valida titulo (min 3 chars). Submit com mock cria card na coluna Copy. Modal fecha. Board atualiza. Toast "Carrossel criado com sucesso." VITE_USE_MOCK=true.

---

#### Dev Feature F3.3: Detalhe do Card (modal com aba Detalhes)

**O que o dev CRIA:**
- `src/lib/dtos/EditarCardDTO.ts` -- readonly, constructor, isValid, toPayload
- `src/lib/components/kanban/CardDetailModal.svelte` -- modal com 3 abas (Detalhes ativo, Comentarios e Atividade como placeholder)
- `src/lib/components/kanban/CardDetailTab.svelte` -- aba com campos editaveis (titulo, copy, disciplina, tecnologia, prioridade, responsaveis) + campos readonly (coluna, criado_por, datas, links)

**O que o dev ADICIONA:**
- `src/lib/repositories/CardRepository.ts` -- buscar(), editar()
- `src/lib/services/CardService.ts` -- buscar(), editar()
- `src/routes/kanban/+page.svelte` -- clique no KanbanCard abre CardDetailModal + query param ?card=id

**Dependencias:** F3.1 (Cards no Board)
**Criterio de pronto:** Clique no card abre modal com 3 abas. Aba Detalhes mostra campos editaveis e readonly. Editar titulo/prioridade funciona com mock. Salvar atualiza card no board. URL muda para ?card=id. Fechar modal remove query param. Viewer ve tudo disabled. VITE_USE_MOCK=true.

---

#### Dev Feature F3.4: Drag-and-Drop para Cancelado

**O que o dev CRIA:**
- Nenhum arquivo novo

**O que o dev ADICIONA:**
- `src/lib/components/kanban/KanbanCard.svelte` -- draggable
- `src/lib/components/kanban/KanbanColumn.svelte` -- drop zone (so coluna Cancelado aceita drop)
- `src/lib/repositories/CardRepository.ts` -- mover()
- `src/lib/services/CardService.ts` -- mover()
- `src/lib/stores/board.ts` -- moveCard() (optimistic update)

**Dependencias:** F3.1 (Cards no Board)
**Criterio de pronto:** Card e arrastavel. Somente coluna Cancelado aceita drop (borda dashed vermelha ativa). Demais colunas nao aceitam. Card arrastado com opacity-50 + rotate-2 + scale-105. Ao soltar: card move para Cancelado (optimistic). Toast "Carrossel movido para Cancelado." Viewer nao pode arrastar. VITE_USE_MOCK=true.

---

### PACOTE BACK-4 -- Dominio: Comment

**Pode comecar apos:** PACOTE BACK-3 (Card -- pelo menos B3.1 e B3.3)

**Casos de uso (dev features):**

#### Dev Feature B4.1: Criar Comentario

**O que o dev CRIA:**
- `dtos/kanban_comment/base.py` -- ComentarioBase
- `dtos/kanban_comment/criar_comentario/request.py` -- CriarComentarioRequest (text)
- `dtos/kanban_comment/criar_comentario/response.py` -- ComentarioResponse (id, card_id, user_id, user_name, user_avatar, text, created_at)
- `factories/kanban_comment_factory.py` -- KanbanCommentFactory.create_comment_doc()
- `mappers/kanban_comment_mapper.py` -- to_comentario_response()
- `services/kanban_comment_service.py` -- criar_comentario()
- `routers/kanban_comment.py` -- POST /api/kanban/cards/{card_id}/comments
- `data/repositories/mongo/kanban_comment_repository.py` -- insert_comment()

**O que o dev ADICIONA:**
- `factories/kanban_activity_factory.py` -- create_comment_added_log()

**Dependencias:** B3.3 (Buscar Card -- para validar que card existe)
**Criterio de pronto:** POST /api/kanban/cards/{card_id}/comments cria comentario. Retorna 201 + ComentarioResponse. Registra "comment_added" no audit log. Viewer retorna 403. Card inexistente retorna 404.

---

#### Dev Feature B4.2: Listar Comentarios

**O que o dev CRIA:**
- `dtos/kanban_comment/listar_comentarios/response.py` -- ListarComentariosResponse

**O que o dev ADICIONA:**
- `services/kanban_comment_service.py` -- listar_comentarios()
- `routers/kanban_comment.py` -- GET /api/kanban/cards/{card_id}/comments
- `data/repositories/mongo/kanban_comment_repository.py` -- find_by_card()

**Dependencias:** B4.1 (Criar Comentario)
**Criterio de pronto:** GET /api/kanban/cards/{card_id}/comments retorna comentarios em ordem cronologica. Exclui comentarios com deleted_at. Inclui nome e avatar do autor.

---

#### Dev Feature B4.3: Editar + Deletar Comentario

**O que o dev CRIA:**
- `dtos/kanban_comment/editar_comentario/request.py` -- EditarComentarioRequest (text)

**O que o dev ADICIONA:**
- `services/kanban_comment_service.py` -- editar_comentario(), deletar_comentario()
- `routers/kanban_comment.py` -- PATCH /api/kanban/comments/{comment_id}, DELETE /api/kanban/comments/{comment_id}
- `data/repositories/mongo/kanban_comment_repository.py` -- update_comment(), soft_delete()
- `factories/kanban_activity_factory.py` -- create_comment_edited_log(), create_comment_deleted_log()

**Regras de negocio:**
- Editar/deletar so pelo autor (RN-005)
- Admin pode deletar qualquer comentario (RN-005)

**Dependencias:** B4.2 (Listar Comentarios)
**Criterio de pronto:** Autor edita/deleta proprio comentario. Admin deleta qualquer comentario. Outro usuario retorna 403. Soft delete (deleted_at). Registra no audit log.

---

### PACOTE FRONT-4 -- Dominio: Comment

**Pode comecar apos:** PACOTE FRONT-3 (Card -- pelo menos F3.3 modal com abas)

**Casos de uso (dev features):**

#### Dev Feature F4.1: Aba Comentarios (no modal do Card)

**O que o dev CRIA:**
- `src/lib/dtos/CommentDTO.ts` -- readonly, constructor, isValid, toPayload
- `src/lib/dtos/CriarComentarioDTO.ts` -- readonly, constructor, isValid (text min 1), toPayload
- `src/lib/components/kanban/CardCommentsTab.svelte` -- lista de comentarios + campo novo comentario
- `src/lib/components/kanban/CommentItem.svelte` -- 1 comentario (avatar, nome, data, texto, botoes editar/deletar)
- `src/lib/repositories/CommentRepository.ts` -- listar(), criar(), editar(), deletar() com mock/real
- `src/lib/services/CommentService.ts` -- metodos static
- `src/lib/mocks/comments.mock.ts` -- 5 comentarios mock realistas

**O que o dev ADICIONA:**
- `src/lib/components/kanban/CardDetailModal.svelte` -- integrar CardCommentsTab na aba "Comentarios"

**Dependencias:** F3.3 (Modal do Card com abas)
**Criterio de pronto:** Aba Comentarios exibe lista mock. Campo de novo comentario funciona. Editar inline funciona. Deletar com confirmacao. Botao editar visivel so para autor. Botao deletar visivel para autor + Admin. Viewer nao ve campo de novo comentario. Estado vazio "Nenhum comentario ainda." VITE_USE_MOCK=true.

**O que os outros devs estao fazendo:** Backend implementa CRUD de Comentarios (B4.1-B4.3). Frontend usa mock.

---

### PACOTE BACK-5 -- Dominio: Activity

**Pode comecar apos:** PACOTE BACK-3 (Card -- os registros de activity ja sao criados em B3.1, B3.4, B3.5, B3.6)

**Casos de uso (dev features):**

#### Dev Feature B5.1: Listar Atividades (Audit Log)

**O que o dev CRIA:**
- `dtos/kanban_activity/base.py` -- AtividadeBase
- `dtos/kanban_activity/listar_atividades/response.py` -- ListarAtividadesResponse (items paginados, total)
- `mappers/kanban_activity_mapper.py` -- to_atividade_response()
- `services/kanban_activity_service.py` -- listar_atividades()
- `routers/kanban_card.py` -- GET /api/kanban/cards/{card_id}/activity (adiciona rota ao router existente)
- `data/repositories/mongo/kanban_activity_repository.py` -- find_by_card() com paginacao (se nao existir; ja pode ter sido criado em B3)

**Nota:** A factory kanban_activity_factory.py e o repository de insert ja foram criados nos pacotes anteriores (B3.1 em diante). Este pacote so adiciona a leitura.

**Dependencias:** B3.1+ (Card -- activities ja existem no banco)
**Criterio de pronto:** GET /api/kanban/cards/{card_id}/activity retorna timeline paginada (default 20 por pagina, mais recente primeiro). Inclui nome do usuario que executou a acao. Metadata varia por tipo de acao.

---

### PACOTE FRONT-5 -- Dominio: Activity

**Pode comecar apos:** PACOTE FRONT-3 (Card -- modal com abas)

**Casos de uso (dev features):**

#### Dev Feature F5.1: Aba Atividade (no modal do Card)

**O que o dev CRIA:**
- `src/lib/dtos/ActivityDTO.ts` -- readonly, constructor, toPayload
- `src/lib/components/kanban/CardActivityTab.svelte` -- timeline vertical com linha conectora, icones por tipo, descricao, usuario, data
- `src/lib/repositories/ActivityRepository.ts` -- listar() com mock/real
- `src/lib/services/ActivityService.ts` -- listar() static
- `src/lib/mocks/activities.mock.ts` -- 8 atividades mock variadas (card_created, column_changed, field_edited, etc.)

**O que o dev ADICIONA:**
- `src/lib/components/kanban/CardDetailModal.svelte` -- integrar CardActivityTab na aba "Atividade"

**Dependencias:** F3.3 (Modal do Card com abas)
**Criterio de pronto:** Aba Atividade exibe timeline mock. Icones corretos por tipo de acao (conforme design). Descricoes auto-geradas ("Carlos moveu de Copy para Design"). Datas relativas. Botao "Carregar mais" funciona com mock. VITE_USE_MOCK=true.

**O que os outros devs estao fazendo:** Backend implementa leitura do audit log (B5.1). Frontend usa mock.

---

### PACOTE BACK-6 -- Dominio: Notification

**Pode comecar apos:** PACOTE BACK-3 (Card -- notificacoes ja sao criadas em B3.5, B3.6)

**Casos de uso (dev features):**

#### Dev Feature B6.1: Listar Notificacoes + Contar Nao-Lidas

**O que o dev CRIA:**
- `dtos/kanban_notification/base.py` -- NotificacaoBase
- `dtos/kanban_notification/listar_notificacoes/response.py` -- ListarNotificacoesResponse
- `dtos/kanban_notification/contar_nao_lidas/response.py` -- ContadorNaoLidasResponse
- `mappers/kanban_notification_mapper.py` -- to_notificacao_response()
- `services/kanban_notification_service.py` -- listar_notificacoes(), contar_nao_lidas()
- `routers/kanban_notification.py` -- GET /api/kanban/notifications, GET /api/kanban/notifications/count
- `data/repositories/mongo/kanban_notification_repository.py` -- find_by_user(), count_unread() (se nao existir)

**Dependencias:** B3.5+ (Mover Card -- notificacoes ja existem no banco)
**Criterio de pronto:** GET /api/kanban/notifications retorna ultimas 20 notificacoes do usuario. GET /api/kanban/notifications/count retorna contador de nao-lidas. Filtra por tenant_id e user_id do JWT.

---

#### Dev Feature B6.2: Marcar como Lida + Marcar Todas

**O que o dev ADICIONA:**
- `services/kanban_notification_service.py` -- marcar_como_lida(), marcar_todas_lidas()
- `routers/kanban_notification.py` -- PATCH /api/kanban/notifications/{id}/read, POST /api/kanban/notifications/read-all
- `data/repositories/mongo/kanban_notification_repository.py` -- mark_read(), mark_all_read()

**Dependencias:** B6.1 (Listar Notificacoes)
**Criterio de pronto:** PATCH marca 1 notificacao como lida. POST marca todas do usuario como lidas. Contador diminui ao marcar.

---

### PACOTE FRONT-6 -- Dominio: Notification

**Pode comecar apos:** PACOTE FRONT-1 (Auth -- precisa do header/layout)

**Casos de uso (dev features):**

#### Dev Feature F6.1: Badge + Dropdown de Notificacoes

**O que o dev CRIA:**
- `src/lib/dtos/NotificationDTO.ts` -- readonly, constructor, isValid
- `src/lib/components/notification/NotificationBell.svelte` -- icone sino + badge numerico (max 9+)
- `src/lib/components/notification/NotificationDropdown.svelte` -- dropdown com lista de notificacoes, indicador lida/nao-lida, "Marcar todas como lidas"
- `src/lib/repositories/NotificationRepository.ts` -- listar(), contarNaoLidas(), marcarLida(), marcarTodasLidas() com mock/real
- `src/lib/services/NotificationService.ts` -- metodos static
- `src/lib/mocks/notifications.mock.ts` -- 5 notificacoes mock (assigned, column_changed)

**O que o dev ADICIONA:**
- `src/routes/+layout.svelte` -- NotificationBell no header direito
- `src/lib/stores/notifications.ts` -- unreadCount, fetchUnreadCount()

**Dependencias:** F1.1 (Login, auth store para user_id)
**Criterio de pronto:** Sino com badge visivel no header em todas as rotas (quando logado). Clique abre dropdown. Notificacoes mock exibidas com icone, mensagem, data relativa, indicador lida/nao-lida. Clicar em notificacao marca como lida e navega para /kanban?card=id. "Marcar todas como lidas" zera badge. Badge oculto quando zero. VITE_USE_MOCK=true.

---

### PACOTE BACK-7 -- Dominio: Pipeline Integration

**Pode comecar apos:** PACOTE BACK-3 (Card -- precisa de criar_card e mover_card)

**Casos de uso (dev features):**

#### Dev Feature B7.1: Criar Card Automatico ao Gerar Conteudo

**O que o dev CRIA:**
- `dtos/kanban_card/vincular_artefato/request.py` -- VincularArtefatoRequest (drive_link, drive_folder_name, pdf_url, image_urls)
- `dtos/kanban_card/vincular_artefato/response.py` -- CardResponse (reutiliza)

**O que o dev ADICIONA:**
- `routers/conteudo.py` -- apos gerar conteudo, chamar kanban_card_service.criar_card() automaticamente (RN-009)
- `services/kanban_card_service.py` -- criar_card_pipeline() (variante que recebe pipeline_id e dados do conteudo gerado)

**Dependencias:** B3.1 (Criar Card), routers/conteudo.py existente
**Criterio de pronto:** POST /api/gerar-conteudo e POST /api/gerar-conteudo-cli criam automaticamente um card na coluna "Copy" com titulo e copy_text do conteudo gerado. pipeline_id vinculado. Audit log registra "card_created".

---

#### Dev Feature B7.2: Mover Card Automatico ao Gerar Imagens

**O que o dev ADICIONA:**
- `routers/imagem.py` -- apos gerar imagens, chamar kanban_card_service.mover_card_pipeline() para "Design" (RN-010)
- `services/kanban_card_service.py` -- mover_card_pipeline() (movimentacao interna, sem restricao de RN-019)
- `services/kanban_card_service.py` -- vincular_artefato() para image_urls

**Dependencias:** B3.5 (Mover Card), routers/imagem.py existente
**Criterio de pronto:** POST /api/gerar-imagem e POST /api/gerar-imagem-slide movem card vinculado para coluna "Design" automaticamente. image_urls atualizadas no card.

---

#### Dev Feature B7.3: Vincular Drive Link ao Salvar no Drive

**O que o dev ADICIONA:**
- `routers/drive.py` -- apos salvar no Drive, chamar kanban_card_service.vincular_artefato() (RN-011)
- `services/kanban_card_service.py` -- vincular_artefato()
- `data/repositories/mongo/kanban_card_repository.py` -- update_artefatos()

**Dependencias:** B3.3 (Buscar Card), routers/drive.py existente
**Criterio de pronto:** POST /api/google-drive/carrossel vincula drive_link e drive_folder_name ao card. Registra "drive_linked" no audit log.

---

## 5. SPRINT PLANNING SUGERIDO

### Sprint 0 (Semana 1): Base + Infra

| Time | Dev Features | Entregavel |
|------|-------------|------------|
| Backend | Pacote Base Backend | MongoDB configurado, scripts executaveis, middleware auth funcional |
| Frontend | Pacote Base Frontend | DTOs Auth, stores, auth guard, tokens CSS, mocks base |

**Criterio de sprint pronta:** Scripts MongoDB rodam sem erro. Frontend redireciona para /login quando nao autenticado.

---

### Sprint 1 (Semana 2): Auth

| Time | Dev Features | Entregavel |
|------|-------------|------------|
| Backend | B1.1, B1.2, B1.3, B1.4 | Login funcional, Me, CRUD usuario basico |
| Frontend | F1.1, F1.3 | Tela login com mock, Tela usuarios com mock |

**Criterio de sprint pronta:** Login funciona ponta a ponta (backend + frontend integrados ao final da sprint). Admin cria/lista usuarios.

---

### Sprint 2 (Semana 3): Auth completo + Board

| Time | Dev Features | Entregavel |
|------|-------------|------------|
| Backend | B1.5, B1.6, B2.1 | Convite, CRUD usuario completo, Board padrao |
| Frontend | F1.2, F2.1 | SSO buttons, Board visual com 6 colunas vazias |

**Criterio de sprint pronta:** Board Kanban visivel no frontend (mock). Backend serve board padrao via API.

---

### Sprint 3 (Semana 4): Card CRUD

| Time | Dev Features | Entregavel |
|------|-------------|------------|
| Backend | B3.1, B3.2, B3.3, B3.4 | Criar/listar/buscar/editar card |
| Frontend | F3.1, F3.2 | Cards no board (mock), modal criar card |

**Criterio de sprint pronta:** Cards aparecem no board. Criar card via modal funciona. Integracao backend-frontend no final da sprint.

---

### Sprint 4 (Semana 5): Card movimentacao + Modal detalhe

| Time | Dev Features | Entregavel |
|------|-------------|------------|
| Backend | B3.5, B3.6 | Mover card, atribuir responsaveis |
| Frontend | F3.3, F3.4 | Modal detalhe (aba Detalhes), drag para Cancelado |

**Criterio de sprint pronta:** Drag-and-drop para Cancelado funciona. Modal de detalhe abre com campos editaveis. Integracao completa card backend-frontend.

---

### Sprint 5 (Semana 6): Comment + Activity + Notification

| Time | Dev Features | Entregavel |
|------|-------------|------------|
| Backend | B4.1, B4.2, B4.3, B5.1 | CRUD comentarios, audit log leitura |
| Frontend | F4.1, F5.1, F6.1 | Aba comentarios, aba atividade, notificacoes |

**Criterio de sprint pronta:** Modal do card com 3 abas funcionais. Notificacoes no header. Tudo integrado ponta a ponta.

---

### Sprint 6 (Semana 7): Notification backend + Pipeline Integration

| Time | Dev Features | Entregavel |
|------|-------------|------------|
| Backend | B6.1, B6.2, B7.1, B7.2, B7.3 | Notificacoes API, pipeline cria/move cards automaticamente |
| Frontend | Integracao final, testes, polish | Remover mocks, conectar tudo ao backend real |

**Criterio de sprint pronta:** Fluxo completo E2E: gerar conteudo cria card em Copy, gerar imagens move para Design, salvar Drive vincula link. Notificacoes funcionais.

---

### Sprint 7 (Semana 8): SSO + QA + Polish

| Time | Dev Features | Entregavel |
|------|-------------|------------|
| Backend | B1.7 (SSO Google/Microsoft) | Login SSO funcional |
| Frontend | Responsividade mobile, estados vazios/erro, acessibilidade | Tudo polido |
| QA | Testes unitarios + integracao + E2E | Cobertura completa |

---

## 6. RISCOS E DEPENDENCIAS

### Riscos Tecnicos

| ID | Risco | Impacto | Mitigacao |
|----|-------|---------|-----------|
| R1 | SSO Google/Microsoft requer client_id/secret e dominio verificado | Bloqueia login SSO | Implementar SSO por ultimo (B1.7). Email+senha funciona independente. |
| R2 | Drag-and-drop no mobile pode ter UX ruim | Experiencia degradada no mobile | Testar em Sprint 4. Se ruim, adicionar botao "Cancelar" como alternativa ao drag. |
| R3 | Pipeline integration modifica routers existentes (conteudo, imagem, drive) | Risco de regressao no sistema atual | Fazer em sprint separada (Sprint 6). Testes de regressao obrigatorios. |
| R4 | MongoDB sem transacoes: mover card + criar activity nao e atomico | Inconsistencia possivel (raro) | Aceitar no MVP. Usar try/except com compensacao se activity falhar. |
| R5 | JWT sem refresh token: usuario perde sessao a cada 24h | UX ruim para uso prolongado | Aceitar no MVP (PRD define refresh token como pos-MVP). |

### Dependencias entre Times

| Dependencia | Frontend espera por | Backend espera por |
|-------------|--------------------|--------------------|
| Login funcional | B1.1 pronto para integrar (Sprint 1) | -- |
| Board com cards | B2.1 + B3.2 prontos (Sprint 3) | -- |
| Drag funcional E2E | B3.5 pronto (Sprint 4) | -- |
| Comentarios E2E | B4.1 + B4.2 prontos (Sprint 5) | -- |
| Notificacoes E2E | B6.1 + B6.2 prontos (Sprint 6) | -- |
| Pipeline integration | -- | Routers existentes (conteudo, imagem, drive) estaveis |

### Regra de ouro: Frontend trabalha com VITE_USE_MOCK=true ate o backend da sprint estar pronto. Integracao real acontece no final de cada sprint.

---

## 7. RESUMO QUANTITATIVO

| Metrica | Valor |
|---------|-------|
| Dominios | 7 (Auth, Board, Card, Comment, Activity, Notification, Pipeline) |
| Dev Features Backend | 20 |
| Dev Features Frontend | 11 |
| Total Dev Features | 31 |
| Sprints estimadas | 7-8 semanas |
| Collections MongoDB | 7 |
| Rotas API novas | 26 |
| Telas novas | 3 (Login, Board Kanban, Usuarios) |
| Componentes novos | 17 |
| DTOs Frontend | 13 |
| DTOs Backend | ~30 arquivos (request + response por caso de uso) |
