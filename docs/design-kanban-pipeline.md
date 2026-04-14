# DESIGN VISUAL -- Kanban Pipeline de Carrosseis

Documento gerado pelo Agente 05 (Arquiteto Designer).
Base: PRD Kanban Pipeline + Documento de Telas + Arquitetura Frontend + Design System existente (app.css, Sidebar, +page.svelte, +layout.svelte).

---

## Principios de Design

1. **Continuidade visual:** Manter a identidade existente -- fundo `bg-global` (#E6EEEC), cards `bg-card` (#FAFCFB), bordas `border-default`, fonte Outfit, paleta steel/teal. Sem dark mode novo; o Kanban segue o mesmo light corporate clean.
2. **Tailwind only:** Zero CSS inline. Todas as classes via Tailwind + design tokens do `app.css`.
3. **Hierarquia por cor de coluna:** Cada coluna Kanban tem uma cor semantica que aparece no header da coluna, no badge do card quando fora do board, e na zona de drop.
4. **Dados mock realistas:** Nomes reais de disciplinas (NLP, Deep Learning), titulos de carrosseis como "Transfer Learning na pratica com PyTorch", prioridades variadas, avatares com iniciais reais.

---

## Paleta de Cores das Colunas

| Coluna | Cor do Header | Tailwind bg | Tailwind text | Tailwind border | Hex |
|--------|--------------|-------------|---------------|-----------------|-----|
| Copy | Azul | `bg-blue-500/10` | `text-blue-600` | `border-blue-500/30` | #3B82F6 |
| Design | Roxo | `bg-purple-500/10` | `text-purple-600` | `border-purple-500/30` | #8B5CF6 |
| Revisao | Amarelo | `bg-amber-500/10` | `text-amber-600` | `border-amber-500/30` | #F59E0B |
| Aprovado | Verde | `bg-emerald-500/10` | `text-emerald-600` | `border-emerald-500/30` | #10B981 |
| Publicado | Ciano | `bg-cyan-500/10` | `text-cyan-600` | `border-cyan-500/30` | #06B6D4 |
| Cancelado | Vermelho/cinza | `bg-red-500/10` | `text-red-500` | `border-red-500/30` | #EF4444 |

---

## Tokens de Design Novos (adicionar ao app.css)

```css
/* === Kanban Column Colors === */
--color-col-copy: #3B82F6;
--color-col-design: #8B5CF6;
--color-col-revisao: #F59E0B;
--color-col-aprovado: #10B981;
--color-col-publicado: #06B6D4;
--color-col-cancelado: #EF4444;
```

Nao precisa registrar no `@theme` como variaveis customizadas. Usar classes Tailwind nativas (blue-500, purple-500, etc.) diretamente nos componentes.

---

## DESIGN -- TELA 1: Login

**Rota:** `/login`

**Padrao de Layout:** Centralizado. Card unico no centro vertical e horizontal da viewport. Fundo `bg-global` com o mesmo gradiente sutil do hero (reutilizar `.hero-bg`). Sem sidebar, sem header.

**Hierarquia Visual:**
1. Logo Content Factory (CF) + nome "Content Factory" -- ancora visual no topo do card
2. Campos email + senha -- area de acao principal
3. Botao "Entrar" -- CTA primario
4. Separador "ou" -- divisor visual
5. Botoes SSO Google / Microsoft -- alternativas secundarias

**Grupos de Campos:**
- 1 coluna, max-width 400px
- Logo + titulo no topo (reutilizar o bloco do Sidebar: icone gradiente CF + texto)
- Campos email e senha empilhados com gap-4
- Botao Entrar full-width abaixo dos campos
- Separador visual (`<hr>` com texto "ou continue com") entre form e SSO
- 2 botoes SSO lado a lado (Google | Microsoft), cada um com icone do provedor

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Container | Card | `padding: lg`, `shadow: lg`, `hover: false` |
| Logo | div customizado | Reutilizar icone CF do Sidebar (w-10 h-10, gradient steel-3 to steel-5) |
| Email | Input | `type: email`, `placeholder: "seu@email.com"`, `disabled: false` |
| Senha | Input | `type: password`, `placeholder: "Sua senha"`, `disabled: false` |
| Toggle senha | Button | `variant: outline`, `size: sm` (icone de olho dentro do input) |
| Entrar | Button | `variant: primary`, `size: lg`, full-width |
| SSO Google | Button | `variant: outline`, `size: md`, icone Google SVG |
| SSO Microsoft | Button | `variant: outline`, `size: md`, icone Microsoft SVG |
| Erro | Alert | `type: error`, `dismissible: false` |
| Loading | LoadingSpinner | `size: sm`, dentro do botao Entrar |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Login com sucesso | Redirect imediato | -- (sem mensagem, redirect para `/`) |
| Email ou senha incorretos | Alert inline abaixo do form | "Email ou senha incorretos. Verifique e tente novamente." |
| Rate limit (429) | Alert inline abaixo do form | "Muitas tentativas. Aguarde 1 minuto antes de tentar novamente." |
| Erro de conexao | Alert inline abaixo do form | "Erro de conexao com o servidor. Verifique sua internet." |
| Loading login | Spinner no botao + botoes desabilitados | Botao muda texto para "Entrando..." com spinner |
| Loading SSO | Botao SSO desabilitado + spinner | -- |

**Estados Visuais:**

| Estado | Comportamento |
|--------|--------------|
| Inicial | Campos vazios, botoes habilitados, sem mensagens de erro |
| Loading | Spinner dentro do botao "Entrar" (substituir texto). Todos os inputs e botoes com `disabled`. Opacidade 50% nos botoes desabilitados |
| Erro | Alert `type: error` aparece abaixo do formulario com animate-fade-up. Campo com erro recebe `border-red` + `ring-red/12` |
| Sucesso | Redirect imediato, sem estado visivel |

**Responsividade:**
- Mobile: Card ocupa `w-full px-6`, sem padding lateral extra
- Tablet+: Card com `max-w-md mx-auto`
- O fundo hero-bg cobre toda a viewport

---

## DESIGN -- TELA 2: Board Kanban

**Rota:** `/kanban`

**Padrao de Layout:** Sidebar esquerda (existente) + area de conteudo principal com scroll horizontal. O board ocupa 100% da largura disponivel. As 6 colunas ficam lado a lado com scroll horizontal quando nao cabem.

**Hierarquia Visual:**
1. Titulo "Kanban" + botao "Novo Card" + botao Refresh -- barra de acoes no topo
2. Barra de filtros -- abaixo do titulo, com busca + dropdowns
3. 6 colunas com cards -- area principal do board
4. Cards dentro de cada coluna -- conteudo principal

**Grupos de Campos:**

Barra superior (1 linha):
- Esquerda: titulo "Kanban" (text-2xl font-bold text-steel-6)
- Direita: botao "Novo Card" (primary, sm) + botao refresh (outline, sm, icone de refresh)

Barra de filtros (1 linha, abaixo do titulo):
- Input de busca (w-64, icone de lupa)
- Select responsavel
- Select coluna (multi-check ou dropdown simples no MVP)
- Select prioridade
- Botao "Limpar filtros" (outline, sm) -- visivel apenas quando ha filtro ativo

Board (area principal):
- Container com `overflow-x-auto` para scroll horizontal
- Flex row com gap-4, min-width por coluna de 280px
- Cada coluna: flex column com header colorido + lista de cards

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Titulo | h1 | `text-2xl font-bold text-steel-6` |
| Novo Card | Button | `variant: primary`, `size: sm`, icone "+" |
| Refresh | Button | `variant: outline`, `size: sm`, icone refresh (setas circulares) |
| Busca | Input | `type: text`, `placeholder: "Buscar por titulo..."`, icone lupa |
| Filtro responsavel | select nativo | dropdown com usuarios |
| Filtro prioridade | select nativo | dropdown: Alta, Media, Baixa |
| Filtro coluna | select nativo | dropdown: 6 colunas |
| Limpar filtros | Button | `variant: outline`, `size: sm` |
| Coluna header | div | Barra colorida no topo (4px border-top com cor da coluna), titulo + contagem de cards |
| Card | Card (KanbanCard) | `padding: sm`, `shadow: sm`, `hover: true` |
| Badge prioridade | Badge | `variant: danger` (alta), `variant: secondary` (media, amarelo), `variant: secondary` (baixa, cinza), `size: sm` |
| Badge disciplina | Badge | `variant: primary`, `size: sm` |
| Avatares | div | Circulos empilhados, 24x24, -space-x-2 |

**Anatomia do KanbanCard (compacto):**

```
+------------------------------------------+
| [Badge prioridade]              ha 2 dias |
| Titulo do carrossel (truncado 2 linhas)  |
| [Badge NLP]  [Avatar A] [Avatar B] [+1] |
|                           [balao 3]      |
+------------------------------------------+
```

- Padding: `p-3`
- Border radius: `rounded-xl`
- Background: `bg-bg-card`
- Border: `border border-border-default`
- Hover: `hover:shadow-md hover:border-purple/30 transition-all cursor-pointer`
- Titulo: `text-sm font-medium text-text-primary line-clamp-2`
- Data: `text-[11px] text-text-muted`
- Badge prioridade alta: `bg-red-500/10 text-red-600 text-[10px] px-1.5 py-0.5 rounded-full font-medium`
- Badge prioridade media: `bg-amber-500/10 text-amber-600 text-[10px] px-1.5 py-0.5 rounded-full font-medium`
- Badge prioridade baixa: `bg-gray-500/10 text-gray-500 text-[10px] px-1.5 py-0.5 rounded-full font-medium`
- Avatares: `w-6 h-6 rounded-full bg-steel-3/20 text-[9px] font-bold text-steel-3 flex items-center justify-center`
- Indicador comentarios: icone balao 14x14 + numero, `text-[11px] text-text-muted`

**Anatomia da KanbanColumn:**

```
+-- border-top 4px (cor da coluna) --+
| [icone] COPY                    12 |
|                                    |
| [Card 1]                          |
| [Card 2]                          |
| [Card 3]                          |
| ...                               |
+------------------------------------+
```

- Container: `min-w-[280px] w-[280px] flex flex-col bg-bg-elevated/50 rounded-xl`
- Header: `px-3 py-2.5 border-t-4` (com a cor da coluna)
- Nome da coluna: `text-xs font-semibold uppercase tracking-wide` (cor da coluna)
- Contagem: `text-[11px] text-text-muted ml-auto bg-bg-card rounded-full px-2 py-0.5`
- Lista de cards: `flex flex-col gap-2 p-2 flex-1 overflow-y-auto scrollbar-thin`

**Drag-and-Drop:**

- Somente para coluna Cancelado (RN-019)
- Card sendo arrastado: `opacity-50 rotate-2 scale-105 shadow-lg`
- Zona de drop Cancelado ativa (quando card esta sendo arrastado): `border-2 border-dashed border-red-500/50 bg-red-500/5` no container da coluna. Texto "Solte aqui para cancelar" aparece se a coluna estiver vazia
- Demais colunas: sem zona de drop ativa (nao aceitam drag)
- Ao soltar: optimistic update (card aparece na coluna Cancelado imediatamente)

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Card movido para Cancelado | Toast success | "Carrossel movido para Cancelado." |
| Erro ao mover | Toast error | "Erro ao cancelar carrossel. Tente novamente." |
| Filtro aplicado | Board re-renderiza | Sem mensagem (resultado visual imediato) |
| Filtros limpos | Board re-renderiza | Sem mensagem |
| Refresh | Board re-carrega + spinner no botao | Botao refresh gira (animate-spin) durante o fetch |
| Card criado | Toast success | "Carrossel criado com sucesso." |

**Estados Visuais:**

| Estado | Comportamento |
|--------|--------------|
| Loading | 6 colunas skeleton: header com shimmer + 3 cards placeholder por coluna (retangulos `animate-shimmer` com border-radius). Reutilizar `.animate-shimmer` do app.css |
| Board vazio | 6 colunas vazias com headers coloridos. No centro do board: mensagem "Nenhum carrossel em producao." + subtexto "Crie um conteudo na Home para comecar." + Button link para `/` (`variant: primary`, `size: md`) |
| Filtro sem resultado | 6 colunas vazias. Mensagem centralizada: "Nenhum card encontrado para esses filtros." + Button "Limpar filtros" (`variant: outline`, `size: sm`) |
| Erro | Banner no topo (reutilizar Banner.svelte existente): `type: error`, texto "Erro ao carregar o board." + botao "Tentar novamente" |
| Sucesso | Board com cards distribuidos. Drag ativo para Cancelado |

**Responsividade:**
- Desktop (md+): 6 colunas visiveis, scroll horizontal se necessario. Colunas com `min-w-[280px]`
- Mobile (<md): Container com `overflow-x-auto`. Colunas em scroll horizontal com snap (`snap-x snap-mandatory`). Cada coluna `snap-center`. Indicador visual de "arraste para ver mais colunas" (sombra gradient na borda direita)
- Barra de filtros: no mobile, colapsa para um botao "Filtros" que abre um drawer/sheet
- Botao "Novo Card": no mobile, FAB (floating action button) no canto inferior direito (`fixed bottom-6 right-6 w-14 h-14 rounded-full bg-purple text-white shadow-lg`)

---

## DESIGN -- TELA 3: Modal Detalhe do Card

**Rota:** `/kanban` (overlay, sem mudar URL base -- adiciona `?card=abc123`)

**Padrao de Layout:** Modal centralizado, max-width 720px, max-height 85vh. Overlay escuro (`bg-black/60`). 3 abas no topo do conteudo.

**Hierarquia Visual:**
1. Titulo do card + badge de coluna atual -- ancora no header do modal
2. Abas (Detalhes | Comentarios | Atividade) -- navegacao principal
3. Conteudo da aba ativa -- area scrollavel
4. Botao fechar (X) -- canto superior direito

**Layout do Modal:**

```
+-- Modal (max-w-3xl) -------------------------+
| [X]                                          |
| Titulo do carrossel                          |
| [Badge coluna: Copy]  [Badge prioridade]     |
|                                              |
| [Detalhes] [Comentarios (3)] [Atividade]     |
| -------------------------------------------- |
|                                              |
| (conteudo da aba ativa, scrollavel)          |
|                                              |
+----------------------------------------------+
```

### Aba 1: Detalhes

**Grupos de Campos:**
- 2 colunas em desktop, 1 coluna em mobile
- Coluna esquerda: titulo, copy_text, disciplina, tecnologia, prioridade, responsaveis (campos editaveis)
- Coluna direita: coluna_atual, criado_por, criado_em, atualizado_em, pipeline_id, drive_link, pdf_url (campos readonly)
- Galeria de imagens: full-width abaixo das 2 colunas (thumbnails 80x80 em grid)

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Modal container | Modal | `open: true`, `title: ""` (titulo customizado no body), `size: lg` |
| Titulo card | Input | `type: text`, inline edit (borda aparece no hover/focus) |
| Copy text | textarea | Inline edit, `rows: 4`, resize-y |
| Disciplina | select | Dropdown com lista de disciplinas |
| Tecnologia | select | Dropdown dependente da disciplina |
| Prioridade | select | Dropdown: Alta, Media, Baixa |
| Responsaveis | select multi | Autocomplete com avatares |
| Coluna atual | Badge | Cor da coluna (readonly) |
| Campos readonly | span | `text-sm text-text-secondary` com label-upper acima |
| Drive link | a (link externo) | `text-purple hover:underline`, icone external-link |
| PDF link | a (link) | `text-purple hover:underline` |
| Galeria imagens | grid de thumbnails | `grid grid-cols-4 gap-2`, imagens `rounded-lg object-cover w-20 h-20` |
| Botao salvar | Button | `variant: primary`, `size: sm` |
| Botao fechar | Button | `variant: outline`, `size: sm`, icone X |

### Aba 2: Comentarios

**Layout:**
- Lista cronologica de comentarios (mais recente embaixo)
- Campo de novo comentario fixo no bottom da aba

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Lista comentarios | div scrollavel | `max-h-[50vh] overflow-y-auto scrollbar-thin` |
| CommentItem | Card | `padding: sm`, `shadow: none`, `hover: false` |
| Avatar autor | div | `w-8 h-8 rounded-full` com iniciais ou foto |
| Nome autor | span | `text-sm font-medium text-text-primary` |
| Data | span | `text-[11px] text-text-muted` (relativa, tooltip absoluta) |
| Texto comentario | p | `text-sm text-text-secondary mt-1` |
| Botao editar | Button | `variant: outline`, `size: sm`, icone lapis (visivel so para autor) |
| Botao deletar | Button | `variant: danger`, `size: sm`, icone lixeira (visivel para autor + Admin) |
| Novo comentario | textarea | `rows: 2`, `placeholder: "Escreva um comentario..."` |
| Enviar | Button | `variant: primary`, `size: sm`, texto "Enviar" |

### Aba 3: Atividade (Audit Log)

**Layout:**
- Timeline vertical com linha conectora a esquerda
- Cada entry: icone + descricao + usuario + data

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Timeline container | div | `relative` com linha vertical `absolute left-4 top-0 bottom-0 w-0.5 bg-border-default` |
| Entry icone | div | `w-8 h-8 rounded-full bg-bg-elevated flex items-center justify-center relative z-10` |
| Descricao | p | `text-sm text-text-primary` |
| Usuario | span | `text-sm font-medium text-purple` |
| Data | span | `text-[11px] text-text-muted` |
| Carregar mais | Button | `variant: outline`, `size: sm`, texto "Carregar mais" |

**Icones por tipo de acao:**

| Acao | Icone | Cor do circulo |
|------|-------|---------------|
| card_created | Plus | `bg-emerald-500/10 text-emerald-600` |
| column_changed | ArrowRight | `bg-blue-500/10 text-blue-600` |
| assignee_changed | User | `bg-purple-500/10 text-purple-600` |
| field_edited | Pencil | `bg-amber-500/10 text-amber-600` |
| comment_added | MessageCircle | `bg-cyan-500/10 text-cyan-600` |
| image_generated | Image | `bg-pink-500/10 text-pink-600` |
| drive_linked | Link | `bg-teal-6/10 text-teal-6` |
| pdf_exported | FileText | `bg-orange-500/10 text-orange-600` |

**Feedback de Acoes (Modal Geral):**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Salvar campo editado | Toast success | "Alteracoes salvas." |
| Erro ao salvar | Toast error | "Erro ao salvar alteracoes. Tente novamente." |
| Comentario enviado | Comentario aparece na lista (optimistic) | Sem toast (visual imediato) |
| Erro ao enviar comentario | Alert inline abaixo do campo | "Erro ao enviar comentario." |
| Deletar comentario | Modal confirmacao | "Tem certeza que deseja excluir este comentario?" |
| Comentario deletado | Comentario some da lista (optimistic) | Toast info: "Comentario excluido." |
| Atribuir responsavel | Toast success | "Responsavel atribuido." + notificacao gerada |

**Estados Visuais:**

| Estado | Aba | Comportamento |
|--------|-----|--------------|
| Loading | Detalhes | Skeleton dos campos: retangulos shimmer onde ficam os inputs |
| Loading | Comentarios | Spinner centralizado na area de comentarios |
| Loading | Atividade | Spinner centralizado na area de timeline |
| Vazio | Comentarios | Texto: "Nenhum comentario ainda. Seja o primeiro a comentar." + icone de balao 48x48 opacidade 30% |
| Vazio | Atividade | Texto: "Nenhuma atividade registrada." (raro) |
| Erro | Comentarios | Inline: "Erro ao carregar comentarios." + Button "Tentar novamente" |
| Erro | Atividade | Inline: "Erro ao carregar atividades." + Button "Tentar novamente" |
| Viewer | Todas | Campos de edicao ficam `disabled`. Campo de novo comentario oculto. Botoes editar/deletar ocultos |

**Responsividade:**
- Desktop: Modal `max-w-3xl`, 2 colunas na aba Detalhes
- Mobile: Modal full-screen (`w-full h-full rounded-none`), 1 coluna, abas com scroll horizontal se necessario

---

## DESIGN -- TELA 4: Modal Criar Card

**Rota:** `/kanban` (overlay)

**Padrao de Layout:** Modal centralizado, menor que o detalhe. Max-width 520px. Formulario simples, 1 coluna.

**Hierarquia Visual:**
1. Titulo "Novo carrossel" -- header do modal
2. Campos do formulario -- area de acao
3. Botoes Cancelar / Criar -- footer do modal

**Grupos de Campos:**
- 1 coluna, todos os campos empilhados com gap-4
- Titulo (text, obrigatorio)
- Copy text (textarea, opcional)
- Disciplina (select)
- Tecnologia (select, dependente)
- Prioridade (select, pre-selecionado "Media")
- Responsaveis (select multi)

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Modal | Modal | `open: true`, `title: "Novo carrossel"`, `size: md` |
| Titulo | Input | `type: text`, `placeholder: "Ex: Transfer Learning na pratica com PyTorch"` |
| Copy text | textarea | `rows: 3`, `placeholder: "Texto do conteudo (opcional)"` |
| Disciplina | select | Dropdown reutilizando store disciplinas |
| Tecnologia | select | Dropdown dependente |
| Prioridade | select | Dropdown: Alta, Media (selected), Baixa |
| Responsaveis | select multi | Autocomplete com avatares dos usuarios |
| Cancelar | Button | `variant: outline`, `size: md` |
| Criar | Button | `variant: primary`, `size: md` |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Criar com sucesso | Modal fecha + toast success no board | "Carrossel criado com sucesso." |
| Erro de validacao | Inline abaixo do campo | "Titulo e obrigatorio (min. 3 caracteres)." |
| Erro do servidor | Alert inline abaixo do formulario | "Erro ao criar carrossel. Tente novamente." |
| Loading | Spinner no botao Criar | Texto muda para "Criando..." + spinner |

**Estados Visuais:**

| Estado | Comportamento |
|--------|--------------|
| Inicial | Campos vazios, prioridade "Media" pre-selecionada, botao Criar habilitado |
| Loading | Spinner no botao Criar, todos os campos e botoes `disabled` |
| Erro validacao | Borda vermelha no campo + mensagem abaixo (`text-xs text-red-500 mt-1`) |
| Erro servidor | Alert `type: error` abaixo do ultimo campo |

**Responsividade:**
- Desktop: Modal `max-w-lg` centralizado
- Mobile: Modal full-width com `mx-4`, ou full-screen se tela < 480px

---

## DESIGN -- TELA 5: Gerenciamento de Usuarios

**Rota:** `/kanban/usuarios`

**Padrao de Layout:** Sidebar esquerda (existente) + conteudo principal com tabela. Mesmo layout das paginas de sistema existentes (Agentes, Config).

**Hierarquia Visual:**
1. Titulo "Usuarios" + botao "Convidar Usuario" -- barra de acoes no topo
2. Tabela de usuarios -- conteudo principal
3. Acoes por linha (Editar, Desativar) -- controles inline

**Grupos de Campos:**
- Barra superior: titulo esquerda + botao convidar direita
- Tabela: 7 colunas (Avatar, Nome, Email, Perfil, Status, Criado em, Acoes)
- Abaixo da tabela: paginacao (se > 20 usuarios)

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Titulo | h1 | `text-2xl font-bold text-steel-6` |
| Convidar | Button | `variant: primary`, `size: sm`, icone "+" |
| Tabela container | div | `bg-bg-card rounded-xl border border-border-default overflow-hidden` |
| Cabecalho tabela | thead | `bg-bg-elevated text-text-muted text-xs uppercase tracking-wide` |
| Avatar na linha | div | `w-8 h-8 rounded-full` com iniciais (bg baseado na role) |
| Badge perfil | Badge | Cores por role abaixo |
| Badge status | Badge | Ativo: `variant: success`, `size: sm`; Desativado: `variant: secondary`, `size: sm` (cinza) |
| Editar | Button | `variant: outline`, `size: sm`, icone lapis |
| Desativar | Button | `variant: danger`, `size: sm`, texto "Desativar" |
| Reativar | Button | `variant: outline`, `size: sm`, texto "Reativar" |

**Cores dos Badges de Perfil:**

| Perfil | Background | Text |
|--------|-----------|------|
| Admin | `bg-purple-500/10` | `text-purple-600` |
| Copywriter | `bg-blue-500/10` | `text-blue-600` |
| Designer | `bg-pink-500/10` | `text-pink-600` |
| Reviewer | `bg-amber-500/10` | `text-amber-600` |
| Viewer | `bg-gray-500/10` | `text-gray-500` |

**Modal Convidar/Editar Usuario:**
- Reutilizar o padrao do Modal Criar Card
- Max-width 480px
- Campos: nome (text), email (email), perfil (select com 5 opcoes), avatar_url (text URL, opcional)
- No modo editar: email readonly (cinza, disabled)
- Botoes: Cancelar (outline) + Salvar (primary)

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Usuario criado | Toast success + tabela atualiza | "Usuario convidado com sucesso." |
| Usuario editado | Toast success + tabela atualiza | "Usuario atualizado." |
| Desativar usuario | Modal confirmacao primeiro | "Desativar Ana Silva? Ela perdera acesso ao sistema." |
| Usuario desativado | Toast info + status muda na tabela | "Usuario desativado." |
| Usuario reativado | Toast success + status muda na tabela | "Usuario reativado." |
| Erro | Toast error | "Erro ao salvar usuario. Tente novamente." |
| Email duplicado | Inline abaixo do campo email | "Ja existe um usuario com este email." |

**Estados Visuais:**

| Estado | Comportamento |
|--------|--------------|
| Loading | Skeleton da tabela: 5 linhas shimmer com colunas placeholder |
| Vazio | Mensagem centralizada: "Nenhum usuario cadastrado alem de voce. Convide sua equipe!" + Button "Convidar Usuario" (`variant: primary`) |
| Erro | Banner `type: error` no topo: "Erro ao carregar usuarios." + Button "Tentar novamente" |
| Sucesso | Tabela preenchida com zebra stripe sutil (`even:bg-bg-elevated/30`) |

**Responsividade:**
- Desktop: Tabela completa com todas as colunas
- Tablet: Ocultar coluna "Criado em"
- Mobile: Transformar tabela em lista de cards. Cada usuario vira um card com avatar + nome + email + badge perfil + acoes

---

## DESIGN -- TELA 6: Notificacoes (Dropdown)

**Rota:** Global (presente em todas as telas, no header)

**Padrao de Layout:** Icone de sino no header direito + dropdown posicionado abaixo do icone, alinhado a direita. Dropdown com largura fixa de 360px.

**Hierarquia Visual:**
1. Icone de sino + badge numerico -- gatilho visual
2. Header do dropdown "Notificacoes" + "Marcar todas como lidas"
3. Lista de notificacoes -- conteudo principal
4. Indicador de nao-lida (bolinha azul) -- destaque por item

**Posicionamento no Header:**
- Desktop: Ao lado direito do header, antes do avatar do usuario logado
- Mobile: No header fixo existente, ao lado do menu hamburger (lado direito)

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Icone sino | button | `p-2 rounded-lg hover:bg-black/5 relative` |
| Badge contador | div | `absolute -top-1 -right-1 w-5 h-5 rounded-full bg-red text-white text-[10px] font-bold flex items-center justify-center`. Oculto se zero. "9+" se > 9 |
| Dropdown container | div | `absolute right-0 top-full mt-2 w-[360px] bg-bg-card rounded-xl border border-border-default shadow-lg z-50 max-h-[480px] overflow-hidden flex flex-col` |
| Header dropdown | div | `px-4 py-3 border-b border-border-default flex items-center justify-between` |
| Titulo | span | `text-sm font-semibold text-text-primary` = "Notificacoes" |
| Marcar todas | Button | `variant: outline`, `size: sm`, texto "Marcar todas como lidas" |
| Lista notificacoes | div | `overflow-y-auto scrollbar-thin flex-1` |
| Item notificacao | button (clicavel) | `w-full px-4 py-3 flex gap-3 hover:bg-bg-elevated transition-all text-left` |
| Icone tipo | div | `w-8 h-8 rounded-full shrink-0` com cor por tipo |
| Bolinha nao-lida | div | `w-2 h-2 rounded-full bg-purple shrink-0 mt-1.5` (ausente se lida) |
| Mensagem | p | `text-sm text-text-primary` (nao-lida: `font-medium`; lida: `font-normal text-text-secondary`) |
| Data | span | `text-[11px] text-text-muted` |

**Cores dos Icones por Tipo:**

| Tipo | Background | Icone |
|------|-----------|-------|
| assigned | `bg-purple-500/10 text-purple-600` | User |
| column_changed | `bg-blue-500/10 text-blue-600` | ArrowRight |
| mentioned | `bg-cyan-500/10 text-cyan-600` | At (pos-MVP) |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Clicar em notificacao | Marca como lida (fundo muda) + navega para card | -- |
| Marcar todas como lidas | Badge zera + todas perdem bolinha azul + perdem font-medium | -- |
| Erro ao carregar | Inline no dropdown | "Erro ao carregar notificacoes." |

**Estados Visuais:**

| Estado | Comportamento |
|--------|--------------|
| Sem notificacoes | Sino sem badge. Dropdown mostra: icone sino grande (48x48, opacidade 20%) + "Nenhuma notificacao." |
| Com nao-lidas | Sino com badge vermelho (numero). Dropdown mostra lista com itens nao-lidos destacados (bolinha azul + font-medium + fundo `bg-purple/3`) |
| Todas lidas | Sino sem badge. Dropdown mostra lista normal (sem destaques) |
| Loading | Spinner centralizado dentro do dropdown |
| Erro | Mensagem inline + botao "Tentar novamente" |

**Responsividade:**
- Desktop: Dropdown `w-[360px]` posicionado absolute
- Mobile: Dropdown `w-[calc(100vw-2rem)]` posicionado `fixed left-4 right-4 top-16` (abaixo do header fixo)

---

## Componentes UI Transversais

### Toast (Notificacao de Acao)

Componente global posicionado no canto superior direito (`fixed top-6 right-6 z-50`). Usado para feedback de acoes (salvar, criar, deletar, mover).

| Variante | Classes | Duracao |
|----------|---------|---------|
| Success | `bg-emerald-500/10 border border-emerald-500/30 text-emerald-700` | 3s auto-dismiss |
| Error | `bg-red-500/10 border border-red-500/30 text-red-700` | 5s auto-dismiss |
| Info | `bg-blue-500/10 border border-blue-500/30 text-blue-700` | 3s auto-dismiss |

- Animacao entrada: `animate-fade-up`
- Animacao saida: fade-out + slide-up
- Dismissible: botao X a direita
- Max 3 toasts visiveis simultaneamente, empilhados com gap-2

### Modal de Confirmacao (Acoes Destrutivas)

Usado para: cancelar card (drag para Cancelado), deletar comentario, desativar usuario.

| Secao | Componente | Props |
|-------|-----------|-------|
| Modal | Modal | `size: sm`, overlay escuro |
| Icone | div | `w-12 h-12 rounded-full bg-red-500/10 text-red-500 mx-auto` com icone AlertTriangle |
| Titulo | h3 | `text-lg font-semibold text-text-primary text-center` |
| Descricao | p | `text-sm text-text-secondary text-center` |
| Cancelar | Button | `variant: outline`, `size: md` |
| Confirmar | Button | `variant: danger`, `size: md` |

### Skeleton Loading

Reutilizar `.animate-shimmer` existente no app.css.

- Cards: `rounded-xl h-24 bg-bg-elevated animate-shimmer`
- Linhas de texto: `rounded h-3 w-3/4 bg-bg-elevated animate-shimmer`
- Avatares: `rounded-full w-8 h-8 bg-bg-elevated animate-shimmer`
- Tabela: linhas de `h-12 bg-bg-elevated animate-shimmer` com gap-2

---

## Alteracoes no Layout Existente

### Sidebar (Sidebar.svelte)

Adicionar 2 itens:

1. Na secao "Principal", entre "Home" e "Historico":
   - Label: "Kanban"
   - Icone: ViewColumns (path SVG para quadro com colunas)
   - Href: `/kanban`

2. Na secao "Sistema", apos "Config":
   - Label: "Usuarios"
   - Icone: UserGroup (path SVG para grupo de pessoas)
   - Href: `/kanban/usuarios`
   - Visibilidade: somente se `role === 'admin'` (ler do store auth)

### Header (+layout.svelte)

Adicionar ao header (tanto desktop quanto mobile):
- NotificationBell component (icone sino + badge) -- lado direito
- Avatar do usuario logado -- lado direito, apos sino
  - `w-8 h-8 rounded-full bg-steel-3/20 text-xs font-bold text-steel-3`
  - Clique abre mini dropdown: "Meu Perfil" (pos-MVP), "Sair" (limpa JWT, redirect `/login`)

---

## Dados Mock Realistas

Usar nos mocks (board.mock.ts, cards.mock.ts, etc.):

**Usuarios:**
- Carlos Viana (Admin, avatar "CV")
- Ana Beatriz (Copywriter, avatar "AB")
- Pedro Nakamura (Designer, avatar "PN")
- Luisa Ferreira (Reviewer, avatar "LF")
- Marcos Oliveira (Viewer, avatar "MO")

**Cards (titulos):**
- "Transfer Learning na pratica com PyTorch"
- "7 habitos de devs que conquistam vagas na gringa"
- "RAG vs Fine-tuning: quando usar cada um"
- "Feature Engineering para modelos preditivos"
- "Deploy serverless na AWS com Lambda e SAM"
- "NLP com Whisper: transcreva audios em segundos"
- "Data Drift: como monitorar modelos em producao"
- "XGBoost vs Random Forest: benchmark completo"
- "OpenCV na pratica: deteccao de objetos em tempo real"
- "ETL moderno com Airflow e dbt"

**Disciplinas nos cards:**
- D5 Deep Learning, D7 IA Gen, D3 ML, D4 Preditiva, D8 Cloud, D6 NLP, D9 MLOps, D1 Linguagens, D2 ETL

**Comentarios:**
- "Ajustei o titulo pra ficar mais viral. O anterior era muito tecnico pro LinkedIn." (Ana Beatriz)
- "Imagem ficou com contraste baixo na parte inferior. Vou regerar com prompt ajustado." (Pedro Nakamura)
- "Aprovado! Texto e imagem estao otimos. Pode publicar." (Luisa Ferreira)
- "Adicionei referencia visual de gradiente escuro. Ficou mais alinhado com a marca." (Pedro Nakamura)

**Notificacoes:**
- "Carlos atribuiu voce ao card 'NLP com Whisper'" (tipo: assigned)
- "Card 'RAG vs Fine-tuning' moveu de Copy para Design" (tipo: column_changed)
- "Pedro mencionou voce em 'Transfer Learning'" (tipo: mentioned, pos-MVP)

---

## Resumo de Componentes Novos

| Componente | Arquivo | Tipo |
|-----------|---------|------|
| KanbanBoard | `components/kanban/KanbanBoard.svelte` | Dominio |
| KanbanColumn | `components/kanban/KanbanColumn.svelte` | Dominio |
| KanbanCard | `components/kanban/KanbanCard.svelte` | Dominio |
| KanbanFilters | `components/kanban/KanbanFilters.svelte` | Dominio |
| CardDetailModal | `components/kanban/CardDetailModal.svelte` | Dominio |
| CardDetailTab | `components/kanban/CardDetailTab.svelte` | Dominio |
| CardCommentsTab | `components/kanban/CardCommentsTab.svelte` | Dominio |
| CardActivityTab | `components/kanban/CardActivityTab.svelte` | Dominio |
| CardCreateModal | `components/kanban/CardCreateModal.svelte` | Dominio |
| CommentItem | `components/kanban/CommentItem.svelte` | Dominio |
| LoginForm | `components/auth/LoginForm.svelte` | Dominio |
| SSOButtons | `components/auth/SSOButtons.svelte` | Dominio |
| NotificationBell | `components/notification/NotificationBell.svelte` | Dominio |
| NotificationDropdown | `components/notification/NotificationDropdown.svelte` | Dominio |
| UserTable | `components/user/UserTable.svelte` | Dominio |
| UserFormModal | `components/user/UserFormModal.svelte` | Dominio |
| Toast | `components/ui/Toast.svelte` | UI generico |
| ConfirmModal | `components/ui/ConfirmModal.svelte` | UI generico |
