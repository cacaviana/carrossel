# TELAS -- Kanban Pipeline de Carrosseis

Documento de telas gerado pelo Agente 02 (Analista de Tela).
Base: PRD Kanban Pipeline (`docs/prd-kanban-pipeline.md`) + analise das telas e navegacao existentes no frontend SvelteKit 5.

---

## Sumario de Telas

| # | Tela | Rota | Status | Observacao |
|---|------|------|--------|------------|
| 1 | Login | `/login` | Nova | Email+senha + SSO Google/Microsoft. Unica tela publica (sem autenticacao). |
| 2 | Board Kanban | `/kanban` | Nova | Quadro visual com 6 colunas fixas, cards, drag-and-drop (so para Cancelado). |
| 3 | Detalhe do Card (Modal/Drawer) | `/kanban` (overlay) | Nova | Modal sobre o board com 3 abas: Detalhes, Comentarios, Atividade. |
| 4 | Gerenciamento de Usuarios | `/kanban/usuarios` | Nova | CRUD de usuarios, convite, atribuicao de perfil. Somente Admin. |
| 5 | Notificacoes (Dropdown) | Global (header/sidebar) | Nova | Badge com contador + dropdown com lista de notificacoes. |

---

## Navegacao Global -- Integracoes com Sistema Existente

O sistema existente usa Sidebar (`Sidebar.svelte`) com 3 secoes: Principal, Formatos, Sistema. O Kanban se integra adicionando itens a essa sidebar.

### Alteracoes na Sidebar

| Secao | Item Novo | Rota | Icone | Observacao |
|-------|-----------|------|-------|------------|
| Principal | Kanban | `/kanban` | Icone de quadro/board (ViewColumns) | Entre "Home" e "Historico" |
| Sistema | Usuarios | `/kanban/usuarios` | Icone de usuarios (UserGroup) | Visivel somente para Admin |

### Alteracoes no Header/Layout

| Elemento | Posicao | Descricao |
|----------|---------|-----------|
| Badge de notificacoes | Header direito (desktop) / Header direito (mobile) | Icone de sino com badge numerico de nao-lidas. Clica para abrir dropdown. |
| Avatar do usuario logado | Header direito, apos notificacoes | Iniciais ou foto. Clica para menu: "Meu Perfil", "Sair". |

### Guarda de Rotas (Auth Guard)

| Rota | Sem autenticacao | Comportamento |
|------|------------------|---------------|
| `/login` | Acessivel | Se ja logado, redireciona para `/` |
| Todas as demais | Bloqueada | Redireciona para `/login` |

---

## Telas Detalhadas

---

### TELA: Login

**Rota:** `/login`
**Perfis com acesso:** Publico (sem autenticacao)
**Descricao:** O usuario se autentica para acessar o sistema. Suporta dois metodos: email+senha com validacao de senha forte, e SSO via Google ou Microsoft (OAuth2). Apos login bem-sucedido, redireciona para a pagina anterior ou `/`.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| email | text (email) | S | Formato email valido (regex) | formulario |
| senha | text (password) | S | Min 8 chars, 1 maiuscula, 1 numero, 1 caractere especial (RN-021) | formulario |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Entrar (email+senha) | submit do formulario | Envia POST /api/auth/login. Sucesso: salva JWT no localStorage, redireciona para `/` ou rota anterior. Erro: exibe mensagem. |
| Entrar com Google | clique no botao "Entrar com Google" | Inicia fluxo OAuth2 Google. Redireciona para consent screen do Google. Callback salva JWT e redireciona. |
| Entrar com Microsoft | clique no botao "Entrar com Microsoft" | Inicia fluxo OAuth2 Microsoft. Redireciona para consent screen da Microsoft. Callback salva JWT e redireciona. |
| Mostrar/ocultar senha | clique no icone de olho | Alterna entre type="password" e type="text" no campo senha |

#### Estados da Tela

- **Loading:** Spinner no botao "Entrar" enquanto aguarda resposta do backend. Botoes SSO tambem ficam desabilitados durante loading.
- **Vazio:** Estado inicial. Formulario vazio, botoes habilitados, sem mensagens.
- **Erro:** Mensagem vermelha abaixo do formulario. Casos: "Email ou senha incorretos" (401), "Conta bloqueada" (429 -- rate limit: 5 tentativas/minuto), "Erro de conexao" (network). Campo com erro recebe borda vermelha.
- **Sucesso:** Breve feedback visual (opcional) e redirecionamento imediato.

#### Fluxos de Navegacao

- Submit com sucesso --> `/` (ou rota protegida que originou o redirect)
- SSO com sucesso --> `/` (ou rota protegida que originou o redirect)
- Nao ha link de "Criar conta" (cadastro e feito pelo Admin via convite)
- Nao ha "Esqueci a senha" no MVP

---

### TELA: Board Kanban

**Rota:** `/kanban`
**Perfis com acesso:** Admin, Copywriter, Designer, Reviewer, Viewer
**Descricao:** Quadro visual estilo Kanban com 6 colunas fixas representando as etapas da pipeline de producao de carrosseis. Cada card representa um carrossel em producao. A movimentacao entre colunas e predominantemente automatica (via pipeline). A unica movimentacao manual permitida e arrastar qualquer card para a coluna "Cancelado" (RN-019). Viewer ve tudo mas nao interage.

#### Campos (Barra de Filtros)

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| busca | text (search) | N | Busca por texto no titulo do card | formulario |
| filtro_responsavel | select (dropdown) | N | Lista de usuarios do tenant | API (GET /api/kanban/users) |
| filtro_coluna | select (multi-check) | N | Opcoes fixas: Copy, Design, Revisao, Aprovado, Publicado, Cancelado | hardcoded |
| filtro_prioridade | select (dropdown) | N | Opcoes: Alta, Media, Baixa | hardcoded |

#### Estrutura do Board

| Coluna | Cor Sugerida | Cards Visiveis | Observacao |
|--------|-------------|----------------|------------|
| Copy | Azul | Cards com conteudo gerado, aguardando design | Criacao automatica ao gerar conteudo (RN-009) |
| Design | Roxo | Cards com imagens em producao | Movimentacao automatica ao gerar imagens (RN-010) |
| Revisao | Amarelo | Cards aguardando revisao humana | Movimentacao automatica ao exportar PDF |
| Aprovado | Verde | Cards aprovados, aguardando publicacao | Movimentacao automatica pelo Reviewer |
| Publicado | Verde escuro | Cards publicados (terminal, RN-007) | Terminal -- nao pode mover para frente |
| Cancelado | Vermelho/cinza | Cards descartados (terminal, RN-007) | Unica coluna que recebe drag manual (RN-019) |

#### Anatomia do Card (no Board)

Cada card exibido no board mostra um resumo compacto:

| Elemento | Descricao |
|----------|-----------|
| Titulo | Texto principal, truncado se longo |
| Prioridade | Badge colorido: alta (vermelho), media (amarelo), baixa (cinza) |
| Avatares dos responsaveis | Circulos empilhados com iniciais ou foto. Max 3 visiveis + "+N" |
| Disciplina | Tag pequena (ex: "NLP", "Deep Learning") |
| Indicador de comentarios | Icone de balao + contagem, se houver comentarios |
| Data de criacao | Texto discreto com data relativa ("ha 2 dias") |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado | Perfis |
|------|---------|-----------|--------|
| Abrir detalhe do card | clique no card | Abre modal/drawer de detalhe (Tela 3) | Todos |
| Arrastar card para Cancelado | drag-and-drop | Move card para coluna Cancelado. Optimistic update no frontend, sync com backend. Registra no audit log (RN-002). | Admin, Copywriter, Designer, Reviewer |
| Filtrar cards | change em qualquer filtro | Re-renderiza o board mostrando apenas cards que atendem os filtros | Todos |
| Limpar filtros | clique em "Limpar filtros" | Remove todos os filtros ativos, mostra todos os cards | Todos |
| Criar card manual | clique no botao "+" ou "Novo Card" | Abre modal de criacao de card (formulario simples) | Admin, Copywriter |
| Atualizar board | clique no botao de refresh | Refetch dos dados do board (polling manual, sem websockets no MVP) | Todos |

#### Estados da Tela

- **Loading:** Skeleton das 6 colunas com placeholders de cards (shimmer effect). Aparece no carregamento inicial e ao trocar filtros.
- **Vazio (board sem cards):** Board com 6 colunas vazias. Mensagem central: "Nenhum carrossel em producao. Crie um conteudo na Home para comecar." com link para `/`.
- **Vazio (filtro sem resultado):** Board com colunas vazias. Mensagem: "Nenhum card encontrado para esses filtros." com botao "Limpar filtros".
- **Erro:** Banner de erro no topo do board: "Erro ao carregar o board. Tente novamente." com botao "Tentar novamente".
- **Sucesso (estado normal):** Board com cards distribuidos nas colunas. Drag-and-drop ativo (somente para Cancelado).

#### Fluxos de Navegacao

- Clique no card --> Modal de Detalhe do Card (overlay, mesma rota)
- Clique em "Novo Card" --> Modal de Criacao (overlay, mesma rota)
- Link na sidebar --> Outras rotas do sistema (Home, Historico, Config, etc.)

---

### TELA: Detalhe do Card (Modal/Drawer)

**Rota:** `/kanban` (overlay -- nao muda a URL)
**Perfis com acesso:** Admin, Copywriter, Designer, Reviewer, Viewer (leitura)
**Descricao:** Modal ou drawer lateral que exibe todas as informacoes de um card de carrossel. Organizado em 3 abas: Detalhes (dados e campos editaveis), Comentarios (comunicacao entre equipe), Atividade (audit log automatico). Viewer ve tudo mas nao edita.

#### Aba 1: Detalhes

##### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem | Editavel por |
|-------|------|-------------|-----------|--------|--------------|
| titulo | text | S | Min 3 caracteres | API (card) / formulario | Admin, Copywriter |
| copy_text | textarea | N | -- | API (card) / formulario | Admin, Copywriter |
| disciplina | select | N | Lista de disciplinas do sistema | API (card) / store disciplinas | Admin, Copywriter |
| tecnologia | select | N | Depende da disciplina selecionada | API (card) / derivado | Admin, Copywriter |
| prioridade | select | S | Alta / Media / Baixa. Default: Media (RN-014) | API (card) / formulario | Admin, Copywriter, Designer, Reviewer |
| responsaveis | select (multi, autocomplete) | N | Lista de usuarios do tenant | API (users) | Admin |
| coluna_atual | text (readonly) | -- | -- | API (card.column_id) | Nao editavel (movimentacao automatica) |
| pipeline_id | text (readonly, link) | -- | -- | API (card.pipeline_id) | Nao editavel |
| drive_link | text (readonly, link externo) | -- | -- | API (card.drive_link) | Nao editavel (vinculado automaticamente, RN-011) |
| pdf_url | text (readonly, link) | -- | -- | API (card.pdf_url) | Nao editavel |
| imagens | galeria (thumbnails readonly) | -- | -- | API (card.image_urls) | Nao editavel |
| criado_por | text (readonly) | -- | -- | API (card.created_by) | Nao editavel |
| criado_em | text (readonly) | -- | -- | API (card.created_at) | Nao editavel |
| atualizado_em | text (readonly) | -- | -- | API (card.updated_at) | Nao editavel |

##### Acoes Disponiveis

| Acao | Gatilho | Resultado | Perfis |
|------|---------|-----------|--------|
| Salvar alteracoes | clique em "Salvar" ou blur de campo | PATCH no card. Registra no audit log. Feedback: toast de sucesso. | Admin, Copywriter, Designer (campos visuais) |
| Atribuir responsavel | change no select de responsaveis | PATCH no card. Notifica usuario atribuido. Registra no audit log. | Admin |
| Abrir no Drive | clique no link do Drive | Abre link externo em nova aba | Todos |
| Abrir pipeline | clique no link do pipeline | Navega para `/pipeline/[id]` | Todos |
| Fechar modal | clique no X ou clique fora | Fecha modal, volta ao board | Todos |

#### Aba 2: Comentarios

##### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| novo_comentario | textarea | S (para enviar) | Min 1 caractere | formulario |

##### Elementos da Lista de Comentarios

| Elemento | Descricao |
|----------|-----------|
| Avatar do autor | Circulo com iniciais ou foto |
| Nome do autor | Nome do usuario que comentou |
| Data/hora | Data relativa ("ha 5 min") com tooltip mostrando data absoluta |
| Texto do comentario | Corpo do comentario |
| Botao editar | Icone de lapis, visivel somente para o autor do comentario |
| Botao deletar | Icone de lixeira, visivel para o autor + Admin (RN-005) |

##### Acoes Disponiveis

| Acao | Gatilho | Resultado | Perfis |
|------|---------|-----------|--------|
| Enviar comentario | submit (botao ou Enter) | POST comentario. Aparece no topo/final da lista. Registra no audit log. | Admin, Copywriter, Designer, Reviewer |
| Editar comentario | clique no icone de editar | Campo de texto fica editavel inline. Botoes "Salvar" e "Cancelar". | Autor do comentario |
| Deletar comentario | clique no icone de lixeira | Confirmacao: "Tem certeza?" Sim: soft delete. Registra no audit log. | Autor do comentario, Admin (RN-005) |

##### Estados da Aba

- **Loading:** Spinner na area de comentarios enquanto carrega.
- **Vazio:** Mensagem: "Nenhum comentario ainda. Seja o primeiro a comentar."
- **Erro:** Mensagem inline: "Erro ao carregar comentarios." com botao "Tentar novamente".
- **Sucesso:** Lista cronologica de comentarios com campo de novo comentario visivel.

#### Aba 3: Atividade (Audit Log)

##### Elementos da Timeline

| Elemento | Descricao |
|----------|-----------|
| Icone da acao | Icone diferente por tipo: seta (movimentacao), lapis (edicao), usuario (atribuicao), balao (comentario), imagem (geracao), link (drive) |
| Descricao da acao | Texto automatico. Ex: "Carlos moveu de Copy para Design", "Ana editou o titulo", "Sistema vinculou link do Drive" |
| Data/hora | Data relativa com tooltip absoluto |
| Usuario | Nome de quem executou a acao (ou "Sistema" para acoes automaticas da pipeline) |

##### Acoes Disponiveis

| Acao | Gatilho | Resultado | Perfis |
|------|---------|-----------|--------|
| Carregar mais | scroll ao final ou botao "Carregar mais" | Paginacao: busca proxima pagina de atividades | Todos |

##### Estados da Aba

- **Loading:** Spinner na area de timeline.
- **Vazio:** Mensagem: "Nenhuma atividade registrada." (caso improvavel -- card sempre tem ao menos "card_created")
- **Erro:** Mensagem inline: "Erro ao carregar atividades." com botao "Tentar novamente".
- **Sucesso:** Timeline vertical com entries em ordem cronologica decrescente (mais recente primeiro).

#### Fluxos de Navegacao

- Fechar modal --> Board Kanban (Tela 2)
- Clique no link do Drive --> Nova aba (link externo)
- Clique no link do Pipeline --> `/pipeline/[id]`

---

### TELA: Criar Card (Modal)

**Rota:** `/kanban` (overlay -- nao muda a URL)
**Perfis com acesso:** Admin, Copywriter
**Descricao:** Modal simples para criacao manual de um card. Cards tambem sao criados automaticamente pela pipeline (RN-009), mas este modal permite criacao manual quando necessario. O card e criado sempre na coluna "Copy".

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| titulo | text | S | Min 3 caracteres | formulario |
| copy_text | textarea | N | -- | formulario |
| disciplina | select | N | Lista de disciplinas do sistema | store disciplinas |
| tecnologia | select | N | Depende da disciplina selecionada | derivado de disciplina |
| prioridade | select | S | Alta / Media / Baixa. Default: Media | formulario |
| responsaveis | select (multi, autocomplete) | N | Lista de usuarios do tenant | API (users) |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Criar card | submit | POST /api/kanban/cards. Card criado na coluna "Copy". Registra no audit log. Fecha modal. Card aparece no board. |
| Cancelar | clique em "Cancelar" ou X | Fecha modal sem salvar |

#### Estados da Tela

- **Loading:** Spinner no botao "Criar" enquanto aguarda resposta.
- **Vazio:** Estado inicial. Campos vazios, prioridade pre-selecionada "Media".
- **Erro:** Mensagem de erro abaixo do formulario (ex: "Titulo obrigatorio", "Erro ao criar card").
- **Sucesso:** Modal fecha. Toast de sucesso no board: "Card criado com sucesso."

#### Fluxos de Navegacao

- Criar com sucesso --> Fecha modal, board atualizado
- Cancelar --> Fecha modal, sem alteracoes

---

### TELA: Gerenciamento de Usuarios

**Rota:** `/kanban/usuarios`
**Perfis com acesso:** Admin
**Descricao:** Tela administrativa para gerenciar os usuarios do tenant. O Admin pode convidar novos usuarios (definindo nome, email e perfil), editar perfis existentes e desativar usuarios. Nao e acessivel para outros perfis (redirect para `/kanban` se nao-Admin tentar acessar).

#### Campos (Lista de Usuarios)

| Elemento | Descricao |
|----------|-----------|
| Avatar | Circulo com iniciais ou foto do usuario |
| Nome | Nome completo |
| Email | Email do usuario |
| Perfil (role) | Badge com cor: Admin (roxo), Copywriter (azul), Designer (rosa), Reviewer (amarelo), Viewer (cinza) |
| Status | Ativo / Desativado |
| Data de criacao | Data em que foi cadastrado |
| Acoes | Botoes: Editar, Desativar/Reativar |

#### Campos (Modal Convidar/Editar Usuario)

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| nome | text | S | Min 2 caracteres | formulario |
| email | text (email) | S | Formato email valido. Unico por tenant. | formulario |
| perfil | select | S | Opcoes: Admin, Copywriter, Designer, Reviewer, Viewer | formulario |
| avatar_url | text (URL) | N | URL valida (formato imagem) | formulario |

**Nota:** Na criacao, o Admin define uma senha temporaria OU o sistema envia um link de convite por email (decisao de implementacao a ser definida). No MVP, o Admin define a senha inicial e informa ao usuario por fora do sistema.

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Convidar usuario | clique em "Convidar Usuario" | Abre modal com formulario de novo usuario |
| Salvar novo usuario | submit no modal | POST /api/kanban/users. Usuario criado com perfil definido. Fecha modal. Lista atualizada. |
| Editar usuario | clique em "Editar" na linha | Abre modal com dados pre-preenchidos. Permite alterar nome, perfil, avatar. Email nao editavel. |
| Salvar edicao | submit no modal | PATCH /api/kanban/users/{id}. Atualiza dados. Fecha modal. |
| Desativar usuario | clique em "Desativar" | Confirmacao: "Desativar usuario? Ele perdera acesso ao sistema." Sim: soft delete (deleted_at). |
| Reativar usuario | clique em "Reativar" (usuario desativado) | Remove soft delete. Usuario volta a ter acesso. |

#### Estados da Tela

- **Loading:** Skeleton da tabela de usuarios com linhas placeholder.
- **Vazio:** Mensagem: "Nenhum usuario cadastrado alem de voce. Convide sua equipe." com botao "Convidar Usuario".
- **Erro:** Banner de erro: "Erro ao carregar usuarios." com botao "Tentar novamente".
- **Sucesso:** Tabela com lista de usuarios, barra de busca no topo, botao "Convidar Usuario" no canto superior direito.

#### Fluxos de Navegacao

- Sidebar --> Volta para qualquer rota do sistema
- Nao-Admin tenta acessar --> Redirect para `/kanban`

---

### TELA: Notificacoes (Dropdown)

**Rota:** Global (componente no header/sidebar, presente em todas as rotas)
**Perfis com acesso:** Todos (cada usuario ve suas proprias notificacoes)
**Descricao:** Componente de notificacoes internas. Aparece como icone de sino com badge numerico no header. Ao clicar, abre dropdown com lista das notificacoes recentes. No MVP, notifica sobre: card atribuido ao usuario e card do usuario que mudou de etapa.

#### Elementos do Badge

| Elemento | Descricao |
|----------|-----------|
| Icone de sino | Sempre visivel no header/sidebar |
| Badge numerico | Circulo vermelho com numero de nao-lidas. Oculto se zero. Max exibido: "9+" |

#### Elementos do Dropdown (Lista de Notificacoes)

| Elemento | Descricao |
|----------|-----------|
| Icone do tipo | Diferente por tipo: usuario (assigned), seta (column_changed) |
| Mensagem | Texto da notificacao. Ex: "Carlos atribuiu voce ao card 'NLP para devs'", "Card 'Deep Learning 101' moveu para Design" |
| Data/hora | Data relativa ("ha 3 min") |
| Indicador de lida/nao-lida | Bolinha azul para nao-lidas, ausente para lidas |
| Card de origem | Clicavel -- leva ao detalhe do card |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Abrir dropdown | clique no icone de sino | Mostra lista de notificacoes recentes (ultimas 20) |
| Fechar dropdown | clique fora ou Esc | Fecha dropdown |
| Clicar em notificacao | clique na notificacao | Marca como lida + abre detalhe do card (modal no board, ou navega para /kanban e abre modal) |
| Marcar todas como lidas | clique em "Marcar todas como lidas" | PATCH todas as notificacoes do usuario como is_read=true. Badge zera. |

#### Estados do Dropdown

- **Loading:** Spinner dentro do dropdown enquanto carrega.
- **Vazio:** Mensagem: "Nenhuma notificacao." Icone de sino sem badge.
- **Erro:** Mensagem: "Erro ao carregar notificacoes."
- **Sucesso (com nao-lidas):** Lista de notificacoes. Nao-lidas com fundo levemente destacado. Badge visivel.
- **Sucesso (todas lidas):** Lista de notificacoes. Sem badge. Todas com fundo normal.

#### Fluxos de Navegacao

- Clique em notificacao --> `/kanban` + abre modal do card referenciado
- "Marcar todas como lidas" --> Permanece no dropdown, badge zera

---

## Fluxos Criticos de Navegacao (End-to-End)

### Fluxo 1: Primeiro Acesso (Admin)

1. Admin acessa qualquer rota --> Auth guard redireciona para `/login`
2. Admin faz login (email+senha ou SSO) --> Redirect para `/`
3. Admin acessa `/kanban/usuarios` --> Convida Copywriter, Designer, Reviewer
4. Admin acessa `/kanban` --> Board vazio com 6 colunas

### Fluxo 2: Pipeline Automatica (Happy Path)

1. Copywriter acessa `/` --> Cria conteudo (gerar conteudo)
2. Pipeline gera conteudo --> Card criado AUTOMATICAMENTE na coluna "Copy" (RN-009)
3. Copywriter acessa `/kanban` --> Ve card na coluna Copy
4. Copywriter gera imagens no pipeline --> Card move AUTOMATICAMENTE para "Design" (RN-010)
5. Designer ve card em Design --> Ajusta se necessario
6. Pipeline exporta PDF --> Card move AUTOMATICAMENTE para "Revisao"
7. Reviewer abre card --> Revisa, sistema move para "Aprovado"
8. Pipeline publica --> Card move AUTOMATICAMENTE para "Publicado"
9. Admin salva no Drive --> Link e pasta vinculados ao card (RN-011)

### Fluxo 3: Cancelamento Manual

1. Qualquer usuario (exceto Viewer) ve card no board
2. Arrasta card para coluna "Cancelado" (unica acao manual de movimentacao, RN-019)
3. Confirmacao: "Cancelar este carrossel? Esta acao pode ser revertida por um Admin."
4. Card move para Cancelado. Audit log registra.

### Fluxo 4: Comunicacao via Comentarios

1. Designer abre card em Design --> Aba Comentarios
2. Escreve: "Imagem ficou com contraste baixo, vou regerar"
3. Comentario salvo, aparece na timeline
4. Copywriter recebe notificacao (badge no sino) ao acessar o sistema
5. Copywriter clica na notificacao --> Abre card, aba Comentarios

---

## Duvidas Tecnicas — Resolvidas

| ID | Duvida | Decisao |
|----|--------|---------|
| DT-001 | Como Admin convida usuario? | Sistema de InviteToken: Admin cria convite, gera token via `secrets.token_urlsafe(32)`, expira em 48h. Admin compartilha o link manualmente. Usuario acessa link, define propria senha (forte). Modelo InviteToken separado (id, user_id, token, expires_at, used). Sem servico de email no MVP. |
| DT-002 | Modal atualiza URL pra deep link? | Sim, `/kanban?card=abc123`. |
| DT-003 | Filtros persistem na URL? | Sim, query params. |
| DT-004 | Notificacao fora do /kanban? | Navega pra `/kanban?card=abc123`. |
| DT-005 | Auto-refresh ou manual? | Refresh MANUAL (botao). Sem polling automatico. |
| DT-006 | Cards cancelados visiveis por quanto tempo? | Ocultos apos 7 dias. Acessiveis via filtro explícito. |
| DT-007 | Viewer ve audit log completo? | Sim, tudo visivel. |

---

## Glossario

| Termo | Definicao |
|-------|-----------|
| Board | Quadro Kanban que contem as colunas e os cards de um tenant |
| Card | Representacao de um carrossel em producao dentro do board |
| Coluna | Etapa da pipeline no board (Copy, Design, Revisao, Aprovado, Publicado, Cancelado) |
| Pipeline | Fluxo automatizado de geracao de conteudo: conteudo (Claude) --> imagens (Gemini) --> PDF --> Drive |
| Tenant | Organizacao/workspace isolado. Todos os dados sao filtrados por tenant_id |
| Audit Log | Registro automatico e imutavel de todas as acoes executadas em um card |
| Optimistic Update | Tecnica de UI: atualiza visualmente antes de confirmar com o backend, revertendo em caso de erro |
| SSO | Single Sign-On: login via provedor externo (Google, Microsoft) |
| JWT | JSON Web Token: token de autenticacao com tenant_id + user_id + role no payload |
| ACL | Access Control List: controle de permissoes por perfil (Admin, Copywriter, Designer, Reviewer, Viewer) |
| Deep Link | URL que aponta diretamente para um recurso especifico (ex: card aberto no modal) |
| Soft Delete | Exclusao logica: campo deleted_at preenchido, registro permanece no banco |
