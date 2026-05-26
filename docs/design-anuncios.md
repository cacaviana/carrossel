# DESIGN -- Modulo Anuncios (Google Ads Display)

Documento gerado pelo Agente 05 (Arquiteto Designer) da esteira IT Valley.
Base: `docs/prd-anuncios.md` (Agente 01) + `docs/telas-anuncios.md` (Agente 02) + `docs/DESIGN.md` (design system do sistema) + `docs/DESIGN_FUNIL.md` + `docs/design-kanban-pipeline.md`.

Guia visual completo para as 6 telas novas do modulo Anuncios e as 8 alteracoes em telas existentes, mantendo a identidade dark mode premium IT Valley School (fonte Outfit, acento roxo `#A78BFA`, glassmorphism sutil em cards).

---

## 1. Tokens Visuais -- Modulo Anuncios

Os tokens base vem do design system do sistema (`docs/DESIGN.md`) -- mesmo fundo `#0A0A0F`, mesmos cards `#12121A`, mesmo acento roxo `#A78BFA`. O modulo Anuncios NAO introduz paleta nova -- reusa as cores ja definidas e adiciona apenas convencoes semanticas especificas para status de dimensao e formato.

### 1.1. Cor semantica do formato "Anuncio"

O badge de formato "Anuncio" recebe cor **ciano** (`cyan-400` / `#22D3EE`), distinta dos formatos existentes:

| Formato | Cor do Badge | Classes Tailwind |
|---------|--------------|------------------|
| Carrossel | roxo (padrao) | `bg-purple/8 text-purple border-purple/20` |
| Post Unico | roxo (padrao) | `bg-purple/8 text-purple border-purple/20` |
| Thumbnail YouTube | roxo (padrao) | `bg-purple/8 text-purple border-purple/20` |
| Capa Reels | roxo (padrao) | `bg-purple/8 text-purple border-purple/20` |
| **Anuncio** | **ciano** | `bg-cyan-400/10 text-cyan-400 border-cyan-400/25` |

Justificativa: o anuncio e uma peca paga / performance (Google Ads Display), diferente dos organicos. Ciano transmite "performance / pago / multiplataforma" e se separa visualmente do roxo dominante sem brigar com ele na paleta dark.

### 1.2. Mapeamento de status do anuncio

Status do anuncio seguem a convencao de cores ja estabelecida no sistema:

| Status | Cor | Badge variant | Icone | Classes Tailwind |
|--------|-----|---------------|-------|-------------------|
| `rascunho` | cinza muted | `secondary` | FileText | `bg-white/6 text-text-secondary border-white/10` |
| `em_andamento` | roxo (ativo) | `primary` | Spinner | `bg-purple/8 text-purple border-purple/20` + `animate-pulse` |
| `parcial` | amber | `warning` | AlertCircle | `bg-amber/10 text-amber border-amber/25` |
| `concluido` | verde | `success` | CheckCircle | `bg-green/10 text-green border-green/25` |
| `erro` | vermelho | `danger` | XCircle | `bg-red/9 text-red border-red/15` |
| `cancelado` | cinza | `secondary` | Archive | `bg-white/6 text-text-muted border-white/10` + `opacity-60` |

Status `parcial` (RN-019) merece destaque: badge sempre mostra contagem `N/4` (ex: "PARCIAL 3/4") -- deixa obvio quantas dimensoes passaram.

### 1.3. Mapeamento de status por dimensao (dentro do grid)

Cada uma das 4 celulas do grid de dimensoes tem seu proprio status visual:

| Status da dimensao | Cor da borda | Overlay/Icone | Classes |
|--------------------|--------------|---------------|---------|
| `valido` | verde | CheckCircle no canto | `border-green/40 ring-1 ring-green/20` |
| `revisao_manual` | amber | AlertCircle amarelo | `border-amber/40 ring-1 ring-amber/20` |
| `falhou` | vermelho | XCircle vermelho + texto "Falhou" | `border-red/40 bg-red/5` |
| `nao_gerada` / `pendente` | cinza tracejada | texto "Aguardando..." | `border-dashed border-border-default` |
| `regenerando` | roxo pulsante | Spinner sobre imagem antiga | `border-purple animate-pulse` + `opacity-50 overlay` |

### 1.4. Icone da sidebar

Item "Anuncios" entre "Kanban" e "Historico" na secao Principal. Icone sugerido: **Megaphone** (mais intuitivo para "anuncio" do que Target ou Ad). Variante outline, 20px. Cor muda conforme rota ativa (igual demais itens).

---

## 2. Componentes Visuais Chave

Nesta secao, os 5 componentes novos que o Dev Mockado (Agente 06) precisa criar. Sao os blocos reutilizaveis que aparecem em multiplas telas do modulo.

### 2.1. AnuncioDimensoesGrid

**Proposito:** Grid 2x2 que mostra as 4 dimensoes do anuncio (1200x628, 1080x1080, 300x600, 300x250) com aspect ratio real, status por celula e acoes contextuais.

**Layout:**

```
+---------------------------------------------------+
|  +-------------------+    +-------------------+   |
|  | 1200x628          |    | 1080x1080         |   |
|  | landscape         |    | square            |   |
|  | aspect-[1200/628] |    | aspect-square     |   |
|  | [Badge Pro]       |    | [Badge Flash]     |   |
|  | [imagem]          |    | [imagem]          |   |
|  | [CheckCircle]     |    | [CheckCircle]     |   |
|  +-------------------+    +-------------------+   |
|                                                   |
|  +-------------------+    +-------------------+   |
|  | 300x600           |    | 300x250           |   |
|  | half page         |    | medium rectangle  |   |
|  | aspect-[300/600]  |    | aspect-[300/250]  |   |
|  | [Badge Flash]     |    | [Badge Flash]     |   |
|  | [imagem]          |    | [imagem]          |   |
|  | [CheckCircle]     |    | [XCircle falhou]  |   |
|  +-------------------+    +-------------------+   |
+---------------------------------------------------+
```

**Props (visuais):**

| Prop | Tipo | Descricao |
|------|------|-----------|
| dimensoes | array[4] | `[{id, imagemUrl, status, modelo, overlay, retries}]` |
| interativo | boolean | Se true, mostra checkbox + botao "Regerar" por celula (tela Editar). Se false, so lupa + status (tela Detalhe) |
| selecionadasParaRegerar | array | IDs das dimensoes marcadas |
| onSelectRegerar | callback | Quando usuario marca/desmarca |
| onRegerarIndividual | callback | Quando clica "Regerar" inline na celula |
| onAmpliar | callback | Quando clica na imagem ou lupa |

**Classes do container:**
- `grid grid-cols-1 sm:grid-cols-2 gap-4` (mobile empilhado, tablet+ 2x2)
- Cada celula: `Card padding="sm" hover={!interativo}` (se leitura, hover sobe; se editavel, sem hover para evitar confusao com checkbox)

**Classes de cada celula (`AnuncioDimensaoCell`):**
- Wrapper: `relative overflow-hidden rounded-xl border`
- Borda varia conforme status (ver secao 1.3)
- Container da imagem: `relative bg-bg-code` (fundo mais escuro para destacar a imagem gerada)
- Aspect ratio dinamico por dimensao: `aspect-[1200/628]`, `aspect-square`, `aspect-[300/600]`, `aspect-[300/250]`
- Imagem: `w-full h-full object-contain` (preserva proporcao real sem crop)

**Detalhes visuais por celula:**

Header da celula (acima da imagem):
- Label: `"1200x628 - landscape"` em Outfit 500 13px branco
- Sublabel: `"Gemini Pro - foto + logo"` em JetBrains Mono 10px text-muted
- Badge modelo no canto direito: `Badge variant="primary" size="sm"` com texto "Pro" (1200x628) ou "Flash" (demais)

Overlay sobre a imagem (canto superior direito):
- Icone de status (w-5 h-5) com fundo circular semi-transparente
- Lupa discreta no canto inferior direito (w-5 h-5 text-text-muted hover:text-purple)

Footer da celula (abaixo da imagem, quando `interativo`):
- Checkbox "Regerar esta dimensao" (text-xs)
- Botao `Button variant="outline" size="sm"` texto "Regerar" (alternativa ao checkbox + acao em lote)
- Contador `Retries: 0/2` em JetBrains Mono 10px text-muted (so aparece se retries > 0)

Estado `regenerando`:
- Imagem antiga com `opacity-30`
- Overlay: Spinner size="md" centralizado + texto "Regenerando..." abaixo em Outfit 500 13px text-purple
- Borda pulsa em roxo (`animate-pulse border-purple`)

Estado `falhou`:
- Imagem cinza com padrao de hachura (ou placeholder escuro)
- Icone XCircle grande (w-12 h-12 text-red/60) centralizado
- Texto "Falhou apos 2 tentativas" em Outfit 500 13px text-red
- Botao `Button variant="outline" size="sm"` com classe extra `text-red border-red/40` texto "Regerar" (sempre visivel)

Estado `nao_gerada`:
- Placeholder: fundo `bg-bg-code` + icone ImageOff (w-10 h-10 text-text-muted opacity-40) centralizado
- Texto "Aguardando geracao..." em Outfit 400 12px text-muted
- Borda tracejada `border-dashed border-border-default`
- Nenhuma acao disponivel (apenas leitura)

### 2.2. AnuncioCopyCard

**Proposito:** Card dedicado a exibir/editar a copy (headline + descricao) com contadores de caracteres visiveis e icone de copiar.

**Layout (modo leitura):**

```
+---------------------------------------------------+
|  COPY                                             |
|  -------------------------------------------      |
|  HEADLINE                        26 / 30    [📋]  |
|  "Aprenda IA do zero em 90 dias"                  |
|                                                   |
|  DESCRICAO                       74 / 90    [📋]  |
|  "Turma IT Valley School abre em maio com bolsas  |
|   para iniciantes."                               |
|                                                   |
|  [Copiar copy.txt]                                |
+---------------------------------------------------+
```

**Layout (modo editar):**

Mesma estrutura, mas os valores viram `Input type="text"` (headline, size md) e `Input type="textarea"` (descricao, 2 rows). Contadores ficam ao lado do label.

**Props:**

| Prop | Tipo | Descricao |
|------|------|-----------|
| headline | string | Texto da headline |
| descricao | string | Texto da descricao |
| editavel | boolean | Controla se e textarea ou readonly |
| onChange | callback | Para modo editavel |

**Componentes e classes:**

| Elemento | Componente | Classes/Props |
|----------|-----------|---------------|
| Wrapper | `Card padding="md"` | `bg-bg-card border-border-default` |
| Titulo secao | h3 | `text-xs font-mono uppercase tracking-wide text-text-muted mb-3` = "COPY" |
| Divisor | hr | `border-border-default mb-4` |
| Label campo | span | `text-[11px] font-mono uppercase tracking-wide text-text-muted` |
| Contador dentro do limite | span | `text-[11px] font-mono text-green` (verde) |
| Contador no limite (80%+) | span | `text-[11px] font-mono text-amber` (amarelo) |
| Contador estourado | span | `text-[11px] font-mono text-red` (vermelho) |
| Botao copiar inline | Button | `variant="ghost" size="sm"` icone Clipboard w-4 h-4 |
| Valor (leitura) | p | `text-base text-text-primary mt-1` (headline), `text-sm text-text-secondary mt-1` (descricao) |
| Input headline | Input | `type="text" maxlength=30` + borda vermelha se `valor.length > 30` |
| Input descricao | Textarea | `rows=3 maxlength=90` + borda vermelha se estoura |
| Botao copy.txt | Button | `variant="outline" size="sm"` texto "Copiar copy.txt" + icone Clipboard |

**Regra do contador:**
- 0 a 70% do limite: `text-green` (verde) -- "dentro"
- 70% a 100% do limite: `text-amber` (amarelo) -- "proximo do limite"
- \>100%: `text-red` (vermelho) + borda do input vermelha + botao "Salvar copy" desabilitado

### 2.3. AnuncioStatusBadge

**Proposito:** Badge especializado que mapeia status do anuncio -> cor + icone + texto, incluindo o caso especial `parcial (N/4)`.

**Props:**

| Prop | Tipo | Descricao |
|------|------|-----------|
| status | enum | rascunho / em_andamento / parcial / concluido / erro / cancelado |
| dimensoesOk | number (0-4) | Usado apenas se status=parcial. Default 4. |
| size | sm / md | Default md |

**Mapeamento completo:**

| Status | Texto do badge | Icone | Variant |
|--------|----------------|-------|---------|
| `rascunho` | "RASCUNHO" | FileText | secondary |
| `em_andamento` | "EM ANDAMENTO" | Spinner (gira) | primary |
| `parcial` | "PARCIAL {N}/4" | AlertCircle | warning |
| `concluido` | "CONCLUIDO" | CheckCircle | success |
| `erro` | "ERRO" | XCircle | danger |
| `cancelado` | "CANCELADO" | Archive | secondary |

Texto em JetBrains Mono 11px uppercase (segue o padrao Badge do sistema). Icone w-3 h-3 antes do texto.

Animacao: quando status muda (ex: em_andamento -> concluido), aplicar `animate-pulse-green` 3 vezes (animacao ja proposta no DESIGN_FUNIL.md) para feedback visual.

### 2.4. AnuncioRegenerateModal

**Proposito:** Modal disparado quando usuario quer regerar 1 ou mais dimensoes. Mostra quais dimensoes sao o alvo, preview lado a lado (imagem atual vs placeholder "nova") e campo de feedback livre.

**Layout:**

```
+-- Modal size="lg" ---------------------------------+
|  Regerar Dimensoes                           [X]   |
|  ------------------------------------------------  |
|                                                    |
|  Voce esta regerando 2 dimensoes:                  |
|                                                    |
|  +-- 1200x628 --+          +-- 300x600 --+        |
|  | Atual        |          | Atual       |        |
|  | [imagem]     |          | [imagem]    |        |
|  | Gemini Pro   |          | Gemini Flash|        |
|  | foto + logo  |          | so logo     |        |
|  +--------------+          +-------------+        |
|                                                    |
|  Feedback para o Art Director (opcional):          |
|  +----------------------------------------+        |
|  | Ex: "aumentar contraste, menos roxo"   |        |
|  |                                        |        |
|  +----------------------------------------+        |
|  0 / 500 caracteres                               |
|                                                    |
|  A copy (headline + descricao) nao muda.           |
|  As demais dimensoes permanecem intactas.          |
|                                                    |
|  ------------------------------------------------  |
|  [Cancelar]                    [Regerar Agora]    |
+----------------------------------------------------+
```

**Props:**

| Prop | Tipo | Descricao |
|------|------|-----------|
| open | boolean | Controla abertura |
| dimensoesAlvo | array | Dimensoes marcadas pelo usuario |
| onConfirm | callback(feedback) | Dispara regeneracao |
| onClose | callback | Fecha modal |

**Componentes e classes:**

| Elemento | Componente | Classes/Props |
|----------|-----------|---------------|
| Wrapper | `Modal size="lg" title="Regerar Dimensoes"` | - |
| Contador dimensoes | p | `text-sm text-text-secondary mb-4` |
| Grid preview | div | `grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6` |
| Card preview | Card | `padding="sm" shadow="sm"` |
| Label "Atual" | span | `text-[11px] font-mono uppercase text-text-muted` |
| Imagem preview | img | `w-full rounded-lg object-contain` + aspect ratio da dimensao |
| Info modelo | p | `text-xs text-text-muted font-mono mt-2` ex: "Gemini Pro - foto + logo" |
| Textarea feedback | Textarea | `rows=4 maxlength=500 placeholder="Ex: aumentar contraste, menos roxo, mais foco no texto"` |
| Contador | span | `text-[11px] font-mono text-text-muted mt-1 text-right block` |
| Aviso copy | p | `text-xs text-text-secondary bg-bg-elevated/50 rounded-lg px-3 py-2 mt-4` + icone Info |
| Botao cancelar | Button | `variant="ghost" size="md"` |
| Botao confirmar | Button | `variant="primary" size="md"` texto "Regerar Agora" + loading:true enquanto aguarda backend |

Animacao: modal entra com fade + scale de 95% para 100% (padrao ja definido).

### 2.5. AnuncioExportButton

**Proposito:** Nao e um botao unico -- e um grupo de acoes de export padronizado que aparece em 3 telas (Detalhe, Editar, Pipeline Export). Garante consistencia visual.

**Layout:**

```
+-- Group de botoes -----------------------------+
|  [Baixar ZIP]   [Salvar no Drive]   [Abrir Drive]
+------------------------------------------------+
```

**Props:**

| Prop | Tipo | Descricao |
|------|------|-----------|
| driveFolderLink | string \| null | Se null, mostra "Salvar no Drive"; se preenchido, mostra "Re-salvar" + "Abrir Drive" |
| salvandoDrive | boolean | Spinner no botao |
| baixandoZip | boolean | Spinner no botao |
| onDownloadZip | callback | Trigger download local |
| onSalvarDrive | callback | Trigger upload |
| statusAnuncio | enum | Usado para ajustar copy do botao em status=parcial |

**Comportamento:**

| Estado | Botao principal | Botao secundario |
|--------|-----------------|-------------------|
| Anuncio concluido, sem Drive | "Salvar no Drive" (primary) | "Baixar ZIP" (outline) |
| Anuncio concluido, com Drive | "Abrir no Drive" (secondary) | "Re-salvar no Drive" (outline) + "Baixar ZIP" (ghost) |
| Anuncio parcial, sem Drive | "Salvar no Drive (N/4)" (warning) | "Baixar ZIP (N/4)" (outline) + tooltip explicando parcial |
| Anuncio em_andamento | Todos desabilitados | - |
| Anuncio erro | Todos desabilitados + alerta inline | - |

**Componentes e classes:**

| Elemento | Componente | Classes/Props |
|----------|-----------|---------------|
| Wrapper | div | `flex flex-wrap gap-3` |
| Botao primary (salvar Drive) | Button | `variant="primary" size="md"` icone Cloud + texto |
| Botao secondary (abrir Drive) | Button | `variant="secondary" size="md"` icone ExternalLink + texto |
| Botao outline (ZIP) | Button | `variant="outline" size="md"` icone Download + texto |
| Feedback salvo | Banner inline | `type="success"` com texto "Salvo em: [link]" (some apos 5s) |

### 2.6. AnuncioListCard (card para a lista)

**Proposito:** Card compacto usado no grid da Lista de Anuncios (`/anuncios`). Mostra resumo do anuncio numa unica olhada.

**Layout:**

```
+-- Card -----------------------------------------+
|  [Badge Anuncio] [Badge CONCLUIDO]  ha 2 dias  |
|                                                 |
|  +--------------------+                         |
|  | thumb 1080x1080    |                         |
|  | (square)           |                         |
|  +--------------------+                         |
|                                                 |
|  "Aprenda IA em 90 dias"                        |
|  Turma IT Valley Schoolabre em maio com...      |
|                                                 |
|  [4/4 dimensoes] [Funil: Conversao]            |
|                                                 |
|  [Editar] [Drive] [Excluir]                    |
+-------------------------------------------------+
```

**Componentes e classes:**

| Elemento | Componente | Classes/Props |
|----------|-----------|---------------|
| Wrapper | Card | `padding="md" hover=true` (sobe 2px + shadow + borda roxa no hover) |
| Linha top | div | `flex items-center justify-between mb-3` |
| Badge formato | Badge | variant customizado ciano + size="sm" + texto "ANUNCIO" |
| Badge status | AnuncioStatusBadge | size="sm" |
| Timestamp | span | `text-[11px] font-mono text-text-muted` |
| Thumbnail | img | `w-full aspect-square rounded-lg object-cover bg-bg-code mb-3` |
| Headline | p | `text-sm font-medium text-text-primary line-clamp-1` |
| Descricao preview | p | `text-xs text-text-secondary line-clamp-2 mt-1` |
| Linha meta | div | `flex flex-wrap gap-2 mt-3` |
| Badge contagem | Badge | variant="secondary" size="sm" texto "4/4 dimensoes" ou "3/4 dimensoes" (warning se parcial) |
| Badge etapa funil | Badge | variant por etapa (topo=primary, meio=success, fundo=warning, avulso=secondary) |
| Linha acoes | div | `flex gap-2 mt-4 pt-3 border-t border-border-default` |
| Botao editar | Button | `variant="outline" size="sm"` icone Pencil |
| Botao Drive | Button | `variant="ghost" size="sm"` icone ExternalLink (oculto se `drive_folder_link` null) |
| Botao excluir | Button | `variant="danger" size="sm"` icone Trash |

Todo o card e clicavel (navegacao para `/anuncios/[id]`). Botoes dentro usam `event.stopPropagation()` para nao navegar quando clicados.

---

## 3. Layout Tela por Tela

### 3.1. TELA: Lista de Anuncios (`/anuncios`)

**Padrao de Layout:** Padding-pagina padrao (`px-8 py-6`). Conteudo full-width ate `max-w-[1200px]`. Header + barra de filtros no topo (sticky em scroll longo). Grid de cards abaixo.

**Wireframe estrutural:**

```
+-- Sidebar --+-- Area principal (max-w-1200px) -----------------------+
|            |                                                         |
|            |  Anuncios                       [+ Novo Anuncio]        |
|            |  Gerencie anuncios Google Ads Display da IT Valley      |
|            |                                                         |
|            |  +-- Barra Filtros (sticky top) ---------------------+  |
|            |  | [busca] [Status ▾] [Funil ▾] [Data inicio] [fim]  |  |
|            |  | Toggle: Incluir excluidos   [Limpar filtros]      |  |
|            |  +---------------------------------------------------+  |
|            |                                                         |
|            |  8 anuncios encontrados                                 |
|            |                                                         |
|            |  +-- Grid 3 colunas (lg) / 2 (md) / 1 (sm) ----------+  |
|            |  | [Card] [Card] [Card]                              |  |
|            |  | [Card] [Card] [Card]                              |  |
|            |  | [Card] [Card]                                     |  |
|            |  +---------------------------------------------------+  |
|            |                                                         |
|            |  [< Anterior] Pagina 1 de 3 [Proximo >]                 |
+-------------+--------------------------------------------------------+
```

**Hierarquia Visual:**
1. Titulo "Anuncios" (Outfit 300 28px) + botao primary "Novo Anuncio" (CTA principal, alinhado a direita)
2. Barra de filtros (segundo plano, funcional)
3. Contador de resultados em text-muted (contexto)
4. Grid de cards (conteudo principal, 70% da area util)

**Grupos de Campos:**

| Grupo | Campos | Layout |
|-------|--------|--------|
| Header | titulo, subtitulo, botao primary | Flex horizontal, `justify-between` |
| Filtros | busca, status, funil, datas, incluir_excluidos | Flex wrap com `gap-3`. Em mobile: colapsam para drawer "Filtros" com botao |
| Resultado | card do anuncio (AnuncioListCard) | Grid `grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4` |

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Titulo | h1 | `text-[28px] font-light text-text-primary` |
| Subtitulo | p | `text-sm text-text-secondary mt-1` |
| Botao Novo Anuncio | Button | `variant="primary" size="md"` icone Plus + texto |
| Busca | Input | `type="text"` placeholder "Buscar por titulo ou headline..." icone Search w-4 h-4 |
| Select status | Input (select) | opcoes: Todos, Em andamento, Concluido, Parcial, Erro, Cancelado |
| Select funil | Input (select) | opcoes: Todas, Topo, Meio, Fundo, Avulso |
| Data | Input | `type="date"` |
| Toggle excluidos | Toggle | label "Incluir excluidos" |
| Limpar filtros | Button | `variant="ghost" size="sm"` |
| Card anuncio | AnuncioListCard | ver secao 2.6 |
| Paginacao | div custom | 3 botoes: Anterior + label + Proximo |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem |
|------|------------------|----------|
| Filtrar em tempo real | Visual imediato | Grid re-renderiza com `animate-fade-up`. Contador atualiza. |
| Filtro sem resultado | Estado vazio | Mensagem central: "Nenhum anuncio encontrado para esses filtros." + `Button variant="outline" size="md"` "Limpar filtros" |
| Clicar card | Navegacao | `/anuncios/[id]` |
| Clicar Novo Anuncio | Navegacao | `/anuncios/novo` |
| Clicar Excluir no card | Modal | Abre AnuncioDeleteModal (Tela 5) |
| Hover card | Visual | `-translate-y-1 shadow-md border-purple/30` (300ms) |
| Erro ao carregar | Banner | `Banner type="error"` no topo: "Erro ao carregar anuncios." + botao "Tentar novamente" |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Loading | Grid de 6 skeleton cards (aspect-square thumbnail + 2 linhas) com shimmer |
| Vazio (sem filtro) | Card central ilustrado: icone Megaphone grande (64px opacity 30%) + "Nenhum anuncio criado ainda." + subtexto "Crie seu primeiro anuncio Google Ads Display" + `Button variant="primary" size="lg"` "Criar primeiro anuncio" |
| Vazio (filtro) | Card central: "Nenhum anuncio encontrado para esses filtros." + botao "Limpar filtros" |
| Erro | Banner vermelho topo + grid vazio |
| Sucesso | Grid populado com cards |

**Responsividade:**
- Desktop (>= 1024px): Grid 3 colunas, filtros em 1 linha
- Tablet (768-1024px): Grid 2 colunas, filtros em 2 linhas com wrap
- Mobile (< 768px): Grid 1 coluna, filtros colapsam em botao "Filtros" (abre drawer), FAB "+" no canto inferior direito para "Novo Anuncio"

**Dados Mock Realistas (para o Dev Mockado):**

```
Anuncio 1 (concluido):
  titulo: "Matriculas IT Valley School Maio 2026"
  headline: "Aprenda IA em 90 dias" (20 chars)
  descricao: "Turma IT Valley School abre em maio com bolsas para iniciantes." (64 chars)
  status: "concluido"
  etapa_funil: "conversao"
  dimensoes_ok_count: 4
  criado_em: "2026-04-20"

Anuncio 2 (parcial):
  titulo: "Formacao Deep Learning - Turma Maio"
  headline: "Deep Learning do Zero" (21 chars)
  descricao: "Formacao completa em Deep Learning com PyTorch. Inscricoes abertas." (68 chars)
  status: "parcial"
  dimensoes_ok_count: 3
  criado_em: "2026-04-18"

Anuncio 3 (em_andamento):
  titulo: "Workshop Gratuito RAG Agents"
  headline: "RAG + Agentes LangChain" (24 chars)
  descricao: "Workshop ao vivo: construa agentes com RAG em 2h. Inscreva-se agora." (69 chars)
  status: "em_andamento"
  etapa_funil: "topo"
  dimensoes_ok_count: 2
  criado_em: "2026-04-23"

Anuncio 4 (erro):
  titulo: "Bolsas Parciais MLOps"
  headline: "MLOps com 50% de bolsa" (22 chars)
  descricao: "Vagas limitadas para a formacao MLOps com 50% de desconto." (59 chars)
  status: "erro"
  dimensoes_ok_count: 0
  criado_em: "2026-04-19"
```

---

### 3.2. TELA: Criar Anuncio (`/anuncios/novo`)

**Padrao de Layout:** Conteudo central com `max-w-[720px]`. Formulario vertical em secoes visuais. Footer fixo com botoes de acao em mobile.

**Decisao de design:** Form unico (NAO wizard). A entrada do anuncio e compacta o suficiente (titulo + tema + disciplina + foto) que divisao em passos seria overhead desnecessario. O pipeline de 6 agentes ja e o "wizard" real -- essa tela so coleta o briefing inicial.

**Wireframe estrutural:**

```
+-- Area principal (max-w-720px) ---------------------+
|                                                     |
|  < Voltar para Anuncios                             |
|                                                     |
|  Novo Anuncio                                       |
|  Briefing inicial para gerar 4 dimensoes + copy     |
|  Google Ads Display                                 |
|                                                     |
|  +-- Secao: Identificacao ----------------------+   |
|  | Titulo interno * [Input]                     |   |
|  | Este titulo aparece na lista, sidebar Drive e|   |
|  | painel do funil. Min 3 caracteres.           |   |
|  +-----------------------------------------------+   |
|                                                     |
|  +-- Secao: Briefing ----------------------------+   |
|  | [Tab Texto Livre] [Tab Disciplina]           |   |
|  |                                               |   |
|  | (Texto livre ativo:)                         |   |
|  | Tema / Briefing * [Textarea grande]          |   |
|  | Descreva o que o anuncio deve comunicar.     |   |
|  | Min 20 caracteres.                           |   |
|  |                                               |   |
|  | (ou Disciplina ativo:)                       |   |
|  | Selecione disciplina [Cards clicaveis]       |   |
|  | Selecione tecnologia [Chips]                 |   |
|  +-----------------------------------------------+   |
|                                                     |
|  +-- Secao: Estrategia --------------------------+   |
|  | Etapa do Funil [Select: topo/meio/fundo/avulso]|  |
|  | Default: Avulso (anuncio standalone)          |   |
|  +-----------------------------------------------+   |
|                                                     |
|  +-- Secao: Identidade --------------------------+   |
|  | Foto do Criador [Galeria horizontal]          |   |
|  | Selecionada aparece nas dimensoes 1200x628 e |   |
|  | 1080x1080 (nas pequenas so o logo).           |   |
|  | [+ Adicionar fotos] -> /configuracoes        |   |
|  +-----------------------------------------------+   |
|                                                     |
|  +-- Info: O que vai acontecer ------------------+   |
|  | i Ao clicar em "Criar Anuncio":               |   |
|  |   - Sera criado um pipeline com formato=anuncio|  |
|  |   - Geradas 4 dimensoes (1200x628, 1080x1080, |   |
|  |     300x600, 300x250)                         |   |
|  |   - Copy Google Ads (headline 30 + descricao 90)|  |
|  |   - Custo estimado: ~R$0,60                   |   |
|  +-----------------------------------------------+   |
|                                                     |
|  [Cancelar]                 [Criar Anuncio]        |
+-----------------------------------------------------+
```

**Hierarquia Visual:**
1. Breadcrumb / botao voltar (contexto)
2. Titulo + subtitulo (contexto)
3. 4 cards de secao (input principal, empilhados com `gap-8`)
4. Card info azul/roxo (expectativa sobre o que vai acontecer)
5. Botoes de acao (CTA final, sticky em mobile)

**Decisoes importantes:**
- NAO ha campo para selecionar dimensoes (RN-001: 4 sao obrigatorias)
- NAO ha campo para headline/descricao (gerados pelo Copywriter no pipeline)
- Foto do Criador e opcional mas altamente recomendada (afeta brand overlay)
- Se `foto_criador` vazia, mostrar callout laranja "Sem foto: o anuncio usara apenas o logo em todas as dimensoes"

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Card de secao | Card | `padding="lg" shadow="sm"` |
| Label do campo | label | `text-xs font-mono uppercase tracking-wide text-text-muted mb-2 block` |
| Input titulo | Input | `type="text" placeholder="Ex: Matriculas IT Valley Maio 2026"` |
| Helper texto | p | `text-xs text-text-muted mt-1` |
| Tabs briefing | Tabs | 2 tabs: "Texto Livre" / "Disciplina" |
| Textarea tema | Input (textarea) | `rows=5 placeholder="Ex: Anunciar abertura de matriculas da turma de maio. Publico: profissionais de TI querendo transicao de carreira. Destacar bolsas disponiveis."` |
| Card disciplina | Card | `padding="sm" hover=true`. Selecionada: `border-purple ring-1 ring-purple/30` |
| Chip tecnologia | Badge | `variant="primary" size="md"` clicavel (muda para outline quando desmarcado) |
| Select etapa funil | Input (select) | opcoes: Avulso (default) / Topo / Meio / Fundo |
| Galeria fotos | Grid custom | 6 colunas, miniaturas circulares 56px |
| Foto item | div | `w-14 h-14 rounded-full overflow-hidden border-2 border-transparent cursor-pointer`. Selecionada: `border-purple ring-2 ring-purple/30` |
| Botao adicionar foto | Button | `variant="ghost" size="sm"` link para `/configuracoes` |
| Card info | Banner | `type="info" dismissible=false` |
| Botao criar | Button | `variant="primary" size="lg"` texto "Criar Anuncio". Desabilitado ate validacao passar. Loading: "Iniciando pipeline..." |
| Botao cancelar | Button | `variant="ghost" size="md"` |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem |
|------|------------------|----------|
| Titulo invalido | Inline abaixo do campo | "Informe um titulo com pelo menos 3 caracteres" |
| Tema invalido | Inline abaixo do campo | "Descreva o tema com pelo menos 20 caracteres" |
| Selecionar foto | Visual imediato | Borda roxa + ring + check sutil |
| Submit sucesso | Redirect | `/pipeline/[id]` |
| Submit erro | Banner | `Banner type="error"` no topo: "Nao foi possivel criar o anuncio. Verifique a conexao." |
| Loading submit | Spinner no botao | "Iniciando pipeline..." + cards desabilitados |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Inicial | Todos os campos vazios, botao primary desabilitado (`opacity-50`) |
| Valido | Botao primary habilitado |
| Loading submit | Botao com spinner + cards com `opacity-60 pointer-events-none` |
| Erro | Banner error topo + campos com borda vermelha |
| Sucesso | Redirect imediato (sem estado visivel) |

**Responsividade:**
- Desktop: `max-w-[720px]` centralizado, cards com `padding="lg"`
- Tablet: `max-w-[680px]` com `px-6`
- Mobile: Full-width com `px-4`, botoes sticky no bottom (`fixed bottom-0 left-0 right-0 bg-bg-global/95 backdrop-blur-md border-t border-border-default p-4`)

---

### 3.3. TELA: Detalhe do Anuncio (`/anuncios/[id]`)

**Padrao de Layout:** Duas colunas em desktop (proporcao 2:1), empilhado em mobile. Esquerda: grid das 4 dimensoes (conteudo principal). Direita: copy + acoes + meta (sidebar contextual).

**Decisao de design:** Grid 2x2 para as 4 dimensoes (NAO carrossel nem abas). Justificativa:
- 4 dimensoes cabem tranquilo em 2x2 em desktop (area principal)
- Visao simultanea e o proposito pedagogico do formato: o usuario compara as 4 lado a lado antes de salvar no Drive
- Carrossel forca interacao desnecessaria
- Abas escondem informacao critica

Em mobile, o grid colapsa para 1 coluna (empilhado), mas preservando aspect ratio real de cada dimensao.

**Wireframe estrutural:**

```
+-- Area principal ---------------------------------------------+
|                                                               |
|  < Voltar para Anuncios                                       |
|                                                               |
|  +-- Header ---------------------------------------------+    |
|  | [Badge ANUNCIO] [AnuncioStatusBadge] [Etapa funil]   |    |
|  | "Matriculas IT Valley School Maio 2026"              |    |
|  | Criado por Carlos em 2026-04-20 - 14:32              |    |
|  | Pipeline: abc123  |  Dimensoes: 4/4                   |    |
|  |                                      [Editar] [...]   |    |
|  +-------------------------------------------------------+    |
|                                                               |
|  +-- Col Esquerda (2/3) --+  +-- Col Direita (1/3) ------+   |
|  |                        |  |                            |   |
|  |  DIMENSOES             |  | COPY                       |   |
|  |  -------------         |  | -------                    |   |
|  |  [1200x628]  [1080x1080]  | HEADLINE       20/30  [📋] |   |
|  |  [300x600]   [300x250]    | "Aprenda IA em 90 dias"   |   |
|  |                        |  |                            |   |
|  |                        |  | DESCRICAO      64/90  [📋] |   |
|  |                        |  | "Turma IT Valley School    |   |
|  |                        |  |  abre em maio..."          |   |
|  |                        |  |                            |   |
|  |                        |  | [Copiar copy.txt]         |   |
|  |                        |  +----------------------------+   |
|  |                        |                                   |
|  |                        |  +-- Export ----------------+     |
|  |                        |  | [Salvar no Drive]        |     |
|  |                        |  | [Baixar ZIP]             |     |
|  |                        |  | (se ja salvo:            |     |
|  |                        |  |  [Abrir no Drive])       |     |
|  |                        |  +----------------------------+   |
|  |                        |                                   |
|  |                        |  +-- Info Pipeline -----------+   |
|  |                        |  | Pipeline: abc123 →         |   |
|  |                        |  | Funil: Conversao           |   |
|  |                        |  | Criado: 2026-04-20         |   |
|  |                        |  +----------------------------+   |
|  +------------------------+  +----------------------------+   |
|                                                               |
+---------------------------------------------------------------+
```

**Hierarquia Visual:**
1. Header com status + titulo + metadados (contexto imediato)
2. Grid 2x2 das 4 dimensoes (conteudo principal, 65% da largura)
3. Card Copy com contadores e botao copiar (informacao textual chave)
4. Card Export com acoes de saida (CTA secundario)
5. Card Info Pipeline (metadados tecnicos, menor destaque)

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Header container | Card | `padding="md" shadow="sm" mb-6` |
| Badge formato | Badge | ciano, size="md" |
| Badge status | AnuncioStatusBadge | size="md" |
| Titulo | h1 | `text-2xl font-semibold text-text-primary` |
| Meta info | p | `text-xs font-mono text-text-muted mt-1` |
| Botao editar | Button | `variant="outline" size="md"` icone Pencil |
| Menu overflow (...) | Button | `variant="ghost" size="md"` dropdown com: Excluir |
| Grid dimensoes | AnuncioDimensoesGrid | `interativo={false}` |
| Card copy | AnuncioCopyCard | `editavel={false}` |
| Card export | AnuncioExportButton | Flex col, botoes empilhados com `w-full` |
| Card info | Card | `padding="md" shadow="sm"` campos em `<dl>` (dt label / dd valor) |

**Acoes e Feedback:**

| Acao | Tipo de Feedback | Mensagem |
|------|------------------|----------|
| Ampliar dimensao | Modal | Modal size="lg" com imagem fullscreen aspect ratio real, botao fechar |
| Copiar headline | Toast | `success` "Headline copiada!" (3s auto-dismiss) |
| Copiar descricao | Toast | `success` "Descricao copiada!" |
| Copiar copy.txt | Toast | `success` "copy.txt copiado para a area de transferencia!" |
| Clicar Editar | Redirect | `/anuncios/[id]/editar` |
| Clicar Salvar no Drive | Loading + Toast | Spinner + "Salvando no Drive..." → `success` "Salvo no Drive!" + botao vira "Re-salvar" + aparece "Abrir no Drive" |
| Clicar Baixar ZIP | Loading + Download | Spinner + "Preparando ZIP..." → download inicia automaticamente |
| Clicar Excluir (menu) | Modal | AnuncioDeleteModal (Tela 5) |
| Hover dimensao | Visual | Lupa fica mais visivel (opacity 0.6 -> 1) + cursor pointer |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Loading | Header skeleton + Grid 2x2 de skeletons retangulares (aspect ratio real por dimensao) + Card copy com linhas skeleton |
| Vazio (nao encontrado) | Card central: "Anuncio nao encontrado" + icone SearchX 48px + botao "Voltar para Anuncios" |
| Erro | Banner error topo + Card "Tentar novamente" |
| Sucesso (concluido) | Grid completo com todas as dimensoes em status valido (borda verde sutil). Botoes export habilitados. AnuncioStatusBadge verde. |
| Sucesso parcial (RN-019) | Banner amber topo: "3 de 4 dimensoes geradas. A dimensao 300x250 falhou - [Regerar dimensao faltante]" (link para `/anuncios/[id]/editar`). Grid mostra 3 imagens + 1 celula em estado `falhou`. |
| Em andamento | Header com badge azul pulsante "EM ANDAMENTO". Botao "Acompanhar pipeline" destacado em cima do grid. Grid mostra dimensoes ja geradas + skeletons nas nao geradas. |
| Erro global | Header badge vermelho. Todas dimensoes em estado `nao_gerada`. Botao "Retomar pipeline" destacado. |
| Excluido (deleted_at) | Card inteiro com `opacity-60`. Banner topo: "Este anuncio foi excluido em 2026-04-15." Acoes de edicao/Drive desabilitadas. |

**Responsividade:**
- Desktop (>= 1024px): 2 colunas `grid-cols-[2fr_1fr] gap-6`
- Tablet (768-1024px): 2 colunas `grid-cols-[3fr_2fr]`
- Mobile (< 768px): 1 coluna empilhada. Copy + Export vao para cima (acima do grid de dimensoes) para priorizar conteudo textual em leitura mobile

---

### 3.4. TELA: Editar Anuncio (`/anuncios/[id]/editar`)

**Padrao de Layout:** Mesma estrutura da Detalhe, mas com campos editaveis e acoes inline por dimensao. Duas colunas (grid 2x2 das dimensoes + coluna direita com copy editavel).

**Decisao de design:** NAO usar modal para edicao de copy -- edita inline na mesma pagina. Grid de dimensoes vira interativo (checkboxes + botoes "Regerar" inline por celula). Botoes de acao em lote na barra inferior sticky.

**Wireframe estrutural:**

```
+-- Area principal ---------------------------------------------+
|                                                               |
|  < Voltar para Detalhe                                        |
|                                                               |
|  Editar Anuncio                                               |
|  [AnuncioStatusBadge: PARCIAL 3/4]                           |
|                                                               |
|  +-- Col Esquerda (2/3) --+  +-- Col Direita (1/3) ------+   |
|  |                        |  |                            |   |
|  |  TITULO                |  | COPY (editavel)            |   |
|  |  [Input: "Matriculas"] |  | HEADLINE       [20/30 ✓]   |   |
|  |                        |  | [Input: "Aprenda IA..."]   |   |
|  |  ETAPA FUNIL           |  |                            |   |
|  |  [Select: Conversao]   |  | DESCRICAO      [64/90 ✓]   |   |
|  |                        |  | [Textarea: "Turma..."]     |   |
|  |  ------                |  |                            |   |
|  |                        |  | [Salvar copy]              |   |
|  |  DIMENSOES             |  +----------------------------+   |
|  |  (interativo=true)     |                                   |
|  |                        |  +-- Foto do Criador ---------+   |
|  |  [✓] [1200x628]        |  | (readonly, link pra config)|   |
|  |     [imagem] [Regerar] |  | [Miniatura Carlos]         |   |
|  |                        |  | [Alterar em Configuracoes] |   |
|  |  [ ] [1080x1080]       |  +----------------------------+   |
|  |     [imagem] [Regerar] |                                   |
|  |                        |  +-- Export ------------------+   |
|  |  [ ] [300x600]         |  | (mesmo AnuncioExportButton)|   |
|  |     [imagem] [Regerar] |  +----------------------------+   |
|  |                        |                                   |
|  |  [ ] [300x250]         |                                   |
|  |     [FALHOU] [Regerar] |                                   |
|  |                        |                                   |
|  +------------------------+  +----------------------------+   |
|                                                               |
|  +-- Sticky bottom bar ----------------------------------+    |
|  | 1 dimensao marcada | [Excluir Anuncio]  [Regerar     |    |
|  |                    |                     dimensoes]  |    |
|  +-------------------------------------------------------+    |
+---------------------------------------------------------------+
```

**Hierarquia Visual:**
1. Status header (feedback visual sobre a situacao atual)
2. Campos editaveis basicos (titulo + etapa funil)
3. Grid de dimensoes interativo (elemento principal)
4. Card copy editavel (sidebar, prioritario em mobile)
5. Barra sticky bottom com acoes em lote

**Componentes por Secao:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Input titulo | Input | `type="text"` com label acima |
| Select etapa | Input (select) | label "Etapa do Funil" |
| Botao salvar copy | Button | `variant="primary" size="md"` |
| AnuncioCopyCard | AnuncioCopyCard | `editavel={true}` |
| AnuncioDimensoesGrid | AnuncioDimensoesGrid | `interativo={true}` com callbacks de checkbox e regerar |
| Barra sticky | div | `sticky bottom-0 bg-bg-global/90 backdrop-blur-md border-t border-border-default py-4 px-6 -mx-8` |
| Botao excluir | Button | `variant="danger" size="md"` |
| Botao regerar em lote | Button | `variant="primary" size="md"` texto "Regerar N dimensoes selecionadas". Desabilitado se nenhuma marcada. |

**Feedback de Acoes:**

| Acao | Tipo de Feedback | Mensagem |
|------|------------------|----------|
| Editar headline | Contador atualiza | 20/30 verde, 28/30 amber, 31/30 vermelho + borda vermelha |
| Editar descricao | Contador atualiza | Mesma logica |
| Salvar copy | Loading + Toast | Spinner no botao → Toast success "Copy salva. Imagens nao foram regeneradas (copy nao aparece na imagem)." |
| Marcar dimensao (checkbox) | Visual imediato | Checkbox marcado + borda roxa tracejada na celula + contador "1 dimensao marcada" aparece na barra |
| Clicar "Regerar" inline | Modal | Abre AnuncioRegenerateModal ja com aquela dimensao pre-selecionada |
| Clicar "Regerar em lote" | Modal | Abre AnuncioRegenerateModal com todas marcadas |
| Regeneracao iniciada | Visual imediato | Modal fecha, dimensao(oes) entram em estado `regenerando` (spinner sobre imagem antiga, borda roxa pulsante) |
| Regeneracao concluida | Toast + visual | Toast success "Dimensao 1200x628 regenerada" + imagem atualiza com animacao fade |
| Regeneracao falhou | Toast + visual | Toast error "Falha na regeneracao apos 2 tentativas" + celula vira estado `falhou` |
| Cancelar com pendencias | Modal confirmacao | "Voce tem alteracoes nao salvas. Deseja descarta-las?" |
| Clicar Excluir | Modal | AnuncioDeleteModal (Tela 5) |

**Estados Visuais:**

| Estado | Tratamento |
|--------|-----------|
| Loading | Skeletons em todas as areas |
| Normal | Campos editaveis, 0 checkbox marcados, botao "Regerar dimensoes" desabilitado |
| 1+ selecionada | Contador na barra aparece + botao regerar habilitado |
| Regenerando | Celulas em estado regenerando, demais interativas |
| Copy invalida | Contador vermelho + borda vermelha + botao "Salvar copy" desabilitado |
| Salvo | Toast success, campos voltam ao estado normal |

**Responsividade:**
- Desktop: 2 colunas + barra sticky bottom
- Mobile: 1 coluna (Copy em cima, Grid abaixo), barra sticky bottom com botoes empilhados

---

### 3.5. TELA: Confirmar Exclusao -- Modal (Tela 5)

**Padrao de Layout:** Modal pequeno (`size="sm"`, max-w-md). Padrao ja estabelecido no sistema para acoes destrutivas.

**Wireframe:**

```
+-- Modal (max-w-md) --------------------+
|  [X]                                   |
|                                        |
|        +-- Icone AlertTriangle --+     |
|        |    w-12 h-12 red         |     |
|        +--------------------------+     |
|                                        |
|  Excluir Anuncio?                      |
|                                        |
|  "Matriculas IT Valley School          |
|   Maio 2026" sera removido do          |
|   modulo Anuncios.                     |
|                                        |
|  - Os arquivos no Google Drive         |
|    permanecem intactos                 |
|  - O anuncio pode ser recuperado via   |
|    filtro "Incluir excluidos"          |
|                                        |
|  [Cancelar]     [Sim, excluir]        |
+----------------------------------------+
```

**Componentes:**

| Secao | Componente | Props |
|-------|-----------|-------|
| Wrapper | Modal | `size="sm" title=""` (titulo custom no body) |
| Icone alerta | div | `w-12 h-12 rounded-full bg-red/10 text-red mx-auto flex items-center justify-center` + icone AlertTriangle w-6 h-6 |
| Titulo | h3 | `text-lg font-semibold text-text-primary text-center mt-4` |
| Descricao | p | `text-sm text-text-secondary text-center mt-2` + span com aspas para o titulo |
| Lista info | ul | `text-xs text-text-muted mt-4 space-y-1` com bullets sutis |
| Botao cancelar | Button | `variant="ghost" size="md"` |
| Botao confirmar | Button | `variant="danger" size="md"` |

**Feedback:**

| Acao | Tipo | Mensagem |
|------|------|----------|
| Cancelar / X / Esc | Fecha modal | - |
| Confirmar | Loading no botao + delete | Botao com spinner + "Excluindo..." |
| Sucesso | Toast + navegacao | Toast "Anuncio excluido" + navega para `/anuncios` (ou remove card se veio da lista) |
| Erro | Alert inline | `Banner type="error"` dentro do modal: "Erro ao excluir. Tente novamente." |

---

### 3.6. TELA: Regenerar Dimensao -- Modal (Tela 6)

Ver secao 2.4 `AnuncioRegenerateModal`. O componente JA descreve completamente o layout e feedback do modal. Resumo de estados:

| Estado | Tratamento |
|--------|-----------|
| Inicial | Preview das dimensoes alvo + feedback vazio + botao Regerar habilitado |
| Digitando feedback | Contador 0/500 em tempo real |
| Submit | Botao com spinner + "Iniciando regeneracao..." + inputs desabilitados |
| Sucesso | Modal fecha + feedback visual na tela pai (dimensoes entram em estado regenerando) |
| Erro | Banner inline dentro do modal: "Erro ao iniciar regeneracao. Tente novamente." |

---

## 4. Estados Visuais Globais do Modulo

Esta secao resume o tratamento visual de cada estado em UMA TABELA PARA CONSULTA RAPIDA.

### 4.1. Matriz Status do Anuncio -> Visual

| Status | AnuncioStatusBadge | Borda do card lista | Acoes disponiveis | Grid dimensoes |
|--------|--------------------|-----|--------------------|----------------|
| rascunho | cinza FileText | default | Criar pipeline, Excluir | Todas em `nao_gerada` |
| em_andamento | roxo Spinner pulsante | roxo sutil | Ver pipeline, Cancelar | Mix de `valido` + `nao_gerada` (skeleton) |
| parcial | amber AlertCircle "N/4" | amber | Editar, Regerar faltantes, Export, Excluir | Mix `valido` + `falhou` |
| concluido | verde CheckCircle | verde sutil ao hover | Editar, Export, Excluir | Todas `valido` |
| erro | vermelho XCircle | vermelho | Retomar pipeline, Excluir | Todas `nao_gerada` ou `falhou` |
| cancelado | cinza Archive | opacity 60% | Nenhuma (readonly) | Grid com opacity reduzida |

### 4.2. Matriz Status da Dimensao (dentro do grid) -> Visual

| Status | Overlay | Borda | Footer acoes (modo edicao) |
|--------|---------|-------|-----------------------------|
| valido | CheckCircle verde canto sup. dir. | `border-green/40` | [✓] Regerar |
| revisao_manual | AlertCircle amber canto sup. dir. | `border-amber/40` | [✓] Regerar + texto "Revisao necessaria" |
| falhou | XCircle vermelho grande centralizado + imagem cinza | `border-red/40` | [Regerar] sempre visivel (destaque) |
| nao_gerada | Texto "Aguardando..." + placeholder | `border-dashed` | Desabilitado |
| regenerando | Spinner centralizado + imagem antiga opacity 30% | `border-purple animate-pulse` | Desabilitado ate terminar |

### 4.3. Loading Padroes

| Contexto | Tipo | Detalhes |
|----------|------|----------|
| Lista de anuncios | Skeleton cards | 6 cards com thumbnail square + 2 linhas texto + barra meta |
| Detalhe do anuncio | Skeleton header + Skeleton 2x2 grid + Skeleton copy | 4 celulas skeleton com aspect ratio real de cada dimensao |
| Regeneracao individual | Spinner overlay na celula | Imagem antiga visivel com opacity-30 + spinner roxo + texto "Regenerando..." |
| Salvar copy | Spinner no botao | "Salvando..." |
| Salvar Drive | Spinner no botao | "Salvando no Drive..." |
| Download ZIP | Spinner no botao | "Preparando ZIP..." |

### 4.4. Empty States

| Contexto | Ilustracao | Mensagem | CTA |
|----------|-----------|----------|-----|
| Lista sem filtros e sem dados | Icone Megaphone 64px opacity 30% | "Nenhum anuncio criado ainda." | [Criar primeiro anuncio] primary lg |
| Lista com filtros sem resultado | Icone SearchX 48px | "Nenhum anuncio encontrado para esses filtros." | [Limpar filtros] outline md |
| Detalhe nao encontrado | Icone FileQuestion 48px | "Anuncio nao encontrado." | [Voltar para Anuncios] outline |
| Historico com filtro formato=anuncio vazio | Icone Megaphone 48px | "Nenhum anuncio no historico." | [Criar Anuncio] primary md |

### 4.5. Erros

| Contexto | Tipo | Mensagem |
|----------|------|----------|
| Lista erro de rede | Banner topo | "Erro ao carregar anuncios. [Tentar novamente]" |
| Detalhe erro de rede | Banner + botao | "Nao foi possivel carregar o anuncio." |
| Criar erro de validacao | Inline abaixo do campo | Ex: "Informe um titulo com pelo menos 3 caracteres" |
| Criar erro de backend | Banner topo do form | "Nao foi possivel criar o anuncio. Verifique a conexao." |
| Regenerar erro | Banner inline no modal | "Erro ao iniciar regeneracao. Tente novamente." |
| Dimensao falhou apos 2 retries | Celula em estado `falhou` + toast persistente (se em AP-4) | Toast warning: "Dimensao 300x250 falhou apos 2 tentativas. Voce pode aprovar em status parcial ou regerar." |

### 4.6. Sucessos

| Contexto | Tipo | Mensagem |
|----------|------|----------|
| Copy copiada | Toast 3s | "Headline copiada!" |
| Copy salva | Toast 3s | "Copy salva. As imagens nao foram alteradas." |
| Dimensao regenerada | Toast 3s + animacao verde na celula | "Dimensao 1200x628 regenerada" + `animate-pulse-green` 3x |
| Anuncio salvo no Drive | Toast 4s + banner inline | "Anuncio salvo no Google Drive!" + link "Abrir pasta" |
| ZIP baixado | Toast 3s | "ZIP baixado com sucesso." |
| Anuncio excluido | Toast 3s + redirect/remove card | "Anuncio excluido." |
| Brand Gate passou em todas 4 | Animacao + toast | Cada celula piscando verde em sequencia (1 a 4) + toast success "Todas as 4 dimensoes passaram no Brand Gate!" |

---

## 5. Micro-interacoes

### 5.1. Copiar para area de transferencia

Quando usuario clica no botao copiar (Clipboard icon):
1. Icone muda de Clipboard para CheckCircle verde por 1s
2. Fundo do botao pulsa verde (`animate-pulse-green` 1x)
3. Toast aparece no canto superior direito com animacao slide-in
4. Apos 3s, toast some com fade-out + slide-up
5. Icone volta a ser Clipboard

### 5.2. Regeneracao individual de dimensao

Feedback em sequencia:
1. Usuario clica "Regerar" na celula (ou confirma no modal)
2. Modal fecha com fade (se era modal)
3. Celula alvo: imagem fica com `opacity-30`, borda vira roxa pulsante (`animate-pulse`)
4. Spinner size="md" aparece centralizado na celula
5. Texto "Regenerando..." em text-purple aparece abaixo do spinner
6. Quando termina:
   - Sucesso: imagem nova substitui com fade-in (200ms), borda vira verde por 1s (`animate-pulse-green`), toast success
   - Falha: celula vira estado `falhou`, toast error

### 5.3. Brand Gate passa em todas dimensoes

Quando anuncio muda de `em_andamento` para `concluido` com Brand Gate OK em todas 4 (comportamento em AP-4 ou logo apos pipeline):
1. Em ordem (1200x628 -> 1080x1080 -> 300x600 -> 300x250), cada celula:
   - CheckCircle verde aparece no canto com `animate-fade-up` (300ms cada)
   - Borda pulsa verde 2x
2. Badge de status do anuncio no header muda de azul para verde com `animate-pulse-green`
3. Toast success: "Todas as 4 dimensoes passaram no Brand Gate!"
4. Botao "Salvar no Drive" ganha shadow roxo destacado por 3s para chamar atencao

### 5.4. Falha apos 2 retries

Feedback em sequencia:
1. Celula que falhou vira estado `falhou` (XCircle vermelho grande)
2. Badge de status do anuncio vira `parcial N/4` com animacao de shake sutil (200ms)
3. Toast warning persistente (5s auto-dismiss): "Dimensao {id} falhou apos 2 tentativas. Voce pode regerar ou aprovar em status parcial."
4. Botao "Regerar" na celula ganha destaque (borda vermelha pulsante 3x)

### 5.5. Edicao inline de copy

Enquanto usuario digita headline:
1. Contador de chars atualiza em tempo real (debounce 100ms para performance)
2. Cor do contador transiciona suavemente (green -> amber em 70% -> red em 100%+)
3. Se estourar 30: borda do input vira vermelha (`border-red`) + mensagem inline abaixo "Maximo 30 caracteres (Google Ads)"
4. Botao "Salvar copy" fica `disabled` com tooltip "Headline excede 30 caracteres"
5. Quando volta ao limite: borda volta ao normal, botao reabilita

### 5.6. Selecao multipla de dimensoes para regerar

Quando usuario marca checkbox em celula:
1. Checkbox: `scale-in` animacao (150ms)
2. Borda da celula ganha `border-dashed border-purple` (distinto do estado normal)
3. Ring sutil aparece ao redor (`ring-1 ring-purple/20`)
4. Contador na barra bottom sticky aparece com `animate-fade-up`: "N dimensoes selecionadas"
5. Botao "Regerar dimensoes" reabilita + recebe shadow roxo

### 5.7. Hover nos cards da lista

1. Card sobe 2px: `hover:-translate-y-0.5`
2. Shadow aumenta: `hover:shadow-md`
3. Borda ganha cor: `hover:border-purple/30`
4. Thumbnail recebe overlay escuro sutil: `hover:after:bg-black/10`
5. Transicao suave em 300ms

### 5.8. Drag-and-drop (futuro -- nao MVP)

Comentario: nao esta no MVP, mas deixar previsto no design que o grid 2x2 pode receber drag-and-drop para reordenar dimensoes no card de lista (sem efeito funcional -- apenas visual).

---

## 6. Integracao Visual com Telas Existentes

### 6.1. Alteracao: Home / Criar Conteudo (`/`)

**O que muda:** Adicionar card "Anuncio" no grid de selecao de formato.

**Layout:**

```
Grid atual (3 cards):
[Carrossel] [Post Unico] [Thumbnail]

Grid novo (4 cards em lg, 2x2 em sm):
[Carrossel] [Post Unico] [Thumbnail] [Anuncio]
```

Em desktop (>= lg), o grid vira `grid-cols-4`. Em tablet (md), `grid-cols-2` empilhando em 2 linhas. Em mobile, `grid-cols-1`.

**Card "Anuncio":**
- Estrutura igual aos demais (Card padding="md", hover=true)
- Icone: Megaphone w-10 h-10 text-cyan-400
- Titulo: "Anuncio" em Outfit 500
- Subtitulo: "Google Ads Display" em JetBrains Mono 11px text-muted
- Sub-subtitulo: "4 dimensoes + copy" em text-secondary 12px
- Quando selecionado: borda ciano (nao roxa) + glow ciano
- Ao selecionar, o campo `tipo_carrossel` (numero de slides) fica oculto (nao se aplica)

### 6.2. Alteracao: Funnel Architect (`/pipeline/[id]/briefing`)

**O que muda:** Lista de pecas do funil agora aceita `formato = anuncio` como opcao no select de edicao de peca.

Card da peca quando formato=anuncio:
- Badge formato muda para badge ciano "ANUNCIO"
- Icone da peca: Megaphone em vez do icone padrao
- Label sub: "4 dimensoes (1200x628, 1080x1080, 300x600, 300x250)" em text-muted
- Nenhuma outra alteracao visual

### 6.3. Alteracao: Historico (`/historico`)

**O que muda:**
- Filtro formato ganha opcao "Anuncio" no dropdown
- Card de anuncio no historico usa thumbnail da dimensao 1080x1080 (square, mais proxima do formato dos demais cards)
- Badge formato ciano no card
- Contador "4 dimensoes" (ou "N/4" se parcial) no card
- Clicar no card leva para `/anuncios/[id]` (NAO para `/pipeline/[id]/export` como nos demais)

O card no historico (`HistoricoCard`) nao precisa de variante nova -- apenas condicionar:
```
if (item.formato === 'anuncio') {
  badgeVariant = 'cyan'; // custom class
  thumbnailUrl = item.image_urls[1]; // 1080x1080
  link = `/anuncios/${item.id}`;
  extraBadge = `${item.dimensoes_ok_count}/4`;
}
```

### 6.4. Alteracao: Board Kanban (`/kanban`)

**O que muda:** Cards do kanban recebem 2 indicadores quando formato=anuncio:

1. **Badge formato ciano "ANUNCIO"** (em vez de badge disciplina ou no lugar dela).
2. **Indicador de dimensoes:** Abaixo do titulo do card, um pequeno grupo de 4 retangulos 6x4px horizontais, cada um colorido conforme status da dimensao (verde=valido, vermelho=falhou, cinza=nao_gerada). Visualmente compacto, passa informacao rapida.

```
+------------------------------------------+
| [Badge prioridade]              ha 2 dias |
| Titulo do anuncio (truncado 2 linhas)    |
| [ANUNCIO]                                |
| [v][v][v][x]  (4 dimensoes: 3/4 ok)      |
| [Avatar] [+2]                             |
+------------------------------------------+
```

**Thumbnail do card kanban:** Se mostrar thumbnail, usar 1080x1080 (igual historico).

### 6.5. Alteracao: Modal Detalhe do Card -- Kanban

**O que muda:** Aba "Detalhes" ganha variante visual quando `card.formato === 'anuncio'`:

Substitui a area de "copy_text" + "imagens" por:
- `AnuncioCopyCard editavel={false}` (headline + descricao readonly)
- `AnuncioDimensoesGrid interativo={false}` (grid 2x2 das 4 dimensoes)
- Banner info: "Para editar a copy ou regenerar dimensoes, abra o anuncio no modulo dedicado" + botao "Abrir no modulo Anuncios" (primary sm) que leva a `/anuncios/[id]`

Abas Comentarios e Atividade ficam iguais (unificadas com outros formatos).

### 6.6. Alteracao: Pipeline AP-4 -- Aprovacao de Imagem (`/pipeline/[id]/imagem`)

**O que muda:** Quando `formato === 'anuncio'`, a tela substitui o layout de "slides com 3 variacoes cada" por um layout de "4 dimensoes (1 imagem cada)".

**Wireframe AP-4 para formato=anuncio:**

```
+-- Area principal ---------------------------------+
|  Breadcrumb: Pipeline > Revisao de Imagens (AP-4) |
|  "Revisar Imagens do Anuncio"                     |
|  [Badge ANUNCIO] [AnuncioStatusBadge]             |
|                                                   |
|  As 4 dimensoes foram geradas. Aprove todas ou   |
|  rejeite individualmente para regerar.            |
|                                                   |
|  +-- AnuncioDimensoesGrid interativo=true ----+   |
|  | [1200x628 valido] [1080x1080 valido]       |   |
|  | [300x600 valido]  [300x250 falhou]         |   |
|  +---------------------------------------------+   |
|                                                   |
|  Se alguma dimensao falhou 2x:                    |
|  Banner warning: "A dimensao 300x250 falhou apos |
|  2 tentativas. Voce pode aprovar em status parcial|
|  (exporta so as 3 prontas) ou regerar agora."     |
|                                                   |
|  [< Voltar] [Rejeitar Todas]  [Aprovar e         |
|                                Finalizar]          |
|  Se parcial:                                      |
|  [Aprovar em status parcial (3/4)] warning style  |
+---------------------------------------------------+
```

**Decisao visual chave:** Reutilizar `AnuncioDimensoesGrid interativo={true}` -- o mesmo componente do Editar serve aqui, so muda a chamada de "Regerar" que vai direto para re-executar Image Generator + Brand Gate naquela dimensao (pipeline interno).

Botao "Aprovar e Finalizar":
- Verde (variant primary com glow), so habilita se todas 4 validas
- Se parcial: botao vira `variant="warning"` com texto "Aprovar em status parcial (N/4)" + tooltip explicando

### 6.7. Alteracao: Pipeline Preview + Export (`/pipeline/[id]/export`)

**O que muda:** Quando `formato === 'anuncio'`:
- NAO mostra botao "Exportar PDF"
- Preview usa `AnuncioDimensoesGrid interativo={false}` em vez de carrossel de slides
- Usa `AnuncioCopyCard editavel={false}` em vez do card de "legenda_linkedin"
- Usa `AnuncioExportButton` (grupo: ZIP + Drive)
- Preview de `copy.txt` renderizado como `<pre>` com fundo `bg-bg-code` para mostrar como ficara o arquivo exportado

**Wireframe:**

```
+-- Area principal ---------------------------------+
|  Titulo: "Matriculas IT Valley Maio 2026"         |
|  [Badge ANUNCIO] [Badge CONCLUIDO]                |
|  Score Content Critic: 8.5/10                     |
|                                                   |
|  +-- Col Esquerda (2/3) ---+ +-- Col Direita ---+|
|  | Preview Dimensoes       | | Score Radar +     ||
|  | AnuncioDimensoesGrid    | | Score Cards       ||
|  | interativo=false        | |                   ||
|  |                         | | AnuncioCopyCard   ||
|  |                         | | editavel=false    ||
|  |                         | |                   ||
|  |                         | | Preview copy.txt: ||
|  |                         | | [bloco de codigo] ||
|  |                         | |                   ||
|  |                         | | AnuncioExportButton||
|  |                         | | [Baixar ZIP]      ||
|  |                         | | [Salvar Drive]    ||
|  |                         | |                   ||
|  |                         | | [Ver no modulo     ||
|  |                         | |  Anuncios]        ||
|  |                         | | [Novo Anuncio]    ||
|  +-------------------------+ +-------------------+|
+---------------------------------------------------+
```

Preview do copy.txt:
```html
<pre class="bg-bg-code border border-border-default rounded-lg p-4 font-mono text-xs text-text-secondary whitespace-pre-wrap">
HEADLINE:
Aprenda IA em 90 dias

DESCRICAO:
Turma IT Valley School abre em maio com bolsas para iniciantes.

---
Anuncio gerado em 2026-04-23 14:32
Pipeline: abc123
</pre>
```

### 6.8. Alteracao: Configuracoes (`/configuracoes`)

**O que muda:** A secao "Platform Rules" (pagina interna da tab "Platform Rules") ganha novo card "Google Ads Display" ao lado dos existentes (LinkedIn, Instagram, Facebook, YouTube).

**Card Google Ads Display:**

```
+-- Card padding="md" ------------------+
| [icone Megaphone] Google Ads Display |
| -------------------------------------|
| Headline max:        30 caracteres   |
| Descricao max:       90 caracteres   |
| Dimensoes suportadas:                |
|   - 1200x628 (landscape, Gemini Pro) |
|   - 1080x1080 (square, Flash)        |
|   - 300x600 (half page, Flash)       |
|   - 300x250 (medium rectangle, Flash)|
|                                      |
| Todos os campos readonly (config via |
| platform_rules.json no backend)      |
+--------------------------------------+
```

Nenhuma alteracao funcional -- apenas exibicao das regras que ja vivem no `platform_rules.json`.

---

## 7. Responsividade -- Resumo

O modulo Anuncios e otimizado para desktop (maioria dos usuarios de marketing trabalham em tela grande). Mobile e totalmente suportado mas com algumas adaptacoes.

### 7.1. Lista de Anuncios (`/anuncios`)

| Breakpoint | Layout |
|------------|--------|
| Desktop (>= 1024px) | Grid 3 colunas, filtros em 1 linha, botao "+ Novo Anuncio" no header |
| Tablet (768-1024px) | Grid 2 colunas, filtros em 2 linhas |
| Mobile (< 768px) | Grid 1 coluna, filtros em drawer (botao "Filtros"), FAB "+" flutuante |

### 7.2. Criar Anuncio (`/anuncios/novo`)

| Breakpoint | Layout |
|------------|--------|
| Desktop | `max-w-[720px]` centralizado, botoes alinhados a direita |
| Tablet | Mesmo layout, padding ajustado |
| Mobile | Full-width, botoes sticky bottom full-width |

### 7.3. Detalhe do Anuncio (`/anuncios/[id]`)

| Breakpoint | Layout |
|------------|--------|
| Desktop | 2 colunas `grid-cols-[2fr_1fr]`. Dimensoes esquerda, copy/export direita |
| Tablet | 2 colunas `grid-cols-[3fr_2fr]` |
| Mobile | 1 coluna. ORDEM ALTERADA: Copy + Export acima, Dimensoes abaixo (leitura prioritaria) |

### 7.4. Editar Anuncio (`/anuncios/[id]/editar`)

| Breakpoint | Layout |
|------------|--------|
| Desktop | 2 colunas. Grid dimensoes esquerda, campos edicao direita. Barra sticky bottom |
| Tablet | 2 colunas mais apertadas |
| Mobile | 1 coluna. Campos editaveis acima, Grid dimensoes abaixo. Barra sticky bottom empilhada |

### 7.5. Modais

| Modal | Desktop | Mobile |
|-------|---------|--------|
| Exclusao | `max-w-md` centralizado | Mesmo tamanho, padding menor |
| Regenerar | `max-w-2xl` (lg) com preview 2 col | `max-w-full mx-4`, preview 1 col |
| Zoom de dimensao | `max-w-5xl` | Fullscreen `w-full h-full` |

### 7.6. Grid de dimensoes dentro do componente

| Breakpoint | Layout do grid |
|------------|----------------|
| >= 640px | `grid-cols-2` (2x2) |
| < 640px | `grid-cols-1` (empilhado, mas preservando aspect ratio real de cada dimensao -- 300x600 fica alto e estreito, 1200x628 fica baixo e largo, etc.) |

---

## 8. Componentes Visuais Novos -- Resumo

Lista dos componentes que o Dev Mockado (Agente 06) precisa criar:

| Componente | Arquivo | Proposito |
|-----------|---------|-----------|
| AnuncioDimensoesGrid | `components/anuncios/AnuncioDimensoesGrid.svelte` | Grid 2x2 das 4 dimensoes com status + acoes opcionais |
| AnuncioDimensaoCell | `components/anuncios/AnuncioDimensaoCell.svelte` | Celula individual do grid (1 dimensao). Usado por AnuncioDimensoesGrid |
| AnuncioCopyCard | `components/anuncios/AnuncioCopyCard.svelte` | Card de copy (headline + descricao) com contadores |
| AnuncioStatusBadge | `components/anuncios/AnuncioStatusBadge.svelte` | Badge com mapeamento status -> cor + icone + texto parcial N/4 |
| AnuncioRegenerateModal | `components/anuncios/AnuncioRegenerateModal.svelte` | Modal de confirmacao de regeneracao com preview + feedback |
| AnuncioExportButton | `components/anuncios/AnuncioExportButton.svelte` | Grupo de botoes (ZIP + Drive) com estados |
| AnuncioListCard | `components/anuncios/AnuncioListCard.svelte` | Card do anuncio na lista (grid) |
| AnuncioDeleteModal | `components/anuncios/AnuncioDeleteModal.svelte` | Modal de confirmacao de exclusao (reutilizavel) |

Componentes reutilizados do sistema existente:
- `Button`, `Card`, `Input`, `Modal`, `Badge`, `Banner`, `Spinner`, `Skeleton`, `Toggle`, `Tabs` (ja existem)
- `ApprovalBar` (para AP-4 adaptado)
- `HistoricoCard` (so recebe condicional novo)
- `KanbanCard` (so recebe indicador novo)

---

## 9. Padroes Visuais Destaque

### 9.1. Grid 2x2 para as 4 dimensoes
Decisao unanime em todas as telas onde as dimensoes aparecem (Detalhe, Editar, Pipeline AP-4, Pipeline Export, Modal Kanban). Nada de carrossel/abas -- visao simultanea e o valor pedagogico do formato.

### 9.2. Cor ciano para badge "ANUNCIO"
Separacao visual clara dos demais formatos (organicos ficam roxo). Mantem a paleta dark sem adicionar cor nova -- usa `cyan-400` do Tailwind.

### 9.3. Aspect ratio real em TODAS as exibicoes
Mesmo em mobile empilhado, cada celula preserva aspect ratio real da dimensao (1200x628 fica baixa/larga, 300x600 fica alta/estreita). O usuario sempre percebe visualmente que sao formatos diferentes.

### 9.4. Badge "PARCIAL N/4" em amber
Status `parcial` NUNCA aparece isolado -- sempre com contagem. Destaque visual maximo em amber para sinalizar "precisa de atencao, mas nao e falha".

### 9.5. Regeneracao individual sempre por modal
Mesmo quando clicado no botao "Regerar" inline em uma celula especifica, abre o mesmo `AnuncioRegenerateModal` com aquela dimensao pre-selecionada. Garante que o feedback livre sempre passe pelo usuario.

### 9.6. Copy card com contador semaforico (verde/amber/vermelho)
Feedback visual imediato sobre limites Google Ads. Nao espera blur -- reage a cada caractere digitado.

### 9.7. `AnuncioExportButton` unificado
Mesmo componente em 3 telas (Detalhe, Editar, Pipeline Export) garante que logica de Drive/ZIP nunca divirja. Estados (salvando, salvo, re-salvar) viram props consistentes.

### 9.8. Brand Gate visual: pulso verde em sequencia
Quando as 4 dimensoes passam, animacao em sequencia (1200x628 -> 1080x1080 -> 300x600 -> 300x250) cria microfeedback narrativo: "o Brand Gate analisou cada uma e todas passaram". Reforca a percepcao de qualidade do sistema.

---

## 10. Duvidas de Design (Em Aberto)

Nenhuma duvida bloqueante. Pontos abaixo sao decisoes tomadas que valem registro explicito:

1. **Grid 2x2 vs carrossel:** Decidido grid 2x2 em todas as telas. Carrossel so pode ser adicionado no futuro se surgir uma tela com mais de 4 dimensoes (fora do MVP).

2. **Wizard vs form unico em Criar Anuncio:** Decidido form unico. Entrada e compacta, wizard seria overhead.

3. **Cor do badge Anuncio:** Decidido ciano (`cyan-400`). Alternativas consideradas e descartadas:
   - Amarelo: conflita com status parcial/warning
   - Verde: conflita com sucesso
   - Roxo: igual aos demais formatos, nao distingue

4. **Icone da sidebar:** Decidido Megaphone (mais intuitivo que Target/BadgeAd). Fonte: Lucide icons (mesma lib ja usada).

5. **Regenerar sempre com modal:** Decidido sim (mesmo quando acionado inline). Garante feedback livre consistente.

6. **Copy editavel em Kanban modal:** Decidido NAO. Redireciona para modulo Anuncios. Mantem simplicidade e unifica edicao.

7. **Preview copy.txt como `<pre>`:** Decidido usar bloco de codigo com fundo `bg-bg-code` -- mostra como ficara o arquivo exportado. Evita confusao entre "texto de leitura" e "conteudo do arquivo".

8. **Responsividade mobile do Detalhe:** Decidido inverter ordem -- Copy/Export ANTES de Dimensoes em mobile. Em telas grandes Dimensoes e o conteudo principal (visual). Em mobile, Copy e mais critico para leitura rapida.

Nenhuma destas decisoes bloqueia os agentes seguintes (06 Dev Mockado, 09 Dev Frontend). Todas podem ser revisitadas se houver feedback do P.O. ou da cliente.

---

*Documento gerado pelo Agente 05 (Arquiteto Designer) da esteira IT Valley.*
*Proximos agentes: Agente 06 (Dev Mockado) e Agente 09 (Dev Frontend) -- em paralelo, pos agentes 03/04.*
