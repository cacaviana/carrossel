# QA Tela -- Kanban Pipeline

Relatorio de conformidade: implementacao vs especificacao (telas-kanban-pipeline.md + design-kanban-pipeline.md).
Gerado por: Agente 13 (QA Tela)
Data: 2026-04-14

---

## 1. TELA LOGIN (/login)

| Item | Esperado | Implementado | Status |
|------|----------|-------------|--------|
| Formulario email + senha | Campos email e password com labels, placeholders | LoginForm.svelte com campos email, password, labels, placeholders corretos | PASS |
| Validacao senha forte | Min 8 chars, 1 maiuscula, 1 numero, 1 especial (RN-021) | LoginRequestDTO.errosSenha com feedback visual inline | PASS |
| Toggle mostrar/ocultar senha | Icone de olho no campo senha | Botao com SVG eye/eye-off, alterna type password/text | PASS |
| Botoes SSO Google/Microsoft | 2 botoes visuais com icones dos provedores | SSOButtons.svelte com grid 2 colunas, icones SVG Google e Microsoft | PASS |
| Separador "ou continue com" | Separador visual entre form e SSO | SSOButtons.svelte inclui separador com texto "ou continue com" | PASS |
| Loading no botao Entrar | Spinner + texto "Entrando..." + inputs desabilitados | Spinner dentro do botao, disabled nos inputs durante loading | PASS |
| Mensagem de erro | Alert inline abaixo do form | div com bg-red/10 border-red/20, data-testid="msg-erro" | PASS |
| Redirect apos login | Redireciona para `/` ou rota anterior | Redireciona para `/historico` | **DIVERGENCIA** |
| Se ja logado, redireciona | Se logado, vai para `/` | onMount redireciona para `/` (correto per spec original) mas layout redireciona para `/historico` | **DIVERGENCIA** |
| Layout sem sidebar/header | Tela fullscreen centralizada | +layout.svelte renderiza sem sidebar quando isLoginPage | PASS |
| Card centralizado + hero-bg | Card max-w-md centralizado no hero-bg | w-full max-w-md bg-bg-card rounded-2xl no hero-bg | PASS |
| Logo CF | Bloco CF + "Content Factory" + "IT Valley School" | Implementado identico ao design | PASS |

**Divergencias encontradas:**
1. **Redirect pos-login:** Spec diz redirecionar para `/` (ou rota anterior). Implementacao redireciona fixo para `/historico`. A +page.svelte (login) faz `goto('/historico')` ao inves de `goto('/')` ou `goto(returnUrl)`.
2. **Redirect se ja logado:** login/+page.svelte redireciona para `/` (correto pela spec TELA 1), mas +layout.svelte redireciona para `/historico` (inconsistente entre os dois).

---

## 2. BOARD KANBAN (aba Kanban no /historico)

| Item | Esperado | Implementado | Status |
|------|----------|-------------|--------|
| 6 colunas fixas: Copy, Design, Revisao, Aprovado, Publicado, Cancelado | 6 colunas no board | **5 colunas**: Copy, Diretor de Arte, Aprovado, Publicado, Cancelado (sem Revisao) | **FAIL** |
| Nomes das colunas conforme spec | Copy, Design, Revisao, Aprovado, Publicado, Cancelado | Copy, **Diretor de Arte** (spec diz "Design"), sem Revisao | **FAIL** |
| Cards com badge de prioridade | Badge colorido: alta (vermelho), media (amarelo), baixa (cinza) | Implementado com cores corretas | PASS |
| Cards com avatares no topo | Circulos empilhados, max 3 + "+N" | Implementado com -space-x-1.5, slice(0,3) + "+N" | PASS |
| Cards com titulo | Texto truncado 2 linhas | line-clamp-2, text-sm font-medium | PASS |
| Cards com prazo | Data do deadline embaixo do titulo, formato "Prazo: dd/mm" | Prazo com icone calendario, formato "Prazo: {deadlineLabel}" | PASS |
| Cards com tag pipeline | Tag com nome da coluna no bottom | Badge com pipelineTagLabels no bottom do card | PASS |
| Cards com indicador de comentarios | Icone balao + contagem | SVG balao + comment_count, visivel se > 0 | PASS |
| Cards com disciplina | Tag pequena ex "NLP" | **NAO implementado** no KanbanCard | **FAIL** |
| Cards com data de criacao | Data relativa "ha 2 dias" | **NAO implementado** no KanbanCard | **FAIL** |
| Drag-and-drop apenas para Cancelado | Somente coluna Cancelado aceita drag | Aceita drag para Cancelado **E** Publicado (isDropTarget inclui col-publicado) | **FAIL** |
| Filtros: busca, responsavel, coluna, prioridade | 4 filtros na barra | Implementado com KanbanFilters.svelte | PASS |
| Botao Limpar filtros | Visivel quando ha filtro ativo | Condicional com hasFilters | PASS |
| Botao Novo Card | Botao "+" ou "Novo Card" | Botao "Novo Card" com icone +, condicional por canCreateCard | PASS |
| Botao Refresh manual | Botao de refresh com spinner ao recarregar | Implementado com animate-spin durante refresh | PASS |
| Skeleton loading 6 colunas | 6 colunas skeleton com shimmer | **5 colunas** skeleton (Array(5)) | **FAIL** |
| Board vazio mensagem | "Nenhum carrossel em producao." + link para / | **NAO implementado** -- nao ha estado vazio explicito no board | **FAIL** |
| Filtro sem resultado mensagem | "Nenhum card encontrado" + limpar filtros | **NAO implementado** -- colunas ficam vazias sem mensagem | **FAIL** |
| Erro com banner | Banner de erro + "Tentar novamente" | Implementado com div red + botao "Tentar novamente" | PASS |

**Divergencias encontradas:**
1. **Numero de colunas:** Spec exige 6 colunas (Copy, Design, Revisao, Aprovado, Publicado, Cancelado). Mock tem apenas 5 (sem Revisao). Nome "Design" foi trocado por "Diretor de Arte".
2. **Drag-and-drop:** Spec (RN-019) diz que somente Cancelado aceita drag. Implementacao aceita drag tambem para Publicado.
3. **Card sem disciplina e data de criacao:** Spec define disciplina (tag) e data relativa no card. Nenhum dos dois esta no KanbanCard.svelte.
4. **Skeleton com 5 colunas** ao inves de 6.
5. **Sem mensagem de board vazio** e **sem mensagem de filtro sem resultado**.

---

## 3. CALENDARIO (aba Calendario no /historico)

| Item | Esperado | Implementado | Status |
|------|----------|-------------|--------|
| Calendario mensal | Grid 7 colunas (Dom-Sab) com dias do mes | Implementado com grid-cols-7 | PASS |
| Tarjas coloridas por formato | Cores diferentes por tipo (carrossel, post, youtube, reels) | formatoColors com 4 cores distintas | PASS |
| Clicar na tarja abre detalhe | Clique navega para detalhe do card | onclick chama onCardClick com card.id | PASS |
| Navegacao por mes | Setas prev/next + botao "Hoje" | prevMonth, nextMonth, goToday implementados | PASS |
| Legenda de cores | Legenda com nome dos formatos | Implementado com formatoLabels | PASS |
| Destaque do dia atual | Ring visual no dia de hoje | ring-2 ring-purple/40 ring-inset quando isToday | PASS |

**Divergencias:** Nenhuma. Calendario conforme.

---

## 4. DEADLINE PICKER (na criacao /)

| Item | Esperado | Implementado | Status |
|------|----------|-------------|--------|
| Comeca fechado | Estado inicial recolhido | expanded = false, botao para expandir | PASS |
| Expande ao clicar | Click no botao abre o calendario | onclick toggle expanded | PASS |
| Mostra tarjas dos cards existentes | Calendario com tarjas visuais dos cards | Carrega cards via CardService e mostra pontos coloridos | PASS |
| Selecionar data | Click em dia seleciona a data | selectDate com toggle (click de novo desseleciona) | PASS |
| Limpar data | Botao ou acao para remover data | Botao "Limpar prazo" visivel quando value existe | PASS |
| Dias passados desabilitados | Nao permite selecionar datas passadas | isPast + disabled + opacity-30 cursor-not-allowed | PASS |

**Divergencias:** Nenhuma. DeadlinePicker conforme.

---

## 5. USUARIOS (aba admin-only no /historico)

| Item | Esperado | Implementado | Status |
|------|----------|-------------|--------|
| Aba visivel somente para Admin | Condicional por role | `{#if auth?.isAdmin}` no tab Usuarios | PASS |
| Tabela de usuarios | Avatar, Nome, Email, Perfil, Status, Acoes | 4 colunas: Usuario (avatar+nome+email), Perfil, Status, Acoes | **DIVERGENCIA** |
| Coluna "Criado em" | Spec pede data de criacao na tabela | **NAO implementada** | **FAIL** |
| Badge perfil por role | Cores diferentes por role | user.roleBadgeColor aplicado | PASS |
| Status Ativo/Inativo | Badge verde (ativo), cinza (inativo) | Implementado com icone circular colorido | PASS |
| Botao Editar | Icone lapis por linha | Botao com SVG pencil, data-testid="btn-editar-{id}" | PASS |
| Botao Desativar/Reativar | Toggle de status por linha | Botao toggle com icones distintos para ativar/desativar | PASS |
| Botao "Convidar Usuario" | Botao no header da tabela | Botao "Convidar" no topo direito | PASS |
| Modal criar usuario | Campos: nome, email, senha, perfil | UserFormModal com nome, email, password (criacao), role | PASS |
| Modal editar usuario | Email readonly, permite alterar nome e perfil | email disabled quando isEdit | PASS |
| Campo avatar_url | Spec pede campo URL de avatar no modal | **NAO implementado** | **FAIL** |
| Modal Convite (InviteToken) | Gera token/link de convite | InviteModal gera convite, exibe link + botao copiar | PASS |
| Link de convite | Exibir URL copiavel apos convite | inviteUrl exibido com botao "Copiar" | PASS |
| Mensagem vazio | "Nenhum usuario cadastrado alem de voce" | "Nenhum usuario encontrado." (texto generico) | **DIVERGENCIA** |

**Divergencias encontradas:**
1. **Colunas da tabela:** Spec define 7 colunas (Avatar, Nome, Email, Perfil, Status, Criado em, Acoes). Implementacao combina Avatar+Nome+Email numa unica coluna, e omite "Criado em".
2. **Campo avatar_url** ausente no modal de criar/editar usuario.
3. **Mensagem de tabela vazia** com texto generico ao inves do texto especificado.

---

## 6. AUTH GUARD

| Item | Esperado | Implementado | Status |
|------|----------|-------------|--------|
| /historico requer login | Redireciona para /login se nao logado | isProtectedPage inclui /historico, redireciona para /login | PASS |
| / (home) nao requer login | Home acessivel sem autenticacao | Home nao esta em isProtectedPage | PASS |
| /convite e publico | Acessivel sem login, sem sidebar | isConvitePage renderiza sem sidebar/header | PASS |
| /login acessivel sem auth | Pagina publica | isLoginPage renderiza sem sidebar | PASS |
| Se logado e na /login, redireciona | Redireciona para / | Redireciona para `/historico` (spec diz `/`) | **DIVERGENCIA** |

**Divergencias encontradas:**
1. **Redirect de /login quando logado:** Spec diz redirecionar para `/`, implementacao redireciona para `/historico`.

---

## 7. SIDEBAR

| Item | Esperado | Implementado | Status |
|------|----------|-------------|--------|
| Item "Kanban" na secao Principal | Entre Home e Historico, rota /kanban | **NAO implementado** -- secao Principal tem apenas Home e Historico | **FAIL** |
| Item "Usuarios" na secao Sistema | Apos Config, visivel somente para Admin | Implementado como `/historico?tab=usuarios`, visivel somente para Admin | **DIVERGENCIA** |

**Divergencias encontradas:**
1. **Item Kanban na sidebar:** Spec pede item separado "Kanban" com rota `/kanban`. Implementacao colocou Kanban como aba dentro de /historico, sem item dedicado na sidebar.
2. **Rota Usuarios:** Spec pede `/kanban/usuarios`. Implementacao usa `/historico?tab=usuarios`.

---

## 8. HEADER / LAYOUT

| Item | Esperado | Implementado | Status |
|------|----------|-------------|--------|
| NotificationBell no header desktop | Icone sino + badge, lado direito | Implementado no header desktop | PASS |
| NotificationBell no header mobile | Icone sino no header fixo mobile | Implementado no header mobile | PASS |
| Avatar do usuario logado | Iniciais + nome + role no header desktop | Implementado com iniciais, nome, roleLabel | PASS |
| Botao Sair | Limpa JWT, redireciona /login | handleLogout com clearAuth + goto('/login') | PASS |
| Badge notificacoes | Circulo vermelho, "9+" se > 9, oculto se zero | Implementado conforme spec | PASS |

**Divergencias:** Nenhuma no header/layout.

---

## 9. NOTIFICACOES (Dropdown)

| Item | Esperado | Implementado | Status |
|------|----------|-------------|--------|
| Dropdown ao clicar no sino | Lista de notificacoes recentes | NotificationDropdown.svelte com lista | PASS |
| Fechar ao clicar fora | Backdrop fecha dropdown | Botao fixed inset-0 como backdrop | PASS |
| Clicar em notificacao | Marca como lida + abre card | handleClick marca como lida + goto `/kanban?card=` | **DIVERGENCIA** |
| Marcar todas como lidas | Botao "Marcar todas como lidas" | Implementado, condicional com unreadCount > 0 | PASS |
| Indicador nao-lida (bolinha) | Bolinha azul/purple para nao-lidas | div w-2 h-2 rounded-full bg-purple | PASS |
| Fundo destacado nao-lida | bg-purple/3 para nao-lidas | Implementado com condicional is_read | PASS |
| Mensagem vazio | "Nenhuma notificacao." | Implementado conforme | PASS |
| Largura 360px | Dropdown fixo 360px | w-[360px] implementado | PASS |
| Icones por tipo | assigned, column_changed, mentioned | 3 tipos implementados com cores corretas | PASS |

**Divergencias encontradas:**
1. **Navegacao de notificacao:** Spec diz navegar para `/kanban?card=`. Implementacao tambem usa `/kanban?card=`, mas a rota real do kanban e uma aba em `/historico?tab=kanban`. O link pode nao funcionar se `/kanban` nao existe como rota.

---

## 10. TELA CONVITE (/convite)

| Item | Esperado | Implementado | Status |
|------|----------|-------------|--------|
| Pagina publica | Acessivel sem login | isConvitePage renderiza sem sidebar | PASS |
| Token via query param | Le token da URL | page.url.searchParams.get('token') | PASS |
| Token invalido/ausente | Mensagem de erro + link para login | "Link de convite invalido ou ausente." + link /login | PASS |
| Campos senha + confirmar senha | 2 campos de senha | Implementado com password e confirmPassword | PASS |
| Validacao senha forte | Mesma regra RN-021 | LoginRequestDTO.errosSenha reutilizado | PASS |
| Senhas devem coincidir | Validacao inline | Verifica senhasIguais com mensagem de erro | PASS |
| Botao "Criar Conta" | Submit com loading | Botao com spinner "Criando conta..." | PASS |
| Redirect pos-aceite | Redireciona apos aceitar | goto('/historico') | PASS |

**Divergencias:** Nenhuma. Tela de convite conforme.

---

## RESUMO GERAL

| Area | Total Itens | PASS | FAIL | DIVERGENCIA |
|------|------------|------|------|-------------|
| Login | 12 | 10 | 0 | 2 |
| Board Kanban | 17 | 9 | 8 | 0 |
| Calendario | 6 | 6 | 0 | 0 |
| DeadlinePicker | 6 | 6 | 0 | 0 |
| Usuarios | 14 | 10 | 2 | 2 |
| Auth Guard | 5 | 4 | 0 | 1 |
| Sidebar | 2 | 0 | 1 | 1 |
| Header/Layout | 5 | 5 | 0 | 0 |
| Notificacoes | 9 | 8 | 0 | 1 |
| Convite | 8 | 8 | 0 | 0 |
| **TOTAL** | **84** | **66** | **11** | **7** |

---

## LISTA DE FALHAS CRITICAS (FAIL)

1. **Board tem 5 colunas ao inves de 6** -- falta a coluna "Revisao". Coluna "Design" foi renomeada para "Diretor de Arte" sem atualizacao na spec.
2. **Drag-and-drop aceita Publicado alem de Cancelado** -- viola RN-019 que permite drag somente para Cancelado.
3. **KanbanCard nao exibe disciplina** -- tag de disciplina (ex: "NLP") ausente no card.
4. **KanbanCard nao exibe data de criacao** -- data relativa ("ha 2 dias") ausente no card.
5. **Skeleton loading com 5 colunas** -- deveria ser 6 conforme spec.
6. **Board sem mensagem de estado vazio** -- spec exige mensagem + link para Home.
7. **Board sem mensagem de filtro sem resultado** -- spec exige "Nenhum card encontrado" + botao limpar.
8. **Tabela de usuarios sem coluna "Criado em"** -- spec exige 7 colunas na tabela.
9. **Modal usuario sem campo avatar_url** -- spec define campo URL de avatar.
10. **Sidebar sem item "Kanban" dedicado** -- spec exige item na secao Principal.
11. **Mensagem vazia da tabela usuarios** generica ao inves da especificada.

## LISTA DE DIVERGENCIAS (nao-bloqueantes)

1. Redirect pos-login vai para `/historico` ao inves de `/` (spec).
2. Redirect de /login quando ja logado vai para `/historico` ao inves de `/`.
3. Rota de usuarios e `/historico?tab=usuarios` ao inves de `/kanban/usuarios`.
4. Notificacoes navegam para `/kanban?card=` mas kanban esta em `/historico?tab=kanban`.
5. Tabela de usuarios combina Avatar+Nome+Email numa unica coluna (design aceitavel mas diferente da spec).
6. Sidebar item "Usuarios" aponta para `/historico?tab=usuarios` ao inves de `/kanban/usuarios`.
7. Decisao arquitetural de embutir Kanban como aba de /historico ao inves de rota propria /kanban -- diverge da spec mas pode ser decisao deliberada.

---

## VEREDICTO

**NAO APROVADO para Playwright (Agente 14).**

As falhas 1-7 (board kanban) sao criticas e precisam ser corrigidas antes de prosseguir para testes E2E. As falhas 8-11 (usuarios e sidebar) sao relevantes mas de menor impacto.

Recomendacao: corrigir as 7 falhas do board kanban como prioridade, depois as demais. Apos correcao, submeter novamente ao QA Tela.
