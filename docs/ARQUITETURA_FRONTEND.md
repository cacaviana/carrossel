# ARQUITETURA FRONTEND -- Content Factory v3

Documento gerado pelo Agente 04 (Arquiteto IT Valley Frontend).
Base: PRD (Agente 01) + TELAS (Agente 02) + codigo existente no frontend SvelteKit 5.

Stack: SvelteKit 5 + Tailwind CSS v4 + Svelte runes ($state, $derived, $props, $effect)
Filosofia: Simples > Complexo. Dominio > Tecnico. Funciona > Bonito.

---

## Dominios Identificados

| Dominio | Casos de Uso | Status |
|---------|-------------|--------|
| **pipeline** | IniciarPipeline, AcompanharPipeline, AprovarEtapa, RejeitarEtapa, RetomarPipeline, CancelarPipeline | Novo |
| **briefing** | VisualizarBriefing, EditarBriefing, AprovarBriefing, RejeitarBriefing | Novo |
| **copy** | VisualizarCopy, EditarCopy, EscolherHook, AprovarCopy, RejeitarCopy | Novo |
| **visual** | VisualizarPrompts, EditarPrompt, AprovarPrompts, RejeitarPrompts | Novo |
| **imagem** | VisualizarVariacoes, EscolherVariacao, AprovarImagens, RejeitarImagens, RegerarVariacao | Novo |
| **export** | VisualizarScore, ExportarPdf, DownloadPng, SalvarDrive | Novo |
| **carrossel** | GerarConteudo, GerarImagens, EditarSlide, ExportarPdf, SalvarDrive | Existente (legado, manter) |
| **historico** | ListarHistorico, FiltrarHistorico, RemoverItem, ReabrirPipeline | Refatorar |
| **agente** | ListarAgentes, VisualizarAgente | Refatorar |
| **config** | SalvarApiKeys, SalvarBrandPalette, SalvarCreatorRegistry, SalvarPlatformRules, GerenciarFotos, GerenciarDesignSystems | Refatorar |

---

## Estrutura de Pastas Completa

```
src/
├── app.css                          # Design tokens (@theme) + utilitarios globais
├── app.d.ts
├── routes/
│   ├── +layout.svelte               # Shell com sidebar (refatorar de header para sidebar)
│   ├── +page.svelte                 # Home / Criar Conteudo (iniciar pipeline)
│   ├── pipeline/
│   │   └── [id]/
│   │       ├── +page.svelte         # Wizard do pipeline (7 etapas)
│   │       ├── briefing/
│   │       │   └── +page.svelte     # AP-1: Aprovacao de briefing
│   │       ├── copy/
│   │       │   └── +page.svelte     # AP-2: Aprovacao de copy + hook
│   │       ├── visual/
│   │       │   └── +page.svelte     # AP-3: Aprovacao de prompt visual
│   │       ├── imagem/
│   │       │   └── +page.svelte     # AP-4: Aprovacao de imagem
│   │       └── export/
│   │           └── +page.svelte     # Score + export PDF/Drive
│   ├── carrossel/
│   │   └── +page.svelte             # Legado (manter)
│   ├── historico/
│   │   └── +page.svelte             # Historico multi-formato
│   ├── agentes/
│   │   └── +page.svelte             # Agentes LLM + Skills
│   └── configuracoes/
│       └── +page.svelte             # Config expandida
│
└── lib/
    ├── components/
    │   ├── ui/                       # Genericos reutilizaveis
    │   │   ├── Badge.svelte          # Existente
    │   │   ├── Button.svelte         # Existente
    │   │   ├── Card.svelte           # Existente
    │   │   ├── Modal.svelte          # Novo
    │   │   ├── Spinner.svelte        # Novo
    │   │   ├── Skeleton.svelte       # Novo
    │   │   ├── Toggle.svelte         # Novo
    │   │   ├── Tabs.svelte           # Novo
    │   │   └── Banner.svelte         # Novo (feedback sucesso/erro)
    │   │
    │   ├── layout/                   # Shell do app
    │   │   └── Sidebar.svelte        # Novo — menu lateral
    │   │
    │   ├── pipeline/                 # Dominio pipeline
    │   │   ├── PipelineWizard.svelte      # Wizard vertical com 7 etapas
    │   │   ├── PipelineStepCard.svelte    # Card de 1 etapa (status, acoes)
    │   │   └── PipelineStatusBadge.svelte # Badge de status (pendente, em_execucao, etc)
    │   │
    │   ├── briefing/                 # Dominio briefing (AP-1)
    │   │   ├── BriefingEditor.svelte      # Textarea editavel do briefing
    │   │   └── FunilPlanner.svelte        # Lista de pecas do funil (se modo funil)
    │   │
    │   ├── copy/                     # Dominio copy (AP-2)
    │   │   ├── CopyEditor.svelte          # Edicao de headline, narrativa, CTA
    │   │   ├── HookSelector.svelte        # 3 cards A/B/C para escolha de hook
    │   │   ├── SlideSequenceEditor.svelte # Lista de slides editavel + reordenavel
    │   │   └── ToneGuideAlerts.svelte     # Correcoes do tone_guide
    │   │
    │   ├── visual/                   # Dominio visual (AP-3)
    │   │   ├── PromptEditor.svelte        # Prompt de imagem por slide (textarea)
    │   │   ├── PromptSlideList.svelte     # Lista de todos os prompts (accordion)
    │   │   ├── BrandPalettePreview.svelte # Preview da paleta de cores
    │   │   └── VisualMemoryPanel.svelte   # Preferencias visuais anteriores
    │   │
    │   ├── imagem/                   # Dominio imagem (AP-4)
    │   │   ├── ImageVariationGrid.svelte  # Grid 3 colunas de variacoes
    │   │   ├── ImageSlideAccordion.svelte # Accordion por slide
    │   │   ├── ImageZoomModal.svelte      # Modal fullscreen de imagem
    │   │   └── BrandGateStatus.svelte     # Status do Brand Gate (valido/revisao)
    │   │
    │   ├── export/                   # Dominio export
    │   │   ├── ScoreRadar.svelte          # Radar chart com 6 dimensoes do score
    │   │   ├── ScoreCard.svelte           # Card de 1 dimensao do score
    │   │   ├── SlidePreviewCarousel.svelte # Preview dos slides finais com navegacao
    │   │   └── ExportActions.svelte       # Botoes PDF, PNG, Drive
    │   │
    │   ├── home/                     # Dominio home (criar conteudo)
    │   │   ├── FormatoSelector.svelte     # Cards de formato (Carrossel, Post, Thumbnail)
    │   │   ├── DisciplinaSelector.svelte  # Existente, mover de carrossel/
    │   │   └── FotoCriadorGaleria.svelte  # Galeria de fotos do criador
    │   │
    │   ├── historico/                # Dominio historico
    │   │   ├── HistoricoCard.svelte       # Refatorar CarrosselCard existente
    │   │   └── HistoricoFiltros.svelte    # Novo — filtros multi-formato
    │   │
    │   ├── agente/                   # Dominio agente
    │   │   ├── AgenteCard.svelte          # Card de agente/skill
    │   │   ├── AgenteDetalhe.svelte       # Painel com system prompt
    │   │   └── PipelineVisual.svelte      # Diagrama visual do pipeline
    │   │
    │   ├── config/                   # Dominio config
    │   │   ├── ApiKeysForm.svelte         # Formulario de chaves
    │   │   ├── BrandPaletteForm.svelte    # Editor de brand palette
    │   │   ├── CreatorRegistryForm.svelte # CRUD de criadores
    │   │   ├── PlatformRulesForm.svelte   # Editor de regras de plataforma
    │   │   ├── DesignSystemManager.svelte # Upload/preview de design systems
    │   │   └── FotoManager.svelte         # Upload/selecao de fotos
    │   │
    │   └── carrossel/                # Dominio carrossel (legado, manter)
    │       ├── CarrosselActions.svelte     # Existente
    │       ├── SlideEditor.svelte         # Existente
    │       ├── SlideNavigation.svelte     # Existente
    │       ├── SlidePreview.svelte        # Existente
    │       └── TextoLivreInput.svelte     # Existente
    │
    ├── dtos/
    │   ├── PipelineDTO.ts            # Novo — pipeline completo
    │   ├── PipelineStepDTO.ts        # Novo — etapa do pipeline
    │   ├── BriefingDTO.ts            # Novo — briefing do Strategist
    │   ├── CopyDTO.ts               # Novo — copy do Copywriter
    │   ├── HookDTO.ts               # Novo — hook do Hook Specialist
    │   ├── PromptVisualDTO.ts        # Novo — prompts do Art Director
    │   ├── ImagemVariacaoDTO.ts      # Novo — variacao de imagem
    │   ├── ScoreDTO.ts              # Novo — score do Content Critic
    │   ├── HistoricoItemDTO.ts       # Novo — item do historico multi-formato
    │   ├── AgenteDTO.ts             # Novo — agente ou skill
    │   ├── BrandPaletteDTO.ts        # Novo — brand palette
    │   ├── CreatorEntryDTO.ts        # Novo — entrada do creator registry
    │   ├── PlatformRuleDTO.ts        # Novo — regra de plataforma
    │   ├── IniciarPipelineDTO.ts     # Novo — request para criar pipeline
    │   ├── carrossel.ts             # Existente (legado)
    │   └── config.ts                # Existente
    │
    ├── services/
    │   ├── PipelineService.ts        # Novo
    │   ├── BriefingService.ts        # Novo
    │   ├── CopyService.ts           # Novo
    │   ├── VisualService.ts          # Novo
    │   ├── ImagemService.ts          # Novo
    │   ├── ExportService.ts          # Novo
    │   ├── HistoricoService.ts       # Novo
    │   ├── AgenteService.ts          # Novo
    │   ├── ConfigService.ts          # Novo (refatorar config-service.ts)
    │   ├── carrossel-service.ts     # Existente (legado)
    │   └── config-service.ts        # Existente (legado, manter ate migrar)
    │
    ├── repositories/
    │   ├── PipelineRepository.ts     # Novo
    │   ├── BriefingRepository.ts     # Novo
    │   ├── CopyRepository.ts        # Novo
    │   ├── VisualRepository.ts       # Novo
    │   ├── ImagemRepository.ts       # Novo
    │   ├── ExportRepository.ts       # Novo
    │   ├── HistoricoRepository.ts    # Novo (refatorar historico-repository.ts)
    │   ├── AgenteRepository.ts       # Novo
    │   ├── ConfigRepository.ts       # Novo (refatorar config-repository.ts)
    │   ├── carrossel-repository.ts  # Existente (legado)
    │   ├── config-repository.ts     # Existente (legado, manter ate migrar)
    │   └── historico-repository.ts  # Existente (legado, manter ate migrar)
    │
    ├── mocks/
    │   ├── pipeline.mock.ts          # Novo
    │   ├── briefing.mock.ts          # Novo
    │   ├── copy.mock.ts             # Novo
    │   ├── visual.mock.ts            # Novo
    │   ├── imagem.mock.ts            # Novo
    │   ├── score.mock.ts             # Novo
    │   ├── historico.mock.ts         # Novo
    │   ├── agente.mock.ts            # Novo
    │   ├── config-brand.mock.ts      # Novo
    │   ├── config-creators.mock.ts   # Novo
    │   ├── config-platform.mock.ts   # Novo
    │   ├── carrossel-mock.ts        # Existente (legado)
    │   └── config-mock.ts           # Existente (legado)
    │
    ├── stores/
    │   ├── config.ts                # Existente (manter)
    │   ├── carrossel.ts             # Existente (legado)
    │   └── fotos.ts                 # Existente (manter)
    │
    ├── data/
    │   └── disciplinas.ts           # Existente (manter)
    │
    └── utils/
        ├── formatters.ts             # Novo — formatDate, formatScore, truncate
        └── validators.ts            # Novo — isValidUrl, isValidHex, isMinLength
```

---

## DTOs -- Codigo Completo

### PipelineDTO.ts

```typescript
// src/lib/dtos/PipelineDTO.ts

export type PipelineStatus = 'pendente' | 'em_execucao' | 'aguardando_aprovacao' | 'aprovado' | 'rejeitado' | 'erro' | 'cancelado';
export type FormatoConteudo = 'carrossel' | 'post_unico' | 'thumbnail_youtube';
export type EtapaPipeline = 'strategist' | 'copywriter' | 'hook_specialist' | 'art_director' | 'image_generator' | 'brand_gate' | 'content_critic';

export class PipelineDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly tema: string;
  readonly formato: FormatoConteudo;
  readonly status: PipelineStatus;
  readonly etapa_atual: EtapaPipeline;
  readonly modo_funil: boolean;
  readonly created_at: string;
  readonly updated_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.tema = data.tema ?? '';
    this.formato = data.formato ?? 'carrossel';
    this.status = data.status ?? 'pendente';
    this.etapa_atual = data.etapa_atual ?? 'strategist';
    this.modo_funil = data.modo_funil ?? false;
    this.created_at = data.created_at ?? '';
    this.updated_at = data.updated_at ?? '';
  }

  get etapaIndex(): number {
    const etapas: EtapaPipeline[] = [
      'strategist', 'copywriter', 'hook_specialist',
      'art_director', 'image_generator', 'brand_gate', 'content_critic'
    ];
    return etapas.indexOf(this.etapa_atual);
  }

  get etapaLabel(): string {
    const labels: Record<EtapaPipeline, string> = {
      strategist: 'Strategist',
      copywriter: 'Copywriter',
      hook_specialist: 'Hook Specialist',
      art_director: 'Art Director',
      image_generator: 'Image Generator',
      brand_gate: 'Brand Gate',
      content_critic: 'Content Critic'
    };
    return labels[this.etapa_atual] ?? this.etapa_atual;
  }

  get isAguardandoAprovacao(): boolean {
    return this.status === 'aguardando_aprovacao';
  }

  get isCompleto(): boolean {
    return this.etapa_atual === 'content_critic' && this.status === 'aprovado';
  }

  get formatoLabel(): string {
    const labels: Record<FormatoConteudo, string> = {
      carrossel: 'Carrossel',
      post_unico: 'Post Unico',
      thumbnail_youtube: 'Thumbnail YouTube'
    };
    return labels[this.formato] ?? this.formato;
  }

  isValid(): boolean {
    return this.id.length > 0 && this.tema.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      tenant_id: this.tenant_id,
      tema: this.tema,
      formato: this.formato,
      status: this.status,
      etapa_atual: this.etapa_atual,
      modo_funil: this.modo_funil
    };
  }
}
```

### PipelineStepDTO.ts

```typescript
// src/lib/dtos/PipelineStepDTO.ts

import type { PipelineStatus, EtapaPipeline } from './PipelineDTO';

export class PipelineStepDTO {
  readonly id: string;
  readonly pipeline_id: string;
  readonly agente: EtapaPipeline;
  readonly status: PipelineStatus;
  readonly entrada: Record<string, any>;
  readonly saida: Record<string, any>;
  readonly aprovado_por: string;
  readonly approved_at: string;
  readonly duracao_ms: number;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? '';
    this.pipeline_id = data.pipeline_id ?? '';
    this.agente = data.agente ?? 'strategist';
    this.status = data.status ?? 'pendente';
    this.entrada = data.entrada ?? {};
    this.saida = data.saida ?? {};
    this.aprovado_por = data.aprovado_por ?? '';
    this.approved_at = data.approved_at ?? '';
    this.duracao_ms = data.duracao_ms ?? 0;
  }

  get agenteLabel(): string {
    const labels: Record<EtapaPipeline, string> = {
      strategist: 'Strategist',
      copywriter: 'Copywriter',
      hook_specialist: 'Hook Specialist',
      art_director: 'Art Director',
      image_generator: 'Image Generator',
      brand_gate: 'Brand Gate',
      content_critic: 'Content Critic'
    };
    return labels[this.agente] ?? this.agente;
  }

  get duracaoFormatada(): string {
    if (this.duracao_ms < 1000) return `${this.duracao_ms}ms`;
    return `${(this.duracao_ms / 1000).toFixed(1)}s`;
  }

  get isPontoAprovacao(): boolean {
    return ['strategist', 'hook_specialist', 'art_director', 'brand_gate'].includes(this.agente);
  }

  get rotaAprovacao(): string | null {
    const rotas: Record<string, string> = {
      strategist: 'briefing',
      hook_specialist: 'copy',
      art_director: 'visual',
      brand_gate: 'imagem'
    };
    return rotas[this.agente] ?? null;
  }

  isValid(): boolean {
    return this.id.length > 0 && this.pipeline_id.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      pipeline_id: this.pipeline_id,
      agente: this.agente,
      status: this.status,
      entrada: this.entrada,
      saida: this.saida
    };
  }
}
```

### IniciarPipelineDTO.ts

```typescript
// src/lib/dtos/IniciarPipelineDTO.ts

import type { FormatoConteudo } from './PipelineDTO';

export class IniciarPipelineDTO {
  readonly tema: string;
  readonly formatos: FormatoConteudo[];
  readonly modo_funil: boolean;
  readonly modo_entrada: 'texto' | 'disciplina';
  readonly disciplina: string;
  readonly tecnologia: string;
  readonly tema_custom: string;
  readonly foto_criador_id: string;

  constructor(data: Record<string, any>) {
    this.tema = data.tema ?? '';
    this.formatos = data.formatos ?? [];
    this.modo_funil = data.modo_funil ?? false;
    this.modo_entrada = data.modo_entrada ?? 'texto';
    this.disciplina = data.disciplina ?? '';
    this.tecnologia = data.tecnologia ?? '';
    this.tema_custom = data.tema_custom ?? '';
    this.foto_criador_id = data.foto_criador_id ?? '';
  }

  get temaEfetivo(): string {
    if (this.modo_entrada === 'texto') return this.tema;
    const partes = [this.disciplina, this.tecnologia, this.tema_custom].filter(Boolean);
    return partes.join(' - ');
  }

  isValid(): boolean {
    if (this.formatos.length === 0) return false;
    if (this.modo_entrada === 'texto') return this.tema.trim().length >= 20;
    return this.disciplina.length > 0 && this.tecnologia.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      tema: this.temaEfetivo,
      formatos: this.formatos,
      modo_funil: this.modo_funil,
      foto_criador_id: this.foto_criador_id || undefined
    };
  }
}
```

### BriefingDTO.ts

```typescript
// src/lib/dtos/BriefingDTO.ts

export type EtapaFunil = 'topo' | 'meio' | 'fundo';

export interface PecaFunil {
  titulo: string;
  etapa_funil: EtapaFunil;
  formato: string;
}

export class BriefingDTO {
  readonly pipeline_id: string;
  readonly briefing_completo: string;
  readonly tema_original: string;
  readonly formato_alvo: string;
  readonly funil_etapa: EtapaFunil | null;
  readonly pecas_funil: PecaFunil[];
  readonly tendencias_usadas: string[];

  constructor(data: Record<string, any>) {
    this.pipeline_id = data.pipeline_id ?? '';
    this.briefing_completo = data.briefing_completo ?? '';
    this.tema_original = data.tema_original ?? '';
    this.formato_alvo = data.formato_alvo ?? '';
    this.funil_etapa = data.funil_etapa ?? null;
    this.pecas_funil = (data.pecas_funil ?? []).map((p: any) => ({
      titulo: p.titulo ?? '',
      etapa_funil: p.etapa_funil ?? 'topo',
      formato: p.formato ?? ''
    }));
    this.tendencias_usadas = data.tendencias_usadas ?? [];
  }

  get temFunil(): boolean {
    return this.pecas_funil.length > 0;
  }

  get totalPecas(): number {
    return this.pecas_funil.length;
  }

  isValid(): boolean {
    return this.pipeline_id.length > 0 && this.briefing_completo.trim().length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      pipeline_id: this.pipeline_id,
      briefing_completo: this.briefing_completo,
      pecas_funil: this.pecas_funil
    };
  }
}
```

### CopyDTO.ts

```typescript
// src/lib/dtos/CopyDTO.ts

export interface SlideItem {
  titulo: string;
  conteudo: string;
  tipo: string;
  ordem: number;
}

export class CopyDTO {
  readonly pipeline_id: string;
  readonly headline: string;
  readonly narrativa: string;
  readonly cta: string;
  readonly sequencia_slides: SlideItem[];

  constructor(data: Record<string, any>) {
    this.pipeline_id = data.pipeline_id ?? '';
    this.headline = data.headline ?? '';
    this.narrativa = data.narrativa ?? '';
    this.cta = data.cta ?? '';
    this.sequencia_slides = (data.sequencia_slides ?? []).map((s: any, i: number) => ({
      titulo: s.titulo ?? '',
      conteudo: s.conteudo ?? '',
      tipo: s.tipo ?? 'content',
      ordem: s.ordem ?? i
    }));
  }

  get totalSlides(): number {
    return this.sequencia_slides.length;
  }

  isValid(): boolean {
    return (
      this.pipeline_id.length > 0 &&
      this.headline.trim().length > 0 &&
      this.cta.trim().length > 0 &&
      this.sequencia_slides.length > 0
    );
  }

  toPayload(): Record<string, any> {
    return {
      pipeline_id: this.pipeline_id,
      headline: this.headline,
      narrativa: this.narrativa,
      cta: this.cta,
      sequencia_slides: this.sequencia_slides
    };
  }
}
```

### HookDTO.ts

```typescript
// src/lib/dtos/HookDTO.ts

export type HookOpcao = 'A' | 'B' | 'C';

export class HookDTO {
  readonly pipeline_id: string;
  readonly hook_a: string;
  readonly hook_b: string;
  readonly hook_c: string;
  readonly hook_selecionado: HookOpcao | null;

  constructor(data: Record<string, any>) {
    this.pipeline_id = data.pipeline_id ?? '';
    this.hook_a = data.hook_a ?? '';
    this.hook_b = data.hook_b ?? '';
    this.hook_c = data.hook_c ?? '';
    this.hook_selecionado = data.hook_selecionado ?? null;
  }

  get hookEscolhido(): string {
    if (!this.hook_selecionado) return '';
    const map: Record<HookOpcao, string> = {
      A: this.hook_a,
      B: this.hook_b,
      C: this.hook_c
    };
    return map[this.hook_selecionado];
  }

  get hooks(): { opcao: HookOpcao; texto: string }[] {
    return [
      { opcao: 'A', texto: this.hook_a },
      { opcao: 'B', texto: this.hook_b },
      { opcao: 'C', texto: this.hook_c }
    ];
  }

  isValid(): boolean {
    return (
      this.pipeline_id.length > 0 &&
      this.hook_a.length > 0 &&
      this.hook_b.length > 0 &&
      this.hook_c.length > 0 &&
      this.hook_selecionado !== null
    );
  }

  toPayload(): Record<string, any> {
    return {
      pipeline_id: this.pipeline_id,
      hook_selecionado: this.hook_selecionado
    };
  }
}
```

### PromptVisualDTO.ts

```typescript
// src/lib/dtos/PromptVisualDTO.ts

export interface PromptSlide {
  slide_index: number;
  titulo: string;
  prompt_imagem: string;
  modelo_sugerido: 'pro' | 'flash';
}

export class PromptVisualDTO {
  readonly pipeline_id: string;
  readonly prompts: PromptSlide[];

  constructor(data: Record<string, any>) {
    this.pipeline_id = data.pipeline_id ?? '';
    this.prompts = (data.prompts ?? []).map((p: any, i: number) => ({
      slide_index: p.slide_index ?? i,
      titulo: p.titulo ?? `Slide ${i + 1}`,
      prompt_imagem: p.prompt_imagem ?? '',
      modelo_sugerido: p.modelo_sugerido ?? 'flash'
    }));
  }

  get totalSlides(): number {
    return this.prompts.length;
  }

  get promptsPro(): PromptSlide[] {
    return this.prompts.filter(p => p.modelo_sugerido === 'pro');
  }

  isValid(): boolean {
    return (
      this.pipeline_id.length > 0 &&
      this.prompts.length > 0 &&
      this.prompts.every(p => p.prompt_imagem.trim().length >= 50)
    );
  }

  toPayload(): Record<string, any> {
    return {
      pipeline_id: this.pipeline_id,
      prompts: this.prompts.map(p => ({
        slide_index: p.slide_index,
        prompt_imagem: p.prompt_imagem,
        modelo_sugerido: p.modelo_sugerido
      }))
    };
  }
}
```

### ImagemVariacaoDTO.ts

```typescript
// src/lib/dtos/ImagemVariacaoDTO.ts

export type BrandGateStatus = 'valido' | 'revisao_manual' | 'pendente';

export interface VariacaoImagem {
  variacao_id: string;
  url: string;
  base64: string;
}

export interface SlideImagens {
  slide_index: number;
  titulo: string;
  variacoes: VariacaoImagem[];
  variacao_selecionada: string | null;
  brand_gate_status: BrandGateStatus;
  brand_gate_retries: number;
}

export class ImagemVariacaoDTO {
  readonly pipeline_id: string;
  readonly slides: SlideImagens[];

  constructor(data: Record<string, any>) {
    this.pipeline_id = data.pipeline_id ?? '';
    this.slides = (data.slides ?? []).map((s: any, i: number) => ({
      slide_index: s.slide_index ?? i,
      titulo: s.titulo ?? `Slide ${i + 1}`,
      variacoes: (s.variacoes ?? []).map((v: any) => ({
        variacao_id: v.variacao_id ?? '',
        url: v.url ?? '',
        base64: v.base64 ?? ''
      })),
      variacao_selecionada: s.variacao_selecionada ?? null,
      brand_gate_status: s.brand_gate_status ?? 'pendente',
      brand_gate_retries: s.brand_gate_retries ?? 0
    }));
  }

  get totalSlides(): number {
    return this.slides.length;
  }

  get slidesComRevisaoManual(): SlideImagens[] {
    return this.slides.filter(s => s.brand_gate_status === 'revisao_manual');
  }

  get todosSelecionados(): boolean {
    return this.slides.every(s => s.variacao_selecionada !== null);
  }

  isValid(): boolean {
    return (
      this.pipeline_id.length > 0 &&
      this.slides.length > 0 &&
      this.todosSelecionados
    );
  }

  toPayload(): Record<string, any> {
    return {
      pipeline_id: this.pipeline_id,
      selecoes: this.slides.map(s => ({
        slide_index: s.slide_index,
        variacao_selecionada: s.variacao_selecionada
      }))
    };
  }
}
```

### ScoreDTO.ts

```typescript
// src/lib/dtos/ScoreDTO.ts

export type ScoreDecision = 'approved' | 'needs_revision';

export class ScoreDTO {
  readonly pipeline_id: string;
  readonly clarity: number;
  readonly impact: number;
  readonly originality: number;
  readonly scroll_stop: number;
  readonly cta_strength: number;
  readonly final_score: number;
  readonly decision: ScoreDecision;
  readonly best_variation: string;

  constructor(data: Record<string, any>) {
    this.pipeline_id = data.pipeline_id ?? '';
    this.clarity = data.clarity ?? 0;
    this.impact = data.impact ?? 0;
    this.originality = data.originality ?? 0;
    this.scroll_stop = data.scroll_stop ?? 0;
    this.cta_strength = data.cta_strength ?? 0;
    this.final_score = data.final_score ?? 0;
    this.decision = data.decision ?? 'needs_revision';
    this.best_variation = data.best_variation ?? '';
  }

  get isAprovado(): boolean {
    return this.decision === 'approved';
  }

  get dimensoes(): { label: string; valor: number }[] {
    return [
      { label: 'Clareza', valor: this.clarity },
      { label: 'Impacto', valor: this.impact },
      { label: 'Originalidade', valor: this.originality },
      { label: 'Scroll Stop', valor: this.scroll_stop },
      { label: 'CTA Strength', valor: this.cta_strength },
      { label: 'Score Final', valor: this.final_score }
    ];
  }

  get scoreCor(): string {
    if (this.final_score >= 8) return 'text-green-500';
    if (this.final_score >= 7) return 'text-green-400';
    if (this.final_score >= 5) return 'text-yellow-500';
    return 'text-red-500';
  }

  isValid(): boolean {
    return this.pipeline_id.length > 0 && this.final_score >= 0 && this.final_score <= 10;
  }

  toPayload(): Record<string, any> {
    return {
      pipeline_id: this.pipeline_id,
      clarity: this.clarity,
      impact: this.impact,
      originality: this.originality,
      scroll_stop: this.scroll_stop,
      cta_strength: this.cta_strength,
      final_score: this.final_score,
      decision: this.decision,
      best_variation: this.best_variation
    };
  }
}
```

### HistoricoItemDTO.ts

```typescript
// src/lib/dtos/HistoricoItemDTO.ts

export class HistoricoItemDTO {
  readonly id: number;
  readonly pipeline_id: string;
  readonly titulo: string;
  readonly formato: string;
  readonly status: string;
  readonly disciplina: string;
  readonly tecnologia_principal: string;
  readonly total_slides: number;
  readonly final_score: number | null;
  readonly google_drive_link: string;
  readonly criado_em: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? 0;
    this.pipeline_id = data.pipeline_id ?? '';
    this.titulo = data.titulo ?? '';
    this.formato = data.formato ?? '';
    this.status = data.status ?? '';
    this.disciplina = data.disciplina ?? '';
    this.tecnologia_principal = data.tecnologia_principal ?? '';
    this.total_slides = data.total_slides ?? 0;
    this.final_score = data.final_score ?? null;
    this.google_drive_link = data.google_drive_link ?? '';
    this.criado_em = data.criado_em ?? '';
  }

  get temScore(): boolean {
    return this.final_score !== null;
  }

  get temDriveLink(): boolean {
    return this.google_drive_link.length > 0;
  }

  get isPipelineV3(): boolean {
    return this.pipeline_id.length > 0;
  }

  get dataFormatada(): string {
    if (!this.criado_em) return '';
    try {
      return new Date(this.criado_em).toLocaleDateString('pt-BR');
    } catch {
      return this.criado_em;
    }
  }

  isValid(): boolean {
    return this.id > 0 && this.titulo.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      pipeline_id: this.pipeline_id,
      titulo: this.titulo,
      formato: this.formato,
      status: this.status
    };
  }
}
```

### AgenteDTO.ts

```typescript
// src/lib/dtos/AgenteDTO.ts

export type TipoAgente = 'llm' | 'skill';

export class AgenteDTO {
  readonly slug: string;
  readonly nome: string;
  readonly descricao: string;
  readonly tipo: TipoAgente;
  readonly conteudo: string;

  constructor(data: Record<string, any>) {
    this.slug = data.slug ?? '';
    this.nome = data.nome ?? '';
    this.descricao = data.descricao ?? '';
    this.tipo = data.tipo ?? 'llm';
    this.conteudo = data.conteudo ?? '';
  }

  get isLLM(): boolean {
    return this.tipo === 'llm';
  }

  get isSkill(): boolean {
    return this.tipo === 'skill';
  }

  isValid(): boolean {
    return this.slug.length > 0 && this.nome.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      slug: this.slug,
      nome: this.nome,
      descricao: this.descricao,
      tipo: this.tipo,
      conteudo: this.conteudo
    };
  }
}
```

### BrandPaletteDTO.ts

```typescript
// src/lib/dtos/BrandPaletteDTO.ts

export class BrandPaletteDTO {
  readonly fundo_principal: string;
  readonly destaque_primario: string;
  readonly destaque_secundario: string;
  readonly texto_principal: string;
  readonly texto_secundario: string;
  readonly fonte: string;
  readonly elementos_obrigatorios: string[];
  readonly estilo: string;

  constructor(data: Record<string, any>) {
    const cores = data.cores ?? data;
    this.fundo_principal = cores.fundo_principal ?? '#0A0A0F';
    this.destaque_primario = cores.destaque_primario ?? '#A78BFA';
    this.destaque_secundario = cores.destaque_secundario ?? '#6D28D9';
    this.texto_principal = cores.texto_principal ?? '#FFFFFF';
    this.texto_secundario = cores.texto_secundario ?? '#94A3B8';
    this.fonte = data.fonte ?? 'Outfit';
    this.elementos_obrigatorios = data.elementos_obrigatorios ?? [];
    this.estilo = data.estilo ?? 'dark_mode_premium';
  }

  get coresArray(): { label: string; valor: string }[] {
    return [
      { label: 'Fundo Principal', valor: this.fundo_principal },
      { label: 'Destaque Primario', valor: this.destaque_primario },
      { label: 'Destaque Secundario', valor: this.destaque_secundario },
      { label: 'Texto Principal', valor: this.texto_principal },
      { label: 'Texto Secundario', valor: this.texto_secundario }
    ];
  }

  isValid(): boolean {
    return (
      this.fundo_principal.startsWith('#') &&
      this.destaque_primario.startsWith('#') &&
      this.fonte.length > 0
    );
  }

  toPayload(): Record<string, any> {
    return {
      cores: {
        fundo_principal: this.fundo_principal,
        destaque_primario: this.destaque_primario,
        destaque_secundario: this.destaque_secundario,
        texto_principal: this.texto_principal,
        texto_secundario: this.texto_secundario
      },
      fonte: this.fonte,
      elementos_obrigatorios: this.elementos_obrigatorios,
      estilo: this.estilo
    };
  }
}
```

### CreatorEntryDTO.ts

```typescript
// src/lib/dtos/CreatorEntryDTO.ts

export type FuncaoCriador = 'TECH_SOURCE' | 'EXPLAINER' | 'VIRAL_ENGINE' | 'THOUGHT_LEADER' | 'DINAMICAS';
export type PlataformaCriador = 'YouTube' | 'Twitter' | 'Blog' | 'dev.to' | 'HN';

export class CreatorEntryDTO {
  readonly id: string;
  readonly nome: string;
  readonly funcao: FuncaoCriador;
  readonly plataforma: PlataformaCriador;
  readonly url: string;
  readonly ativo: boolean;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? '';
    this.nome = data.nome ?? '';
    this.funcao = data.funcao ?? 'TECH_SOURCE';
    this.plataforma = data.plataforma ?? 'YouTube';
    this.url = data.url ?? '';
    this.ativo = data.ativo ?? true;
  }

  get funcaoLabel(): string {
    const labels: Record<FuncaoCriador, string> = {
      TECH_SOURCE: 'Fonte Tecnica',
      EXPLAINER: 'Explicador',
      VIRAL_ENGINE: 'Motor Viral',
      THOUGHT_LEADER: 'Lider de Opiniao',
      DINAMICAS: 'Dinamico'
    };
    return labels[this.funcao] ?? this.funcao;
  }

  isValid(): boolean {
    return this.nome.length > 0 && this.funcao.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      nome: this.nome,
      funcao: this.funcao,
      plataforma: this.plataforma,
      url: this.url,
      ativo: this.ativo
    };
  }
}
```

### PlatformRuleDTO.ts

```typescript
// src/lib/dtos/PlatformRuleDTO.ts

export class PlatformRuleDTO {
  readonly nome: string;
  readonly max_caracteres: number;
  readonly hashtags_max: number;
  readonly specs: string;

  constructor(data: Record<string, any>) {
    this.nome = data.nome ?? '';
    this.max_caracteres = data.max_caracteres ?? 0;
    this.hashtags_max = data.hashtags_max ?? 0;
    this.specs = data.specs ?? '';
  }

  isValid(): boolean {
    return this.nome.length > 0 && this.max_caracteres > 0;
  }

  toPayload(): Record<string, any> {
    return {
      nome: this.nome,
      max_caracteres: this.max_caracteres,
      hashtags_max: this.hashtags_max,
      specs: this.specs
    };
  }
}
```

---

## Services -- Codigo Completo

### PipelineService.ts

```typescript
// src/lib/services/PipelineService.ts

import { PipelineRepository } from '$lib/repositories/PipelineRepository';
import type { PipelineDTO } from '$lib/dtos/PipelineDTO';
import type { PipelineStepDTO } from '$lib/dtos/PipelineStepDTO';
import type { IniciarPipelineDTO } from '$lib/dtos/IniciarPipelineDTO';

export class PipelineService {
  static async iniciar(dto: IniciarPipelineDTO): Promise<PipelineDTO> {
    if (!dto.isValid()) throw new Error('Dados do pipeline invalidos');
    return PipelineRepository.iniciar(dto.toPayload());
  }

  static async buscarPorId(id: string): Promise<PipelineDTO> {
    if (!id) throw new Error('ID do pipeline e obrigatorio');
    return PipelineRepository.buscarPorId(id);
  }

  static async listarEtapas(pipelineId: string): Promise<PipelineStepDTO[]> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    const steps = await PipelineRepository.listarEtapas(pipelineId);
    return steps.filter(s => s.isValid());
  }

  static async cancelar(pipelineId: string): Promise<void> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return PipelineRepository.cancelar(pipelineId);
  }

  static async retomar(pipelineId: string): Promise<PipelineDTO> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return PipelineRepository.retomar(pipelineId);
  }
}
```

### BriefingService.ts

```typescript
// src/lib/services/BriefingService.ts

import { BriefingRepository } from '$lib/repositories/BriefingRepository';
import type { BriefingDTO } from '$lib/dtos/BriefingDTO';

export class BriefingService {
  static async buscar(pipelineId: string): Promise<BriefingDTO> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return BriefingRepository.buscar(pipelineId);
  }

  static async aprovar(dto: BriefingDTO): Promise<void> {
    if (!dto.isValid()) throw new Error('Briefing invalido');
    return BriefingRepository.aprovar(dto.toPayload());
  }

  static async rejeitar(pipelineId: string, feedback: string): Promise<void> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return BriefingRepository.rejeitar(pipelineId, feedback);
  }
}
```

### CopyService.ts

```typescript
// src/lib/services/CopyService.ts

import { CopyRepository } from '$lib/repositories/CopyRepository';
import type { CopyDTO } from '$lib/dtos/CopyDTO';
import type { HookDTO } from '$lib/dtos/HookDTO';

export class CopyService {
  static async buscarCopy(pipelineId: string): Promise<CopyDTO> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return CopyRepository.buscarCopy(pipelineId);
  }

  static async buscarHooks(pipelineId: string): Promise<HookDTO> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return CopyRepository.buscarHooks(pipelineId);
  }

  static async aprovar(copyPayload: Record<string, any>, hookPayload: Record<string, any>): Promise<void> {
    return CopyRepository.aprovar(copyPayload, hookPayload);
  }

  static async rejeitar(pipelineId: string, feedback: string): Promise<void> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return CopyRepository.rejeitar(pipelineId, feedback);
  }
}
```

### VisualService.ts

```typescript
// src/lib/services/VisualService.ts

import { VisualRepository } from '$lib/repositories/VisualRepository';
import type { PromptVisualDTO } from '$lib/dtos/PromptVisualDTO';
import type { BrandPaletteDTO } from '$lib/dtos/BrandPaletteDTO';

export class VisualService {
  static async buscarPrompts(pipelineId: string): Promise<PromptVisualDTO> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return VisualRepository.buscarPrompts(pipelineId);
  }

  static async buscarBrandPalette(): Promise<BrandPaletteDTO> {
    return VisualRepository.buscarBrandPalette();
  }

  static async aprovar(dto: PromptVisualDTO): Promise<void> {
    if (!dto.isValid()) throw new Error('Prompts visuais invalidos (minimo 50 caracteres cada)');
    return VisualRepository.aprovar(dto.toPayload());
  }

  static async rejeitar(pipelineId: string, feedback: string): Promise<void> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return VisualRepository.rejeitar(pipelineId, feedback);
  }
}
```

### ImagemService.ts

```typescript
// src/lib/services/ImagemService.ts

import { ImagemRepository } from '$lib/repositories/ImagemRepository';
import type { ImagemVariacaoDTO } from '$lib/dtos/ImagemVariacaoDTO';

export class ImagemService {
  static async buscarVariacoes(pipelineId: string): Promise<ImagemVariacaoDTO> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return ImagemRepository.buscarVariacoes(pipelineId);
  }

  static async aprovar(dto: ImagemVariacaoDTO): Promise<void> {
    if (!dto.isValid()) throw new Error('Selecione uma variacao para cada slide');
    return ImagemRepository.aprovar(dto.toPayload());
  }

  static async rejeitar(pipelineId: string): Promise<void> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return ImagemRepository.rejeitarTodas(pipelineId);
  }

  static async regerarVariacao(pipelineId: string, slideIndex: number, variacaoId: string): Promise<void> {
    return ImagemRepository.regerarVariacao(pipelineId, slideIndex, variacaoId);
  }
}
```

### ExportService.ts

```typescript
// src/lib/services/ExportService.ts

import { ExportRepository } from '$lib/repositories/ExportRepository';
import type { ScoreDTO } from '$lib/dtos/ScoreDTO';

export class ExportService {
  static async buscarScore(pipelineId: string): Promise<ScoreDTO> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return ExportRepository.buscarScore(pipelineId);
  }

  static async buscarSlidesFinais(pipelineId: string): Promise<{ titulo: string; slides: string[] }> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return ExportRepository.buscarSlidesFinais(pipelineId);
  }

  static async exportarPdf(slides: { imageBase64?: string }[], title: string): Promise<void> {
    const comImagem = slides.filter(s => s.imageBase64);
    if (comImagem.length === 0) throw new Error('Nenhuma imagem para exportar');

    const { jsPDF } = await import('jspdf');
    const pdf = new jsPDF({ orientation: 'portrait', unit: 'px', format: [1080, 1350] });
    let first = true;
    for (const slide of comImagem) {
      if (!first) pdf.addPage([1080, 1350]);
      pdf.addImage(slide.imageBase64!, 'PNG', 0, 0, 1080, 1350);
      first = false;
    }
    pdf.save(`${title || 'conteudo'}.pdf`);
  }

  static async salvarNoDrive(pipelineId: string): Promise<string> {
    if (!pipelineId) throw new Error('ID do pipeline e obrigatorio');
    return ExportRepository.salvarNoDrive(pipelineId);
  }
}
```

### HistoricoService.ts

```typescript
// src/lib/services/HistoricoService.ts

import { HistoricoRepository as HistoricoRepo } from '$lib/repositories/HistoricoRepository';
import type { HistoricoItemDTO } from '$lib/dtos/HistoricoItemDTO';

export class HistoricoService {
  static async listar(): Promise<HistoricoItemDTO[]> {
    const items = await HistoricoRepo.listar();
    return items.filter(i => i.isValid());
  }

  static async remover(id: number): Promise<void> {
    if (!id || id <= 0) throw new Error('ID invalido');
    return HistoricoRepo.remover(id);
  }
}
```

### AgenteService.ts

```typescript
// src/lib/services/AgenteService.ts

import { AgenteRepository } from '$lib/repositories/AgenteRepository';
import type { AgenteDTO } from '$lib/dtos/AgenteDTO';

export class AgenteService {
  static async listarTodos(): Promise<AgenteDTO[]> {
    const agentes = await AgenteRepository.listar();
    return agentes.filter(a => a.isValid());
  }

  static async listarLLM(): Promise<AgenteDTO[]> {
    const todos = await AgenteService.listarTodos();
    return todos.filter(a => a.isLLM);
  }

  static async listarSkills(): Promise<AgenteDTO[]> {
    const todos = await AgenteService.listarTodos();
    return todos.filter(a => a.isSkill);
  }
}
```

### ConfigService.ts (novo, substitui config-service.ts)

```typescript
// src/lib/services/ConfigService.ts

import { ConfigRepository } from '$lib/repositories/ConfigRepository';
import type { BrandPaletteDTO } from '$lib/dtos/BrandPaletteDTO';
import type { CreatorEntryDTO } from '$lib/dtos/CreatorEntryDTO';
import type { PlatformRuleDTO } from '$lib/dtos/PlatformRuleDTO';

export class ConfigService {
  static async carregarStatus(): Promise<Record<string, any>> {
    return ConfigRepository.getStatus();
  }

  static async salvarApiKeys(payload: Record<string, string>): Promise<void> {
    if (Object.keys(payload).length === 0) throw new Error('Nenhuma chave para salvar');
    return ConfigRepository.salvarApiKeys(payload);
  }

  static async buscarBrandPalette(): Promise<BrandPaletteDTO> {
    return ConfigRepository.buscarBrandPalette();
  }

  static async salvarBrandPalette(dto: BrandPaletteDTO): Promise<void> {
    if (!dto.isValid()) throw new Error('Brand palette invalida');
    return ConfigRepository.salvarBrandPalette(dto.toPayload());
  }

  static async listarCriadores(): Promise<CreatorEntryDTO[]> {
    const criadores = await ConfigRepository.listarCriadores();
    return criadores.filter(c => c.isValid());
  }

  static async salvarCriadores(criadores: CreatorEntryDTO[]): Promise<void> {
    const payloads = criadores.map(c => c.toPayload());
    return ConfigRepository.salvarCriadores(payloads);
  }

  static async buscarPlatformRules(): Promise<PlatformRuleDTO[]> {
    const rules = await ConfigRepository.buscarPlatformRules();
    return rules.filter(r => r.isValid());
  }

  static async salvarPlatformRules(rules: PlatformRuleDTO[]): Promise<void> {
    const payloads = rules.map(r => r.toPayload());
    return ConfigRepository.salvarPlatformRules(payloads);
  }
}
```

---

## Repositories -- Codigo Completo

### PipelineRepository.ts

```typescript
// src/lib/repositories/PipelineRepository.ts

import { browser } from '$app/environment';
import { PipelineDTO } from '$lib/dtos/PipelineDTO';
import { PipelineStepDTO } from '$lib/dtos/PipelineStepDTO';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class PipelineRepository {
  static async iniciar(payload: Record<string, any>): Promise<PipelineDTO> {
    if (USE_MOCK) {
      const { pipelineMock } = await import('$lib/mocks/pipeline.mock');
      await new Promise(r => setTimeout(r, 500));
      return new PipelineDTO(pipelineMock(payload));
    }
    const res = await fetch(`${API_BASE}/api/pipeline`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) {
      const data = await res.json();
      throw new Error(data.detail || 'Erro ao iniciar pipeline');
    }
    const data = await res.json();
    return new PipelineDTO(data);
  }

  static async buscarPorId(id: string): Promise<PipelineDTO> {
    if (USE_MOCK) {
      const { pipelineDetalhesMock } = await import('$lib/mocks/pipeline.mock');
      await new Promise(r => setTimeout(r, 300));
      return new PipelineDTO(pipelineDetalhesMock(id));
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${id}`);
    if (!res.ok) throw new Error('Pipeline nao encontrado');
    const data = await res.json();
    return new PipelineDTO(data);
  }

  static async listarEtapas(pipelineId: string): Promise<PipelineStepDTO[]> {
    if (USE_MOCK) {
      const { pipelineStepsMock } = await import('$lib/mocks/pipeline.mock');
      await new Promise(r => setTimeout(r, 300));
      return pipelineStepsMock(pipelineId).map((s: any) => new PipelineStepDTO(s));
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/steps`);
    if (!res.ok) throw new Error('Erro ao carregar etapas');
    const data = await res.json();
    return data.map((s: any) => new PipelineStepDTO(s));
  }

  static async cancelar(pipelineId: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/cancelar`, { method: 'POST' });
    if (!res.ok) throw new Error('Erro ao cancelar pipeline');
  }

  static async retomar(pipelineId: string): Promise<PipelineDTO> {
    if (USE_MOCK) {
      const { pipelineDetalhesMock } = await import('$lib/mocks/pipeline.mock');
      await new Promise(r => setTimeout(r, 300));
      return new PipelineDTO(pipelineDetalhesMock(pipelineId));
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/retomar`, { method: 'POST' });
    if (!res.ok) throw new Error('Erro ao retomar pipeline');
    const data = await res.json();
    return new PipelineDTO(data);
  }
}
```

### BriefingRepository.ts

```typescript
// src/lib/repositories/BriefingRepository.ts

import { browser } from '$app/environment';
import { BriefingDTO } from '$lib/dtos/BriefingDTO';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class BriefingRepository {
  static async buscar(pipelineId: string): Promise<BriefingDTO> {
    if (USE_MOCK) {
      const { briefingMock } = await import('$lib/mocks/briefing.mock');
      await new Promise(r => setTimeout(r, 300));
      return new BriefingDTO(briefingMock(pipelineId));
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/briefing`);
    if (!res.ok) throw new Error('Erro ao carregar briefing');
    const data = await res.json();
    return new BriefingDTO(data);
  }

  static async aprovar(payload: Record<string, any>): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${payload.pipeline_id}/briefing/aprovar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Erro ao aprovar briefing');
  }

  static async rejeitar(pipelineId: string, feedback: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/briefing/rejeitar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback })
    });
    if (!res.ok) throw new Error('Erro ao rejeitar briefing');
  }
}
```

### CopyRepository.ts

```typescript
// src/lib/repositories/CopyRepository.ts

import { browser } from '$app/environment';
import { CopyDTO } from '$lib/dtos/CopyDTO';
import { HookDTO } from '$lib/dtos/HookDTO';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class CopyRepository {
  static async buscarCopy(pipelineId: string): Promise<CopyDTO> {
    if (USE_MOCK) {
      const { copyMock } = await import('$lib/mocks/copy.mock');
      await new Promise(r => setTimeout(r, 300));
      return new CopyDTO(copyMock(pipelineId));
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/copy`);
    if (!res.ok) throw new Error('Erro ao carregar copy');
    const data = await res.json();
    return new CopyDTO(data);
  }

  static async buscarHooks(pipelineId: string): Promise<HookDTO> {
    if (USE_MOCK) {
      const { hooksMock } = await import('$lib/mocks/copy.mock');
      await new Promise(r => setTimeout(r, 200));
      return new HookDTO(hooksMock(pipelineId));
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/hooks`);
    if (!res.ok) throw new Error('Erro ao carregar hooks');
    const data = await res.json();
    return new HookDTO(data);
  }

  static async aprovar(copyPayload: Record<string, any>, hookPayload: Record<string, any>): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }
    const pipelineId = copyPayload.pipeline_id;
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/copy/aprovar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ ...copyPayload, ...hookPayload })
    });
    if (!res.ok) throw new Error('Erro ao aprovar copy');
  }

  static async rejeitar(pipelineId: string, feedback: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/copy/rejeitar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback })
    });
    if (!res.ok) throw new Error('Erro ao rejeitar copy');
  }
}
```

### VisualRepository.ts

```typescript
// src/lib/repositories/VisualRepository.ts

import { browser } from '$app/environment';
import { PromptVisualDTO } from '$lib/dtos/PromptVisualDTO';
import { BrandPaletteDTO } from '$lib/dtos/BrandPaletteDTO';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class VisualRepository {
  static async buscarPrompts(pipelineId: string): Promise<PromptVisualDTO> {
    if (USE_MOCK) {
      const { promptsVisualMock } = await import('$lib/mocks/visual.mock');
      await new Promise(r => setTimeout(r, 300));
      return new PromptVisualDTO(promptsVisualMock(pipelineId));
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/visual`);
    if (!res.ok) throw new Error('Erro ao carregar prompts visuais');
    const data = await res.json();
    return new PromptVisualDTO(data);
  }

  static async buscarBrandPalette(): Promise<BrandPaletteDTO> {
    if (USE_MOCK) {
      const { brandPaletteMock } = await import('$lib/mocks/config-brand.mock');
      await new Promise(r => setTimeout(r, 100));
      return new BrandPaletteDTO(brandPaletteMock());
    }
    const res = await fetch(`${API_BASE}/api/config/brand-palette`);
    if (!res.ok) throw new Error('Erro ao carregar brand palette');
    const data = await res.json();
    return new BrandPaletteDTO(data);
  }

  static async aprovar(payload: Record<string, any>): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${payload.pipeline_id}/visual/aprovar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Erro ao aprovar prompts visuais');
  }

  static async rejeitar(pipelineId: string, feedback: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/visual/rejeitar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback })
    });
    if (!res.ok) throw new Error('Erro ao rejeitar prompts visuais');
  }
}
```

### ImagemRepository.ts

```typescript
// src/lib/repositories/ImagemRepository.ts

import { browser } from '$app/environment';
import { ImagemVariacaoDTO } from '$lib/dtos/ImagemVariacaoDTO';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class ImagemRepository {
  static async buscarVariacoes(pipelineId: string): Promise<ImagemVariacaoDTO> {
    if (USE_MOCK) {
      const { imagemVariacoesMock } = await import('$lib/mocks/imagem.mock');
      await new Promise(r => setTimeout(r, 500));
      return new ImagemVariacaoDTO(imagemVariacoesMock(pipelineId));
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/imagens`);
    if (!res.ok) throw new Error('Erro ao carregar variacoes de imagem');
    const data = await res.json();
    return new ImagemVariacaoDTO(data);
  }

  static async aprovar(payload: Record<string, any>): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${payload.pipeline_id}/imagens/aprovar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Erro ao aprovar imagens');
  }

  static async rejeitarTodas(pipelineId: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 300));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/imagens/rejeitar`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Erro ao rejeitar imagens');
  }

  static async regerarVariacao(pipelineId: string, slideIndex: number, variacaoId: string): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 500));
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/imagens/regerar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ slide_index: slideIndex, variacao_id: variacaoId })
    });
    if (!res.ok) throw new Error('Erro ao regerar variacao');
  }
}
```

### ExportRepository.ts

```typescript
// src/lib/repositories/ExportRepository.ts

import { browser } from '$app/environment';
import { ScoreDTO } from '$lib/dtos/ScoreDTO';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class ExportRepository {
  static async buscarScore(pipelineId: string): Promise<ScoreDTO> {
    if (USE_MOCK) {
      const { scoreMock } = await import('$lib/mocks/score.mock');
      await new Promise(r => setTimeout(r, 300));
      return new ScoreDTO(scoreMock(pipelineId));
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/score`);
    if (!res.ok) throw new Error('Erro ao carregar score');
    const data = await res.json();
    return new ScoreDTO(data);
  }

  static async buscarSlidesFinais(pipelineId: string): Promise<{ titulo: string; slides: string[] }> {
    if (USE_MOCK) {
      const { slidesFinaisMock } = await import('$lib/mocks/score.mock');
      await new Promise(r => setTimeout(r, 200));
      return slidesFinaisMock(pipelineId);
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/export`);
    if (!res.ok) throw new Error('Erro ao carregar slides finais');
    return res.json();
  }

  static async salvarNoDrive(pipelineId: string): Promise<string> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 500));
      return 'https://drive.google.com/drive/folders/mock-folder-id';
    }
    const res = await fetch(`${API_BASE}/api/pipeline/${pipelineId}/drive`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Erro ao salvar no Drive');
    const data = await res.json();
    return data.web_view_link;
  }
}
```

### HistoricoRepository.ts (novo)

```typescript
// src/lib/repositories/HistoricoRepository.ts

import { browser } from '$app/environment';
import { HistoricoItemDTO } from '$lib/dtos/HistoricoItemDTO';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class HistoricoRepository {
  static async listar(): Promise<HistoricoItemDTO[]> {
    if (USE_MOCK) {
      const { historicoMock } = await import('$lib/mocks/historico.mock');
      await new Promise(r => setTimeout(r, 300));
      return historicoMock().map((h: any) => new HistoricoItemDTO(h));
    }
    const res = await fetch(`${API_BASE}/api/historico`);
    if (!res.ok) throw new Error('Erro ao carregar historico');
    const data = await res.json();
    return data.map((h: any) => new HistoricoItemDTO(h));
  }

  static async remover(id: number): Promise<void> {
    if (USE_MOCK) {
      await new Promise(r => setTimeout(r, 200));
      return;
    }
    const res = await fetch(`${API_BASE}/api/historico/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Erro ao remover item');
  }
}
```

### AgenteRepository.ts

```typescript
// src/lib/repositories/AgenteRepository.ts

import { browser } from '$app/environment';
import { AgenteDTO } from '$lib/dtos/AgenteDTO';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class AgenteRepository {
  static async listar(): Promise<AgenteDTO[]> {
    if (USE_MOCK) {
      const { agentesMock } = await import('$lib/mocks/agente.mock');
      await new Promise(r => setTimeout(r, 300));
      return agentesMock().map((a: any) => new AgenteDTO(a));
    }
    const res = await fetch(`${API_BASE}/api/agentes`);
    if (!res.ok) throw new Error('Erro ao carregar agentes');
    const data = await res.json();
    return data.map((a: any) => new AgenteDTO(a));
  }
}
```

### ConfigRepository.ts (novo)

```typescript
// src/lib/repositories/ConfigRepository.ts

import { browser } from '$app/environment';
import { BrandPaletteDTO } from '$lib/dtos/BrandPaletteDTO';
import { CreatorEntryDTO } from '$lib/dtos/CreatorEntryDTO';
import { PlatformRuleDTO } from '$lib/dtos/PlatformRuleDTO';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class ConfigRepository {
  static async getStatus(): Promise<Record<string, any>> {
    if (USE_MOCK) {
      const { configStatusMock } = await import('$lib/mocks/config-mock');
      await new Promise(r => setTimeout(r, 100));
      return configStatusMock();
    }
    const res = await fetch(`${API_BASE}/api/config`);
    if (!res.ok) throw new Error('Erro ao buscar status');
    return res.json();
  }

  static async salvarApiKeys(payload: Record<string, string>): Promise<void> {
    if (USE_MOCK) return;
    const res = await fetch(`${API_BASE}/api/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Erro ao salvar API keys');
  }

  static async buscarBrandPalette(): Promise<BrandPaletteDTO> {
    if (USE_MOCK) {
      const { brandPaletteMock } = await import('$lib/mocks/config-brand.mock');
      await new Promise(r => setTimeout(r, 100));
      return new BrandPaletteDTO(brandPaletteMock());
    }
    const res = await fetch(`${API_BASE}/api/config/brand-palette`);
    if (!res.ok) throw new Error('Erro ao carregar brand palette');
    const data = await res.json();
    return new BrandPaletteDTO(data);
  }

  static async salvarBrandPalette(payload: Record<string, any>): Promise<void> {
    if (USE_MOCK) return;
    const res = await fetch(`${API_BASE}/api/config/brand-palette`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Erro ao salvar brand palette');
  }

  static async listarCriadores(): Promise<CreatorEntryDTO[]> {
    if (USE_MOCK) {
      const { criadoresMock } = await import('$lib/mocks/config-creators.mock');
      await new Promise(r => setTimeout(r, 200));
      return criadoresMock().map((c: any) => new CreatorEntryDTO(c));
    }
    const res = await fetch(`${API_BASE}/api/config/creator-registry`);
    if (!res.ok) throw new Error('Erro ao carregar criadores');
    const data = await res.json();
    return data.map((c: any) => new CreatorEntryDTO(c));
  }

  static async salvarCriadores(payloads: Record<string, any>[]): Promise<void> {
    if (USE_MOCK) return;
    const res = await fetch(`${API_BASE}/api/config/creator-registry`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payloads)
    });
    if (!res.ok) throw new Error('Erro ao salvar criadores');
  }

  static async buscarPlatformRules(): Promise<PlatformRuleDTO[]> {
    if (USE_MOCK) {
      const { platformRulesMock } = await import('$lib/mocks/config-platform.mock');
      await new Promise(r => setTimeout(r, 100));
      return platformRulesMock().map((r: any) => new PlatformRuleDTO(r));
    }
    const res = await fetch(`${API_BASE}/api/config/platform-rules`);
    if (!res.ok) throw new Error('Erro ao carregar platform rules');
    const data = await res.json();
    return data.map((r: any) => new PlatformRuleDTO(r));
  }

  static async salvarPlatformRules(payloads: Record<string, any>[]): Promise<void> {
    if (USE_MOCK) return;
    const res = await fetch(`${API_BASE}/api/config/platform-rules`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payloads)
    });
    if (!res.ok) throw new Error('Erro ao salvar platform rules');
  }
}
```

---

## Estrutura das Paginas (+page.svelte)

### Home / Criar Conteudo (`/+page.svelte`)

```svelte
<script lang="ts">
  import { goto } from '$app/navigation';
  import { IniciarPipelineDTO } from '$lib/dtos/IniciarPipelineDTO';
  import { PipelineService } from '$lib/services/PipelineService';
  import FormatoSelector from '$lib/components/home/FormatoSelector.svelte';
  import DisciplinaSelector from '$lib/components/home/DisciplinaSelector.svelte';
  import FotoCriadorGaleria from '$lib/components/home/FotoCriadorGaleria.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Banner from '$lib/components/ui/Banner.svelte';
  import Toggle from '$lib/components/ui/Toggle.svelte';

  // Estado do formulario
  let modo = $state<'texto' | 'disciplina'>('texto');
  let tema = $state('');
  let formatosSelecionados = $state<string[]>([]);
  let modoFunil = $state(false);
  let disciplina = $state('');
  let tecnologia = $state('');
  let temaCustom = $state('');
  let fotoCriadorId = $state('');

  let loading = $state(false);
  let erro = $state('');

  const dto = $derived(new IniciarPipelineDTO({
    tema,
    formatos: formatosSelecionados,
    modo_funil: modoFunil,
    modo_entrada: modo,
    disciplina,
    tecnologia,
    tema_custom: temaCustom,
    foto_criador_id: fotoCriadorId
  }));

  const podeCriar = $derived(dto.isValid());

  async function iniciarPipeline() {
    if (!podeCriar) return;
    loading = true;
    erro = '';
    try {
      const pipeline = await PipelineService.iniciar(dto);
      goto(`/pipeline/${pipeline.id}`);
    } catch (e: any) {
      erro = e.message;
    } finally {
      loading = false;
    }
  }
</script>

<!-- Layout: FormatoSelector + Toggle funil + Tabs texto/disciplina + tema + foto + botao -->
```

### Pipeline Wizard (`/pipeline/[id]/+page.svelte`)

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { PipelineService } from '$lib/services/PipelineService';
  import type { PipelineDTO } from '$lib/dtos/PipelineDTO';
  import type { PipelineStepDTO } from '$lib/dtos/PipelineStepDTO';
  import PipelineWizard from '$lib/components/pipeline/PipelineWizard.svelte';
  import Banner from '$lib/components/ui/Banner.svelte';
  import Spinner from '$lib/components/ui/Spinner.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';

  const pipelineId = $derived($page.params.id);

  let pipeline = $state<PipelineDTO | null>(null);
  let steps = $state<PipelineStepDTO[]>([]);
  let loading = $state(true);
  let erro = $state('');
  let modalCancelar = $state(false);

  // Polling para atualizar status (a cada 3s quando em execucao)
  let pollingInterval: ReturnType<typeof setInterval> | null = null;

  async function carregarPipeline() {
    try {
      [pipeline, steps] = await Promise.all([
        PipelineService.buscarPorId(pipelineId),
        PipelineService.listarEtapas(pipelineId)
      ]);
    } catch (e: any) {
      erro = e.message;
    } finally {
      loading = false;
    }
  }

  function navegarAprovacao(rota: string) {
    goto(`/pipeline/${pipelineId}/${rota}`);
  }

  async function cancelarPipeline() {
    await PipelineService.cancelar(pipelineId);
    goto('/historico');
  }

  async function retomarPipeline() {
    pipeline = await PipelineService.retomar(pipelineId);
  }

  // Carrega ao montar
  $effect(() => {
    carregarPipeline();
    return () => { if (pollingInterval) clearInterval(pollingInterval); };
  });
</script>

<!-- Layout: Wizard vertical com 7 etapas, botoes de acao contextual -->
```

### Aprovacao de Briefing AP-1 (`/pipeline/[id]/briefing/+page.svelte`)

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { BriefingService } from '$lib/services/BriefingService';
  import { BriefingDTO } from '$lib/dtos/BriefingDTO';
  import BriefingEditor from '$lib/components/briefing/BriefingEditor.svelte';
  import FunilPlanner from '$lib/components/briefing/FunilPlanner.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const pipelineId = $derived($page.params.id);

  let briefing = $state<BriefingDTO | null>(null);
  let briefingEditado = $state('');
  let loading = $state(true);
  let salvando = $state(false);
  let erro = $state('');

  async function carregarBriefing() {
    try {
      briefing = await BriefingService.buscar(pipelineId);
      briefingEditado = briefing.briefing_completo;
    } catch (e: any) {
      erro = e.message;
    } finally {
      loading = false;
    }
  }

  async function aprovar() {
    if (!briefing) return;
    salvando = true;
    try {
      const dtoEditado = new BriefingDTO({
        ...briefing.toPayload(),
        briefing_completo: briefingEditado
      });
      await BriefingService.aprovar(dtoEditado);
      goto(`/pipeline/${pipelineId}`);
    } catch (e: any) {
      erro = e.message;
    } finally {
      salvando = false;
    }
  }

  async function rejeitar() {
    salvando = true;
    try {
      await BriefingService.rejeitar(pipelineId, 'Regenerar com ajustes');
      carregarBriefing();
    } catch (e: any) {
      erro = e.message;
    } finally {
      salvando = false;
    }
  }

  $effect(() => { carregarBriefing(); });
</script>
```

### Aprovacao de Copy + Hook AP-2 (`/pipeline/[id]/copy/+page.svelte`)

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { CopyService } from '$lib/services/CopyService';
  import { CopyDTO } from '$lib/dtos/CopyDTO';
  import { HookDTO } from '$lib/dtos/HookDTO';
  import CopyEditor from '$lib/components/copy/CopyEditor.svelte';
  import HookSelector from '$lib/components/copy/HookSelector.svelte';
  import SlideSequenceEditor from '$lib/components/copy/SlideSequenceEditor.svelte';
  import ToneGuideAlerts from '$lib/components/copy/ToneGuideAlerts.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const pipelineId = $derived($page.params.id);

  let copy = $state<CopyDTO | null>(null);
  let hooks = $state<HookDTO | null>(null);
  let hookSelecionado = $state<'A' | 'B' | 'C' | null>(null);
  let headlineEditado = $state('');
  let narrativaEditada = $state('');
  let ctaEditado = $state('');
  let loading = $state(true);
  let salvando = $state(false);
  let erro = $state('');

  async function carregar() {
    try {
      [copy, hooks] = await Promise.all([
        CopyService.buscarCopy(pipelineId),
        CopyService.buscarHooks(pipelineId)
      ]);
      headlineEditado = copy.headline;
      narrativaEditada = copy.narrativa;
      ctaEditado = copy.cta;
    } catch (e: any) {
      erro = e.message;
    } finally {
      loading = false;
    }
  }

  async function aprovar() {
    if (!copy || !hookSelecionado) return;
    salvando = true;
    try {
      const copyEditado = new CopyDTO({
        pipeline_id: pipelineId,
        headline: headlineEditado,
        narrativa: narrativaEditada,
        cta: ctaEditado,
        sequencia_slides: copy.sequencia_slides
      });
      const hookEditado = new HookDTO({
        pipeline_id: pipelineId,
        hook_a: hooks!.hook_a,
        hook_b: hooks!.hook_b,
        hook_c: hooks!.hook_c,
        hook_selecionado: hookSelecionado
      });
      await CopyService.aprovar(copyEditado.toPayload(), hookEditado.toPayload());
      goto(`/pipeline/${pipelineId}`);
    } catch (e: any) {
      erro = e.message;
    } finally {
      salvando = false;
    }
  }

  $effect(() => { carregar(); });
</script>
```

### Aprovacao de Prompt Visual AP-3 (`/pipeline/[id]/visual/+page.svelte`)

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { VisualService } from '$lib/services/VisualService';
  import { PromptVisualDTO } from '$lib/dtos/PromptVisualDTO';
  import type { BrandPaletteDTO } from '$lib/dtos/BrandPaletteDTO';
  import PromptSlideList from '$lib/components/visual/PromptSlideList.svelte';
  import BrandPalettePreview from '$lib/components/visual/BrandPalettePreview.svelte';
  import VisualMemoryPanel from '$lib/components/visual/VisualMemoryPanel.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const pipelineId = $derived($page.params.id);

  let prompts = $state<PromptVisualDTO | null>(null);
  let brandPalette = $state<BrandPaletteDTO | null>(null);
  let loading = $state(true);
  let salvando = $state(false);
  let erro = $state('');

  async function carregar() {
    try {
      [prompts, brandPalette] = await Promise.all([
        VisualService.buscarPrompts(pipelineId),
        VisualService.buscarBrandPalette()
      ]);
    } catch (e: any) {
      erro = e.message;
    } finally {
      loading = false;
    }
  }

  async function aprovar() {
    if (!prompts) return;
    salvando = true;
    try {
      await VisualService.aprovar(prompts);
      goto(`/pipeline/${pipelineId}`);
    } catch (e: any) {
      erro = e.message;
    } finally {
      salvando = false;
    }
  }

  $effect(() => { carregar(); });
</script>
```

### Aprovacao de Imagem AP-4 (`/pipeline/[id]/imagem/+page.svelte`)

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { ImagemService } from '$lib/services/ImagemService';
  import { ImagemVariacaoDTO } from '$lib/dtos/ImagemVariacaoDTO';
  import ImageSlideAccordion from '$lib/components/imagem/ImageSlideAccordion.svelte';
  import ImageZoomModal from '$lib/components/imagem/ImageZoomModal.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const pipelineId = $derived($page.params.id);

  let variacoes = $state<ImagemVariacaoDTO | null>(null);
  let imagemZoom = $state<string | null>(null);
  let loading = $state(true);
  let salvando = $state(false);
  let erro = $state('');

  const podeAprovar = $derived(variacoes?.todosSelecionados ?? false);

  async function carregar() {
    try {
      variacoes = await ImagemService.buscarVariacoes(pipelineId);
    } catch (e: any) {
      erro = e.message;
    } finally {
      loading = false;
    }
  }

  async function aprovar() {
    if (!variacoes || !podeAprovar) return;
    salvando = true;
    try {
      await ImagemService.aprovar(variacoes);
      goto(`/pipeline/${pipelineId}`);
    } catch (e: any) {
      erro = e.message;
    } finally {
      salvando = false;
    }
  }

  $effect(() => { carregar(); });
</script>
```

### Preview e Export (`/pipeline/[id]/export/+page.svelte`)

```svelte
<script lang="ts">
  import { page } from '$app/stores';
  import { ExportService } from '$lib/services/ExportService';
  import type { ScoreDTO } from '$lib/dtos/ScoreDTO';
  import ScoreRadar from '$lib/components/export/ScoreRadar.svelte';
  import ScoreCard from '$lib/components/export/ScoreCard.svelte';
  import SlidePreviewCarousel from '$lib/components/export/SlidePreviewCarousel.svelte';
  import ExportActions from '$lib/components/export/ExportActions.svelte';
  import Banner from '$lib/components/ui/Banner.svelte';

  const pipelineId = $derived($page.params.id);

  let score = $state<ScoreDTO | null>(null);
  let slides = $state<string[]>([]);
  let titulo = $state('');
  let loading = $state(true);
  let erro = $state('');
  let driveSalvo = $state(false);
  let driveLink = $state('');

  async function carregar() {
    try {
      const [scoreResult, slidesResult] = await Promise.all([
        ExportService.buscarScore(pipelineId),
        ExportService.buscarSlidesFinais(pipelineId)
      ]);
      score = scoreResult;
      slides = slidesResult.slides;
      titulo = slidesResult.titulo;
    } catch (e: any) {
      erro = e.message;
    } finally {
      loading = false;
    }
  }

  async function salvarDrive() {
    try {
      driveLink = await ExportService.salvarNoDrive(pipelineId);
      driveSalvo = true;
    } catch (e: any) {
      erro = e.message;
    }
  }

  $effect(() => { carregar(); });
</script>
```

---

## Design Tokens Necessarios (app.css)

Adicionar ao `app.css` existente:

```css
@theme {
  /* Cores existentes (manter) */
  --color-teal-0: #F4F9F7;
  --color-teal-1: #EEF5F2;
  --color-teal-2: #E6EEEC;
  --color-teal-3: #DAE6E2;
  --color-teal-4: #C8DDD7;
  --color-teal-5: #B4CECA;
  --color-teal-6: #7AADA6;
  --color-steel-0: #EAF2F9;
  --color-steel-1: #C2DCF0;
  --color-steel-2: #8BBADE;
  --color-steel-3: #3578B0;
  --color-steel-4: #265A87;
  --color-steel-5: #173650;
  --color-steel-6: #0D2033;
  --color-bg-page: #E6EEEC;
  --color-bg-card: #FAFCFB;
  --color-bg-dark: #0D2033;
  --color-bg-dark-card: #122840;

  /* Cores de status do pipeline (novas) */
  --color-status-pendente: #94A3B8;
  --color-status-executando: #3B82F6;
  --color-status-aguardando: #F59E0B;
  --color-status-aprovado: #22C55E;
  --color-status-rejeitado: #EF4444;
  --color-status-erro: #EF4444;

  /* Cores de score (novas) */
  --color-score-alto: #22C55E;
  --color-score-medio: #F59E0B;
  --color-score-baixo: #EF4444;

  /* Brand palette reference (novas) */
  --color-brand-fundo: #0A0A0F;
  --color-brand-primario: #A78BFA;
  --color-brand-secundario: #6D28D9;

  /* Fonte (manter) */
  --font-family-outfit: 'Outfit', 'Helvetica Neue', sans-serif;
}

/* Classes utilitarias globais de espacamento */
.sidebar-padding { padding: 1rem; }
.card-padding { padding: 1.25rem; }
.section-padding { padding: 1.5rem 0; }
.wizard-gap { gap: 1rem; }
.approval-actions-gap { gap: 0.75rem; }

/* Status badges */
.badge-status-pendente { background-color: var(--color-status-pendente); color: white; }
.badge-status-executando { background-color: var(--color-status-executando); color: white; }
.badge-status-aguardando { background-color: var(--color-status-aguardando); color: white; }
.badge-status-aprovado { background-color: var(--color-status-aprovado); color: white; }
.badge-status-rejeitado { background-color: var(--color-status-rejeitado); color: white; }
.badge-status-erro { background-color: var(--color-status-erro); color: white; }

/* Animacoes do pipeline */
@keyframes pulse-approval {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.animate-pulse-approval {
  animation: pulse-approval 2s ease-in-out infinite;
}
```

---

## Mapa de Endpoints API (Frontend -> Backend)

Endpoints que o frontend precisa consumir. Cada um mapeado para o Repository correspondente.

| Metodo | Endpoint | Repository | Caso de Uso |
|--------|----------|------------|-------------|
| POST | `/api/pipeline` | PipelineRepository | IniciarPipeline |
| GET | `/api/pipeline/:id` | PipelineRepository | AcompanharPipeline |
| GET | `/api/pipeline/:id/steps` | PipelineRepository | ListarEtapas |
| POST | `/api/pipeline/:id/cancelar` | PipelineRepository | CancelarPipeline |
| POST | `/api/pipeline/:id/retomar` | PipelineRepository | RetomarPipeline |
| GET | `/api/pipeline/:id/briefing` | BriefingRepository | VisualizarBriefing |
| POST | `/api/pipeline/:id/briefing/aprovar` | BriefingRepository | AprovarBriefing |
| POST | `/api/pipeline/:id/briefing/rejeitar` | BriefingRepository | RejeitarBriefing |
| GET | `/api/pipeline/:id/copy` | CopyRepository | VisualizarCopy |
| GET | `/api/pipeline/:id/hooks` | CopyRepository | VisualizarHooks |
| POST | `/api/pipeline/:id/copy/aprovar` | CopyRepository | AprovarCopy |
| POST | `/api/pipeline/:id/copy/rejeitar` | CopyRepository | RejeitarCopy |
| GET | `/api/pipeline/:id/visual` | VisualRepository | VisualizarPrompts |
| POST | `/api/pipeline/:id/visual/aprovar` | VisualRepository | AprovarPrompts |
| POST | `/api/pipeline/:id/visual/rejeitar` | VisualRepository | RejeitarPrompts |
| GET | `/api/pipeline/:id/imagens` | ImagemRepository | VisualizarVariacoes |
| POST | `/api/pipeline/:id/imagens/aprovar` | ImagemRepository | AprovarImagens |
| POST | `/api/pipeline/:id/imagens/rejeitar` | ImagemRepository | RejeitarImagens |
| POST | `/api/pipeline/:id/imagens/regerar` | ImagemRepository | RegerarVariacao |
| GET | `/api/pipeline/:id/score` | ExportRepository | VisualizarScore |
| GET | `/api/pipeline/:id/export` | ExportRepository | BuscarSlidesFinais |
| POST | `/api/pipeline/:id/drive` | ExportRepository | SalvarNoDrive |
| GET | `/api/historico` | HistoricoRepository | ListarHistorico |
| DELETE | `/api/historico/:id` | HistoricoRepository | RemoverItem |
| GET | `/api/agentes` | AgenteRepository | ListarAgentes |
| GET | `/api/config` | ConfigRepository | CarregarStatus |
| POST | `/api/config` | ConfigRepository | SalvarApiKeys |
| GET | `/api/config/brand-palette` | ConfigRepository | BuscarBrandPalette |
| PUT | `/api/config/brand-palette` | ConfigRepository | SalvarBrandPalette |
| GET | `/api/config/creator-registry` | ConfigRepository | ListarCriadores |
| PUT | `/api/config/creator-registry` | ConfigRepository | SalvarCriadores |
| GET | `/api/config/platform-rules` | ConfigRepository | BuscarPlatformRules |
| PUT | `/api/config/platform-rules` | ConfigRepository | SalvarPlatformRules |

**Endpoints legados (manter):**
| POST | `/api/gerar-conteudo` | carrossel-repository | GerarConteudo (legado) |
| POST | `/api/gerar-conteudo-cli` | carrossel-repository | GerarConteudoCli (legado) |
| POST | `/api/gerar-imagem` | carrossel-repository | GerarImagens (legado) |
| POST | `/api/gerar-imagem-slide` | carrossel-repository | GerarImagemSlide (legado) |
| POST | `/api/google-drive/carrossel` | carrossel-repository | SalvarDrive (legado) |

---

## Notas para o Dev Mockado (Agente 06)

### pipeline.mock.ts

Dados necessarios:
- `pipelineMock(payload)`: retorna pipeline com id UUID gerado, status 'em_execucao', etapa_atual 'strategist'
- `pipelineDetalhesMock(id)`: retorna pipeline com status 'aguardando_aprovacao' na etapa 'strategist' para simular AP-1
- `pipelineStepsMock(pipelineId)`: retorna array de 7 PipelineStepDTO. Etapas ate a atual com status 'aprovado', etapa atual com 'aguardando_aprovacao', restante 'pendente'. Incluir duracao_ms realista (5000-30000ms para LLM, 500-2000ms para skills).

### briefing.mock.ts

- `briefingMock(pipelineId)`: retorna briefing com texto realista sobre "Transfer Learning" (contexto IT Valley). Incluir tendencias_usadas com 2-3 fontes. Se funil, incluir 5 pecas com distribuicao topo/meio/fundo.

### copy.mock.ts

- `copyMock(pipelineId)`: retorna copy com headline, narrativa (3 paragrafos), CTA, e sequencia de 7 slides com titulos e conteudo. Slides devem ter tipos variados (cover, content, code, comparison, cta).
- `hooksMock(pipelineId)`: retorna 3 hooks com abordagens distintas (curiosidade, autoridade, provocacao). Textos com 1-2 linhas cada.

### visual.mock.ts

- `promptsVisualMock(pipelineId)`: retorna 7 prompts (1 por slide) com texto de prompt de imagem detalhado (>50 chars). Slides de capa e CTA com modelo_sugerido 'pro', restante 'flash'.

### imagem.mock.ts

- `imagemVariacoesMock(pipelineId)`: retorna 7 slides, cada um com 3 variacoes. Usar base64 de imagens placeholder (1x1 pixel roxo/azul/verde para diferenciar). brand_gate_status 'valido' para todos exceto 1 slide com 'revisao_manual'.

### score.mock.ts

- `scoreMock(pipelineId)`: retorna score com valores realistas (clarity: 8.5, impact: 7.8, originality: 7.2, scroll_stop: 8.0, cta_strength: 7.5, final_score: 7.8, decision: 'approved').
- `slidesFinaisMock(pipelineId)`: retorna titulo + array de 7 URLs de imagens placeholder.

### historico.mock.ts

- `historicoMock()`: retorna 8 itens variados. Mix de formatos (carrossel, post_unico, thumbnail_youtube), status (completo, em_andamento, erro), com e sem score, com e sem drive_link. Datas dos ultimos 30 dias.

### agente.mock.ts

- `agentesMock()`: retorna 12 entradas (6 LLM + 6 skills). Cada um com slug, nome, descricao curta (1 linha), tipo ('llm' ou 'skill'), conteudo (system prompt resumido em 3-5 linhas).

### config-brand.mock.ts

- `brandPaletteMock()`: retorna os valores do brand_palette.json do PRD (fundo #0A0A0F, primario #A78BFA, etc.).

### config-creators.mock.ts

- `criadoresMock()`: retorna 11 criadores da lista do PRD (Fireship, Karpathy, etc.) com funcoes e plataformas corretas.

### config-platform.mock.ts

- `platformRulesMock()`: retorna 3 plataformas MVP (LinkedIn: 3000 chars, 5 hashtags; Instagram: 2200 chars, 30 hashtags; YouTube: 100 chars titulo, 0 hashtags).

---

## Dev Features -- Ordem de Implementacao Sugerida

Cada feature e 1 caso de uso completo. Ordem pensada para validacao incremental.

| # | Dev Feature | Dominio | Dependencias |
|---|------------|---------|-------------|
| 1 | ListarAgentes | agente | Nenhuma |
| 2 | CarregarStatusConfig | config | Nenhuma |
| 3 | SalvarApiKeys | config | CarregarStatusConfig |
| 4 | BuscarBrandPalette | config | Nenhuma |
| 5 | SalvarBrandPalette | config | BuscarBrandPalette |
| 6 | ListarCriadores | config | Nenhuma |
| 7 | SalvarCriadores | config | ListarCriadores |
| 8 | IniciarPipeline | pipeline | Nenhuma |
| 9 | AcompanharPipeline | pipeline | IniciarPipeline |
| 10 | VisualizarBriefing | briefing | AcompanharPipeline |
| 11 | AprovarBriefing | briefing | VisualizarBriefing |
| 12 | VisualizarCopy | copy | AprovarBriefing |
| 13 | EscolherHook | copy | VisualizarCopy |
| 14 | AprovarCopy | copy | EscolherHook |
| 15 | VisualizarPrompts | visual | AprovarCopy |
| 16 | AprovarPrompts | visual | VisualizarPrompts |
| 17 | VisualizarVariacoes | imagem | AprovarPrompts |
| 18 | EscolherVariacao | imagem | VisualizarVariacoes |
| 19 | AprovarImagens | imagem | EscolherVariacao |
| 20 | VisualizarScore | export | AprovarImagens |
| 21 | ExportarPdf | export | VisualizarScore |
| 22 | SalvarDrive | export | VisualizarScore |
| 23 | ListarHistorico | historico | Nenhuma |
| 24 | FiltrarHistorico | historico | ListarHistorico |
| 25 | RemoverHistorico | historico | ListarHistorico |

---

## Checklist -- Arquitetura Completa

### Dominios Novos

- [ ] pipeline: PipelineDTO, PipelineStepDTO, IniciarPipelineDTO, PipelineRepository, PipelineService, pipeline.mock.ts, 3 componentes
- [ ] briefing: BriefingDTO, BriefingRepository, BriefingService, briefing.mock.ts, 2 componentes
- [ ] copy: CopyDTO, HookDTO, CopyRepository, CopyService, copy.mock.ts, 4 componentes
- [ ] visual: PromptVisualDTO, VisualRepository, VisualService, visual.mock.ts, 4 componentes
- [ ] imagem: ImagemVariacaoDTO, ImagemRepository, ImagemService, imagem.mock.ts, 4 componentes
- [ ] export: ScoreDTO, ExportRepository, ExportService, score.mock.ts, 4 componentes
- [ ] home: FormatoSelector, DisciplinaSelector (mover), FotoCriadorGaleria
- [ ] historico: HistoricoItemDTO, HistoricoRepository (novo), HistoricoService, historico.mock.ts, 2 componentes
- [ ] agente: AgenteDTO, AgenteRepository, AgenteService, agente.mock.ts, 3 componentes
- [ ] config: BrandPaletteDTO, CreatorEntryDTO, PlatformRuleDTO, ConfigRepository (novo), ConfigService (novo), 3 mocks, 6 componentes

### Componentes UI Novos

- [ ] Modal.svelte
- [ ] Spinner.svelte
- [ ] Skeleton.svelte
- [ ] Toggle.svelte
- [ ] Tabs.svelte
- [ ] Banner.svelte

### Layout

- [ ] Sidebar.svelte (migrar de header horizontal para sidebar)
- [ ] +layout.svelte (refatorar para usar Sidebar)

### Design Tokens

- [ ] Cores de status no app.css
- [ ] Cores de score no app.css
- [ ] Classes utilitarias de espacamento
- [ ] Animacao pulse-approval

### Rotas Novas

- [ ] /pipeline/[id]/+page.svelte
- [ ] /pipeline/[id]/briefing/+page.svelte
- [ ] /pipeline/[id]/copy/+page.svelte
- [ ] /pipeline/[id]/visual/+page.svelte
- [ ] /pipeline/[id]/imagem/+page.svelte
- [ ] /pipeline/[id]/export/+page.svelte

---

## Decisoes Tecnicas

| Decisao | Escolha | Justificativa |
|---------|---------|---------------|
| Atualizacao de status do pipeline | Polling (3s) | Mais simples que SSE/WebSocket. Adequado para uso interno com poucos usuarios. |
| Sub-telas de aprovacao | Rotas separadas | Permite deep-linking, retomada via URL, e compartilhamento de link. |
| Funil com multiplas pecas | 1 peca por vez + navegacao lateral | Wizard fica simples. Tabs ou select para navegar entre pecas. |
| Imagens por slide (AP-4) | Accordion por slide, 3 colunas | Organiza visualmente ate 30 imagens. Accordion evita scroll infinito. |
| Layout global | Sidebar (pendente Designer) | PRD menciona sidebar. Header atual sera migrado. Decisao visual final do Agente 05. |
| Config expandida | Sections com accordion/tabs | Evita pagina longa. Cada secao independente. |

---

## Principio de Opacidade -- Validacao

| Camada | Conhece campos? | Muda quando campo muda? |
|--------|-----------------|------------------------|
| DTOs (14 arquivos) | Sim | Sim |
| Mocks (11 arquivos) | Sim | Sim |
| Repositories (9 arquivos) | Sim (cria DTO) | Sim |
| **Services (9 arquivos)** | **Nao** | **NAO** |
| **Componentes** | Recebe DTO | Depende (so se exibe o campo) |
| **+page.svelte** | Cria DTO | Sim (fabrica de DTOs) |

Todos os Services usam apenas `dto.isValid()`, `dto.toPayload()`, e getters publicos. Nenhum Service acessa `dto.campo` diretamente.

---

*Documento gerado pelo Agente 04 (Arquiteto IT Valley Frontend) da esteira IT Valley.*
*Proximo: Agente 06 (Dev Mockado) + Agente 09 (Dev Frontend).*
