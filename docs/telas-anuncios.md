# TELAS -- Modulo Anuncios (Google Ads Display)

Documento de telas gerado pelo Agente 02 (Analista de Tela).
Base: PRD Anuncios (`docs/prd-anuncios.md`) + telas existentes do sistema (`docs/TELAS.md`, `docs/telas-kanban-pipeline.md`).

Escopo: mapear as telas que o modulo Anuncios introduz ou altera, cobrindo CRUD de anuncios, regeneracao individual por dimensao (RN-018), exibicao das 4 dimensoes (RN-001, RN-016), entrega parcial (RN-019), integracao com Historico unificado (RN-014), Kanban (RN-021) e Funnel Architect.

---

## Sumario de Telas

| # | Tela | Rota | Status | Observacao |
|---|------|------|--------|------------|
| 1 | Lista de Anuncios | `/anuncios` | Nova | CRUD list com filtros por status, data e etapa de funil. Entrada principal do modulo. |
| 2 | Criar Anuncio | `/anuncios/novo` | Nova | Entrada de briefing/tema. Dispara pipeline existente com formato `anuncio`. |
| 3 | Detalhe do Anuncio | `/anuncios/[id]` | Nova | Mostra as 4 dimensoes lado a lado + copy (headline 30 / descricao 90) + status + link Drive. |
| 4 | Editar Anuncio | `/anuncios/[id]/editar` | Nova | Edicao de copy + regeneracao individual por dimensao (RN-018). Tambem cobre retomada de dimensao faltante apos status `parcial` (RN-019). |
| 5 | Confirmar Exclusao (Modal) | `/anuncios` / `/anuncios/[id]` (overlay) | Nova | Modal de confirmacao para soft delete (RN-013). |
| 6 | Regenerar Dimensao (Modal) | `/anuncios/[id]/editar` (overlay) | Nova | Modal que confirma regeneracao de 1 das 4 dimensoes, mantendo as demais. |
| 7 | Home / Criar Conteudo (alteracao) | `/` | Alterar | Adicionar `Anuncio` como formato selecionavel, ao lado de Carrossel, Post Unico, Thumbnail YouTube. |
| 8 | Funnel Architect (alteracao) | `/pipeline/[id]/briefing` | Alterar | Permitir que pecas do plano do funil tenham `formato = anuncio`. Sem tela nova -- so campo novo na lista de pecas. |
| 9 | Historico (alteracao) | `/historico` | Alterar | Filtro por formato ja existe (RN-014). Anuncios aparecem na mesma lista. Card de anuncio mostra thumbnail da dimensao 1080x1080 e badge "Anuncio". |
| 10 | Board Kanban (alteracao) | `/kanban` | Alterar | Cards de anuncio participam igual os demais (RN-021). Card mostra badge "Anuncio" + indicador das 4 dimensoes. |
| 11 | Detalhe do Card -- Kanban (alteracao) | `/kanban?card=...` | Alterar | Aba "Detalhes" do card: se formato = anuncio, mostra grid das 4 dimensoes + headline/descricao + link para `/anuncios/[id]`. |
| 12 | Pipeline -- Aprovacao de Imagem AP-4 (alteracao) | `/pipeline/[id]/imagem` | Alterar | Quando formato = anuncio, mostra 4 dimensoes (uma por dimensao) ao inves de variacoes por slide. |
| 13 | Pipeline -- Preview e Export (alteracao) | `/pipeline/[id]/export` | Alterar | Quando formato = anuncio: sem PDF; mostra download ZIP (4 PNGs + copy.txt) e salvar no Drive (subpasta). |
| 14 | Configuracoes (alteracao) | `/configuracoes` | Alterar | Nenhum campo novo de usuario. Apenas reflete que `dimensions.json` agora suporta array (RN-011) e `platform_rules.json` tem regras Google Ads (30/90). Secao "Platform Rules" passa a mostrar "Google Ads Display". |

---

## Navegacao Global -- Integracoes com Sistema Existente

O modulo Anuncios adiciona um novo item "Anuncios" na Sidebar (secao Formatos / Principal) e integra com as rotas existentes sem criar rotas paralelas para Historico ou Kanban (RN-014, RN-021).

### Alteracoes na Sidebar

| Secao | Item Novo | Rota | Icone Sugerido | Observacao |
|-------|-----------|------|----------------|------------|
| Principal | Anuncios | `/anuncios` | Icone de megafone / target / ad | Entre "Kanban" e "Historico" |

A decisao visual do icone fica com o Designer (Agente 05). O item e visivel para Marketing e Admin (RN-022).

---

## Telas Detalhadas

---

### TELA: Lista de Anuncios

**Rota:** `/anuncios`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Ponto de entrada do modulo. Lista todos os anuncios do tenant com filtros por status, data e etapa do funil. Mostra cartoes compactos com titulo, status, headline, thumbnail da dimensao 1080x1080 e data. Suporta soft delete (RN-013). O titulo e a lista respeitam `tenant_id` (RN-009).

#### Campos (Barra de Filtros)

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| busca | text (search) | N | Busca no titulo e headline | formulario |
| filtro_status | select (dropdown) | N | Todos / Em andamento / Concluido / Parcial / Erro / Cancelado | hardcoded |
| filtro_etapa_funil | select (dropdown) | N | Todas / Topo / Meio / Fundo / Avulso | hardcoded |
| filtro_data_inicio | date | N | Data valida | formulario |
| filtro_data_fim | date | N | Data valida, >= data_inicio | formulario |
| incluir_excluidos | toggle | N | Default: desligado (oculta soft deleted) | formulario |

#### Campos (Card de Anuncio na Lista)

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| id | text (readonly) | S | UUID valido | API |
| titulo | text (readonly) | S | - | API |
| headline | text (readonly) | S | Max 30 chars (RN-002) | API |
| descricao_preview | text (readonly) | N | Max 90 chars (RN-003), truncado no card | API |
| thumbnail_1080 | image (readonly) | N | URL da imagem 1080x1080 (a 2a dimensao do array image_urls) | API |
| status | text (readonly) | S | em_andamento / concluido / parcial / erro / cancelado | API |
| etapa_funil | text (readonly) | N | topo / meio / fundo / avulso | API |
| pipeline_id | text (readonly) | N | UUID valido | API |
| drive_folder_link | text (readonly) | N | URL Drive, so presente se concluido ou parcial com export feito | API |
| dimensoes_ok_count | number (readonly) | S | 0 a 4. Em status `parcial`, indica quantas das 4 foram geradas (RN-019) | API |
| criado_em | text (readonly) | S | - | API |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Filtrar por texto | change no campo de busca | Filtra lista em tempo real |
| Filtrar por status | change no select | Filtra lista |
| Filtrar por etapa de funil | change no select | Filtra lista |
| Filtrar por data | change nos campos de data | Filtra lista |
| Alternar incluir_excluidos | toggle change | Mostra ou oculta anuncios com `deleted_at` preenchido |
| Criar novo anuncio | clique em "Novo Anuncio" | Navega para `/anuncios/novo` |
| Abrir detalhe | clique no card | Navega para `/anuncios/[id]` |
| Editar | clique em "Editar" no card | Navega para `/anuncios/[id]/editar` |
| Abrir pipeline | clique no link do pipeline (se presente) | Navega para `/pipeline/[id]` |
| Abrir no Drive | clique em "Abrir no Drive" | Abre link externo em nova aba |
| Excluir | clique em "Excluir" no card | Abre Modal de Confirmacao de Exclusao (Tela 5) |

#### Estados da Tela

- **Loading:** Skeleton de cards (grid 3 colunas) com shimmer enquanto carrega lista do backend.
- **Vazio (sem filtro):** Nenhum anuncio criado. Mensagem central: "Nenhum anuncio criado ainda." + botao destacado "Criar primeiro anuncio".
- **Vazio (com filtro):** Filtros nao retornaram resultados. Mensagem: "Nenhum anuncio encontrado para esses filtros." + botao "Limpar filtros".
- **Erro:** Banner vermelho no topo: "Erro ao carregar anuncios. Tente novamente." + botao "Tentar novamente".
- **Sucesso (estado normal):** Grid de cards com anuncios. Badge de status colorido por card. Badge especial "Parcial (N/4)" nos anuncios com status `parcial` (RN-019).

#### Fluxos de Navegacao

- Clique em "Novo Anuncio" --> `/anuncios/novo`
- Clique no card --> `/anuncios/[id]`
- Clique em "Editar" --> `/anuncios/[id]/editar`
- Clique em "Excluir" --> Modal de Confirmacao (Tela 5)
- Clique em "Abrir no Drive" --> nova aba (link externo)
- Clique em "Abrir pipeline" --> `/pipeline/[id]`
- Nav: qualquer item da sidebar global

---

### TELA: Criar Anuncio

**Rota:** `/anuncios/novo`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Tela onde o usuario informa tema/briefing para criar um novo anuncio. Nao substitui `/` -- e uma entrada direta focada no formato Anuncio. Dispara o pipeline existente (6 agentes + Brand Gate) com `formato = anuncio` (RN-004), gerando obrigatoriamente as 4 dimensoes (RN-001) e copy Google Ads (RN-002, RN-003). Pode opcionalmente ser disparada dentro do fluxo de um funil (via Funnel Architect), caso em que a etapa de funil ja vem preenchida.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| titulo | text | S | Min 3 caracteres. Usado como nome da subpasta Drive (RN-008). | formulario |
| tema_ou_briefing | text (textarea) | S | Minimo 20 caracteres | formulario |
| modo_entrada | select (tabs) | S | "texto" ou "disciplina" (manter padrao da Home) | formulario |
| disciplina | select (cards) | S (se modo=disciplina) | Deve estar na lista de disciplinas | store (disciplinas) |
| tecnologia | select (chips) | S (se modo=disciplina) | Deve pertencer a disciplina selecionada | formulario |
| etapa_funil | select | N | topo / meio / fundo / avulso. Default: avulso. Se veio do Funnel Architect, ja vem preenchida e bloqueada. | formulario / query param |
| pipeline_funil_id | text (readonly) | N | UUID do pipeline de funil (se veio dali). Associa este anuncio como peca de um funil existente. | query param |
| foto_criador | select (galeria) | N | Foto previamente carregada em Config. Usada no brand overlay das dimensoes 1200x628 e 1080x1080 (RN-016). | store (fotos) |

Observacoes:
- Nao ha campo de "dimensoes a gerar" -- as 4 dimensoes sao obrigatorias (RN-001).
- Nao ha campo de headline/descricao aqui -- ambos sao gerados pelo Copywriter respeitando limites 30/90 (RN-002, RN-003). Edicao manual acontece em `/anuncios/[id]/editar`.

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Alternar modo de entrada | clique na tab texto/disciplina | Mostra textarea ou selecao de disciplina |
| Selecionar disciplina | clique no card | Exibe chips de tecnologias da disciplina |
| Selecionar tecnologia | clique no chip | Marca tecnologia |
| Selecionar foto | clique na miniatura | Define foto do criador para brand overlay |
| Selecionar etapa de funil | change no select | Associa anuncio a etapa topo/meio/fundo ou avulso |
| Iniciar criacao | clique em "Criar Anuncio" (submit) | POST backend cria anuncio + pipeline (formato=anuncio). Redireciona para `/pipeline/[id]` para acompanhar as 6 etapas. |
| Cancelar | clique em "Cancelar" | Volta para `/anuncios` sem salvar |

#### Estados da Tela

- **Loading:** Enquanto o backend cria o anuncio + inicia pipeline. Botao mostra spinner + "Iniciando pipeline...".
- **Vazio:** Estado inicial. Titulo e tema vazios. Botao "Criar Anuncio" desabilitado ate titulo (min 3) e tema (min 20) serem preenchidos.
- **Erro:** Validacao falhou (titulo curto, tema curto) ou backend indisponivel. Banner vermelho inline com a mensagem de erro do backend.
- **Sucesso:** Anuncio criado. Redireciona automaticamente para `/pipeline/[id]` (wizard de pipeline ja existente).

#### Fluxos de Navegacao

- Submit com sucesso --> `/pipeline/[id]` (wizard ja existente conduz AP-1 a AP-4)
- Apos AP-4 aprovada + Export --> usuario aterrissa em `/pipeline/[id]/export`, e de la pode voltar ao `/anuncios/[id]`
- Cancelar --> `/anuncios`
- Se `foto_criador` ausente --> link "Adicionar fotos" redireciona para `/configuracoes`

---

### TELA: Detalhe do Anuncio

**Rota:** `/anuncios/[id]`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Mostra um anuncio completo em modo leitura. Exibe as 4 dimensoes lado a lado (grid responsivo), a copy unica (headline + descricao, RN-017), status atual, badges indicando quais dimensoes passaram no Brand Gate, link para a subpasta do Drive e metadados do pipeline. Esta tela e somente leitura; para alterar copy ou regenerar dimensoes, use "Editar" (Tela 4).

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| id | text (readonly) | S | UUID valido | URL (param [id]) |
| titulo | text (readonly) | S | - | API |
| headline | text (readonly) | S | Max 30 chars (RN-002) | API |
| descricao | text (readonly) | S | Max 90 chars (RN-003) | API |
| status | text (readonly) | S | em_andamento / concluido / parcial / erro / cancelado | API |
| etapa_funil | text (readonly) | N | topo / meio / fundo / avulso | API |
| pipeline_id | text (readonly, link) | N | UUID valido | API |
| drive_folder_link | text (readonly, link) | N | URL Drive | API |
| dimensao_1200x628 | image (readonly) | N | URL PNG da dimensao landscape (Gemini Pro, brand overlay foto+logo -- RN-015, RN-016) | API (image_urls[0]) |
| dimensao_1080x1080 | image (readonly) | N | URL PNG da dimensao square (Gemini Flash, brand overlay foto+logo -- RN-015, RN-016) | API (image_urls[1]) |
| dimensao_300x600 | image (readonly) | N | URL PNG da dimensao half page (Gemini Flash, so logo -- RN-016) | API (image_urls[2]) |
| dimensao_300x250 | image (readonly) | N | URL PNG da dimensao medium rectangle (Gemini Flash, so logo -- RN-016) | API (image_urls[3]) |
| brand_gate_status_por_dimensao[] | list (readonly) | S | 4 entradas: valido / revisao_manual / falhou | API |
| criado_em | text (readonly) | S | - | API |
| atualizado_em | text (readonly) | S | - | API |
| criado_por | text (readonly) | S | Nome do usuario que criou | API |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Ampliar dimensao | clique em imagem / icone de lupa | Abre imagem em modal fullscreen com aspect ratio real |
| Copiar headline | clique em "Copiar" ao lado da headline | Copia texto para clipboard + toast "Headline copiada" |
| Copiar descricao | clique em "Copiar" ao lado da descricao | Copia texto para clipboard + toast "Descricao copiada" |
| Copiar copy.txt | clique em "Copiar copy.txt" | Copia headline + descricao formatados como no arquivo exportado |
| Editar | clique em "Editar" | Navega para `/anuncios/[id]/editar` |
| Download ZIP | clique em "Baixar ZIP" | Gera ZIP local com 4 PNGs + copy.txt (RN-007) e faz download |
| Abrir no Drive | clique em "Abrir no Drive" | Abre subpasta Drive em nova aba (RN-008) |
| Salvar / Re-salvar no Drive | clique em "Salvar no Drive" | Cria subpasta (se ainda nao existe) com 4 PNGs + copy.txt. Atualiza `drive_folder_link`. |
| Abrir pipeline | clique no link do pipeline | Navega para `/pipeline/[id]` |
| Excluir | clique em "Excluir" | Abre Modal de Confirmacao (Tela 5) |
| Voltar | clique em "Voltar" | Navega para `/anuncios` |

#### Estados da Tela

- **Loading:** Skeleton: cabecalho cinza + grid 2x2 de placeholders para as dimensoes + linhas cinzas para headline/descricao.
- **Vazio (anuncio nao encontrado ou soft deleted sem permissao):** Mensagem "Anuncio nao encontrado" + link para `/anuncios`.
- **Erro:** Banner vermelho: "Erro ao carregar anuncio. Tente novamente." + botao "Tentar novamente".
- **Sucesso (concluido):** Badge verde "Concluido". 4 dimensoes com badge verde "Brand Gate OK". Botoes "Baixar ZIP" e "Abrir no Drive" ativos.
- **Sucesso parcial (RN-019):** Badge amarelo "Parcial (N/4)". Dimensoes que passaram com badge verde; dimensoes que falharam mostram placeholder cinza com texto "Falhou -- regerar" e botao inline "Regerar esta dimensao" que navega para `/anuncios/[id]/editar` ja com a dimensao selecionada.
- **Em andamento:** Badge azul "Em andamento". As dimensoes ainda nao geradas aparecem como skeleton. Botao "Acompanhar pipeline" destacado (leva a `/pipeline/[id]`).
- **Erro global:** Status `erro`. Badge vermelho. Todas as dimensoes vazias. Botao "Retomar pipeline" leva a `/pipeline/[id]`.
- **Excluido:** Status `cancelado` ou `deleted_at` preenchido. Card em cinza, acoes de edicao desabilitadas. Admin pode restaurar (fora do MVP; no MVP, soft delete definitivo via interface).

#### Fluxos de Navegacao

- Editar --> `/anuncios/[id]/editar`
- Excluir --> Modal de Confirmacao, em caso de confirmacao volta para `/anuncios`
- Abrir pipeline --> `/pipeline/[id]`
- Voltar --> `/anuncios`
- Abrir no Drive --> nova aba
- Download ZIP --> download local (permanece na tela)

---

### TELA: Editar Anuncio

**Rota:** `/anuncios/[id]/editar`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Tela que concentra as duas capacidades da RN-018: **editar copy** (headline ate 30 chars, descricao ate 90 chars) e **regenerar individualmente** qualquer uma das 4 dimensoes mantendo as demais intactas. Tambem e a tela usada para **retomar dimensoes faltantes** quando o anuncio esta em status `parcial` (RN-019). Edicao de copy nao dispara regeneracao automatica de imagens -- headline/descricao afetam apenas o `copy.txt` exportado (a copy nao esta impressa na imagem). Regeneracao de dimensao reaproveita o prompt base do Art Director e reexecuta Image Generator + Brand Gate apenas para aquela dimensao.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| id | text (readonly) | S | UUID valido | URL (param [id]) |
| titulo | text (editavel) | S | Min 3 caracteres | API / formulario |
| headline | text (editavel) | S | Min 1, max 30 caracteres (RN-002). Contador visivel ao lado do campo. | API / formulario |
| descricao | text (textarea, editavel) | S | Min 1, max 90 caracteres (RN-003). Contador visivel. | API / formulario |
| etapa_funil | select (editavel) | N | topo / meio / fundo / avulso | API / formulario |
| dimensoes[] | list (grid 2x2) | S | 4 dimensoes fixas (RN-001) | API (image_urls + brand_gate_status) |
| dimensao.dimensao_id | text (readonly) | S | "1200x628" / "1080x1080" / "300x600" / "300x250" | derivado |
| dimensao.imagem_url | image (readonly) | N | URL PNG ou placeholder se nao gerada | API |
| dimensao.brand_gate_status | text (readonly) | S | valido / revisao_manual / falhou / nao_gerada | API |
| dimensao.retries_usados | number (readonly) | N | 0, 1 ou 2 (RN-019) | API |
| dimensao.selecionada_para_regerar | checkbox | N | Marca quais dimensoes regenerar nesta rodada | formulario |
| foto_criador | select (galeria, readonly) | N | Usada no brand overlay. Edicao de foto exige regerar as dimensoes 1200x628 e 1080x1080 (RN-016). | store (fotos) |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Editar headline | digitacao no campo | Atualiza contador de caracteres (30). Se passar do limite, campo fica vermelho e botao "Salvar copy" desabilita. |
| Editar descricao | digitacao no textarea | Atualiza contador de caracteres (90). Se passar, campo fica vermelho e botao desabilita. |
| Editar titulo | digitacao no campo | Atualiza titulo em memoria |
| Editar etapa de funil | change no select | Atualiza em memoria |
| Salvar copy | clique em "Salvar copy" (submit parcial) | PUT no backend persistindo titulo, headline, descricao, etapa_funil. Nao dispara regeneracao de imagem. Toast "Copy salva". |
| Selecionar dimensao para regerar | checkbox na dimensao | Marca dimensao para rodada de regeneracao |
| Regerar dimensoes selecionadas | clique em "Regerar dimensoes selecionadas" | Abre Modal de Regeneracao (Tela 6) com lista das dimensoes marcadas |
| Regerar dimensao individual | clique em "Regerar" dentro da card da dimensao | Abre Modal de Regeneracao (Tela 6) com apenas aquela dimensao |
| Ampliar dimensao | clique na imagem / icone de lupa | Abre imagem em modal fullscreen |
| Excluir | clique em "Excluir" | Abre Modal de Confirmacao de Exclusao (Tela 5) |
| Cancelar edicao | clique em "Cancelar" | Volta para `/anuncios/[id]` sem salvar alteracoes pendentes (com confirm se houver pendencias) |

Observacoes:
- Editar a copy **nao** dispara nova rodada do Copywriter. E edicao direta dos campos persistidos (RN-017). O tone_guide / limites de 30-90 sao aplicados no frontend como validacao + opcionalmente no backend na persistencia.
- Editar titulo nao renomeia automaticamente a subpasta Drive ja criada. Re-salvar no Drive cria nova subpasta com o novo titulo (comportamento padrao do sistema).

#### Estados da Tela

- **Loading:** Carregando dados do anuncio. Skeleton com campos cinzas.
- **Vazio:** Anuncio nao encontrado. Mensagem "Anuncio nao encontrado" + link para `/anuncios`.
- **Erro:** Falha ao salvar ou ao carregar. Banner vermelho inline por secao (copy, dimensoes).
- **Sucesso (copy salva):** Toast "Copy salva com sucesso". Campos voltam a estado normal.
- **Regeneracao em andamento:** A dimensao sendo regerada mostra skeleton / spinner sobre a imagem antiga + badge "Regenerando...". As demais permanecem interativas.
- **Regeneracao concluida:** Imagem atualizada. Badge "Brand Gate OK" verde. Toast "Dimensao 300x600 regenerada".
- **Regeneracao falhou (2 retries, RN-019):** Badge vermelho "Falhou". Botao "Regerar" ativo para nova tentativa manual. Anuncio permanece em status `parcial`.

#### Fluxos de Navegacao

- Salvar copy --> permanece na tela, toast de sucesso
- Regerar dimensao(oes) --> Modal de Regeneracao (Tela 6) -- apos confirmar, dimensao entra em modo "Regenerando..." e pagina continua aqui
- Concluir edicao --> clique em "Voltar" ou "Concluido" --> `/anuncios/[id]`
- Excluir --> Modal de Confirmacao (Tela 5) --> em caso de confirmacao, vai para `/anuncios`

---

### TELA: Confirmar Exclusao (Modal)

**Rota:** overlay em `/anuncios`, `/anuncios/[id]` ou `/anuncios/[id]/editar`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Modal de confirmacao para soft delete (RN-013). Nao remove registro do banco -- preenche `deleted_at`. Historico continua acessivel via filtro "Incluir excluidos" na Lista de Anuncios. Nao afeta a subpasta do Drive (arquivos permanecem la). Texto deixa isso claro.

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| titulo_do_anuncio | text (readonly) | S | - | API |
| confirmacao_digitada | text | N | Opcional no MVP (pode ser so clique em "Excluir"). Se usado, deve bater com o titulo. | formulario |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Excluir | clique em "Excluir" (botao vermelho) | DELETE no backend (soft delete, `deleted_at`). Fecha modal. Toast "Anuncio excluido". Se veio da Lista: remove o card. Se veio de Detalhe/Editar: redireciona para `/anuncios`. |
| Cancelar | clique em "Cancelar" ou X ou Esc | Fecha modal sem alteracoes |

#### Estados da Tela

- **Loading:** Spinner no botao "Excluir" enquanto aguarda backend.
- **Erro:** Mensagem inline: "Erro ao excluir anuncio. Tente novamente."
- **Sucesso:** Fecha modal, toast de sucesso.

#### Fluxos de Navegacao

- Confirmar a partir da Lista --> permanece em `/anuncios` com card removido
- Confirmar a partir de Detalhe/Editar --> `/anuncios`
- Cancelar --> permanece na tela de origem

---

### TELA: Regenerar Dimensao (Modal)

**Rota:** overlay em `/anuncios/[id]/editar`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Modal disparado ao regerar 1 ou mais dimensoes (RN-018). Lista as dimensoes marcadas, mostra o modelo Gemini que sera usado (Pro para 1200x628, Flash para as demais -- RN-015), explica que copy nao muda e que o brand overlay sera aplicado conforme a dimensao (RN-016). Permite escrever um feedback livre opcional que e anexado ao prompt do Art Director na rodada (ex: "menos roxo, mais azul").

#### Campos

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| dimensoes_alvo[] | list (readonly) | S | 1 a 4 dimensoes marcadas | propagado da Tela 4 |
| feedback_livre | text (textarea) | N | Max 500 caracteres | formulario |
| manter_prompt_base | toggle | N | Default: ligado. Se desligado, forca Art Director a gerar novo prompt base (comportamento nao previsto no MVP; manter default ligado). | formulario |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Confirmar regeneracao | clique em "Regerar" | Backend dispara pipeline parcial: para cada dimensao alvo, executa Image Generator + Brand Gate (usando prompt base existente + feedback, se houver). Modal fecha. Cada dimensao alvo entra em estado "Regenerando..." na Tela 4. |
| Cancelar | clique em "Cancelar" ou X ou Esc | Fecha modal. Nenhuma regeneracao disparada. |

#### Estados da Tela

- **Loading:** Spinner no botao "Regerar" ao clicar (breve, enquanto backend aceita o job).
- **Erro:** Mensagem inline: "Erro ao iniciar regeneracao. Tente novamente."
- **Sucesso:** Fecha modal. Na tela de Editar, as dimensoes alvo entram em "Regenerando...".

#### Fluxos de Navegacao

- Confirmar --> fecha modal --> permanece em `/anuncios/[id]/editar` com dimensoes em estado de regeneracao
- Cancelar --> fecha modal --> permanece em `/anuncios/[id]/editar`

---

### TELA: Home / Criar Conteudo (alteracao)

**Rota:** `/`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Tela existente. A unica alteracao e adicionar `Anuncio` como uma das opcoes do seletor de formato, ao lado de Carrossel, Post Unico e Thumbnail YouTube. Selecionar `Anuncio` leva o submit para o pipeline com `formato=anuncio`, equivalente ao caminho direto via `/anuncios/novo`.

#### Campos alterados

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| formato | select (multi-check) | S | Pelo menos 1 formato. **Adiciona opcao:** Anuncio. Opcoes MVP: Carrossel, Post Unico, Thumbnail YouTube, **Anuncio**. | formulario |

#### Acoes Disponiveis (sem alteracao de fluxo)

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Selecionar Anuncio | clique no card "Anuncio" | Marca `anuncio` como formato selecionado |
| Iniciar pipeline | clique em "Criar Conteudo" com `anuncio` marcado | Cria pipeline com formato=anuncio. Redireciona para `/pipeline/[id]`. Ao final, gera anuncio e aparece em `/anuncios`. |

Observacoes:
- Selecionar multiplos formatos incluindo Anuncio gera multiplos pipelines em paralelo (comportamento ja existente).
- Quando formato=anuncio esta selecionado, o campo `tipo_carrossel` (numero de slides) nao se aplica e pode ser ocultado.

#### Estados da Tela

Sem alteracoes alem da adicao do card "Anuncio" no seletor.

#### Fluxos de Navegacao

- Submit com anuncio --> `/pipeline/[id]` --> apos conclusao, anuncio fica acessivel em `/anuncios/[id]`

---

### TELA: Funnel Architect -- Aprovacao de Briefing (AP-1) (alteracao)

**Rota:** `/pipeline/[id]/briefing`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Tela existente (aprovacao do Strategist em modo funil). A unica alteracao e o campo `pecas_funil[].formato` passar a aceitar o valor `anuncio` (RN-006). Quando o Funnel Architect sugere uma peca `anuncio` no plano, ela aparece na lista editavel com badge "Anuncio" e, ao ser aprovada, a peca segue o pipeline com formato=anuncio.

#### Campos alterados

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| pecas_funil[].formato | select | S | **Adiciona opcao:** anuncio. Opcoes: carrossel, post_unico, thumbnail_youtube, capa_reels, **anuncio**. | API (saida Strategist) + formulario |

#### Acoes Disponiveis

Sem novas acoes. Editar peca do funil (existente) passa a permitir trocar o formato para `anuncio`.

#### Fluxos de Navegacao

Sem alteracao.

---

### TELA: Historico (alteracao)

**Rota:** `/historico`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Tela existente. Historico e unificado (RN-014) -- anuncios aparecem na mesma lista dos demais formatos. A alteracao e: (a) garantir que `filtro_formato` aceita o valor `anuncio`, (b) exibir thumbnail correto para anuncios (usar dimensao 1080x1080 como miniatura do card), (c) na acao "Ver detalhes", redirecionar anuncios para `/anuncios/[id]` ao inves de `/pipeline/[id]/export`.

#### Campos alterados

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| filtro_formato | select | N | **Adiciona opcao:** Anuncio. Opcoes: Todos / Carrossel / Post Unico / Thumbnail YouTube / **Anuncio**. | formulario |
| item.formato | text (readonly) | S | Aceita valor `anuncio` | API |
| item.thumbnail_url | image (readonly) | N | Para formato=anuncio, usar `image_urls[1]` (1080x1080) como miniatura | API |
| item.total_dimensoes | number (readonly) | N | So aparece para formato=anuncio. Sempre 4/4 em status `concluido`, N/4 em `parcial`. | API |

#### Acoes Disponiveis

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Ver detalhes (formato=anuncio) | clique no card | Navega para `/anuncios/[id]` (nao `/pipeline/[id]/export`) |
| Ver detalhes (demais formatos) | clique no card | Mantem comportamento existente |

#### Fluxos de Navegacao

- Card de anuncio --> `/anuncios/[id]`
- Demais formatos --> sem alteracao

---

### TELA: Board Kanban (alteracao)

**Rota:** `/kanban`
**Perfis com acesso:** Admin, Copywriter, Designer, Reviewer, Viewer
**Descricao:** Tela existente. RN-021 determina que anuncios participam do Kanban como qualquer outro formato. Card de anuncio entra em "A fazer" (ou "Copy" na nomenclatura existente) quando criado e segue as movimentacoes automaticas do Kanban. A unica alteracao visual e: (a) adicionar badge "Anuncio" no card, (b) mostrar indicador "(4 dimensoes)" no card, (c) o filtro `filtro_coluna` continua o mesmo.

#### Campos alterados (Card no Board)

| Elemento | Descricao |
|----------|-----------|
| Badge de formato | Novo badge colorido: "Anuncio" (cor diferente de carrossel/post/thumbnail). Decidido pelo Designer. |
| Indicador de dimensoes | Texto discreto "4 dimensoes" ou "3/4 dimensoes" (se `parcial`, RN-019) |
| Thumbnail | Se card e de anuncio, usa `image_urls[1]` (1080x1080) como miniatura quadrada |

#### Acoes Disponiveis

Sem novas acoes. Arrastar para Cancelado continua sendo a unica movimentacao manual (RN-019 Kanban).

#### Fluxos de Navegacao

- Clique no card de anuncio --> abre Modal de Detalhe do Card no Kanban (Tela 11) com comportamento adaptado para anuncio

---

### TELA: Detalhe do Card -- Kanban (alteracao)

**Rota:** `/kanban?card=[id]` (modal/drawer)
**Perfis com acesso:** Admin, Copywriter, Designer, Reviewer, Viewer
**Descricao:** Modal existente do Kanban. Quando o card representa um anuncio, a aba "Detalhes" adapta o layout: mostra headline + descricao + grid das 4 dimensoes + link "Abrir no modulo Anuncios" que leva a `/anuncios/[id]`. Comentarios e Atividade continuam iguais.

#### Campos alterados (Aba 1: Detalhes)

| Campo | Tipo | Obrigatorio | Validacao | Origem | Editavel por |
|-------|------|-------------|-----------|--------|--------------|
| formato | text (readonly) | S | Valor `anuncio` | API (card) | Nao editavel |
| headline | text (readonly) | S | Max 30 chars | API (card.headline ou card.anuncio.headline via join) | Nao editavel aqui -- editar em `/anuncios/[id]/editar` |
| descricao | text (readonly) | S | Max 90 chars | API | Nao editavel aqui |
| dimensoes_grid | grid 2x2 (thumbnails) | S | 4 imagens ou placeholder se parcial | API (image_urls) | Nao editavel |
| link_modulo_anuncios | text (link) | S | URL `/anuncios/[id]` | derivado | Nao editavel |

Observacoes:
- Copy do anuncio (headline/descricao) **nao** e editavel a partir do modal do Kanban. Editar exige navegar para `/anuncios/[id]/editar`. Isso mantem o modal simples e unifica edicao de anuncio num lugar so.
- Titulo e prioridade continuam editaveis como nos demais formatos.

#### Acoes Disponiveis (novas)

| Acao | Gatilho | Resultado | Perfis |
|------|---------|-----------|--------|
| Abrir no modulo Anuncios | clique em "Abrir anuncio" | Navega para `/anuncios/[id]` | Todos |
| Abrir no Drive | clique no link Drive | Nova aba (igual outros formatos) | Todos |

#### Fluxos de Navegacao

- Abrir anuncio --> `/anuncios/[id]`
- Fechar modal --> volta ao board
- Abrir no Drive --> nova aba

---

### TELA: Pipeline -- Aprovacao de Imagem AP-4 (alteracao)

**Rota:** `/pipeline/[id]/imagem`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Tela existente (escolha de variacao de imagem por slide). Para formato=anuncio, o modelo de exibicao muda: **nao ha slides**, ha **4 dimensoes**. Cada dimensao aparece como 1 card mostrando a imagem gerada + status do Brand Gate + botao "Regerar esta dimensao" (equivalente a `retry` dentro do pipeline). Nao ha multiplas variacoes por dimensao -- o Brand Gate valida diretamente a unica imagem gerada por dimensao (com ate 2 retries, RN-019). A aprovacao global libera o pipeline para Content Critic.

#### Campos alterados (quando formato=anuncio)

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| dimensoes[] | list (4 cards) | S | Exatamente 4 | API |
| dimensao.dimensao_id | text (readonly) | S | "1200x628" / "1080x1080" / "300x600" / "300x250" | API |
| dimensao.imagem_url | image (readonly) | N | URL PNG ou placeholder | API |
| dimensao.brand_gate_status | text (readonly) | S | valido / revisao_manual / falhou | API |
| dimensao.brand_gate_retries | number (readonly) | N | 0, 1 ou 2 (RN-019) | API |
| dimensao.modelo_usado | text (readonly) | S | "gemini-pro" (1200x628) ou "gemini-flash" (outras) -- RN-015 | API |
| dimensao.overlay_aplicado | text (readonly) | S | "foto+logo" (1200x628 e 1080x1080) ou "so_logo" (300x600 e 300x250) -- RN-016 | API |

#### Acoes Disponiveis (quando formato=anuncio)

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Ampliar dimensao | clique na imagem / lupa | Abre modal fullscreen |
| Regerar dimensao individual | clique em "Regerar" no card da dimensao | Re-executa Image Generator + Brand Gate para aquela dimensao (mesmo comportamento do modal de regeneracao da Tela 6, mas inline) |
| Aprovar todas | clique em "Aprovar e Finalizar" | Envia selecao, pipeline avanca para Content Critic. Se alguma dimensao estiver em `falhou` (2 retries esgotados), o anuncio e aprovado em status `parcial` (RN-019) apos confirmacao. |
| Rejeitar todas | clique em "Rejeitar Todas e Regerar" | Re-executa Image Generator para as 4 dimensoes |
| Voltar | clique em "Voltar" | `/pipeline/[id]` |

#### Estados da Tela (quando formato=anuncio)

- **Loading:** Grid 2x2 de skeletons.
- **Vazio:** Image Generator ainda nao executou. Mensagem "Aguardando geracao das 4 dimensoes...".
- **Erro (1+ dimensao falhou 2x):** Badge "revisao manual necessaria" ou "falhou" na dimensao. Botao "Aprovar mesmo assim (status parcial)" + "Regerar".
- **Sucesso:** Todas as 4 dimensoes validas. Badge verde em todas. Botao "Aprovar e Finalizar" destacado.

#### Fluxos de Navegacao

- Aprovar --> `/pipeline/[id]` (Content Critic executa) --> `/pipeline/[id]/export`
- Aprovar em status parcial --> idem, anuncio final fica com status `parcial` e aparece assim em `/anuncios/[id]`
- Rejeitar --> permanece, Image Generator re-executa
- Voltar --> `/pipeline/[id]`

---

### TELA: Pipeline -- Preview e Export (alteracao)

**Rota:** `/pipeline/[id]/export`
**Perfis com acesso:** Marketing, Admin
**Descricao:** Tela existente (preview final + export). Para formato=anuncio, o comportamento de export muda (RN-007): **nao gera PDF**. Gera subpasta Drive com 4 PNGs + `copy.txt` (RN-008) ou ZIP local. O preview mostra as 4 dimensoes lado a lado em vez de carrossel swipe.

#### Campos alterados (quando formato=anuncio)

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| dimensoes_finais[] | list (4 imagens) | S | Exatamente 4 (ou menos em status parcial -- RN-019) | API |
| headline | text (readonly) | S | Max 30 chars | API |
| descricao | text (readonly) | S | Max 90 chars | API |
| preview_copy_txt | text (readonly) | S | Prewiew do conteudo de `copy.txt` (headline + descricao formatados) | derivado |

Campos ocultos quando formato=anuncio: `legenda_linkedin` (nao se aplica), `slides_finais[]` (substituido por `dimensoes_finais[]`).

#### Acoes Disponiveis (quando formato=anuncio)

| Acao | Gatilho | Resultado |
|------|---------|-----------|
| Navegar entre dimensoes | clique / swipe | Alterna preview entre as 4 dimensoes |
| Ampliar dimensao | clique na imagem / lupa | Abre modal fullscreen |
| Copiar headline | clique em "Copiar" | Clipboard |
| Copiar descricao | clique em "Copiar" | Clipboard |
| Copiar copy.txt | clique em "Copiar copy.txt" | Clipboard |
| Download PNG individual | clique em "Download" no card da dimensao | Faz download daquele PNG |
| Download ZIP | clique em "Baixar ZIP" | Gera ZIP local com 4 PNGs + copy.txt (RN-007) |
| Salvar no Drive | clique em "Salvar no Drive" | Cria subpasta Drive (RN-008) com `ad-1200x628.png`, `ad-1080x1080.png`, `ad-300x600.png`, `ad-300x250.png` e `copy.txt`. Atualiza `drive_folder_link` do anuncio. |
| Abrir no modulo Anuncios | clique em "Ver anuncio" | Navega para `/anuncios/[id]` |
| Voltar | clique em "Voltar" | `/pipeline/[id]` |
| Novo anuncio | clique em "Novo anuncio" | `/anuncios/novo` |

Acoes ocultas quando formato=anuncio: "Exportar PDF".

#### Estados da Tela (quando formato=anuncio)

- **Sucesso:** 4 dimensoes exibidas. Badge "Concluido". Botoes "Baixar ZIP" e "Salvar no Drive" ativos.
- **Parcial (RN-019):** Apenas N/4 dimensoes exibidas. Badge amarelo "Parcial (N/4)". Botao "Regerar faltantes" leva a `/anuncios/[id]/editar`. Export habilitado mesmo assim (ZIP / Drive contem apenas as dimensoes geradas + copy.txt).

#### Fluxos de Navegacao

- Baixar ZIP --> download local (permanece)
- Salvar no Drive --> permanece com link
- Ver anuncio --> `/anuncios/[id]`
- Novo anuncio --> `/anuncios/novo`
- Voltar --> `/pipeline/[id]`

---

### TELA: Configuracoes (alteracao)

**Rota:** `/configuracoes`
**Perfis com acesso:** Admin
**Descricao:** Tela existente. A unica alteracao visivel e na secao "Platform Rules" passar a listar "Google Ads Display" com as regras RN-002 (headline 30) e RN-003 (descricao 90). Nenhuma edicao manual e necessaria no MVP -- os valores ja vem do backend (`platform_rules.json`). Tambem reflete que `dimensions.json` suporta array (RN-011) para o formato Anuncio, mas nao ha campo editavel para isso no MVP.

#### Campos alterados (secao Platform Rules)

| Campo | Tipo | Obrigatorio | Validacao | Origem |
|-------|------|-------------|-----------|--------|
| plataformas[] | list (readonly) | S | Lista inclui "Google Ads Display" alem das existentes | API (platform_rules.json) |
| plataforma.headline_max | number (readonly) | S | 30 para Google Ads | API |
| plataforma.descricao_max | number (readonly) | S | 90 para Google Ads | API |
| plataforma.dimensoes[] | list (readonly) | N | Array das 4 dimensoes (RN-011): 1200x628, 1080x1080, 300x600, 300x250 | API (dimensions.json) |

Observacao: brand palette continua unico e compartilhado (RN-012). Nao ha alteracao na secao Brand Palette.

#### Acoes Disponiveis

Sem novas acoes.

#### Fluxos de Navegacao

Sem alteracao.

---

## Fluxos Criticos de Navegacao (End-to-End)

### Fluxo 1: Criar Anuncio Avulso (Happy Path)

1. Usuario (Marketing ou Admin) --> sidebar --> `/anuncios`
2. Lista vazia --> clique em "Criar primeiro anuncio" --> `/anuncios/novo`
3. Preenche titulo + tema + foto_criador --> clique "Criar Anuncio"
4. Backend cria anuncio + dispara pipeline (formato=anuncio) --> redirect para `/pipeline/[id]`
5. AP-1 (Briefing), AP-2 (Copy+Hook, com validacao 30/90 via Copywriter+tone_guide), AP-3 (Prompt Visual)
6. AP-4 (Imagem): 4 dimensoes geradas. Usuario aprova --> Content Critic --> `/pipeline/[id]/export`
7. Export: "Salvar no Drive" + "Baixar ZIP" --> pronto
8. Clique em "Ver anuncio" --> `/anuncios/[id]` mostra anuncio completo com as 4 dimensoes e link Drive

### Fluxo 2: Criar Anuncio via Funnel Architect

1. Usuario cria funil na Home --> pipeline em modo funil inicia
2. Strategist gera plano --> `/pipeline/[id]/briefing` mostra pecas
3. Uma das pecas tem `formato = anuncio` (sugestao do Funnel Architect, RN-006). Usuario aprova o plano.
4. Pipeline executa cada peca. Ao chegar na peca anuncio, segue AP-2/AP-3/AP-4 adaptadas para anuncio.
5. Ao final, anuncio aparece em `/anuncios` associado ao `pipeline_funil_id`.

### Fluxo 3: Regeneracao Individual por Dimensao (RN-018)

1. Usuario ve anuncio em `/anuncios/[id]` -- dimensao 300x600 ficou com contraste baixo
2. Clique em "Editar" --> `/anuncios/[id]/editar`
3. Marca checkbox da dimensao 300x600 --> clique em "Regerar dimensoes selecionadas"
4. Modal de Regeneracao abre -- usuario escreve "aumentar contraste" e confirma
5. Dimensao 300x600 entra em "Regenerando..." -- demais permanecem intactas
6. Image Generator + Brand Gate executam apenas para 300x600
7. Dimensao atualizada. Usuario clica em "Voltar" --> `/anuncios/[id]` mostra nova versao da 300x600
8. Usuario re-salva no Drive -- arquivo `ad-300x600.png` sobrescreve o antigo na subpasta

### Fluxo 4: Entrega Parcial + Retomada (RN-019)

1. Pipeline executa. Dimensao 300x250 falha 2 vezes no Brand Gate.
2. Usuario aprova mesmo assim em AP-4 (com aviso de status `parcial`).
3. Anuncio fica em `/anuncios/[id]` com status `parcial` (3/4 dimensoes).
4. Export gera ZIP com 3 PNGs + copy.txt. Drive subpasta tem os 3 arquivos.
5. Usuario abre `/anuncios/[id]/editar` --> dimensao 300x250 mostra "Falhou -- regerar" --> clique em "Regerar esta dimensao"
6. Modal confirma --> regeneracao isolada roda --> se OK, status vira `concluido`
7. Usuario re-salva no Drive -- arquivo `ad-300x250.png` e adicionado a subpasta

### Fluxo 5: Editar Apenas a Copy

1. Usuario ve anuncio concluido. Quer ajustar headline.
2. `/anuncios/[id]/editar` --> edita headline de "Aprenda IA agora" para "Aprenda IA em 90 dias" (26 chars, dentro do limite)
3. Contador mostra 26/30 em verde. Clique em "Salvar copy".
4. Backend persiste. Toast "Copy salva". Imagens nao sao regeneradas (a copy nao esta impressa nas imagens).
5. Usuario re-salva no Drive --> `copy.txt` e atualizado na subpasta. PNGs permanecem os mesmos.

### Fluxo 6: Excluir Anuncio (Soft Delete, RN-013)

1. Usuario em `/anuncios` --> clique em "Excluir" no card
2. Modal de Confirmacao --> "Excluir"
3. Backend preenche `deleted_at`. Card some da lista.
4. Arquivos no Drive permanecem.
5. Usuario ativa toggle "Incluir excluidos" --> card reaparece com indicador de excluido.

---

## Duvidas Tecnicas -- Resolvidas (2026-04-23)

Todas as duvidas foram confirmadas pela cliente aceitando as sugestoes. As decisoes abaixo sao fonte de verdade para os agentes 03 (Backend), 04 (Frontend) e 05 (Designer):

| ID | Decisao |
|----|---------|
| DT-A01 | Editar Anuncio usa **edicao manual direta** de copy, com contador de caracteres (30/90). Nao ha botao "Regenerar copy via LLM" no MVP. |
| DT-A02 | Edicao de copy **nao sincroniza automaticamente** com o Drive -- exige botao "Re-salvar no Drive" explicito. |
| DT-A03 | Status `parcial` exporta **apenas as dimensoes que passaram**. `copy.txt` sempre presente. Incluir nota no ZIP: "X de 4 dimensoes -- gere a faltante antes de publicar". |
| DT-A04 | Modal "Regenerar Dimensao" aceita **apenas feedback livre** anexado ao prompt. Edicao de prompt base fica fora do MVP. |
| DT-A05 | Criacao multi-formato via Home gera **1 card por formato** no Kanban (consistente com comportamento existente). |
| DT-A06 | AP-4 (Aprovacao de Imagem) abre apenas quando **todas as 4 dimensoes terminam** (sucesso ou falha apos 2 retries). Evita decisoes parciais. |

---

## Glossario

| Termo | Definicao |
|-------|-----------|
| Anuncio | Peca de conteudo dedicada a Google Ads Display: 4 dimensoes de imagem + 1 copy (headline + descricao) |
| Dimensao | Uma das 4 variacoes de tamanho obrigatorias do anuncio: 1200x628 (landscape), 1080x1080 (square), 300x600 (half page), 300x250 (medium rectangle) |
| Headline | Texto curto do anuncio (max 30 chars, RN-002), usado como titulo na plataforma Google Ads |
| Descricao | Texto complementar do anuncio (max 90 chars, RN-003), usado como subtitulo na plataforma Google Ads |
| Copy | Conjunto `headline + descricao` do anuncio. Unica por anuncio, compartilhada pelas 4 dimensoes (RN-017) |
| Brand Gate | Checkpoint deterministico que valida conformidade visual (cores, tipografia, overlay). Adaptado por aspect ratio para os 4 formatos (RN-020) |
| Brand Overlay | Composicao Pillow aplicada sobre a imagem gerada pelo Gemini: foto redonda do criador + logo IT Valley (ou so logo em dimensoes pequenas, RN-016) |
| Regeneracao Individual | Acao de refazer apenas 1 das 4 dimensoes mantendo as demais intactas (RN-018). Reexecuta Image Generator + Brand Gate para aquela dimensao. |
| Entrega Parcial | Status do anuncio quando 1 ou mais dimensoes falharam apos 2 retries. Anuncio e entregue com as dimensoes que passaram (RN-019). |
| Subpasta Drive | Pasta no Google Drive criada automaticamente com padrao `"{titulo} - {YYYY-MM-DD}"`, contendo 4 PNGs + copy.txt (RN-007, RN-008) |
| Gemini Pro | Modelo de imagem usado na dimensao 1200x628 (feed principal, mais exposto) -- RN-015 |
| Gemini Flash | Modelo de imagem usado nas dimensoes 1080x1080, 300x600, 300x250 -- RN-015 |
| Status `parcial` | Anuncio cujo pipeline terminou com menos de 4 dimensoes. Pode ser completado depois via EditarAnuncio. |

---

*Documento gerado pelo Agente 02 (Analista de Tela) da esteira IT Valley.*
*Fonte: `docs/prd-anuncios.md` + telas existentes de `docs/TELAS.md` e `docs/telas-kanban-pipeline.md`.*
*Proximo: Agentes 03 (Arquiteto Backend), 04 (Arquiteto Frontend), 05 (Arquiteto Designer) -- em paralelo.*
