# DESIGN -- Telas do Funil de Conteudo

Guia visual completo para as 3 telas novas do Modo Funil.
Segue o Design System IT Valley dark mode premium ja implementado no projeto.

> Produzido pelo Agente 05 (Arquiteto Designer).
> Entrada: PRD-funil.md + Analista de Tela.
> Saida: Guia para Dev Mockado (Agente 06).

---

## Tokens de Referencia (ja existem em app.css)

| Token | Valor | Uso |
|-------|-------|-----|
| `bg-global` | `#0A0A0F` | Fundo da pagina |
| `bg-card` | `#12121A` | Fundo dos cards |
| `bg-elevated` | `#1A1A2A` | Fundo de sub-elementos dentro de cards |
| `border-default` | `rgba(167,139,250,0.2)` | Borda padrao |
| `border-active` | `#A78BFA` | Borda com foco/ativo |
| `text-primary` | `#FFFFFF` | Texto principal |
| `text-secondary` | `#9896A3` | Texto auxiliar |
| `text-muted` | `#5A5A66` | Labels, meta |
| `purple` | `#A78BFA` | Cor principal, CTAs |
| `green` | `#34D399` | Sucesso, meio do funil |
| `amber` | `#FBBF24` | Atencao, fundo do funil |
| `red` | `#F87171` | Erro, conversao |

## Paleta de Etapas do Funil

| Etapa | Cor | Badge variant | Tailwind bg | Tailwind text | Tailwind border |
|-------|-----|---------------|-------------|---------------|-----------------|
| Topo | purple | `primary` | `bg-purple/8` | `text-purple` | `border-purple/20` |
| Meio | green | `success` | `bg-green/10` | `text-green` | `border-green/25` |
| Fundo | amber | `warning` | `bg-amber/10` | `text-amber` | `border-amber/25` |
| Conversao | red | `danger` | `bg-red/9` | `text-red` | `border-red/15` |

## Componentes UI Disponiveis (ja implementados)

| Componente | Arquivo | Props |
|------------|---------|-------|
| Button | `ui/Button.svelte` | variant: primary/secondary/outline/ghost/danger, size: sm/md/lg, loading |
| Card | `ui/Card.svelte` | hover, glow, padding: sm/md/lg |
| Badge | `ui/Badge.svelte` | variant: primary/secondary/success/danger/warning, size: sm/md |
| Banner | `ui/Banner.svelte` | type: success/error/warning/info, dismissible |
| Modal | `ui/Modal.svelte` | open, title, size: sm/md/lg, onclose, footer snippet |
| Spinner | `ui/Spinner.svelte` | size: sm/md/lg |
| Skeleton | `ui/Skeleton.svelte` | variant: block/circle, height |
| ApprovalBar | `pipeline/ApprovalBar.svelte` | pipelineId, aprovando, rejeitando, onaprovar, onrejeitar |

---

## TELA 1: Plano do Funil (`/funil-plano`)

### Padrao de Layout

```
+------------------------------------------------------------------+
| Header: titulo + Badge "AP" + contagem de pecas                  |
+------------------------------------------------------------------+
|                                                                  |
|  Timeline vertical (linha pontilhada)                            |
|  |                                                               |
|  o--- [Card Peca 1: Topo]        [Card Peca 2: Topo]            |
|  |                                                               |
|  o--- [Card Peca 3: Meio]        [Card Peca 4: Fundo]           |
|  |                                                               |
|  o--- [Card Peca 5: Conversao]                                   |
|  |                                                               |
+------------------------------------------------------------------+
| ApprovalBar (sticky bottom)                                      |
+------------------------------------------------------------------+
```

- Container: `max-w-[1000px] mx-auto`
- Layout dos cards: `grid grid-cols-1 md:grid-cols-2 gap-4`
- Timeline: posicionada a esquerda dos cards em mobile (1 coluna), entre as colunas em desktop

### Hierarquia Visual

1. Cards das pecas com badges coloridos por etapa (foco principal, 70% da tela)
2. Header com titulo do funil e badge de status (ancora de contexto)
3. ApprovalBar sticky no rodape (call-to-action persistente)
4. Timeline visual conectando os cards (elemento decorativo de coesao)

### Header

```
Componentes:
- h1: "Plano do Funil" | text-xl font-semibold text-text-primary
- Badge variant="warning" size="md": "Aguardando Aprovacao"
- Subtitulo: tema do funil | text-sm text-text-secondary
- Contagem: "5 pecas planejadas" | text-xs text-text-muted font-mono

Container:
- Card padding="md"
- mb-8
```

### Card de Peca

Cada card representa uma peca do funil. O card e interativo (campos editaveis).

```
+----------------------------------------------------------+
|  [Badge Etapa: "TOPO"]  [Badge Formato: "CARROSSEL 7"]   |
|                                                          |
|  Titulo (editavel)                                       |
|  input text-sm, bg-transparent, border-bottom on focus   |
|                                                          |
|  Angulo (editavel)                                       |
|  textarea text-xs text-text-secondary, 2 linhas          |
|                                                          |
|  ---                                                     |
|  Acoes: [Trocar Etapa v] [Trocar Formato v] [x Remover] |
+----------------------------------------------------------+
```

**Componentes por Secao:**

| Secao | Componente | Props/Classes |
|-------|-----------|---------------|
| Card wrapper | Card | `padding="md"` + borda esquerda colorida por etapa |
| Borda esquerda | CSS | `border-l-4 border-l-{cor-etapa}` (purple/green/amber/red) |
| Badge etapa | Badge | variant por etapa (ver paleta), size="sm" |
| Badge formato | Badge | variant="secondary", size="sm" |
| Titulo editavel | Input (inline) | `bg-transparent border-0 border-b border-transparent focus:border-purple/40 text-sm font-medium text-text-primary w-full py-1` |
| Angulo editavel | Textarea (inline) | `bg-transparent border-0 border-b border-transparent focus:border-purple/40 text-xs text-text-secondary w-full py-1 resize-none` rows=2 |
| Separador | hr | `border-border-default mt-3 mb-2` |
| Trocar etapa | Select/Dropdown | `bg-bg-elevated border border-border-default rounded-lg px-2 py-1 text-xs text-text-secondary` |
| Trocar formato | Select/Dropdown | mesmo estilo |
| Remover | Button | variant="ghost", size="sm", icone X, `text-text-muted hover:text-red` |

**Borda esquerda por etapa (diferencial visual):**
- Topo: `border-l-purple`
- Meio: `border-l-green`
- Fundo: `border-l-amber`
- Conversao: `border-l-red`

### Timeline Visual

A timeline conecta visualmente os cards para dar sensacao de fluxo/sequencia.

```
Mobile (1 coluna):
- Linha pontilhada vertical a esquerda: absolute left-3 top-0 bottom-0
- border-l-2 border-dashed border-purple/20
- Cada card tem um circulo indicador (w-6 h-6 rounded-full) na cor da etapa
- Circulo posicionado: absolute -left-6 top-5

Desktop (2 colunas):
- Timeline desaparece (os cards no grid ja comunicam a sequencia)
- Badges de etapa sao suficientes para distinguir
```

### ApprovalBar

Reutilizar `ApprovalBar.svelte` existente com:
- `aprovarLabel="Aprovar Plano e Executar"`
- `aprovandoLabel="Criando sub-pipelines..."`
- Posicao: `sticky bottom-4`
- Background blur para nao cobrir conteudo: `bg-bg-global/80 backdrop-blur-sm rounded-xl p-3`

### Feedback de Acoes

| Acao | Tipo | Mensagem |
|------|------|----------|
| Aprovar plano | Redirect | Redireciona para `/funil` (acompanhamento) |
| Rejeitar plano | Modal + Textarea | "Rejeitar plano? O Funnel Architect sera re-executado com seu feedback." |
| Editar titulo/angulo | Inline (auto-save visual) | Badge "Editado" aparece no header (como no briefing) |
| Remover peca | Modal confirmacao | "Remover esta peca do plano? Voce pode regenerar o plano completo depois." |
| Trocar etapa | Inline | Badge muda de cor instantaneamente, sem confirmacao |
| Trocar formato | Inline | Badge atualiza instantaneamente |

### Estados Visuais

| Estado | Visual | Detalhes |
|--------|--------|----------|
| Loading | Skeleton | 1 Skeleton bloco (header) + 4 Skeleton blocos (cards) em grid 2 colunas |
| Vazio | Mensagem central | "Nenhuma peca no plano." + CTA "Regenerar Plano" (Button variant="outline") |
| Erro ao carregar | Banner type="error" | "Erro ao carregar plano do funil." acima do grid |
| Erro ao aprovar | Banner type="error" | "Erro ao aprovar plano. Tente novamente." |
| Editado | Badge variant="primary" | Badge "Editado" no header (igual ao briefing existente) |

### Responsividade

| Breakpoint | Layout | Detalhes |
|------------|--------|----------|
| Mobile (< 768px) | 1 coluna + timeline esquerda | Cards empilhados, timeline pontilhada conectando |
| Tablet (768-1024px) | 2 colunas, sem timeline | Grid 2 colunas |
| Desktop (> 1024px) | 2 colunas, sem timeline | max-w-[1000px] centralizado |

### Dados Mock Realistas

```
Peca 1 (Topo):
  etapa: "topo"
  formato: "carrossel_7"
  titulo: "5 Erros que Todo Iniciante Comete com Python"
  angulo: "Abordagem didatica mostrando erros comuns com solucoes praticas"

Peca 2 (Topo):
  etapa: "topo"
  formato: "post_unico"
  titulo: "Python e a Linguagem #1 do Mercado em 2026"
  angulo: "Dados de mercado e tendencias que geram curiosidade"

Peca 3 (Meio):
  etapa: "meio"
  formato: "carrossel_10"
  titulo: "Como Construi Meu Primeiro Modelo de ML em 7 Dias"
  angulo: "Case pessoal do Carlos com passo-a-passo replicavel"

Peca 4 (Fundo):
  etapa: "fundo"
  formato: "thumbnail_youtube"
  titulo: "Aula Gratuita: Pipeline de Dados com Python"
  angulo: "Chamar para aula gratuita como porta de entrada"

Peca 5 (Conversao):
  etapa: "conversao"
  formato: "capa_reels"
  titulo: "Matriculas Abertas: Formacao Completa em IA"
  angulo: "Urgencia + prova social com depoimentos de alunos"
```

---

## TELA 2: Acompanhamento do Funil (`/funil`)

### Padrao de Layout

```
+------------------------------------------------------------------+
| Header: titulo + barra de progresso geral                        |
+------------------------------------------------------------------+
|                                                                  |
|  [Card Peca 1]   [Card Peca 2]                                  |
|  status: pronto  status: executando                              |
|  [mini-wizard]   [mini-wizard + spinner]                         |
|                                                                  |
|  [Card Peca 3]   [Card Peca 4]                                  |
|  status: aguard. status: pendente                                |
|  [mini-wizard]   [mini-wizard]                                   |
|                                                                  |
|  [Card Peca 5]                                                   |
|  status: erro                                                    |
|  [mini-wizard]                                                   |
|                                                                  |
+------------------------------------------------------------------+
| Rodape: link "Ver Exportacao" (quando todas prontas)             |
+------------------------------------------------------------------+
```

- Container: `max-w-[1000px] mx-auto`
- Layout dos cards: `grid grid-cols-1 md:grid-cols-2 gap-4`

### Hierarquia Visual

1. Barra de progresso geral no header (quanto falta? - resposta imediata)
2. Cards das pecas com borda colorida por status (o que precisa de atencao?)
3. Mini-wizard horizontal em cada card (em que etapa esta cada peca?)
4. Botoes de acao nos cards que precisam de intervencao (o que eu faco agora?)

### Header com Progresso

```
+------------------------------------------------------------------+
| Funil: "5 Erros que Todo Iniciante Comete..."    [3 de 5 prontas]|
|                                                                  |
| [=============================                    ] 60%          |
| "Peca 3 executando: Gerando imagens... (~2min)"                  |
+------------------------------------------------------------------+
```

**Componentes:**

| Secao | Componente | Props/Classes |
|-------|-----------|---------------|
| Container | Card | `padding="md"` |
| Titulo | h1 | `text-lg font-semibold text-text-primary line-clamp-1` |
| Contagem | span | `text-sm font-mono text-text-muted` — "3 de 5 prontas" |
| Barra progresso | div | Container: `w-full h-2 rounded-full bg-bg-elevated overflow-hidden` |
| Barra preenchida | div | `h-full rounded-full bg-purple transition-all duration-500` + width dinamico |
| Label progresso | p | `text-xs text-text-secondary mt-2` — descreve o que esta acontecendo |

### Card de Peca (com Mini-Wizard)

Cada card mostra o status da peca e seu progresso pelas 6 etapas do pipeline.

```
+----------------------------------------------------------+
|  [Badge Etapa]  [Badge Formato]           [Status label]  |
|                                                          |
|  "5 Erros que Todo Iniciante Comete com Python"          |
|                                                          |
|  Mini-wizard (6 circulos):                               |
|  (v) (v) (v) (*) ( ) ( )                                |
|  STR  CPY  ART  IMG  BRD  CRT                           |
|                                                          |
|  [Botao de acao contextual]                              |
+----------------------------------------------------------+
```

**Mini-wizard (6 circulos horizontais):**

Os 6 circulos representam as 6 etapas do sub-pipeline (strategist, copywriter, art_director, image_generator, brand_gate, content_critic).

```
Classes do container:
  flex items-center gap-1 mt-3

Cada circulo:
  w-5 h-5 rounded-full flex items-center justify-center text-[8px] font-mono

Linha conectora entre circulos:
  flex-1 h-0.5 bg-bg-elevated (entre cada circulo, usando flex gap)

Estados do circulo:
  Completo:  bg-green text-white         — checkmark (svg w-3 h-3)
  Executando: bg-purple/20 border border-purple animate-pulse — Spinner size="sm"
  Aguardando: bg-amber/10 border border-amber — icone relogio
  Erro:       bg-red/10 border border-red text-red — icone X
  Pendente:   bg-bg-elevated text-text-muted — numero da etapa

Labels abaixo dos circulos:
  text-[8px] text-text-muted font-mono uppercase mt-1
  "STR" "CPY" "ART" "IMG" "BRD" "CRT"
```

**Variantes de card por status da peca:**

| Status | Borda | Icone/Efeito | Botao |
|--------|-------|--------------|-------|
| Executando | `border-2 border-purple animate-pulse` | Spinner size="sm" ao lado do titulo | Nenhum (aguardar) |
| Aguardando aprovacao | `border-2 border-amber animate-pulse-border` | Icone relogio | Button variant="primary" size="sm": "Revisar" |
| Pronto (completo/aprovado) | `border border-green/40` | Checkmark verde ao lado do titulo | Button variant="outline" size="sm": "Ver Resultado" |
| Erro | `border-2 border-red/40` | Icone X vermelho | Button variant="outline" size="sm": "Retomar" + mensagem de erro |
| Pendente | `border border-border-default` (padrao) | Nenhum | Nenhum |

**Componentes por Secao:**

| Secao | Componente | Props/Classes |
|-------|-----------|---------------|
| Card wrapper | Card | `padding="md"` + classes de borda por status |
| Badge etapa | Badge | variant por etapa (paleta), size="sm" |
| Badge formato | Badge | variant="secondary", size="sm" |
| Status label | span | `text-xs font-mono px-2 py-0.5 rounded-full` + cores por status |
| Titulo | p | `text-sm font-medium text-text-primary mt-2 line-clamp-2` |
| Mini-wizard | Custom | 6 circulos + linhas conectoras (ver acima) |
| Botao revisar | Button | variant="primary", size="sm" |
| Botao ver resultado | Button | variant="outline", size="sm" |
| Botao retomar | Button | variant="outline", size="sm", classe extra `text-red` |

### Botao Final (todas prontas)

Quando todas as 5 pecas estiverem com status "completo" ou "aprovado":

```
<div class="mt-8 text-center">
  <a href="/funil-export" class="...btn-primary-lg...">
    Exportar Funil Completo
  </a>
</div>
```

- Button variant="primary" size="lg"
- Glow effect: `hover:shadow-[0_0_30px_rgba(167,139,250,0.3)]`
- Mesma linguagem visual do "Ver Imagens" da pagina de pipeline

### Feedback de Acoes

| Acao | Tipo | Mensagem |
|------|------|----------|
| Clicar "Revisar" | Redirect | Vai para `/pipeline/{pecaId}/{etapaAtual}` (copy, visual, briefing) |
| Clicar "Ver Resultado" | Redirect | Vai para `/editor?pipeline={pecaId}&brand={brandSlug}` |
| Clicar "Retomar" | Inline + Polling | Spinner no botao, polling recarrega status |
| Peca muda de status | Transicao suave | Card faz transition de borda/cor (transition-all duration-500) |
| Todas prontas | CTA aparece | Botao "Exportar Funil Completo" aparece com animate-fade-up |

### Estados Visuais

| Estado | Visual | Detalhes |
|--------|--------|----------|
| Loading | Skeleton | 1 Skeleton bloco (header) + 4 Skeleton blocos (cards) em grid |
| Funil nao encontrado | Mensagem central | "Funil nao encontrado." + CTA "Voltar para Home" |
| Todas pendentes | Cards com borda default | Primeiro card muda para "executando" automaticamente |
| Todas prontas | Cards com borda green | Botao "Exportar" aparece no rodape |
| Polling ativo | Indicador sutil | Ponto verde piscante no header: `w-2 h-2 rounded-full bg-green animate-pulse` |

### Responsividade

| Breakpoint | Layout | Detalhes |
|------------|--------|----------|
| Mobile (< 768px) | 1 coluna | Cards empilhados, mini-wizard com circulos menores (w-4 h-4) |
| Tablet (768-1024px) | 2 colunas | Grid padrao |
| Desktop (> 1024px) | 2 colunas | max-w-[1000px] centralizado |

### Dados Mock Realistas

```
Peca 1 (Pronto):
  titulo: "5 Erros que Todo Iniciante Comete com Python"
  etapa: "topo", formato: "carrossel_7"
  status: "completo"
  etapas: [aprovado, aprovado, aprovado, aprovado, aprovado, aprovado]

Peca 2 (Executando):
  titulo: "Python e a Linguagem #1 do Mercado em 2026"
  etapa: "topo", formato: "post_unico"
  status: "em_execucao"
  etapas: [aprovado, aprovado, aprovado, em_execucao, pendente, pendente]
  progresso: { detalhe: "Gerando imagem slide 3/7", atual: 3, total: 7 }

Peca 3 (Aguardando):
  titulo: "Como Construi Meu Primeiro Modelo de ML em 7 Dias"
  etapa: "meio", formato: "carrossel_10"
  status: "aguardando_aprovacao"
  etapas: [aprovado, aguardando_aprovacao, pendente, pendente, pendente, pendente]

Peca 4 (Pendente):
  titulo: "Aula Gratuita: Pipeline de Dados com Python"
  etapa: "fundo", formato: "thumbnail_youtube"
  status: "pendente"
  etapas: [pendente, pendente, pendente, pendente, pendente, pendente]

Peca 5 (Erro):
  titulo: "Matriculas Abertas: Formacao Completa em IA"
  etapa: "conversao", formato: "capa_reels"
  status: "erro"
  etapas: [aprovado, aprovado, erro, pendente, pendente, pendente]
  erro_msg: "Falha na geracao de imagem: timeout Gemini API"
```

---

## TELA 3: Export do Funil (`/funil-export`)

### Padrao de Layout

```
+------------------------------------------------------------------+
| Header: titulo + contagem + badges                               |
+------------------------------------------------------------------+
|                                                                  |
|  [Card Preview 1]   [Card Preview 2]   [Card Preview 3]         |
|  thumbnail          thumbnail          thumbnail                 |
|  titulo + badges    titulo + badges    titulo + badges            |
|  [Editar] [PDF]     [Editar] [PDF]     [Editar] [PDF]            |
|                                                                  |
|  [Card Preview 4]   [Card Preview 5]                             |
|  thumbnail          thumbnail                                    |
|  titulo + badges    titulo + badges                               |
|  [Editar] [PDF]     [Editar] [PDF]                               |
|                                                                  |
+------------------------------------------------------------------+
| Barra fixa rodape: [Baixar Todos PDFs] [Salvar Tudo no Drive]   |
+------------------------------------------------------------------+
```

- Container: `max-w-[1200px] mx-auto`
- Layout dos cards: `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6`

### Hierarquia Visual

1. Grid de cards com thumbnails (preview visual imediato do resultado)
2. Barra fixa no rodape (acoes em lote, sempre visivel)
3. Badges por etapa em cada card (contexto rapido)
4. Botoes individuais por card (acoes granulares)

### Header

```
Componentes:
- h1: "Exportar Funil" | text-xl font-semibold text-text-primary
- Badge variant="success" size="md": "5 pecas prontas"
- Subtitulo: tema do funil | text-sm text-text-secondary
- Breadcrumb: Home > Funil > Export | text-xs text-text-muted

Container:
- Card padding="md"
- mb-8
```

### Card de Preview

Cada card mostra o preview do primeiro slide da peca com acoes de export.

```
+------------------------------------------+
|  +------------------------------------+  |
|  |                                    |  |
|  |    Thumbnail (preview slide 1)     |  |
|  |    aspect-[4/5]                    |  |
|  |    bg-bg-elevated                  |  |
|  |                                    |  |
|  +------------------------------------+  |
|                                          |
|  [Badge TOPO]  [Badge CARROSSEL 7]       |
|                                          |
|  "5 Erros que Todo Iniciante Comete..."  |
|  7 slides | Gerado em 12 abr 2026        |
|                                          |
|  [Editar]  [PDF]  [Drive]                |
+------------------------------------------+
```

**Componentes por Secao:**

| Secao | Componente | Props/Classes |
|-------|-----------|---------------|
| Card wrapper | Card | `padding="sm"` hover=true |
| Thumbnail container | div | `aspect-[4/5] rounded-lg overflow-hidden bg-bg-elevated mb-3` |
| Thumbnail imagem | img | `w-full h-full object-cover` (primeiro slide como PNG) |
| Thumbnail placeholder | div | `w-full h-full flex items-center justify-center` + icone imagem `text-text-muted` |
| Badge etapa | Badge | variant por etapa, size="sm" |
| Badge formato | Badge | variant="secondary", size="sm" |
| Titulo | p | `text-sm font-medium text-text-primary mt-2 line-clamp-2` |
| Meta info | p | `text-xs text-text-muted mt-1 font-mono` — "7 slides | 12 abr 2026" |
| Grupo botoes | div | `flex gap-2 mt-3` |
| Botao Editar | Button | variant="ghost", size="sm" — icone lapis + "Editar" |
| Botao PDF | Button | variant="outline", size="sm" — icone download + "PDF" |
| Botao Drive | Button | variant="outline", size="sm" — icone nuvem + "Drive" |

**Hover no card:**
- Card sobe 4px: `hover:-translate-y-1`
- Shadow sutil: `hover:shadow-md`
- Borda ilumina: `hover:border-purple/30`
- Thumbnail recebe overlay escuro sutil com icone de "ampliar": `hover:after:bg-black/40`

### Barra Fixa no Rodape

Sempre visivel na parte inferior da viewport. Contem acoes em lote.

```
+------------------------------------------------------------------+
|  5 pecas prontas para exportar     [Baixar Todos] [Salvar Drive] |
+------------------------------------------------------------------+
```

**Classes do container:**
```
fixed bottom-0 left-0 right-0 z-40
bg-bg-card/90 backdrop-blur-md
border-t border-border-default
px-6 py-4
```

**Layout interno:**
```
max-w-[1200px] mx-auto flex items-center justify-between gap-4
```

**Componentes:**

| Secao | Componente | Props/Classes |
|-------|-----------|---------------|
| Label | p | `text-sm text-text-secondary` — "5 pecas prontas para exportar" |
| Grupo botoes | div | `flex gap-3` |
| Baixar Todos | Button | variant="outline", size="md" — icone download + "Baixar Todos os PDFs" |
| Salvar Drive | Button | variant="primary", size="md" — icone Google Drive + "Salvar Tudo no Drive" |

**Padding bottom no conteudo:**
- Adicionar `pb-24` no container principal para o conteudo nao ficar atras da barra fixa

### Feedback de Acoes

| Acao | Tipo | Mensagem |
|------|------|----------|
| Clicar "Editar" | Redirect | Vai para `/editor?pipeline={pecaId}&brand={brandSlug}` |
| Clicar "PDF" (individual) | Download + Toast | Toast success: "PDF da peca 'titulo' baixado com sucesso" |
| Clicar "Drive" (individual) | Loading no botao + Toast | Spinner no botao durante upload, Toast success: "Peca salva no Google Drive" |
| Clicar "Baixar Todos" | Loading no botao + Toast | Spinner + "Gerando PDFs..." -> Toast: "5 PDFs baixados com sucesso" |
| Clicar "Salvar Drive" | Loading no botao + Toast | Spinner + "Salvando no Drive..." -> Toast: "Funil completo salvo no Google Drive" |
| Erro no upload Drive | Toast error | "Erro ao salvar no Drive: verifique as credenciais em Configuracoes" |
| Erro ao gerar PDF | Toast error | "Erro ao gerar PDF da peca 'titulo'" |

### Estados Visuais

| Estado | Visual | Detalhes |
|--------|--------|----------|
| Loading | Skeleton | 3-5 Skeleton blocos em grid com aspect-[4/5] (simulam thumbnails) |
| Sem pecas prontas | Mensagem central | "Nenhuma peca finalizada ainda." + CTA "Ver Acompanhamento" -> `/funil` |
| Parcialmente pronto | Cards prontos + cards desabilitados | Cards nao prontos: `opacity-50 pointer-events-none`, badge "Em andamento" |
| Todas prontas | Todos os cards ativos | Barra de rodape totalmente habilitada |
| Download em progresso | Button loading | Spinner + texto "Gerando..." no botao clicado |
| Upload Drive em progresso | Button loading | Spinner + texto "Salvando..." |
| Sucesso global | Toast success | "Funil completo exportado com sucesso!" |

### Responsividade

| Breakpoint | Layout | Detalhes |
|------------|--------|----------|
| Mobile (< 640px) | 1 coluna | Cards empilhados, barra rodape com botoes empilhados verticalmente |
| Tablet (640-1024px) | 2 colunas | Grid 2 colunas |
| Desktop (> 1024px) | 3 colunas | max-w-[1200px] centralizado |

**Barra de rodape responsiva:**
- Mobile: `flex-col gap-2 text-center` (label em cima, botoes embaixo empilhados)
- Desktop: `flex-row justify-between` (label esquerda, botoes direita)

### Dados Mock Realistas

```
Peca 1:
  titulo: "5 Erros que Todo Iniciante Comete com Python"
  etapa: "topo", formato: "carrossel_7"
  total_slides: 7
  data_geracao: "2026-04-12"
  thumbnail: "/mock/slide-01-erros-python.png" (ou placeholder)

Peca 2:
  titulo: "Python e a Linguagem #1 do Mercado em 2026"
  etapa: "topo", formato: "post_unico"
  total_slides: 1
  data_geracao: "2026-04-12"

Peca 3:
  titulo: "Como Construi Meu Primeiro Modelo de ML em 7 Dias"
  etapa: "meio", formato: "carrossel_10"
  total_slides: 10
  data_geracao: "2026-04-12"

Peca 4:
  titulo: "Aula Gratuita: Pipeline de Dados com Python"
  etapa: "fundo", formato: "thumbnail_youtube"
  total_slides: 1
  data_geracao: "2026-04-12"

Peca 5:
  titulo: "Matriculas Abertas: Formacao Completa em IA"
  etapa: "conversao", formato: "capa_reels"
  total_slides: 1
  data_geracao: "2026-04-12"
```

---

## Animacoes e Transicoes

Reutilizar as animacoes ja definidas em `app.css`:

| Animacao | Classe | Uso |
|----------|--------|-----|
| Entrada da pagina | `animate-fade-up` | Container principal de cada tela |
| Borda pulsante (amber) | `animate-pulse-border` | Cards aguardando aprovacao |
| Shimmer (loading) | `animate-shimmer` | Skeleton loading |
| Pulse nativo | `animate-pulse` | Cards executando (borda purple) |

**Transicoes novas necessarias (adicionar em app.css):**

```css
@keyframes pulse-green {
  0%, 100% { border-color: rgba(52, 211, 153, 0.3); }
  50% { border-color: rgba(52, 211, 153, 0.7); }
}
.animate-pulse-green {
  animation: pulse-green 2s ease-in-out infinite;
}
```

Uso: feedback visual momentaneo quando uma peca muda para "completo" (pisca verde 3x e para).

---

## Componentes Novos Necessarios

Componentes que o Dev Mockado (Agente 06) precisara criar:

| Componente | Arquivo | Descricao |
|------------|---------|-----------|
| FunilPecaCard | `components/funil/FunilPecaCard.svelte` | Card de peca com badges, campos editaveis, borda por etapa |
| FunilMiniWizard | `components/funil/FunilMiniWizard.svelte` | 6 circulos horizontais com status por etapa do pipeline |
| FunilProgressBar | `components/funil/FunilProgressBar.svelte` | Barra de progresso geral (X de N) |
| FunilExportCard | `components/funil/FunilExportCard.svelte` | Card com thumbnail + badges + botoes de export |
| FunilExportBar | `components/funil/FunilExportBar.svelte` | Barra fixa no rodape com acoes em lote |
| EtapaBadge | `components/funil/EtapaBadge.svelte` | Badge com cor automatica por etapa (wrapper do Badge) |

**Props do EtapaBadge:**
```typescript
interface Props {
  etapa: 'topo' | 'meio' | 'fundo' | 'conversao';
  size?: 'sm' | 'md';
}
// Mapeia etapa -> variant do Badge automaticamente
// topo -> primary, meio -> success, fundo -> warning, conversao -> danger
```

**Props do FunilMiniWizard:**
```typescript
interface Props {
  etapas: Array<{
    agente: string;
    label: string;       // "STR", "CPY", etc
    status: 'pendente' | 'em_execucao' | 'aguardando_aprovacao' | 'aprovado' | 'erro';
  }>;
}
```

---

## Navegacao entre Telas

```
Home (/) 
  -> Criar Funil (tema + brand)
    -> /funil-plano (revisar plano)
      -> Aprovar -> /funil (acompanhamento)
        -> Todas prontas -> /funil-export (exportar)
        -> Clicar peca -> /pipeline/{pecaId}/... (fluxo existente)
          -> Voltar -> /funil (acompanhamento)
```

Links de retorno:
- `/funil-plano` -> botao "Voltar" -> `/` (home)
- `/funil` -> botao "Voltar" -> `/funil-plano` ou `/` dependendo do status
- `/funil-export` -> botao "Voltar" -> `/funil`

---

## Consistencia com Telas Existentes

As 3 telas novas devem manter identidade visual com:

1. **Pipeline wizard** (`/pipeline/[id]`): mesma linguagem de status (cores, badges, icones)
2. **Briefing** (`/pipeline/[id]/briefing`): mesma abordagem de campos editaveis inline + ApprovalBar
3. **Home** (`/`): mesma tipografia e espacamentos (text-xl, text-sm, text-xs)
4. **Layout geral**: mesma sidebar + conteudo principal, mesma fonte Outfit, mesma paleta dark mode

Regras:
- NUNCA CSS inline — sempre Tailwind
- NUNCA `style=` em elementos — usar classes utilitarias
- Bordas sempre `rounded-xl` para cards, `rounded-full` para badges e botoes
- Espacamento consistente: `gap-4` entre cards, `mb-8` entre secoes, `p-5` dentro de cards
