# DESIGN -- Content Factory v3

Documento gerado pelo Agente 05 (Arquiteto Designer) da esteira IT Valley.
Base: PRD (Agente 01) + TELAS (Agente 02) + ARQUITETURA_FRONTEND (Agente 04) + design-system.html + nano-banana-carrossel.md + codigo existente no frontend SvelteKit 5.

---

## Decisao Critica: Migracao de Tema

O frontend existente usa um tema **light** (paleta teal/steel, fundo #E6EEEC, cards #FAFCFB). O design system da marca, o PRD e as skills todas definem um **dark mode premium** (#0A0A0F fundo, #12121A cards, #A78BFA roxo). A v3 deve migrar integralmente para o dark mode premium, alinhando app e conteudo gerado sob a mesma identidade visual.

### Tokens de Cor (app.css @theme) -- v3

| Token | Valor | Uso |
|-------|-------|-----|
| --color-bg-global | #0A0A0F | Fundo de toda a aplicacao |
| --color-bg-card | #12121A | Cards, paineis, sidebar |
| --color-bg-code | #0D0D18 | Blocos de codigo |
| --color-bg-elevated | #1A1A2A | Elementos elevados (menus, tooltips, titlebar) |
| --color-bg-input | #12121A | Campos de input |
| --color-border-default | rgba(167,139,250,0.2) | Bordas de cards, inputs, divisores |
| --color-border-active | #A78BFA | Borda ao focar ou selecionar |
| --color-text-primary | #FFFFFF | Titulos, conteudo principal |
| --color-text-secondary | #9896A3 | Corpo, legendas |
| --color-text-muted | #5A5A66 | Paginacao, placeholders |
| --color-purple | #A78BFA | Acento principal, keywords, links |
| --color-purple-soft | #C4B5FD | Citacoes, hovers suaves |
| --color-purple-deep | #6D28D9 | Gradientes, backgrounds ativos |
| --color-green | #34D399 | Sucesso, badges positivos, codigo |
| --color-amber | #FBBF24 | Atencao, metricas, numeros |
| --color-red | #F87171 | Erro, perigo, acoes destrutivas |

### Tipografia

| Fonte | Uso | Pesos |
|-------|-----|-------|
| Outfit | Toda a UI (titulos, corpo, botoes, labels) | 300 (light), 400 (regular), 500 (medium), 600 (semibold) |
| JetBrains Mono | Badges pill, metricas numericas, codigo, IDs | 400 (regular), 600 (semibold) |

---

## Layout Global: Sidebar + Conteudo

**Decisao DT-005:** O layout migra de header horizontal para sidebar esquerda fixa, conforme PRD. A sidebar e o ponto de navegacao central e suporta o fluxo pipeline-centrico da v3.

### Sidebar (esquerda)

- **Largura:** 240px (desktop), colapsavel para 64px (icones), drawer overlay (mobile)
- **Fundo:** #12121A com borda direita rgba(167,139,250,0.2)
- **Logo:** Icone "CF" (Content Factory) em gradiente roxo + texto "Content Factory" abaixo em Outfit 600 branco. Texto some quando colapsada.
- **Itens de navegacao:** Icone + label. Ativo: fundo rgba(167,139,250,0.08) + borda esquerda 3px #A78BFA + texto #A78BFA. Inativo: texto #9896A3. Hover: texto #FFFFFF + fundo rgba(255,255,255,0.04).
- **Separador:** Linha horizontal rgba(167,139,250,0.1) entre grupos de menu.
- **Grupo Principal:** Home, Pipeline (se ativo), Historico
- **Grupo Sistema:** Agentes, Config
- **Grupo Legado:** Carrossel (com badge "legado" em amber, removido quando pipeline estavel)
- **Rodape da sidebar:** Versao "v3.0" em JetBrains Mono 10px, text-muted

### Area de Conteudo

- **Fundo:** #0A0A0F
- **Padding:** px-8 py-6 (desktop), px-4 py-4 (mobile)
- **Max-width:** 1200px centralizado
- **Scroll:** Vertical no conteudo, sidebar fixa

### Responsividade

| Breakpoint | Sidebar | Conteudo |
|------------|---------|----------|
| >= 1024px (lg) | Fixa 240px | Ao lado |
| >= 768px (md) | Colapsada 64px (so icones) | Ao lado |
| < 768px (sm) | Drawer overlay (botao hamburger) | Full width |

---

## Componentes UI -- Design System v3

### Button

| Variant | Fundo | Texto | Borda | Hover | Uso |
|---------|-------|-------|-------|-------|-----|
| primary | #A78BFA | #0A0A0F | nenhuma | shadow-purple + opacity 0.9 | Acoes principais (Criar, Aprovar) |
| secondary | #34D399 | #0A0A0F | nenhuma | shadow-green + opacity 0.9 | Acoes positivas (Salvar Drive) |
| outline | transparente | #A78BFA | 1px rgba(167,139,250,0.2) | bg #12121A + border #A78BFA | Acoes alternativas (Editar, Voltar) |
| ghost | transparente | #A78BFA | nenhuma | bg #12121A | Acoes terciarias (Cancelar) |
| danger | rgba(248,113,113,0.09) | #F87171 | 1px rgba(248,113,113,0.15) | bg rgba(248,113,113,0.15) | Acoes destrutivas (Remover, Rejeitar) |

| Size | Padding | Font |
|------|---------|------|
| sm | px-3 py-1.5 | text-xs |
| md | px-5 py-2.5 | text-sm |
| lg | px-6 py-3 | text-base |

Forma: rounded-full (pill). Transicao: all 0.25s ease.
Loading: spinner branco 16px girando + texto ao lado.

### Card

| Prop | Descricao |
|------|-----------|
| padding sm | p-3 |
| padding md | p-5 |
| padding lg | p-7 |
| shadow sm | shadow-sm (0 1px 6px rgba(0,0,0,0.4)) |
| shadow md | shadow-md (0 4px 16px rgba(0,0,0,0.5)) |
| shadow lg | shadow-lg (0 8px 36px rgba(0,0,0,0.6)) |
| hover true | hover:-translate-y-1 hover:shadow-md hover:border-purple transition-all |

Fundo: #12121A. Borda: 1px rgba(167,139,250,0.2). Border-radius: rounded-xl (14px).
Variante **glow**: pseudo-elemento radial-gradient roxo no canto superior direito, opacity 8%.

### Input

Fundo: #12121A. Borda: 1px rgba(167,139,250,0.2). Border-radius: rounded-lg (10px).
Padding: px-4 py-2.5. Fonte: Outfit 14px. Cor texto: #FFFFFF.
Placeholder: #5A5A66.
Focus: border #A78BFA + ring 3px rgba(167,139,250,0.12).
Disabled: opacity 50% + cursor not-allowed.
Textarea: mesmas regras, min-h-[120px].

### Modal

Overlay: bg-black/60 backdrop-blur-sm.
Container: bg #12121A, border 1px rgba(167,139,250,0.2), rounded-xl, shadow-lg.
Header: px-6 pt-6, titulo em Outfit 600 18px branco, botao fechar (X) ghost.
Body: px-6 py-4.
Footer: px-6 pb-6, flex justify-end gap-3.

| Size | Max-width |
|------|-----------|
| sm | max-w-sm (384px) |
| md | max-w-lg (512px) |
| lg | max-w-2xl (672px) |

Animacao: fade in + scale de 95% para 100%.

### Alert / Banner

| Type | Fundo | Borda | Icone cor | Texto cor |
|------|-------|-------|-----------|-----------|
| success | rgba(52,211,153,0.1) | 1px rgba(52,211,153,0.25) | #34D399 | #34D399 |
| error | rgba(248,113,113,0.09) | 1px rgba(248,113,113,0.15) | #F87171 | #F87171 |
| warning | rgba(251,191,36,0.1) | 1px rgba(251,191,36,0.25) | #FBBF24 | #FBBF24 |
| info | rgba(167,139,250,0.08) | 1px rgba(167,139,250,0.2) | #A78BFA | #A78BFA |

Border-radius: rounded-lg. Padding: px-4 py-3. Dismissible: botao X no canto direito.

### Badge

| Variant | Fundo | Borda | Texto |
|---------|-------|-------|-------|
| primary | rgba(167,139,250,0.08) | 1px rgba(167,139,250,0.2) | #A78BFA |
| secondary | rgba(255,255,255,0.06) | 1px rgba(255,255,255,0.1) | #9896A3 |
| success | rgba(52,211,153,0.1) | 1px rgba(52,211,153,0.25) | #34D399 |
| danger | rgba(248,113,113,0.09) | 1px rgba(248,113,113,0.15) | #F87171 |
| warning | rgba(251,191,36,0.1) | 1px rgba(251,191,36,0.25) | #FBBF24 |

Forma: rounded-full (pill). Fonte: JetBrains Mono 11px uppercase letter-spacing 0.5px.
Size sm: px-2 py-0.5. Size md: px-3 py-1.

### LoadingSpinner

Borda: 2px border-purple/30 border-t-purple rounded-full animate-spin.
Size sm: w-4 h-4. Size md: w-6 h-6. Size lg: w-8 h-8.

### Skeleton

Fundo: #1A1A2A. Animacao: shimmer (gradiente roxo 6% opacity se movendo). Border-radius: rounded-lg.
Variantes: linha (h-4), bloco (h-24), circulo (rounded-full).

### Toggle

Track off: bg #1A1A2A border rgba(167,139,250,0.2).
Track on: bg #A78BFA.
Thumb: bg branco, shadow-sm.
Transicao: 200ms ease.

### Tabs

Tab inativa: text #9896A3, bg transparente.
Tab ativa: text #A78BFA, bg rgba(167,139,250,0.08), border-bottom 2px #A78BFA.
Hover: text #FFFFFF.
Container: border-bottom 1px rgba(167,139,250,0.1).

---

## DESIGN POR TELA

---

### DESIGN -- TELA: Home / Criar Conteudo

**Rota:** `/`

**Padrao de Layout:** Conteudo central com max-width 720px. Formulario vertical em secoes visuais.

**Hierarquia Visual:**
1. Titulo "Criar Conteudo" (Outfit 300, 28px) com subtitulo "Escolha o formato e defina o tema" (#9896A3)
2. Cards de selecao de formato (3 cards lado a lado)
3. Formulario de tema (textarea grande)
4. Botao "Criar Conteudo" (primary, lg)

**Grupos de Campos:**

| Grupo | Campos | Layout | Descricao |
|-------|--------|--------|-----------|
| Formato | formato, modo_funil | Grid 3 colunas (md) / 1 coluna (sm) | Cards clicaveis com icone + nome + dimensao. Card selecionado: borda #A78BFA + glow. Toggle funil abaixo dos cards. |
| Entrada | modo_entrada, tema / disciplina+tech | Full width | Tabs "Texto Livre" / "Disciplina" no topo. Se texto: textarea grande. Se disciplina: grid de cards de disciplina + chips de tecnologia. |
| Criador | foto_criador | Galeria horizontal | Miniaturas circulares 48px com borda. Selecionada: borda #A78BFA. Link "Adicionar fotos" se vazio. |
| Acao | botao submit | Full width | Botao primary lg centralizado. Desabilitado ate preencher obrigatorios. |

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Formato - Carrossel | Card | padding: md, shadow: sm, hover: true |
| Formato - Post Unico | Card | padding: md, shadow: sm, hover: true |
| Formato - Thumbnail | Card | padding: md, shadow: sm, hover: true |
| Formato selecionado | Badge (dentro do card) | variant: primary, size: sm |
| Toggle funil | Toggle | - |
| Tabs entrada | Tabs | - |
| Campo tema | Input (textarea) | type: text, placeholder: "Descreva o tema do conteudo. Seja especifico: qual tecnologia, qual problema, qual resultado..." |
| Card disciplina | Card | padding: sm, shadow: sm, hover: true |
| Chip tecnologia | Badge | variant: primary, size: md |
| Foto criador | - (img circular) | - |
| Botao criar | Button | variant: primary, size: lg, loading: true (quando criando) |

**Cards de formato (detalhe):**
- Carrossel: Icone de slides empilhados. "Carrossel" em Outfit 500. "1080 x 1350" em JetBrains Mono 11px muted. "LinkedIn, Instagram" em text-secondary 12px.
- Post Unico: Icone de imagem. "Post Unico". "1080 x 1080". "Feed Instagram, Facebook, LinkedIn".
- Thumbnail YouTube: Icone de play. "Thumbnail YouTube". "1280 x 720". "YouTube".

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Selecionar formato | Visual imediato | Card com borda roxa + glow. Sem mensagem. |
| Ativar funil | Visual imediato | Toggle ativo + texto "O Strategist criara 5-7 pecas conectadas a partir do seu tema." aparece abaixo |
| Validacao campo vazio | Inline (abaixo do campo) | "Informe o tema do conteudo (minimo 20 caracteres)" |
| Nenhum formato selecionado | Inline (acima do botao) | "Selecione pelo menos um formato de saida" |
| Pipeline criando | Loading no botao | Spinner + "Iniciando pipeline..." |
| Erro backend | Banner (topo do form) | Alert error: "Nao foi possivel iniciar o pipeline. Verifique a conexao com o backend." |
| Pipeline criado | Redirect | Redireciona para `/pipeline/[id]` |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Loading (criando pipeline) | Botao com spinner + texto "Iniciando pipeline...". Cards de formato desabilitados. |
| Vazio (estado inicial) | Todos os campos vazios. Nenhum formato selecionado. Botao desabilitado (opacity 50%). |
| Erro (validacao) | Borda vermelha no campo + mensagem inline #F87171 abaixo do campo. |
| Erro (backend) | Alert type error no topo do formulario. Dismissible. |
| Sucesso | Nao mostra nada na tela -- redireciona imediatamente. |

---

### DESIGN -- TELA: Pipeline (Wizard de Etapas)

**Rota:** `/pipeline/[id]`

**Padrao de Layout:** Conteudo central com max-width 900px. Wizard vertical no centro com cards de etapa.

**Hierarquia Visual:**
1. Header do pipeline: tema (Outfit 600 20px) + formato (Badge primary) + status geral (Badge success/warning/danger)
2. Wizard vertical: 7 etapas com linha conectora
3. Botao de acao da etapa ativa (Aprovar / Retomar)

**Wizard Vertical (detalhe):**
- Linha vertical roxa 2px rgba(167,139,250,0.2) conectando as etapas
- Cada etapa e um PipelineStepCard com:
  - Circulo indicador esquerdo: 32px, posicionado sobre a linha
    - Pendente: borda dashed #5A5A66, fundo transparente
    - Em execucao: borda #A78BFA com animacao pulse, fundo rgba(167,139,250,0.08)
    - Aguardando aprovacao: borda #FBBF24, fundo rgba(251,191,36,0.1), icone relogio
    - Aprovado: fundo #34D399, icone check branco
    - Rejeitado: fundo #F87171, icone X branco
    - Erro: fundo #F87171, icone ! branco
  - Conteudo direito: Card com padding md
    - Titulo da etapa (Outfit 500 16px)
    - Subtitulo (nome do agente, text-secondary 13px)
    - Badge de status (PipelineStatusBadge)
    - Se aguardando aprovacao: Botao "Revisar [Tipo]" (primary, md)
    - Se em execucao: Spinner + "Agente [Nome] trabalhando..." + tempo estimado
    - Se erro: Alert inline error + Botao "Retomar" (outline)

**Etapas do Wizard:**

| # | Etapa | Agente | Icone sugerido |
|---|-------|--------|----------------|
| 1 | Estrategia | Strategist | Alvo/bullseye |
| 2 | Copywriting | Copywriter | Caneta |
| 3 | Hooks | Hook Specialist | Gancho |
| 4 | Direcao de Arte | Art Director | Paleta |
| 5 | Geracao de Imagens | Image Generator | Imagem |
| 6 | Brand Gate | Brand Gate | Escudo |
| 7 | Avaliacao Final | Content Critic | Estrela |

**Info do Pipeline (header):**

| Secao | Componente | Props |
|-------|-----------|-------|
| Tema | Texto | Outfit 600 20px branco |
| Formato | Badge | variant: primary, size: md |
| Status geral | Badge | variant: success/warning/danger, size: md |
| Modo funil (se ativo) | Badge | variant: warning, size: sm, texto: "Funil: 5 pecas" |
| Botao cancelar | Button | variant: ghost, size: sm |

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Header pipeline | Card | padding: md, shadow: sm |
| Etapa do wizard | Card (PipelineStepCard) | padding: md, hover: true |
| Status da etapa | Badge (PipelineStatusBadge) | variant: varies, size: sm |
| Botao aprovar | Button | variant: primary, size: md |
| Botao retomar | Button | variant: outline, size: md |
| Botao cancelar pipeline | Button | variant: danger, size: sm |
| Spinner de execucao | LoadingSpinner | size: md, color: purple |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Pipeline carregando | Skeleton | 7 blocos skeleton com linha conectora |
| Pipeline nao encontrado | Tela vazia | "Pipeline nao encontrado. Verifique o ID ou crie um novo conteudo." + Botao "Ir para Home" |
| Etapa em execucao | Spinner + texto | "Agente Strategist trabalhando... (~15s)" |
| Etapa aguardando | Badge pulsante + botao | Badge amber pulsando + botao primary "Revisar Briefing" |
| Cancelar pipeline | Modal confirmacao | Modal md: "Cancelar pipeline? O progresso sera mantido no historico, mas o pipeline nao podera ser retomado." Botoes: "Cancelar" (ghost) / "Sim, cancelar" (danger) |
| Etapa com erro | Alert inline | Alert error dentro do card da etapa: "Falha na execucao do Strategist. Tente novamente." |
| Pipeline completo | Visual | Todas as 7 etapas com check verde. Botao "Ver Resultado" (primary, lg) aparece abaixo do wizard. |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Loading | Skeleton: 7 cards retangulares com linha vertical cinza, shimmer |
| Vazio (ID invalido) | Card central com mensagem + botao "Ir para Home" (primary) |
| Em execucao | Etapa ativa com spinner + pulse na borda. Demais etapas estaticas. |
| Aguardando aprovacao | Etapa ativa com borda amber pulsante. Botao de acao proeminente. |
| Erro | Etapa com erro em vermelho. Botao "Retomar". |
| Completo | Todas etapas verdes. Card de resumo aparece + botao "Ver Resultado". |

---

### DESIGN -- TELA: Aprovacao de Briefing (AP-1)

**Rota:** `/pipeline/[id]/briefing`

**Padrao de Layout:** Duas colunas (lg) ou empilhado (sm). Esquerda: contexto (readonly). Direita: briefing editavel.

**Hierarquia Visual:**
1. Breadcrumb: "Pipeline > Briefing (AP-1)" em text-muted
2. Titulo: "Revisar Briefing" (Outfit 600 24px) + Badge "Aguardando Aprovacao" (warning)
3. Conteudo do briefing (textarea editavel, ocupa maior area visual)
4. Botoes de acao (Aprovar / Rejeitar)

**Grupos de Campos:**

| Grupo | Campos | Layout |
|-------|--------|--------|
| Contexto | tema_original, formato_alvo, tendencias_usadas | Coluna esquerda (lg) ou card no topo (sm). Card com padding md, campos readonly em text-secondary. |
| Briefing | briefing_completo | Coluna direita (lg) ou abaixo (sm). Textarea grande (min-h-[300px]) com borda que fica roxa ao focar. |
| Funil (condicional) | pecas_funil[] | Abaixo do briefing. Lista de cards compactos com titulo + etapa (badge) + formato (badge). Editavel. |
| Acoes | aprovar, rejeitar, voltar | Footer fixo na parte inferior. Flex com gap-3. |

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Breadcrumb | Texto | text-muted, links em text-purple |
| Card contexto | Card | padding: md, shadow: sm |
| Briefing editavel | Input (textarea) | placeholder: nenhum (ja vem preenchido), min-h-[300px] |
| Badge etapa funil | Badge | variant: primary (topo) / success (meio) / warning (fundo) |
| Botao aprovar | Button | variant: primary, size: lg, texto: "Aprovar e Continuar" |
| Botao rejeitar | Button | variant: danger, size: md, texto: "Rejeitar e Regerar" |
| Botao voltar | Button | variant: ghost, size: md, texto: "Voltar" |
| Tendencias | Badge (lista) | variant: secondary, size: sm |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Editar briefing | Visual imediato | Borda do textarea muda para roxo. Indicador "Editado" aparece (Badge primary sm). |
| Aprovar | Loading no botao + redirect | Spinner + "Aprovando..." -> redireciona para `/pipeline/[id]` |
| Rejeitar | Modal confirmacao | Modal sm: "Rejeitar briefing? O Strategist sera re-executado com seu feedback." Textarea para feedback opcional. |
| Erro ao aprovar | Toast | Alert error no topo: "Falha ao aprovar o briefing. Tente novamente." |
| Loading | Skeleton | Bloco skeleton grande para o briefing + card skeleton para contexto |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Loading | Skeleton: bloco grande + card lateral |
| Vazio (agente nao executou) | Card central: "Aguardando geracao do briefing..." + Spinner md |
| Erro (agente falhou) | Alert error + Botao "Tentar novamente" (outline) |
| Sucesso (apos aprovar) | Redirect para `/pipeline/[id]` |

---

### DESIGN -- TELA: Aprovacao de Copy + Hook (AP-2)

**Rota:** `/pipeline/[id]/copy`

**Padrao de Layout:** Scroll vertical com secoes claras. Hook Selector no topo, copy editavel abaixo, sequencia de slides na base.

**Hierarquia Visual:**
1. Breadcrumb + Titulo "Revisar Copy e Hook" + Badge AP-2
2. Hook Selector: 3 cards A/B/C lado a lado (elemento de maior destaque visual)
3. Copy editavel: headline, narrativa, CTA
4. Sequencia de slides editavel
5. Alertas do tone_guide (se houver)
6. Botoes de acao

**Grupos de Campos:**

| Grupo | Campos | Layout |
|-------|--------|--------|
| Hooks | hook_a, hook_b, hook_c, hook_selecionado | Grid 3 colunas (lg) / 1 coluna (sm). 3 cards grandes com radio implicito. |
| Copy | headline, narrativa, cta | Stack vertical. Cada campo editavel inline com click-to-edit. |
| Slides | sequencia_slides[] | Lista vertical com drag-and-drop. Cada item e um Card compacto com campos editaveis. |
| Tone Guide | correcoes_tone_guide | Card com lista de correcoes (se houver). Alert type warning. |
| Acoes | aprovar, rejeitar, voltar | Footer fixo. |

**Hook Selector (detalhe):**
- 3 Cards (HookSelector.svelte), cada um com:
  - Letra grande: "A", "B", "C" em JetBrains Mono 32px, cor roxo/amber/verde
  - Texto do hook em Outfit 400 14px branco
  - Card nao selecionado: borda default, fundo #12121A
  - Card selecionado: borda #A78BFA 2px, glow roxo, shadow-purple
  - Hover: borda rgba(167,139,250,0.4)
  - Radio visual: circulo no canto superior direito. Vazio = borda default. Selecionado = preenchido #A78BFA com check

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Hook A | Card | padding: lg, shadow: md, hover: true |
| Hook B | Card | padding: lg, shadow: md, hover: true |
| Hook C | Card | padding: lg, shadow: md, hover: true |
| Campo headline | Input | type: text, placeholder: "Headline do conteudo" |
| Campo narrativa | Input (textarea) | type: text, placeholder: nenhum |
| Campo CTA | Input | type: text, placeholder: "Call to action" |
| Slide da sequencia | Card | padding: sm, shadow: sm, hover: true |
| Alerta tone_guide | Alert | type: warning, dismissible: false |
| Botao aprovar | Button | variant: primary, size: lg, texto: "Aprovar e Continuar" |
| Botao rejeitar | Button | variant: danger, size: md |
| Botao add slide | Button | variant: outline, size: sm, texto: "+ Adicionar slide" |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Selecionar hook | Visual imediato | Card selecionado ganha borda roxa + glow. Radio preenchido. |
| Editar campo copy | Visual imediato | Borda roxa no campo ativo. Badge "Editado" no campo modificado. |
| Reordenar slides | Visual imediato (drag) | Slide arrastado fica semi-transparente. Posicao de destino tem indicador roxo. |
| Nenhum hook selecionado (submit) | Inline | Alert warning acima dos hooks: "Selecione um dos 3 hooks para continuar." |
| Aprovar | Loading + redirect | Spinner + "Aprovando..." -> redirect `/pipeline/[id]` |
| Rejeitar | Modal | Modal sm: "Rejeitar copy? O Copywriter e Hook Specialist serao re-executados." |
| Correcoes tone_guide | Alert persistente | Alert warning: "O Tone Guide corrigiu 3 termos: 'sinergia' -> 'integracao', 'disruptivo' -> 'inovador', 'alavancagem' -> 'crescimento'." |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Loading | Skeleton: 3 cards de hook (retangulos) + linhas de texto abaixo |
| Vazio | Card: "Aguardando geracao da copy..." + Spinner |
| Erro | Alert error + Botao "Tentar novamente" |
| Sucesso | Redirect |

---

### DESIGN -- TELA: Aprovacao de Prompt Visual (AP-3)

**Rota:** `/pipeline/[id]/visual`

**Padrao de Layout:** Conteudo vertical com accordion por slide. Painel lateral (lg) com brand palette e visual memory.

**Hierarquia Visual:**
1. Breadcrumb + Titulo "Revisar Prompts Visuais" + Badge AP-3
2. Accordion de slides (cada item expansivel com prompt editavel)
3. Painel lateral: Brand Palette Preview + Visual Memory
4. Botoes de acao

**Grupos de Campos:**

| Grupo | Campos | Layout |
|-------|--------|--------|
| Prompts | prompts_por_slide[] | Accordion vertical. Cada slide: titulo (readonly) + Badge modelo (pro/flash) + textarea editavel do prompt. |
| Brand Palette | brand_palette | Sidebar card (lg) ou card acima (sm). Preview das 5 cores como circulos + nome da fonte + lista de elementos obrigatorios. |
| Visual Memory | preferencias_visuais[] | Sidebar card (lg) ou abaixo (sm). Lista de estilos aprovados (badge success) e rejeitados (badge danger). |
| Acoes | aprovar, rejeitar, voltar | Footer fixo. |

**Accordion de Slides (detalhe):**
- Cada item do accordion:
  - Header colapsado: "Slide 1: Capa" (Outfit 500 14px) + Badge "Pro" (primary) ou "Flash" (success) + icone seta
  - Header expandido: mesma info + seta invertida
  - Corpo: textarea com prompt da imagem (min-h-[120px])
  - Borda entre itens: rgba(167,139,250,0.1)

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Accordion slide | Card | padding: sm |
| Badge modelo Pro | Badge | variant: primary, size: sm |
| Badge modelo Flash | Badge | variant: success, size: sm |
| Textarea prompt | Input (textarea) | min-h-[120px] |
| Card brand palette | Card | padding: md, shadow: sm |
| Swatch de cor | - (div circular 32px) | - |
| Card visual memory | Card | padding: md, shadow: sm |
| Badge aprovado | Badge | variant: success, size: sm |
| Badge rejeitado | Badge | variant: danger, size: sm |
| Botao aprovar | Button | variant: primary, size: lg, texto: "Aprovar e Gerar Imagens" |
| Botao rejeitar | Button | variant: danger, size: md |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Editar prompt | Visual imediato | Borda roxa + Badge "Editado" no header do accordion |
| Aprovar | Loading + redirect | Spinner + "Enviando para geracao de imagens..." -> redirect |
| Rejeitar | Modal | "Rejeitar prompts? O Art Director sera re-executado com seu feedback." |
| Expandir accordion | Animacao | Slide-down suave (200ms) |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Loading | Skeleton: 7-10 linhas de accordion + card lateral |
| Vazio | "Aguardando geracao dos prompts visuais..." + Spinner |
| Erro | Alert error + Botao "Tentar novamente" |
| Sucesso | Redirect |

---

### DESIGN -- TELA: Aprovacao de Imagem (AP-4)

**Rota:** `/pipeline/[id]/imagem`

**Padrao de Layout:** Scroll vertical. Cada slide e uma secao com grid de 3 variacoes. Layout pesado em imagens.

**Hierarquia Visual:**
1. Breadcrumb + Titulo "Escolher Variacoes de Imagem" + Badge AP-4
2. Secoes por slide (accordion aberto por padrao para o primeiro)
3. Grid de 3 variacoes por slide
4. Brand Gate status por slide
5. Botoes de acao

**Grupos de Campos:**

| Grupo | Campos | Layout |
|-------|--------|--------|
| Slide secao | slide.titulo, slide.brand_gate_status | Accordion (todos abertos por padrao, colapsaveis). Header com titulo + Badge Brand Gate. |
| Variacoes | slide.variacoes[] | Grid 3 colunas (lg) / 2 colunas (md) / 1 coluna (sm). Cada variacao e uma imagem clicavel com radio visual. |
| Acoes | aprovar, rejeitar, regerar, voltar | Footer fixo. |

**Grid de Variacoes (detalhe):**
- Cada variacao e um Card com:
  - Imagem: aspect-ratio 4:5 (carrossel) ou 1:1 (post) ou 16:9 (thumbnail). Object-fit contain. Fundo #0D0D18.
  - Label: "Variacao 1", "Variacao 2", "Variacao 3" em JetBrains Mono 11px muted
  - Nao selecionada: borda default
  - Selecionada: borda #A78BFA 2px, shadow-purple
  - Hover: borda rgba(167,139,250,0.4), cursor pointer
  - Canto superior direito: radio visual (circulo, preenchido quando selecionado)
  - Canto inferior direito: icone lupa (click para zoom modal)
  - Botao "Regerar" (outline sm) abaixo de cada variacao

**Brand Gate Status por Slide:**
- Valido: Badge success "Brand Gate: Aprovado"
- Revisao manual: Badge danger "Brand Gate: Revisao Necessaria" + Alert warning inline "Esta imagem nao passou na validacao automatica da marca. Verifique conformidade visual."
- Retries: Badge secondary "Retries: 1/2"

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Accordion slide | Card | padding: md |
| Card variacao | Card | padding: sm, shadow: md, hover: true |
| Imagem | img | rounded-lg, aspect-ratio dinâmico |
| Radio visual | - (div circular) | - |
| Badge brand gate | Badge | variant: success/danger, size: sm |
| Botao regerar | Button | variant: outline, size: sm, texto: "Regerar" |
| Modal zoom | Modal | size: lg |
| Botao aprovar | Button | variant: primary, size: lg, texto: "Aprovar e Finalizar" |
| Botao rejeitar todas | Button | variant: danger, size: md, texto: "Rejeitar Todas e Regerar" |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Selecionar variacao | Visual imediato | Borda roxa + radio preenchido. Demais perdem selecao naquele slide. |
| Ampliar imagem | Modal | Modal lg com imagem fullscreen sobre fundo escuro. Botao fechar no canto. |
| Regerar variacao individual | Loading no card | Spinner sobreposto na imagem + texto "Regerando..." |
| Nao selecionou todas (submit) | Alert | Alert warning: "Selecione uma variacao para cada slide antes de aprovar." |
| Aprovar | Loading + redirect | Spinner + "Finalizando selecao..." -> redirect |
| Rejeitar todas | Modal | Modal md: "Rejeitar todas as imagens? O Image Generator sera re-executado para todos os slides." |
| Brand Gate revisao manual | Alert inline | Alert warning dentro do accordion do slide |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Loading | Skeleton: blocos retangulares em grid 3 colunas com shimmer |
| Vazio | "Aguardando geracao de imagens..." + Spinner lg centralizado |
| Erro (Brand Gate falhou) | Badge danger no slide afetado. Imagem disponivel mas com alerta. |
| Sucesso | Redirect |

---

### DESIGN -- TELA: Preview e Export

**Rota:** `/pipeline/[id]/export`

**Padrao de Layout:** Duas colunas (lg). Esquerda: preview dos slides (carrossel navegavel). Direita: scores + acoes de export.

**Hierarquia Visual:**
1. Titulo do conteudo (Outfit 600 24px) + Badge formato + Badge score
2. Preview dos slides (maior area visual, esquerda)
3. Score do Content Critic (radar chart + cards, direita)
4. Legenda LinkedIn (copiavel)
5. Acoes de export (PDF, PNG, Drive)

**Grupos de Campos:**

| Grupo | Campos | Layout |
|-------|--------|--------|
| Preview | slides_finais[] | Coluna esquerda (lg) ou topo (sm). Carrossel com setas + dots de navegacao. Imagem com aspect-ratio nativo do formato. |
| Score | score.* (6 dimensoes + final + decision) | Coluna direita superior (lg). Radar chart (ScoreRadar) + grid 2x3 de ScoreCards. |
| Legenda | legenda_linkedin | Card com texto copiavel. Botao "Copiar" (outline sm) no canto. |
| Export | acoes | Coluna direita inferior (lg). 3 botoes empilhados. |

**Score (detalhe):**
- Radar chart: 6 eixos (clarity, impact, originality, scroll_stop, cta_strength, final_score). Cor do preenchimento: #A78BFA 20% opacity. Cor da linha: #A78BFA. Labels em JetBrains Mono 10px.
- Score cards: Grid 2 colunas x 3 linhas
  - Cada card: numero grande (JetBrains Mono 28px, cor por range) + label (10px muted uppercase)
  - Range: >= 8 verde, 6-7.9 amber, < 6 vermelho
- Final score: Card maior com decisao
  - Approved: Badge success "Aprovado" + score em verde
  - Needs revision: Badge warning "Recomenda Ajustes" + score em amber + texto de sugestao

**Preview de Slides (detalhe):**
- Container: fundo #0D0D18, rounded-xl, padding 0
- Imagem centralizada com object-fit contain
- Navegacao: setas esquerda/direita (botoes ghost circular 40px) + dots abaixo (8px, ativo #A78BFA, inativo #5A5A66)
- Counter: "03 / 10" em JetBrains Mono 11px muted, canto inferior direito

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Preview carousel | Card | padding: nenhum (imagem full bleed) |
| Setas navegacao | Button | variant: ghost, size: sm (circular) |
| Score radar | ScoreRadar | custom component |
| Score card | Card (ScoreCard) | padding: sm |
| Score numero | Texto | JetBrains Mono 28px |
| Badge aprovado | Badge | variant: success, size: md |
| Badge ajustes | Badge | variant: warning, size: md |
| Legenda | Card | padding: md |
| Botao copiar | Button | variant: outline, size: sm |
| Botao PDF | Button | variant: primary, size: md, texto: "Exportar PDF" |
| Botao PNG | Button | variant: outline, size: md, texto: "Download PNGs" |
| Botao Drive | Button | variant: secondary, size: md, texto: "Salvar no Drive" |
| Botao novo | Button | variant: ghost, size: md, texto: "Novo Conteudo" |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Navegar slides | Visual imediato | Slide transiciona com fade 200ms. Dot ativo muda. Counter atualiza. |
| Copiar legenda | Toast | Alert success (toast canto superior): "Legenda copiada!" (auto-dismiss 3s) |
| Exportar PDF | Loading no botao | Spinner + "Gerando PDF..." -> download automatico |
| Download PNGs | Loading no botao | Spinner + "Preparando imagens..." -> download zip ou individual |
| Salvar no Drive | Loading no botao | Spinner + "Salvando no Drive..." -> Alert success: "Salvo no Drive!" com link "Abrir pasta" |
| Erro de export | Toast | Alert error: "Falha ao exportar. Tente novamente." |
| Score < 7 | Banner persistente | Alert warning (nao dismissible): "O Content Critic recomenda ajustes. Score: 6.2/10." + detalhes das dimensoes fracas. |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Loading (Content Critic) | Skeleton: radar chart circular + 6 cards retangulares + imagem grande |
| Vazio | "Avaliando qualidade do conteudo..." + Spinner lg |
| Erro (Critic falhou) | Preview dos slides disponivel normalmente. Onde ficaria o score: Alert info "Score indisponivel. Voce pode exportar normalmente." |
| Drive salvo | Banner success persistente com link para a pasta no Drive |

---

### DESIGN -- TELA: Editor de Conteudo (legado)

**Rota:** `/carrossel`

**Padrao de Layout:** Manter layout existente. Nenhuma alteracao de design na v3, apenas migrar os tokens de cor para dark mode.

**Migracao de Cores:**
- Fundo: bg-page (#E6EEEC) -> bg-global (#0A0A0F)
- Cards: bg-card (#FAFCFB) -> bg-card (#12121A)
- Texto: steel-6 (#0D2033) -> text-primary (#FFFFFF)
- Bordas: teal-4/30 -> border-default rgba(167,139,250,0.2)
- Botoes: gradiente steel -> variantes do novo design system

**Badge no menu:** Badge warning "Legado" ao lado do item "Carrossel" na sidebar.

**Demais estados e feedback:** Manter comportamento existente, adaptado ao dark mode.

---

### DESIGN -- TELA: Historico

**Rota:** `/historico`

**Padrao de Layout:** Barra de filtros no topo. Grid de cards abaixo (3 colunas lg, 2 md, 1 sm).

**Hierarquia Visual:**
1. Titulo "Historico" (Outfit 300 28px) + contador de resultados (text-muted)
2. Barra de filtros (horizontal, wrap em mobile)
3. Grid de cards de conteudo

**Grupos de Campos:**

| Grupo | Campos | Layout |
|-------|--------|--------|
| Filtros | filtro_texto, filtro_formato, filtro_status, filtro_data_inicio, filtro_data_fim | Flex horizontal com wrap. Inputs e selects inline. |
| Grid de resultados | itens_historico[] | Grid 3 colunas (lg) / 2 (md) / 1 (sm). |

**Card de Historico (HistoricoCard, detalhe):**
- Fundo: #12121A. Borda default. Rounded-xl. Padding md.
- Topo: Badge formato (primary) + Badge status (success/warning/danger/secondary)
- Titulo: Outfit 500 16px branco, max 2 linhas com truncate
- Meta: disciplina + tecnologia em text-secondary 12px
- Score: se existir, numero grande (JetBrains Mono 20px, cor por range) no canto
- Data: text-muted 11px JetBrains Mono
- Rodape do card: flex com icones: "Drive" (link externo), "Reabrir" (link para pipeline), "Remover" (danger, com modal)
- Hover: translate-y -2px + shadow-md + border-purple

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Input filtro texto | Input | type: text, placeholder: "Buscar por titulo..." |
| Select formato | Input (select) | opcoes: Todos, Carrossel, Post Unico, Thumbnail |
| Select status | Input (select) | opcoes: Todos, Completo, Em andamento, Erro, Cancelado |
| Input data | Input | type: date |
| Card conteudo | Card (HistoricoCard) | padding: md, shadow: sm, hover: true |
| Badge formato | Badge | variant: primary, size: sm |
| Badge status | Badge | variant: varies, size: sm |
| Botao Drive | Button | variant: ghost, size: sm |
| Botao reabrir | Button | variant: outline, size: sm |
| Botao remover | Button | variant: danger, size: sm |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Filtrar | Visual imediato | Grid re-renderiza com animacao fade. Contador atualiza. |
| Filtro sem resultado | Estado vazio | Card central: "Nenhum resultado para os filtros selecionados." |
| Remover item | Modal | Modal sm: "Remover este conteudo do historico? A acao nao pode ser desfeita." |
| Item removido | Toast | Alert success: "Conteudo removido do historico." |
| Abrir no Drive | Nova aba | Link externo, sem feedback na tela |
| Loading | Spinner | Spinner md centralizado |
| Erro backend | Banner | Alert error: "Nao foi possivel carregar o historico." |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Loading | Spinner centralizado |
| Vazio (sem conteudo) | Card central: "Nenhum conteudo salvo ainda." + texto "Salve conteudos no Google Drive para ve-los aqui." + Botao "Criar Conteudo" (primary) |
| Vazio (filtro sem resultado) | Card: "Nenhum resultado encontrado." + Botao "Limpar filtros" (ghost) |
| Erro | Banner error topo |

---

### DESIGN -- TELA: Agentes

**Rota:** `/agentes`

**Padrao de Layout:** Master-detail. Lista esquerda (1/3 width) + painel detalhes direita (2/3 width). Empilhado em mobile.

**Hierarquia Visual:**
1. Titulo "Agentes e Skills" (Outfit 300 28px)
2. Tabs "Agentes LLM (6)" / "Skills (6)" no topo da lista
3. Lista de cards de agente (esquerda)
4. Painel de detalhes do agente selecionado (direita)
5. Pipeline visual na base (diagrama horizontal do fluxo)

**Grupos de Campos:**

| Grupo | Campos | Layout |
|-------|--------|--------|
| Lista | agentes_llm[] ou skills_deterministicas[] | Coluna esquerda 1/3. Cards compactos com nome + tipo + badge status. |
| Detalhes | agente.nome, agente.descricao, agente.conteudo | Coluna direita 2/3. Card grande com system prompt em bloco de codigo (JetBrains Mono). |
| Pipeline Visual | pipeline_visual | Full width abaixo das colunas. Diagrama horizontal com 7 etapas conectadas por linhas. |

**Card de Agente na Lista (detalhe):**
- Compacto: padding sm. Nome em Outfit 500 14px. Descricao em text-secondary 12px truncada 1 linha.
- Badge: "LLM" (primary) ou "Skill" (success) no canto
- Selecionado: borda esquerda 3px #A78BFA + bg rgba(167,139,250,0.04)
- Hover: bg rgba(255,255,255,0.02)

**Painel de Detalhes:**
- Card com padding lg
- Titulo do agente: Outfit 600 20px + Badge tipo
- Descricao: text-secondary 14px
- System prompt: bloco de codigo estilo janela macOS (titlebar com bolinhas + fundo #0D0D18 + fonte JetBrains Mono 12px verde)

**Pipeline Visual (diagrama):**
- Horizontal: 7 circulos (48px) conectados por linhas (2px)
- Cada circulo: icone do agente + nome abaixo em text-muted 10px
- Pontos AP marcados com badge amber entre os circulos relevantes
- Scroll horizontal em mobile

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Tabs | Tabs | 2 tabs |
| Card agente (lista) | Card (AgenteCard) | padding: sm, hover: true |
| Badge tipo | Badge | variant: primary (LLM) / success (Skill), size: sm |
| Painel detalhes | Card (AgenteDetalhe) | padding: lg, shadow: md |
| Bloco codigo | Code window | estilo macOS (titlebar + body) |
| Pipeline visual | PipelineVisual | custom component |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Selecionar agente | Visual imediato | Card na lista ganha borda esquerda roxa. Painel direito atualiza com fade 200ms. |
| Alternar tab | Visual imediato | Lista filtra com fade. Primeiro item da nova tab auto-selecionado. |
| Loading | Skeleton | Lista: 6 cards skeleton. Painel: bloco skeleton grande. |
| Erro | Banner | Alert error: "Nao foi possivel carregar os agentes." |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Loading | Skeleton na lista + painel |
| Vazio | "Nenhum agente encontrado." (improvavel) |
| Erro | Banner error |
| Sucesso | Lista populada, primeiro agente selecionado por padrao |

---

### DESIGN -- TELA: Configuracoes

**Rota:** `/configuracoes`

**Padrao de Layout:** Scroll vertical com secoes em accordion ou tabs verticais. Cada secao e independente com seu proprio botao "Salvar".

**Decisao DT-006:** Usar tabs verticais (sidebar interna) em desktop e accordion em mobile. Secoes: API Keys, Google Drive, Brand Palette, Creator Registry, Platform Rules, Design Systems, Fotos, Backend.

**Hierarquia Visual:**
1. Titulo "Configuracoes" (Outfit 300 28px)
2. Tabs verticais esquerda (200px) com secoes
3. Conteudo da secao ativa direita

**Secao: API Keys**

| Campo | Componente | Props |
|-------|-----------|-------|
| Claude API Key | Input | type: password, placeholder: "sk-ant-..." |
| Gemini API Key | Input | type: password, placeholder: "AI..." |
| Google Drive Credentials | Input (textarea) | placeholder: "Cole o JSON da service account..." |
| Drive Folder ID | Input | type: text |
| Status da chave | Badge | variant: success (configurada) / danger (nao configurada), size: sm |
| Botao salvar | Button | variant: primary, size: md, texto: "Salvar Chaves" |

**Secao: Brand Palette**

| Campo | Componente | Props |
|-------|-----------|-------|
| Cores (5 campos) | Input | type: color (nativo) + text hex ao lado |
| Fonte | Input | type: text, placeholder: "Outfit" |
| Elementos obrigatorios | Badge (chips) | variant: primary, size: sm, editaveis |
| Estilo | Input | type: text |
| Preview | Card | preview ao vivo com as cores selecionadas |
| Botao salvar | Button | variant: primary, size: md |

**Secao: Creator Registry**

| Campo | Componente | Props |
|-------|-----------|-------|
| Lista de criadores | Cards empilhados | Cada card: nome (input), funcao (select), plataforma (select), url (input), ativo (toggle) |
| Botao adicionar | Button | variant: outline, size: sm, texto: "+ Adicionar Criador" |
| Botao remover | Button | variant: danger, size: sm (icone X no card) |
| Botao salvar | Button | variant: primary, size: md |

**Secao: Platform Rules**

| Campo | Componente | Props |
|-------|-----------|-------|
| Card por plataforma | Card | padding: md. Nome da plataforma (Outfit 500) + campos editaveis |
| Max caracteres | Input | type: number |
| Max hashtags | Input | type: number |
| Specs | Texto readonly | text-secondary |
| Botao salvar | Button | variant: primary, size: md |

**Secao: Design Systems**

| Campo | Componente | Props |
|-------|-----------|-------|
| Lista de DS | Cards | Nome + botoes "Ver" (outline) + "Remover" (danger) |
| Upload | Input | type: file, accept: ".md,.html" |
| Preview | Modal | size: lg, conteudo renderizado do DS |

**Secao: Fotos**

| Campo | Componente | Props |
|-------|-----------|-------|
| Galeria | Grid de thumbnails circulares | 64px, borda default. Ativa: borda #A78BFA |
| Upload | Input | type: file, accept: "image/*", multiple |
| Remover | Botao X | variant: danger, size: sm, overlay na foto |

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Tab vertical | Tabs (vertical) | custom layout |
| Secao card | Card | padding: lg |
| Cada input | Input | varies |
| Toggle ativo | Toggle | - |
| Botao salvar (cada secao) | Button | variant: primary, size: md |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem Sugerida |
|------|-----------------|-------------------|
| Salvar qualquer secao | Toast | Alert success: "Configuracoes salvas com sucesso!" (auto-dismiss 4s) |
| Erro ao salvar | Toast | Alert error: "Falha ao salvar. Verifique a conexao." |
| Chave configurada | Badge | Badge success "Configurada" ao lado do campo |
| Chave nao configurada | Badge | Badge danger "Nao configurada" ao lado do campo |
| Upload DS | Loading + toast | Spinner no botao + "Design system enviado!" |
| Deletar DS | Modal | Modal sm: "Remover este design system?" |
| Adicionar criador | Visual imediato | Novo card vazio aparece na lista com animacao fade-up |
| Remover criador | Modal | Modal sm: "Remover criador [nome]?" |
| Preview brand palette | Visual em tempo real | Card de preview atualiza cores em tempo real conforme usuario edita |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Loading | Spinner no topo enquanto carrega status das chaves |
| Vazio (chaves) | Todos os badges "Nao configurada" em vermelho |
| Erro | Banner error topo |
| Sucesso | Toast success |

---

## Padroes Globais de Feedback

### Toast (notificacoes temporarias)

- Posicao: canto superior direito, abaixo do topo 24px
- Max-width: 400px
- Auto-dismiss: success 3s, error 5s, warning 4s
- Animacao: slide-in da direita + fade
- Stack: maximo 3 toasts simultaneos, o mais antigo sai

### Modal de Confirmacao (acoes destrutivas)

Toda acao destrutiva (remover, rejeitar, cancelar pipeline) requer modal de confirmacao:
- Titulo claro da acao
- Descricao do impacto
- Botao de cancelar (ghost) + botao de confirmar (danger)
- ESC ou click fora fecha o modal

### Erros de Validacao

- Inline: mensagem vermelha (#F87171) 12px abaixo do campo. Borda do campo muda para rgba(248,113,113,0.5).
- Campo invalido ganha borda vermelha ao perder foco (blur) se validacao falhar.

### Loading Global

- Skeleton para carregamentos de pagina (dados estruturais)
- Spinner para acoes pontuais (botao, card individual)
- Shimmer animation nos skeletons (gradiente roxo 6% opacity)

---

## Espacamento e Grid

| Token | Valor | Uso |
|-------|-------|-----|
| gap-secoes | 32px (gap-8) | Entre secoes de uma tela |
| gap-campos | 16px (gap-4) | Entre campos de um formulario |
| gap-cards | 16px (gap-4) | Entre cards de um grid |
| gap-botoes | 12px (gap-3) | Entre botoes de acao |
| padding-pagina | 32px horizontal, 24px vertical | Padding do conteudo principal |
| padding-card | 20px (p-5) padrao | Padding interno dos cards |

---

## Animacoes

| Animacao | Uso | Duracao |
|---------|-----|---------|
| fade-up | Entrada de elementos na tela | 650ms ease-out |
| shimmer | Skeleton loading | 2s infinite |
| spin | Spinner de loading | 1s linear infinite |
| pulse | Indicador de etapa aguardando aprovacao | 2s ease-in-out infinite |
| slide-down | Abertura de accordion | 200ms ease |
| fade | Transicao entre slides do preview | 200ms ease |
| scale-in | Abertura de modal | 200ms ease |

---

## Acessibilidade

- Todos os botoes interativos tem `cursor-pointer`
- Focus visivel: ring 3px roxo em todos os elementos interativos
- Contraste: texto branco sobre fundo #0A0A0F = ratio 19.3:1 (AAA)
- Contraste: texto #9896A3 sobre fundo #0A0A0F = ratio 5.1:1 (AA)
- Aria-labels em botoes de icone (setas de navegacao, fechar modal, hamburger)
- Disabled: opacity 50% + cursor not-allowed + aria-disabled

---

*Documento gerado pelo Agente 05 (Arquiteto Designer) da esteira IT Valley.*
*Proximo: Agente 06 (Dev Mockado).*
