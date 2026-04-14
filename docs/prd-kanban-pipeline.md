# PRD - Kanban Pipeline de Carrosseis

## 1. Visao Geral

**Problema:** O sistema de carrosseis IT Valley atualmente opera como ferramenta individual: um usuario gera conteudo, edita, exporta e publica. Nao existe visibilidade compartilhada sobre o status de cada carrossel na pipeline de producao (copy, design, revisao, aprovacao, publicacao). Quando ha mais de uma pessoa envolvida -- copywriter, designer, revisor -- a coordenacao acontece por mensagens informais, sem rastreabilidade de quem fez o que e quando. Carrosseis se perdem, etapas sao puladas, e nao ha historico de decisoes.

**Solucao:** Adicionar ao sistema existente um modulo Kanban que trata cada carrossel como um card passando por etapas configuráveis da pipeline de producao. O modulo oferece: quadro visual com drag-and-drop, atribuicao de responsaveis, comentarios com mencoes, historico automatico de acoes (audit log), notificacoes internas e filtros por responsavel/etapa/data. O Kanban integra-se com a pipeline existente: gerar conteudo cria um card; gerar imagens avanca etapa; exportar PDF e salvar no Drive vincula os artefatos ao card.

**Usuarios-alvo:** Carlos Viana (admin/copywriter), designers contratados, revisores eventuais, visualizadores (clientes ou gestores que so acompanham).

**Multitenante:** Sim. O sistema ja possui tenant_id em toda tabela (TenantMixin). O Kanban segue o mesmo padrao: toda collection MongoDB tera tenant_id em todo documento e toda query filtra por tenant_id. Cada tenant ve apenas seus boards, cards e atividades.

## 2. Perfis de Usuario (ACL)

| Perfil | Descricao | Permissoes Principais |
|--------|-----------|----------------------|
| Admin | Dono do workspace. Configura boards, colunas, usuarios. | Tudo: CRUD board, CRUD colunas, CRUD cards, atribuir qualquer responsavel, deletar comentarios de terceiros, ver audit log completo, gerenciar perfis de usuario |
| Copywriter | Cria e edita o conteudo textual dos carrosseis. | Criar cards, editar copy dos cards atribuidos, mover cards entre Copy e Design, comentar, ver audit log dos seus cards |
| Designer | Responsavel pela geracao e ajuste das imagens. | Editar campos visuais dos cards atribuidos, mover cards entre Design e Revisao, comentar, fazer upload/re-gerar imagens |
| Reviewer | Revisa e aprova carrosseis. | Mover cards entre Revisao e Aprovado (ou devolver para etapas anteriores), comentar, ver todos os cards |
| Viewer | Visualizador somente leitura. | Ver board, ver cards, ver comentarios. Nao pode editar, mover, nem comentar. |

## 3. Modulos do Sistema

### Modulo Board (Quadro Kanban)

- **Descricao:** Gerencia o quadro Kanban e suas colunas. Cada tenant pode ter 1+ boards. As colunas representam etapas da pipeline e sao configuráveis (nome, ordem, cor).
- **Perfis com acesso:** Admin (CRUD completo), Copywriter/Designer/Reviewer (leitura), Viewer (leitura)
- **Funcionalidades:**
  - Criar/editar/arquivar board
  - CRUD de colunas: nome, ordem (drag para reordenar), cor opcional
  - Board padrao pre-configurado com colunas: Copy, Design, Revisao, Aprovado, Publicado
  - Visualizacao do board com todos os cards posicionados nas colunas

### Modulo Card (Carrossel como Card)

- **Descricao:** Cada card representa um carrossel em producao. Contem dados do conteudo, referencias, responsaveis, prioridade, e links para artefatos gerados (PDF, imagens, Drive).
- **Perfis com acesso:** Admin (tudo), Copywriter (criar, editar copy), Designer (editar campos visuais), Reviewer (mover para aprovado/devolver), Viewer (leitura)
- **Funcionalidades:**
  - Criar card manualmente ou automaticamente ao gerar conteudo na pipeline
  - Editar campos: titulo, copy text, referencias visuais, prioridade (alta/media/baixa), disciplina, tecnologia
  - Atribuir 1 ou mais responsaveis por card
  - Auto-assign opcional por etapa (ex: ao mover para Design, atribuir designer padrao)
  - Vincular artefatos: PDF exportado, link Google Drive, imagens geradas
  - Arrastar card entre colunas (drag-and-drop) -- muda status e registra no audit log
  - Visualizacao detalhada do card (modal/drawer) com abas: Detalhes, Comentarios, Atividade
  - Filtros no board: por responsavel, por coluna/etapa, por data de criacao, por prioridade, busca por texto no titulo/copy

### Modulo Comentarios

- **Descricao:** Sistema de comentarios por card para comunicacao entre os envolvidos na producao do carrossel.
- **Perfis com acesso:** Admin, Copywriter, Designer, Reviewer (CRUD nos proprios comentarios). Admin pode deletar comentarios de terceiros. Viewer nao comenta.
- **Funcionalidades:**
  - Adicionar comentario em texto livre
  - @mencao de usuarios (autocomplete ao digitar @)
  - Editar/deletar proprio comentario
  - Thread de respostas (reply to) -- 1 nivel de profundidade
  - Exibicao cronologica com avatar, nome, data/hora

### Modulo Historico de Acoes (Audit Log)

- **Descricao:** Registra automaticamente toda acao relevante em um card. Nenhuma acao manual -- o sistema grava ao detectar mudancas.
- **Perfis com acesso:** Admin (log completo de todos os cards), Copywriter/Designer/Reviewer (log dos cards que participam), Viewer (log dos cards que pode ver)
- **Funcionalidades:**
  - Registro automatico de: criacao do card, mudanca de coluna/etapa, mudanca de responsavel, edicao de campos (copy, titulo, prioridade), upload/re-geracao de imagem, adicao/edicao/exclusao de comentario, vinculacao de PDF/Drive link
  - Aba "Atividade" no detalhe do card com timeline visual
  - Cada entrada: acao, usuario, data/hora, metadata (ex: "moveu de Copy para Design")

### Modulo Notificacoes

- **Descricao:** Notifica usuarios sobre eventos relevantes nos cards em que estao envolvidos.
- **Perfis com acesso:** Todos os perfis (cada um recebe notificacoes dos cards que participa)
- **Funcionalidades:**
  - Notificacao interna (badge no sistema) quando: card atribuido ao usuario, usuario mencionado em comentario, card do usuario muda de etapa
  - Marcar como lida / marcar todas como lidas
  - Contador de nao-lidas visivel no header do sistema
  - Email opcional (fora do MVP)

### Modulo Autenticacao e Usuarios

- **Descricao:** Sistema de login e gerenciamento de usuarios para suportar multiusuario. Hoje o sistema nao tem autenticacao.
- **Perfis com acesso:** Admin (gerencia usuarios), todos (login)
- **Funcionalidades:**
  - Login por email + senha (hash bcrypt, JWT) com senha forte (min 8 chars, maiuscula, numero, caractere especial)
  - Login por SSO Google e Microsoft (OAuth2)
  - Cadastro de usuarios pelo Admin (convite)
  - Perfil do usuario: nome, email, avatar (URL), perfil ACL
  - JWT com tenant_id + user_id + role no payload
  - Middleware de autorizacao no backend (checa role por rota)
  - Tela de login no frontend
  - Persistencia da sessao (token no localStorage, refresh token opcional pos-MVP)

## 4. Regras de Negocio

| ID | Regra | Modulo |
|----|-------|--------|
| RN-001 | Todo card pertence a exatamente 1 board e esta em exatamente 1 coluna por vez | Card |
| RN-002 | Ao mover um card de coluna, o sistema registra automaticamente no audit log com usuario, coluna de origem e coluna de destino | Card / Audit Log |
| RN-003 | Um card pode ter 0 ou mais responsaveis. Se nenhum responsavel for atribuido, o card aparece como "nao atribuido" | Card |
| RN-004 | Se auto-assign estiver configurado para uma coluna, ao mover o card para essa coluna o(s) usuario(s) padrao sao adicionados como responsaveis (sem remover os existentes) | Card |
| RN-005 | Comentarios so podem ser editados/deletados pelo proprio autor, exceto Admin que pode deletar qualquer comentario | Comentarios |
| RN-006 | @mencoes em comentarios geram notificacao para o usuario mencionado | Comentarios / Notificacoes |
| RN-007 | A coluna "Publicado" e terminal: cards nessa coluna nao podem ser movidos para frente. A coluna "Cancelado" tambem e terminal. | Board |
| RN-008 | Viewer nao pode criar, editar, mover cards nem comentar. Apenas visualizar. | ACL |
| RN-009 | Ao gerar conteudo via pipeline (POST /api/gerar-conteudo ou gerar-conteudo-cli), o sistema CRIA automaticamente um card na coluna "Copy" | Integracao Pipeline |
| RN-010 | Ao gerar imagens de um card vinculado (POST /api/gerar-imagem), o card MOVE automaticamente para a coluna "Design" | Integracao Pipeline |
| RN-011 | Ao salvar no Google Drive, o link do Drive e o nome da pasta sao vinculados ao card automaticamente | Integracao Pipeline |
| RN-019 | A UNICA movimentacao MANUAL permitida e mover qualquer card para a coluna "Cancelado". Todas as outras movimentacoes sao automaticas via pipeline. | Card / Board |
| RN-020 | Colunas do MVP sao fixas: Copy, Design, Revisao, Aprovado, Publicado, Cancelado. Nao podem ser editadas/reordenadas/deletadas no MVP. | Board |
| RN-021 | Senha forte obrigatoria: minimo 8 caracteres, pelo menos 1 maiuscula, 1 numero, 1 caractere especial | Autenticacao |
| RN-022 | SSO Google e Microsoft disponivel como alternativa ao login email+senha | Autenticacao |
| RN-012 | Todo documento MongoDB do Kanban deve conter tenant_id. Toda query deve filtrar por tenant_id. | Todos |
| RN-013 | O audit log e append-only: registros nunca sao editados ou deletados | Audit Log |
| RN-014 | Prioridade do card aceita 3 valores: alta, media, baixa. Default: media | Card |
| RN-015 | Colunas tem ordem (inteiro). Ao reordenar, os valores de ordem sao recalculados. | Board |
| RN-016 | Um board deve ter no minimo 1 coluna. Nao e possivel deletar a ultima coluna. | Board |
| RN-017 | Deletar uma coluna so e permitido se ela nao contiver cards. Cards devem ser movidos antes. | Board |
| RN-018 | JWT expira em 24h. Apos expirar, o usuario deve fazer login novamente (refresh token e pos-MVP). | Autenticacao |

## 5. Integracoes Externas

| Sistema | Tipo | Finalidade |
|---------|------|-----------|
| Pipeline de Conteudo (interno) | Evento interno | Ao gerar conteudo via Claude API/CLI, criar card no Kanban automaticamente |
| Pipeline de Imagens (interno) | Evento interno | Ao gerar imagens via Gemini, atualizar card com referencia das imagens e opcionalmente avancar etapa |
| Google Drive (existente) | API REST (Google Drive API) | Ao salvar PDF/PNGs no Drive, vincular link e nome da pasta ao card |
| MongoDB Atlas / Cosmos DB | Driver nativo (pymongo) | Persistencia de boards, cards, comentarios, audit log, notificacoes, usuarios |

## 6. Requisitos Nao Funcionais

- **Performance:** Carregar board com ate 200 cards em menos de 2 segundos. Drag-and-drop com feedback visual instantaneo (otimistic update no frontend, sync com backend em background).
- **Seguranca:** Multitenante por tenant_id em toda collection e toda query. Autenticacao JWT. Senhas com hash bcrypt (nunca em texto plano). CORS restrito aos dominios do frontend. Rate limiting nas rotas de login (5 tentativas/minuto).
- **Escalabilidade:** Indices MongoDB em tenant_id + board_id + column_id para queries de board. Indice em tenant_id + card_id para audit log. Suportar ate 10 usuarios simultaneos no MVP (sem websockets -- polling ou refetch manual).
- **Disponibilidade:** Mesmo nivel do sistema atual (Azure App Service, single instance).
- **Observabilidade:** Logs estruturados no backend para acoes do Kanban (criacao, movimentacao, erros). Integrar com logging existente.

## 7. MVP - Escopo do Primeiro Lancamento

1. **Autenticacao:** login email+senha (senha forte) + SSO Google/Microsoft, JWT, cadastro de usuarios por Admin, 5 perfis (Admin, Copywriter, Designer, Reviewer, Viewer)
2. **Board Kanban:** 1 board padrao por tenant com 6 colunas fixas (Copy, Design, Revisao, Aprovado, Publicado, Cancelado)
3. **Cards:** CRUD completo, atribuicao de responsaveis, prioridade, drag-and-drop entre colunas
4. **Comentarios:** adicionar, editar, deletar (sem thread, sem @mencao no MVP)
5. **Audit Log:** registro automatico de criacao, mudanca de coluna, mudanca de responsavel, edicao de campos
6. **Filtros:** por responsavel, por coluna, por prioridade, busca por titulo
7. **Integracao pipeline:** criacao e movimentacao AUTOMATICA de cards. Gerar conteudo = cria card em Copy. Gerar imagens = move pra Design. Unica movimentacao manual = arrastar pra Cancelado.
8. **Notificacoes:** badge simples com contador de nao-lidas (card atribuido, card mudou de etapa)
9. **Frontend:** nova rota /kanban com board visual, modal de detalhe do card com abas (Detalhes, Comentarios, Atividade)

## 8. Roadmap - Fora do MVP

- @mencoes em comentarios com autocomplete e notificacao
- Threads de respostas em comentarios (1 nivel)
- Auto-assign por coluna (configuracao no board)
- Notificacoes por email (integrar com servico de email)
- Refresh token para sessao persistente
- Multiplos boards por tenant
- Customizacao de colunas (criar/editar/reordenar/deletar)
- Websockets para atualizacao em tempo real do board entre usuarios
- Anexos/arquivos no card (alem de PDF/Drive link)
- Labels/tags customizaveis nos cards
- Metricas de throughput: tempo medio por etapa, gargalos
- Arquivamento de cards (soft delete com visualizacao de arquivo)
- Drag-and-drop para reordenar cards dentro da mesma coluna (priorizacao visual)

## 9. Duvidas Resolvidas

| ID | Duvida | Decisao |
|----|--------|---------|
| DA-001 | Provedor de email para notificacoes? | Pos-MVP. Decidir quando chegar la. |
| DA-002 | PWA/offline ou apenas online? | Apenas online. |
| DA-003 | Quantos usuarios simultaneos? | Poucos (< 10). Polling basta, sem websockets no MVP. |
| DA-004 | Viewer ve comentarios? | Sim, ve tudo mas nao edita/comenta. |
| DA-005 | SSO ou email+senha? | **Ambos.** Email+senha com validacao de senha forte (minimo 8 chars, maiuscula, numero, especial) + SSO Google/Microsoft. Os dois metodos de login disponiveis. |
| DA-006 | Cards com deadline/prazo? | Nao no MVP. |
| DA-007 | Audit log com retencao? | Indefinido, manter tudo. |
| DA-008 | Disparar pipeline de dentro do card? | **Sim.** Cards tem criacao e movimentacao AUTOMATICA vinculada a pipeline. Gerar conteudo = cria card em Copy. Gerar imagens = move pra Design. Exportar PDF = move pra Revisao. Salvar Drive = vincula link. A unica movimentacao MANUAL permitida e mover qualquer card para a coluna "Cancelado" (lixo/descarte). |
| DA-009 | Colunas fixas ou customizaveis? | Fixas no MVP: Copy, Design, Revisao, Aprovado, Publicado, Cancelado. |

## 10. Modelo de Dados (MongoDB Collections)

> Referencia para o Agente 07 (Arquiteto SQL/MongoDB). Todas as collections no database `content_factory` (mesmo banco ja em uso).

### Collection: `kanban_users`
```
{
  _id: ObjectId,
  tenant_id: string,          // obrigatorio
  email: string,              // unico por tenant
  name: string,
  avatar_url: string | null,
  password_hash: string,      // bcrypt
  role: "admin" | "copywriter" | "designer" | "reviewer" | "viewer",
  created_at: datetime,
  updated_at: datetime | null,
  deleted_at: datetime | null  // soft delete
}
```

### Collection: `kanban_boards`
```
{
  _id: ObjectId,
  tenant_id: string,
  name: string,
  columns: [
    {
      id: string (uuid),
      name: string,
      order: int,
      color: string | null,
      auto_assign_user_ids: [string] | []   // pos-MVP
    }
  ],
  created_at: datetime,
  updated_at: datetime | null
}
```

### Collection: `kanban_cards`
```
{
  _id: ObjectId,
  tenant_id: string,
  board_id: string,
  column_id: string,
  title: string,
  copy_text: string | null,
  disciplina: string | null,
  tecnologia: string | null,
  priority: "alta" | "media" | "baixa",
  assigned_user_ids: [string],
  created_by: string,          // user_id
  pipeline_id: string | null,  // vinculo com pipeline existente
  drive_link: string | null,
  drive_folder_name: string | null,
  pdf_url: string | null,
  image_urls: [string] | [],
  order_in_column: int,        // posicao dentro da coluna
  created_at: datetime,
  updated_at: datetime | null,
  archived_at: datetime | null  // soft delete
}
```

### Collection: `kanban_comments`
```
{
  _id: ObjectId,
  tenant_id: string,
  card_id: string,
  user_id: string,
  text: string,
  parent_comment_id: string | null,  // thread (pos-MVP)
  mentions: [string] | [],           // user_ids mencionados (pos-MVP)
  created_at: datetime,
  updated_at: datetime | null,
  deleted_at: datetime | null
}
```

### Collection: `kanban_activity_log`
```
{
  _id: ObjectId,
  tenant_id: string,
  card_id: string,
  user_id: string,
  action: string,    // "card_created" | "column_changed" | "assignee_changed" | "field_edited" | "comment_added" | "comment_edited" | "comment_deleted" | "image_generated" | "drive_linked" | "pdf_exported"
  metadata: {
    // varia por acao, ex:
    from_column: string,
    to_column: string,
    field_name: string,
    old_value: any,
    new_value: any
  },
  created_at: datetime
}
```

### Collection: `kanban_notifications`
```
{
  _id: ObjectId,
  tenant_id: string,
  user_id: string,           // destinatario
  card_id: string,
  type: "assigned" | "mentioned" | "column_changed",
  message: string,
  is_read: boolean,
  created_at: datetime
}
```

### Indices recomendados
- `kanban_cards`: `{ tenant_id: 1, board_id: 1, column_id: 1 }`
- `kanban_cards`: `{ tenant_id: 1, assigned_user_ids: 1 }`
- `kanban_activity_log`: `{ tenant_id: 1, card_id: 1, created_at: -1 }`
- `kanban_comments`: `{ tenant_id: 1, card_id: 1, created_at: 1 }`
- `kanban_notifications`: `{ tenant_id: 1, user_id: 1, is_read: 1 }`
- `kanban_users`: `{ tenant_id: 1, email: 1 }` (unique)
