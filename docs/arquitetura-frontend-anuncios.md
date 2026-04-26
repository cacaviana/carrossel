# Arquitetura Frontend -- Modulo Anuncios (Google Ads Display)

Documento gerado pelo Agente 04 (Arquiteto IT Valley Frontend).
Base: PRD Anuncios (`docs/prd-anuncios.md`) + Telas Anuncios (`docs/telas-anuncios.md`) + Arquitetura Frontend existente (`docs/ARQUITETURA_FRONTEND.md`, `docs/arquitetura-frontend-kanban.md`) + codigo existente em `frontend/src/`.

Stack: SvelteKit 5 + Tailwind CSS v4 + Svelte runes (`$state`, `$derived`, `$props`, `$effect`).
Filosofia: Simples > Complexo. Dominio > Tecnico. Funciona > Bonito.

---

## 1. Overview -- O que muda no Frontend

O modulo Anuncios adiciona um novo **dominio** (`anuncio`) ao frontend, com CRUD proprio e rotas dedicadas sob `/anuncios`, seguindo o mesmo padrao de organizacao dos dominios ja existentes (`pipeline`, `kanban`, `historico`, `agente`, `config`).

**O que e novo:**

- Novo dominio `anuncio` com 5 casos de uso (CriarAnuncio, ListarAnuncios, ObterAnuncio, EditarAnuncio, ExcluirAnuncio) + 1 operacao de pipeline (RegerarDimensao).
- 4 rotas novas: `/anuncios`, `/anuncios/novo`, `/anuncios/[id]`, `/anuncios/[id]/editar`.
- 2 modais (componentes, nao rotas): confirmar exclusao e regerar dimensao.
- Pasta `components/anuncio/` com os componentes do dominio.
- DTOs, Service, Repository, Mocks novos para o dominio `anuncio`.
- 1 store dedicado (`anuncio.svelte.ts`) para estado reativo de filtros da lista e regeneracoes em andamento.

**O que e alteracao de telas existentes (tocar arquivos ja existentes):**

- Seletor de formato na Home (`/`) ganha card `Anuncio`.
- Funnel Architect (`/pipeline/[id]/briefing`) aceita `formato=anuncio` nas pecas.
- Historico (`/historico`) reconhece `formato=anuncio` (filtro, thumbnail, redirect de "ver detalhes" para `/anuncios/[id]`).
- Kanban (`/kanban`): card ganha badge "Anuncio" + indicador "4 dimensoes". Modal de detalhe mostra grid 2x2 das dimensoes.
- Pipeline AP-4 (`/pipeline/[id]/imagem`) troca grid de slides por grid de 4 dimensoes quando `formato=anuncio`.
- Pipeline Export (`/pipeline/[id]/export`): oculta PDF, expoe ZIP multi-dimensao + Drive subpasta.
- Configuracoes (`/configuracoes`): secao Platform Rules lista "Google Ads Display" com headline_max=30 e descricao_max=90.
- Sidebar (`components/layout/Sidebar.svelte`): novo item "Anuncios" entre "Kanban" e "Historico".

**Invariantes preservadas:**

- `VITE_USE_MOCK` alterna entre repository mock e real (RN-009 do codigo e regra IT Valley #6).
- DTOs imutaveis com `readonly`, `constructor(Record)`, `isValid()`, `toPayload()`.
- Services opacos (nunca acessam `dto.campo`).
- Componentes por dominio, nao por tipo tecnico.
- Import direto, sem barrel exports.
- `tenant_id` carregado em todo DTO vindo do backend.

---

## 2. Arvore de Arquivos -- Criar e Modificar

### 2.1 Criar

```
frontend/src/routes/
└── anuncios/
    ├── +page.svelte                  # Tela 1: Lista de Anuncios
    ├── novo/
    │   └── +page.svelte              # Tela 2: Criar Anuncio
    └── [id]/
        ├── +page.svelte              # Tela 3: Detalhe do Anuncio
        └── editar/
            └── +page.svelte          # Tela 4: Editar Anuncio

frontend/src/lib/
├── components/
│   └── anuncio/                      # Novo dominio
│       ├── AnuncioCard.svelte               # Card compacto da lista
│       ├── AnuncioFiltros.svelte            # Barra de filtros da lista
│       ├── AnuncioStatusBadge.svelte        # Badge de status (em_andamento, concluido, parcial, erro, cancelado)
│       ├── AnuncioDimensoesGrid.svelte      # Grid 2x2 das 4 dimensoes (usado em detalhe e editar)
│       ├── AnuncioDimensaoCard.svelte       # 1 card de dimensao (imagem + badge + acoes)
│       ├── AnuncioImageZoomModal.svelte     # Modal fullscreen de uma imagem de dimensao
│       ├── AnuncioCopyDisplay.svelte        # Display readonly de headline + descricao + copiar
│       ├── AnuncioCopyEditor.svelte         # Editor de headline (30) + descricao (90) com contadores
│       ├── AnuncioBriefingForm.svelte       # Formulario de criar anuncio (titulo, tema, etapa_funil, foto)
│       ├── AnuncioExportBadge.svelte        # Badge "Parcial N/4" ou "Concluido 4/4"
│       ├── AnuncioExcluirModal.svelte       # Modal de confirmar exclusao (Tela 5)
│       ├── AnuncioRegenerarModal.svelte     # Modal de regerar dimensao (Tela 6)
│       └── AnuncioDriveActions.svelte       # Botoes "Baixar ZIP" / "Abrir no Drive" / "Salvar no Drive"
│
├── dtos/                              # Plano nas pastas existentes, nome PascalCaseDTO.ts
│   ├── AnuncioDTO.ts                         # Anuncio completo (ObterAnuncio response)
│   ├── AnuncioDimensaoDTO.ts                 # 1 dimensao (url, status, retries, overlay, modelo)
│   ├── AnuncioCopyDTO.ts                     # Par headline + descricao (value object)
│   ├── CriarAnuncioDTO.ts                    # Request de criacao
│   ├── ListarAnunciosFiltroDTO.ts            # Filtros da lista (busca, status, etapa_funil, datas, incluir_excluidos)
│   ├── EditarAnuncioCopyDTO.ts               # Request de editar copy (titulo, headline, descricao, etapa_funil)
│   └── RegerarDimensaoDTO.ts                 # Request de regerar dimensao(oes) (dimensoes_alvo, feedback)
│
├── services/
│   └── AnuncioService.ts              # Camada opaca unica para o dominio
│
├── repositories/
│   └── AnuncioRepository.ts           # VITE_USE_MOCK alterna mock vs real (ambos na mesma classe)
│
├── mocks/
│   └── anuncio.mock.ts                # Lista de anuncios variados (concluido, parcial, em_andamento, erro)
│
└── stores/
    └── anuncio.svelte.ts              # Estado reativo: filtros da lista, regeracoes em andamento
```

### 2.2 Modificar

```
frontend/src/
├── routes/
│   ├── +page.svelte                       # Home: adicionar card "Anuncio" no FormatoSelector
│   ├── historico/+page.svelte             # Filtro formato=anuncio + redirect para /anuncios/[id]
│   ├── kanban/+page.svelte                # Carga do card ja traz formato; sem mudanca de fluxo
│   ├── pipeline/[id]/briefing/+page.svelte # Funnel Architect: aceitar formato=anuncio nas pecas
│   ├── pipeline/[id]/imagem/+page.svelte  # AP-4: branch por formato (slides vs dimensoes)
│   └── pipeline/[id]/export/+page.svelte  # Export: branch por formato (PDF vs ZIP multi-dimensao)
│
├── lib/components/
│   ├── home/FormatoSelector.svelte        # Adicionar opcao "Anuncio"
│   ├── layout/Sidebar.svelte              # Novo item "Anuncios"
│   ├── historico/HistoricoCard.svelte     # Thumbnail = image_urls[1] quando formato=anuncio + badge
│   ├── historico/HistoricoFiltros.svelte  # Adicionar opcao "Anuncio" no filtro de formato
│   ├── kanban/KanbanCard.svelte           # Badge "Anuncio" + indicador dimensoes
│   ├── kanban/CardDetailTab.svelte        # Se card.formato=anuncio, mostrar grid 2x2
│   └── pipeline/PipelineWizard.svelte     # Rotulos de etapas sem alteracao; cuida de branch por formato nas sub-paginas
│
└── lib/dtos/
    ├── HistoricoItemDTO.ts                # Aceitar formato='anuncio' + getter thumbnailUrl
    ├── CardDTO.ts                         # (ja aceita formato via pipeline_id; nao precisa campo novo -- opcional)
    ├── IniciarPipelineDTO.ts              # Aceitar 'anuncio' em FormatoConteudo
    └── PipelineDTO.ts                     # Aceitar 'anuncio' em FormatoConteudo
```

Observacao: o tipo `FormatoConteudo` ja existe em `PipelineDTO.ts`. Basta incluir `'anuncio'` no union type e no mapeamento de `formatoLabel`.

---

## 3. DTOs -- Assinaturas Completas

Todos os DTOs seguem o contrato IT Valley: campos `readonly`, `constructor(data: Record<string, any>)`, getters derivados, `isValid(): boolean`, `toPayload(): Record<string, any>`.

### 3.1 AnuncioDTO.ts

```typescript
// src/lib/dtos/AnuncioDTO.ts

import { AnuncioDimensaoDTO } from './AnuncioDimensaoDTO';
import { AnuncioCopyDTO } from './AnuncioCopyDTO';

export type AnuncioStatus = 'em_andamento' | 'concluido' | 'parcial' | 'erro' | 'cancelado';
export type EtapaFunil = 'topo' | 'meio' | 'fundo' | 'avulso';

export class AnuncioDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly titulo: string;
  readonly copy: AnuncioCopyDTO;
  readonly status: AnuncioStatus;
  readonly etapa_funil: EtapaFunil;
  readonly pipeline_id: string;
  readonly pipeline_funil_id: string;
  readonly dimensoes: AnuncioDimensaoDTO[];
  readonly drive_folder_link: string;
  readonly criado_por: string;
  readonly created_at: string;
  readonly updated_at: string;
  readonly deleted_at: string;

  constructor(data: Record<string, any>);

  // Getters derivados (nao acessam campos privados, so combinam os readonly)
  get isConcluido(): boolean;                // status === 'concluido'
  get isParcial(): boolean;                  // status === 'parcial'
  get isEmAndamento(): boolean;              // status === 'em_andamento'
  get isErro(): boolean;                     // status === 'erro'
  get isDeletado(): boolean;                 // deleted_at nao vazio
  get dimensoesOkCount(): number;            // conta dimensoes com brand_gate_status === 'valido'
  get dimensoesTotalCount(): number;         // sempre 4 no MVP
  get statusLabel(): string;                 // "Em andamento", "Concluido", "Parcial (3/4)", etc
  get etapaFunilLabel(): string;             // "Topo", "Meio", "Fundo", "Avulso"
  get thumbnailUrl(): string;                // image_urls[1] (1080x1080) -- usado em Historico e Kanban
  get tituloTruncado(): string;              // 50 chars com "..."
  get driveFolderName(): string;             // "{titulo} - {YYYY-MM-DD}" (RN-008)
  get hasDriveLink(): boolean;
  get podeExportar(): boolean;               // concluido OU parcial (RN-019: exporta parcial)
  get dimensaoPorId(id: string): AnuncioDimensaoDTO | undefined;  // metodo, nao getter

  isValid(): boolean;                        // id nao vazio && titulo >= 3 && dimensoes.length === 4
  toPayload(): Record<string, any>;
}
```

### 3.2 AnuncioDimensaoDTO.ts

```typescript
// src/lib/dtos/AnuncioDimensaoDTO.ts

export type DimensaoId = '1200x628' | '1080x1080' | '300x600' | '300x250';
export type BrandGateStatus = 'valido' | 'revisao_manual' | 'falhou' | 'nao_gerada';
export type OverlayTipo = 'foto+logo' | 'so_logo';
export type ModeloGemini = 'gemini-pro' | 'gemini-flash';

export class AnuncioDimensaoDTO {
  readonly dimensao_id: DimensaoId;
  readonly imagem_url: string;
  readonly brand_gate_status: BrandGateStatus;
  readonly brand_gate_retries: number;       // 0, 1 ou 2 (RN-019)
  readonly modelo_usado: ModeloGemini;
  readonly overlay_tipo: OverlayTipo;
  readonly largura: number;                  // derivado de dimensao_id para layout
  readonly altura: number;
  readonly regenerada_em: string;

  constructor(data: Record<string, any>);

  get aspectRatio(): string;                 // ex: "16:9" para 1200x628
  get labelCompleto(): string;               // "1200x628 (landscape) - Gemini Pro"
  get isValida(): boolean;                   // brand_gate_status === 'valido' && imagem_url nao vazia
  get isFalha(): boolean;                    // brand_gate_status === 'falhou'
  get isNaoGerada(): boolean;                // brand_gate_status === 'nao_gerada'
  get podeRegerar(): boolean;                // true sempre -- RN-018
  get temOverlayFoto(): boolean;             // overlay_tipo === 'foto+logo' (RN-016)
  get statusLabel(): string;
  get estiloGrid(): string;                  // classe CSS para o grid (col-span, row-span)

  isValid(): boolean;
  toPayload(): Record<string, any>;
}
```

### 3.3 AnuncioCopyDTO.ts

```typescript
// src/lib/dtos/AnuncioCopyDTO.ts

export const HEADLINE_MAX = 30;    // RN-002
export const DESCRICAO_MAX = 90;   // RN-003

export class AnuncioCopyDTO {
  readonly headline: string;
  readonly descricao: string;

  constructor(data: Record<string, any>);

  // Validacoes de formulario -- UI usa em tempo real
  get headlineLength(): number;
  get descricaoLength(): number;
  get headlineExcedido(): boolean;
  get descricaoExcedido(): boolean;
  get headlineRestante(): number;
  get descricaoRestante(): number;

  // Preview do copy.txt exportado (RN-007)
  get copyTxtPreview(): string;              // "Headline: ...\nDescricao: ..."

  isValid(): boolean;                        // headline >= 1 && <= 30 && descricao >= 1 && <= 90
  toPayload(): Record<string, any>;
}
```

### 3.4 CriarAnuncioDTO.ts

```typescript
// src/lib/dtos/CriarAnuncioDTO.ts

import type { EtapaFunil } from './AnuncioDTO';

export type ModoEntrada = 'texto' | 'disciplina';

export class CriarAnuncioDTO {
  readonly titulo: string;
  readonly tema_ou_briefing: string;
  readonly modo_entrada: ModoEntrada;
  readonly disciplina: string;
  readonly tecnologia: string;
  readonly etapa_funil: EtapaFunil;
  readonly pipeline_funil_id: string;        // UUID se vem do Funnel Architect, "" se avulso
  readonly foto_criador_id: string;

  constructor(data: Record<string, any>);

  get tituloValido(): boolean;               // >= 3
  get temaValido(): boolean;                 // >= 20
  get precisaDisciplina(): boolean;          // modo_entrada === 'disciplina'
  get vindoDoFunil(): boolean;               // pipeline_funil_id nao vazio

  isValid(): boolean;
  toPayload(): Record<string, any>;
}
```

### 3.5 ListarAnunciosFiltroDTO.ts

```typescript
// src/lib/dtos/ListarAnunciosFiltroDTO.ts

import type { AnuncioStatus, EtapaFunil } from './AnuncioDTO';

export class ListarAnunciosFiltroDTO {
  readonly busca: string;
  readonly status: AnuncioStatus | 'todos';
  readonly etapa_funil: EtapaFunil | 'todas';
  readonly data_inicio: string;              // ISO date ou ""
  readonly data_fim: string;
  readonly incluir_excluidos: boolean;

  constructor(data: Record<string, any>);

  get temFiltroAtivo(): boolean;             // qualquer filtro diferente do default
  get queryString(): string;                 // para GET ?q=...&status=...

  isValid(): boolean;                        // sempre true, filtros sao opcionais
  toPayload(): Record<string, any>;
}
```

### 3.6 EditarAnuncioCopyDTO.ts

```typescript
// src/lib/dtos/EditarAnuncioCopyDTO.ts

import type { EtapaFunil } from './AnuncioDTO';

export class EditarAnuncioCopyDTO {
  readonly id: string;
  readonly titulo: string;
  readonly headline: string;
  readonly descricao: string;
  readonly etapa_funil: EtapaFunil;

  constructor(data: Record<string, any>);

  get tituloValido(): boolean;               // >= 3
  get headlineValido(): boolean;             // >= 1 && <= 30
  get descricaoValido(): boolean;            // >= 1 && <= 90

  isValid(): boolean;
  toPayload(): Record<string, any>;
}
```

### 3.7 RegerarDimensaoDTO.ts

```typescript
// src/lib/dtos/RegerarDimensaoDTO.ts

import type { DimensaoId } from './AnuncioDimensaoDTO';

export class RegerarDimensaoDTO {
  readonly anuncio_id: string;
  readonly dimensoes_alvo: DimensaoId[];     // 1 a 4 (RN-018)
  readonly feedback_livre: string;           // opcional, max 500 chars
  readonly manter_prompt_base: boolean;      // default true no MVP

  constructor(data: Record<string, any>);

  get feedbackDentroLimite(): boolean;       // <= 500
  get dimensoesValidas(): boolean;           // length entre 1 e 4

  isValid(): boolean;
  toPayload(): Record<string, any>;
}
```

---

## 4. Services -- Camada Opaca

```typescript
// src/lib/services/AnuncioService.ts

import { AnuncioRepository } from '$lib/repositories/AnuncioRepository';
import { AnuncioDTO } from '$lib/dtos/AnuncioDTO';
import { CriarAnuncioDTO } from '$lib/dtos/CriarAnuncioDTO';
import { EditarAnuncioCopyDTO } from '$lib/dtos/EditarAnuncioCopyDTO';
import { ListarAnunciosFiltroDTO } from '$lib/dtos/ListarAnunciosFiltroDTO';
import { RegerarDimensaoDTO } from '$lib/dtos/RegerarDimensaoDTO';

export class AnuncioService {
  /** Lista anuncios do tenant aplicando filtros. Filtra por isValid(). */
  static async listar(filtro: ListarAnunciosFiltroDTO): Promise<AnuncioDTO[]>;

  /** Busca anuncio por id. Erro se id invalido ou nao encontrado. */
  static async obter(id: string): Promise<AnuncioDTO>;

  /** Cria novo anuncio + dispara pipeline. Retorna pipeline_id para navegacao. */
  static async criar(dto: CriarAnuncioDTO): Promise<{ anuncio_id: string; pipeline_id: string }>;

  /** Atualiza copy do anuncio (titulo, headline, descricao, etapa_funil). Sem regeneracao. */
  static async editarCopy(dto: EditarAnuncioCopyDTO): Promise<AnuncioDTO>;

  /** Dispara regeneracao de 1+ dimensoes mantendo as demais. RN-018. */
  static async regerarDimensoes(dto: RegerarDimensaoDTO): Promise<{ anuncio_id: string; job_id: string }>;

  /** Soft delete -- backend preenche deleted_at. RN-013. */
  static async excluir(id: string): Promise<void>;

  /** Gera ZIP local (4 PNGs + copy.txt) como Blob. Usa dados ja carregados do DTO. */
  static async baixarZip(id: string): Promise<Blob>;

  /** Cria subpasta Drive com 4 PNGs + copy.txt. Atualiza drive_folder_link. RN-008. */
  static async salvarNoDrive(id: string): Promise<{ drive_folder_link: string }>;
}
```

**Regras obrigatorias:**

- Metodos `static`, nunca instancia.
- **Nunca** acessa `dto.campo` -- so chama `dto.isValid()` / `dto.toPayload()` / getters.
- Delega acesso a dados para `AnuncioRepository`. **Nao faz `fetch` direto.**
- Filtra listas por `isValid()` antes de retornar.
- Valida input minimo (id != "", dto != null) antes de delegar. Lanca `Error` claro.

---

## 5. Repository -- Mock + Real via VITE_USE_MOCK

```typescript
// src/lib/repositories/AnuncioRepository.ts

import { AnuncioDTO } from '$lib/dtos/AnuncioDTO';
import type { CriarAnuncioDTO } from '$lib/dtos/CriarAnuncioDTO';
import type { ListarAnunciosFiltroDTO } from '$lib/dtos/ListarAnunciosFiltroDTO';
import type { EditarAnuncioCopyDTO } from '$lib/dtos/EditarAnuncioCopyDTO';
import type { RegerarDimensaoDTO } from '$lib/dtos/RegerarDimensaoDTO';
import { anunciosMock, buscarAnuncioMockPorId, filtrarAnunciosMock } from '$lib/mocks/anuncio.mock';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true';

function sleep(ms = 300): Promise<void> { return new Promise(r => setTimeout(r, ms)); }

export class AnuncioRepository {
  static async listar(filtro: ListarAnunciosFiltroDTO): Promise<AnuncioDTO[]> {
    if (USE_MOCK) {
      await sleep();
      return filtrarAnunciosMock(filtro.toPayload()).map(d => new AnuncioDTO(d));
    }
    const res = await fetch(`${API_BASE}/api/anuncios?${filtro.queryString}`);
    if (!res.ok) throw new Error('Falha ao listar anuncios');
    const data = await res.json();
    return data.map((d: any) => new AnuncioDTO(d));
  }

  static async obterPorId(id: string): Promise<AnuncioDTO> {
    if (USE_MOCK) {
      await sleep();
      const raw = buscarAnuncioMockPorId(id);
      if (!raw) throw new Error('Anuncio nao encontrado');
      return new AnuncioDTO(raw);
    }
    const res = await fetch(`${API_BASE}/api/anuncios/${id}`);
    if (!res.ok) throw new Error('Anuncio nao encontrado');
    const data = await res.json();
    return new AnuncioDTO(data);
  }

  static async criar(dto: CriarAnuncioDTO): Promise<{ anuncio_id: string; pipeline_id: string }> {
    if (USE_MOCK) {
      await sleep(500);
      return { anuncio_id: crypto.randomUUID(), pipeline_id: crypto.randomUUID() };
    }
    const res = await fetch(`${API_BASE}/api/anuncios`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dto.toPayload())
    });
    if (!res.ok) throw new Error('Falha ao criar anuncio');
    return res.json();
  }

  static async editarCopy(dto: EditarAnuncioCopyDTO): Promise<AnuncioDTO> {
    if (USE_MOCK) {
      await sleep();
      const raw = buscarAnuncioMockPorId(dto.toPayload().id);
      if (!raw) throw new Error('Anuncio nao encontrado');
      const atualizado = { ...raw, ...dto.toPayload(), updated_at: new Date().toISOString() };
      return new AnuncioDTO(atualizado);
    }
    const payload = dto.toPayload();
    const res = await fetch(`${API_BASE}/api/anuncios/${payload.id}/copy`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Falha ao editar copy');
    return new AnuncioDTO(await res.json());
  }

  static async regerarDimensoes(dto: RegerarDimensaoDTO): Promise<{ anuncio_id: string; job_id: string }> {
    if (USE_MOCK) {
      await sleep(400);
      const payload = dto.toPayload();
      return { anuncio_id: payload.anuncio_id, job_id: crypto.randomUUID() };
    }
    const payload = dto.toPayload();
    const res = await fetch(`${API_BASE}/api/anuncios/${payload.anuncio_id}/regenerar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Falha ao iniciar regeneracao');
    return res.json();
  }

  static async excluir(id: string): Promise<void> {
    if (USE_MOCK) { await sleep(); return; }
    const res = await fetch(`${API_BASE}/api/anuncios/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error('Falha ao excluir anuncio');
  }

  static async baixarZip(id: string): Promise<Blob> {
    if (USE_MOCK) {
      await sleep(600);
      // mock devolve um blob vazio simbolico
      return new Blob(['mock-zip'], { type: 'application/zip' });
    }
    const res = await fetch(`${API_BASE}/api/anuncios/${id}/zip`);
    if (!res.ok) throw new Error('Falha ao baixar ZIP');
    return res.blob();
  }

  static async salvarNoDrive(id: string): Promise<{ drive_folder_link: string }> {
    if (USE_MOCK) {
      await sleep(800);
      return { drive_folder_link: 'https://drive.google.com/drive/folders/mock-folder-id' };
    }
    const res = await fetch(`${API_BASE}/api/anuncios/${id}/drive`, { method: 'POST' });
    if (!res.ok) throw new Error('Falha ao salvar no Drive');
    return res.json();
  }
}
```

**Notas:**

- 1 classe unica `AnuncioRepository` com branch interno por `USE_MOCK`. Nao ha arquivo separado `anuncio.repository.mock.ts` -- segue o padrao ja usado pelas repositories existentes do projeto (`PipelineRepository`, `CardRepository`, etc.).
- Mock delega para helpers em `mocks/anuncio.mock.ts` (`buscarAnuncioMockPorId`, `filtrarAnunciosMock`). Mantem o repository limpo e o mock testavel isoladamente.
- Todo retorno publico e `AnuncioDTO` (ou primitivo). Nunca vaza `Record<string, any>`.

---

## 6. Mocks -- Dados Realistas

```typescript
// src/lib/mocks/anuncio.mock.ts
//
// Lista variada cobrindo todos os estados da tela:
// - concluido (happy path, 4/4 dimensoes validas, com Drive link)
// - parcial (3/4 dimensoes, RN-019)
// - em_andamento (pipeline rodando, 0/4 dimensoes)
// - erro (pipeline falhou, 0/4 dimensoes)
// - deletado (deleted_at preenchido)
// - avulso vs funil (com pipeline_funil_id)
// - diferentes etapas de funil (topo, meio, fundo)

export const anunciosMock: Record<string, any>[] = [
  {
    id: 'anu-001',
    tenant_id: 'tenant-itvalley',
    titulo: 'Curso YOLO v8 - Turma Outubro',
    copy: {
      headline: 'Aprenda YOLO em 30 dias',        // 26 chars
      descricao: 'Deteccao de objetos com Python: curso ao vivo com Carlos Viana e certificado.'  // 82 chars
    },
    status: 'concluido',
    etapa_funil: 'fundo',
    pipeline_id: 'pipe-anu-001',
    pipeline_funil_id: '',
    dimensoes: [
      { dimensao_id: '1200x628', imagem_url: '/mock/ads/anu-001-1200x628.png',
        brand_gate_status: 'valido', brand_gate_retries: 0,
        modelo_usado: 'gemini-pro', overlay_tipo: 'foto+logo',
        largura: 1200, altura: 628, regenerada_em: '' },
      { dimensao_id: '1080x1080', imagem_url: '/mock/ads/anu-001-1080x1080.png',
        brand_gate_status: 'valido', brand_gate_retries: 0,
        modelo_usado: 'gemini-flash', overlay_tipo: 'foto+logo',
        largura: 1080, altura: 1080, regenerada_em: '' },
      { dimensao_id: '300x600', imagem_url: '/mock/ads/anu-001-300x600.png',
        brand_gate_status: 'valido', brand_gate_retries: 1,
        modelo_usado: 'gemini-flash', overlay_tipo: 'so_logo',
        largura: 300, altura: 600, regenerada_em: '' },
      { dimensao_id: '300x250', imagem_url: '/mock/ads/anu-001-300x250.png',
        brand_gate_status: 'valido', brand_gate_retries: 0,
        modelo_usado: 'gemini-flash', overlay_tipo: 'so_logo',
        largura: 300, altura: 250, regenerada_em: '' }
    ],
    drive_folder_link: 'https://drive.google.com/drive/folders/mock-folder-anu-001',
    criado_por: 'Carlos Viana',
    created_at: '2026-04-20T14:00:00Z',
    updated_at: '2026-04-20T14:35:00Z',
    deleted_at: ''
  },
  // anu-002: PARCIAL -- dimensao 300x250 falhou apos 2 retries (RN-019)
  {
    id: 'anu-002',
    tenant_id: 'tenant-itvalley',
    titulo: 'Disciplina ETL - Turma Novembro',
    copy: {
      headline: 'ETL com Python e Airflow',       // 26 chars
      descricao: 'Dominio de pipelines de dados. Curso pratico com projeto real.'  // 63 chars
    },
    status: 'parcial',
    etapa_funil: 'meio',
    pipeline_id: 'pipe-anu-002',
    pipeline_funil_id: '',
    dimensoes: [
      { dimensao_id: '1200x628', imagem_url: '/mock/ads/anu-002-1200x628.png',
        brand_gate_status: 'valido', brand_gate_retries: 0,
        modelo_usado: 'gemini-pro', overlay_tipo: 'foto+logo',
        largura: 1200, altura: 628, regenerada_em: '' },
      { dimensao_id: '1080x1080', imagem_url: '/mock/ads/anu-002-1080x1080.png',
        brand_gate_status: 'valido', brand_gate_retries: 0,
        modelo_usado: 'gemini-flash', overlay_tipo: 'foto+logo',
        largura: 1080, altura: 1080, regenerada_em: '' },
      { dimensao_id: '300x600', imagem_url: '/mock/ads/anu-002-300x600.png',
        brand_gate_status: 'valido', brand_gate_retries: 1,
        modelo_usado: 'gemini-flash', overlay_tipo: 'so_logo',
        largura: 300, altura: 600, regenerada_em: '' },
      { dimensao_id: '300x250', imagem_url: '',
        brand_gate_status: 'falhou', brand_gate_retries: 2,
        modelo_usado: 'gemini-flash', overlay_tipo: 'so_logo',
        largura: 300, altura: 250, regenerada_em: '' }
    ],
    drive_folder_link: 'https://drive.google.com/drive/folders/mock-folder-anu-002',
    criado_por: 'Carlos Viana',
    created_at: '2026-04-18T09:00:00Z',
    updated_at: '2026-04-18T09:42:00Z',
    deleted_at: ''
  },
  // anu-003: EM ANDAMENTO -- pipeline rodando, ainda sem imagens
  {
    id: 'anu-003',
    tenant_id: 'tenant-itvalley',
    titulo: 'Agentes LangChain - Workshop',
    copy: {
      headline: 'Crie agentes com LangChain',     // 28 chars
      descricao: 'Workshop pratico de 4h com RAG + tools + memory. Inscricoes abertas.'  // 71 chars
    },
    status: 'em_andamento',
    etapa_funil: 'topo',
    pipeline_id: 'pipe-anu-003',
    pipeline_funil_id: 'funnel-001',
    dimensoes: [
      { dimensao_id: '1200x628', imagem_url: '',
        brand_gate_status: 'nao_gerada', brand_gate_retries: 0,
        modelo_usado: 'gemini-pro', overlay_tipo: 'foto+logo',
        largura: 1200, altura: 628, regenerada_em: '' },
      // ... 3 dimensoes em 'nao_gerada'
    ],
    drive_folder_link: '',
    criado_por: 'Carlos Viana',
    created_at: '2026-04-23T08:00:00Z',
    updated_at: '2026-04-23T08:05:00Z',
    deleted_at: ''
  },
  // anu-004: ERRO -- pipeline cancelado manualmente
  // anu-005: DELETADO (soft delete, deleted_at preenchido)
  // anu-006: CONCLUIDO mas sem Drive salvo ainda
  // anu-007: AVULSO em topo de funil
  // anu-008: FUNIL -- pipeline_funil_id preenchido
];

// Helpers usados pelo Repository
export function buscarAnuncioMockPorId(id: string): Record<string, any> | undefined;
export function filtrarAnunciosMock(filtro: Record<string, any>): Record<string, any>[];
export function listarNaoExcluidosMock(): Record<string, any>[];
```

**Notas para o Dev Mockado (Agente 06):**

- Precisa de **pelo menos 8 mocks** cobrindo: concluido, parcial (3/4 e 2/4), em_andamento, erro, deletado, avulso, funil, diferentes etapas.
- Imagens mock podem apontar para `/mock/ads/*.png` (servidos como assets estaticos) ou URLs externas (picsum.photos com query de dimensao).
- `drive_folder_link` pode ser string fake `https://drive.google.com/drive/folders/mock-folder-anu-XXX`.
- Todos os campos `readonly` do DTO precisam estar no mock (mesmo que vazios "") -- o DTO cuida de `?? ''` / `?? 0`.
- `brand_gate_retries` em 0-2. Se `falhou`, retries deve ser 2.
- `overlay_tipo` deriva do `dimensao_id`: `foto+logo` para 1200x628 e 1080x1080, `so_logo` para 300x600 e 300x250 (RN-016).
- `modelo_usado` deriva do `dimensao_id`: `gemini-pro` somente em 1200x628; `gemini-flash` nas outras 3 (RN-015).

---

## 7. Store -- Estado Reativo

```typescript
// src/lib/stores/anuncio.svelte.ts

import { ListarAnunciosFiltroDTO } from '$lib/dtos/ListarAnunciosFiltroDTO';
import type { DimensaoId } from '$lib/dtos/AnuncioDimensaoDTO';

class AnuncioStore {
  // Filtros ativos da lista (/anuncios)
  filtro = $state(new ListarAnunciosFiltroDTO({
    busca: '',
    status: 'todos',
    etapa_funil: 'todas',
    data_inicio: '',
    data_fim: '',
    incluir_excluidos: false
  }));

  // Map de anuncio_id -> Set<DimensaoId> em regeneracao em andamento.
  // Usado pela tela de Editar para mostrar spinner nas dimensoes certas
  // mesmo se o usuario navegar e voltar.
  regeracoesEmAndamento = $state<Record<string, Set<DimensaoId>>>({});

  resetFiltros(): void;
  aplicarFiltros(novoFiltro: ListarAnunciosFiltroDTO): void;

  marcarRegenerando(anuncioId: string, dims: DimensaoId[]): void;
  marcarRegenerado(anuncioId: string, dim: DimensaoId): void;
  estaRegerando(anuncioId: string, dim: DimensaoId): boolean;
  limparRegeracoes(anuncioId: string): void;
}

export const anuncioStore = new AnuncioStore();
```

**Por que store e necessario:**

- Filtros da Lista precisam persistir quando o usuario navega para Detalhe e volta.
- Regeracoes em andamento precisam ser visiveis mesmo se o usuario sair de `/anuncios/[id]/editar` e voltar (polling continua no backend; UI reflete estado via store).

**Escopo:** single-user (sem tenant prefix). O backend ja filtra por `tenant_id` nas queries.

---

## 8. Componentes por Tela

Todos os componentes seguem: `$props()` tipado, sem logica de negocio (delegam ao Service via page), sem barrel exports, sem pasta-por-componente.

### 8.1 `/anuncios` -- Lista de Anuncios (Tela 1)

**`routes/anuncios/+page.svelte`** (orquestrador)

Responsabilidades:
- Carregar `AnuncioService.listar(anuncioStore.filtro)` no mount e quando filtros mudam.
- Estados: loading, vazio, vazio-com-filtro, erro, sucesso.
- Renderiza `AnuncioFiltros` + grid de `AnuncioCard` + botao "Novo Anuncio".
- Confirmar exclusao abre `AnuncioExcluirModal`.

Componentes consumidos:

| Componente | Props | Eventos | Responsabilidade |
|-----------|-------|---------|------------------|
| `AnuncioFiltros` | `filtro: ListarAnunciosFiltroDTO` | `onChange(filtro: ListarAnunciosFiltroDTO)` | Controla inputs de busca, status, etapa, datas, toggle incluir_excluidos |
| `AnuncioCard` | `anuncio: AnuncioDTO` | `onClick(id)`, `onEditar(id)`, `onExcluir(id)`, `onAbrirDrive(url)`, `onAbrirPipeline(id)` | Exibe thumbnail, titulo, headline, status badge, acoes |
| `AnuncioStatusBadge` | `status: AnuncioStatus`, `dimensoesOk?: number` | -- | Badge colorido com label |
| `AnuncioExportBadge` | `anuncio: AnuncioDTO` | -- | Badge "Parcial 3/4" ou "4/4" |
| `AnuncioExcluirModal` | `anuncio: AnuncioDTO`, `aberto: boolean` | `onConfirmar()`, `onCancelar()` | Modal do soft delete |

### 8.2 `/anuncios/novo` -- Criar Anuncio (Tela 2)

**`routes/anuncios/novo/+page.svelte`**

Responsabilidades:
- Recebe query params `?etapa_funil=...&pipeline_funil_id=...` (caso venha do Funnel Architect).
- Formulario controlado por `CriarAnuncioDTO` em `$state`.
- Submit chama `AnuncioService.criar(dto)` -> redirect `/pipeline/[pipeline_id]`.
- Estados: inicial, submetendo, erro de validacao inline, erro backend, sucesso (redirect).

Componentes:

| Componente | Props | Eventos | Responsabilidade |
|-----------|-------|---------|------------------|
| `AnuncioBriefingForm` | `dto: CriarAnuncioDTO`, `disciplinas: Disciplina[]`, `fotos: FotoCriador[]` | `onChange(dto)`, `onSubmit(dto)`, `onCancelar()` | Formulario completo com tabs texto/disciplina + selecao de foto |
| `FotoCriadorGaleria` (reuso -- componente existente) | `fotos`, `selecionadaId` | `onSelecionar(id)` | Galeria de fotos |

### 8.3 `/anuncios/[id]` -- Detalhe do Anuncio (Tela 3)

**`routes/anuncios/[id]/+page.svelte`**

Responsabilidades:
- Carrega `AnuncioService.obter(id)` no mount.
- Estados: loading, nao_encontrado, erro, em_andamento, parcial, concluido, excluido.
- Aciona `AnuncioService.baixarZip(id)` / `salvarNoDrive(id)` / `excluir(id)`.

Componentes:

| Componente | Props | Eventos | Responsabilidade |
|-----------|-------|---------|------------------|
| `AnuncioStatusBadge` | `status`, `dimensoesOk` | -- | Badge topo da pagina |
| `AnuncioCopyDisplay` | `copy: AnuncioCopyDTO` | -- | Exibe headline + descricao com botao "Copiar" por campo |
| `AnuncioDimensoesGrid` | `dimensoes: AnuncioDimensaoDTO[]`, `readonly: true` | `onAmpliar(dim)`, `onRegerar(dim)` (so se `parcial`) | Grid 2x2 das 4 dimensoes |
| `AnuncioDimensaoCard` | `dimensao: AnuncioDimensaoDTO`, `readonly: boolean` | `onAmpliar()`, `onRegerar()` | 1 card com imagem + badge + acoes |
| `AnuncioImageZoomModal` | `imagemUrl`, `aspectRatio`, `aberto` | `onFechar()` | Modal fullscreen |
| `AnuncioDriveActions` | `anuncio: AnuncioDTO` | `onBaixarZip()`, `onAbrirDrive()`, `onSalvarDrive()` | Botoes de export |
| `AnuncioExcluirModal` | `anuncio`, `aberto` | `onConfirmar()`, `onCancelar()` | Modal exclusao |

### 8.4 `/anuncios/[id]/editar` -- Editar Anuncio (Tela 4)

**`routes/anuncios/[id]/editar/+page.svelte`**

Responsabilidades:
- Carrega anuncio no mount.
- Dois fluxos independentes:
  - **Salvar copy**: chama `AnuncioService.editarCopy(dto)` -> toast.
  - **Regerar dimensoes**: abre `AnuncioRegenerarModal`, confirma -> chama `AnuncioService.regerarDimensoes(dto)` -> marca dims como "regenerando" no store.
- Estados por secao (copy-carregada, copy-salvando, copy-erro; dimensao-regenerando, dimensao-regenerada, dimensao-falhou).

Componentes:

| Componente | Props | Eventos | Responsabilidade |
|-----------|-------|---------|------------------|
| `AnuncioCopyEditor` | `dto: EditarAnuncioCopyDTO` | `onChange(dto)`, `onSalvar(dto)` | Inputs titulo + headline + descricao + select etapa_funil, com contadores (30/90) e validacao inline |
| `AnuncioDimensoesGrid` | `dimensoes`, `readonly: false`, `regeneracoes: Set<DimensaoId>` | `onAmpliar(dim)`, `onToggleSelecao(dim)`, `onRegerarUma(dim)` | Grid com checkboxes de selecao |
| `AnuncioDimensaoCard` | `dimensao`, `readonly: false`, `estaRegenerando: boolean`, `selecionada: boolean` | `onToggleSelecao()`, `onRegerar()`, `onAmpliar()` | Card com checkbox + acao inline |
| `AnuncioRegenerarModal` | `dimensoesAlvo: DimensaoId[]`, `aberto: boolean` | `onConfirmar(feedback)`, `onCancelar()` | Modal com textarea feedback + info do modelo Gemini por dimensao |
| `AnuncioExcluirModal` | idem | idem | Modal exclusao |

### 8.5 Modais (Telas 5 e 6)

Ambos implementados como **componentes** (nao rotas), exibidos como overlays sobre a pagina atual.

**`AnuncioExcluirModal.svelte`**:
- Props: `anuncio: AnuncioDTO`, `aberto: boolean`.
- Eventos: `onConfirmar()`, `onCancelar()`.
- Usa `Modal.svelte` generico de `ui/`.

**`AnuncioRegenerarModal.svelte`**:
- Props: `dimensoesAlvo: DimensaoId[]`, `aberto: boolean`.
- Eventos: `onConfirmar(feedback: string)`, `onCancelar()`.
- Interno: textarea `feedback_livre` em `$state`, exibe modelo Gemini que sera usado por dimensao (derivado de `dimensao_id`).

---

## 9. Integracoes com Telas Existentes

### 9.1 Home / Criar Conteudo (`routes/+page.svelte`)

Arquivo a tocar: `src/lib/components/home/FormatoSelector.svelte` (ja existe).

Alteracoes:
- Adicionar card `Anuncio` no array de formatos.
- Icone sugerido: megafone / target (decisao do Agente 05 Designer).
- Ao submeter com `formato=anuncio` selecionado, seguir o mesmo fluxo ja existente (`PipelineService.iniciar(...)` + redirect `/pipeline/[id]`). Nao ha branch adicional no frontend aqui.

Arquivos a tocar:
- `src/lib/components/home/FormatoSelector.svelte` -- adicionar opcao.
- `src/lib/dtos/IniciarPipelineDTO.ts` -- aceitar `'anuncio'` em `formatos`.
- `src/lib/dtos/PipelineDTO.ts` -- incluir `'anuncio'` em `FormatoConteudo` + `formatoLabel`.

### 9.2 Funnel Architect (`routes/pipeline/[id]/briefing/+page.svelte`)

Arquivo a tocar: `src/lib/components/briefing/FunilPlanner.svelte`.

Alteracoes:
- O `select` de formato por peca do funil aceita `anuncio` como opcao.
- Nenhum componente novo; apenas o union type de formatos.

### 9.3 Historico (`routes/historico/+page.svelte`)

Arquivos a tocar:
- `src/lib/components/historico/HistoricoFiltros.svelte` -- adicionar opcao `Anuncio` no filtro de formato.
- `src/lib/components/historico/HistoricoCard.svelte` -- quando `item.formato === 'anuncio'`:
  - `thumbnailUrl` vem de `item.image_urls[1]` (dimensao 1080x1080).
  - Mostra badge "Anuncio".
  - Mostra indicador "N/4 dimensoes".
  - Clique em "Ver detalhes" navega para `/anuncios/[id]` (e nao `/pipeline/[id]/export`).
- `src/lib/dtos/HistoricoItemDTO.ts` -- aceitar `formato='anuncio'` + getter `isAnuncio` + `thumbnailUrl` condicional.

### 9.4 Kanban (`routes/kanban/+page.svelte`)

Arquivos a tocar:
- `src/lib/components/kanban/KanbanCard.svelte` -- se `card.formato === 'anuncio'`:
  - Badge "Anuncio" ao lado da prioridade.
  - Linha discreta "4 dimensoes" ou "3/4 dimensoes".
  - Thumbnail = `image_urls[1]` (1080x1080).
- `src/lib/components/kanban/CardDetailTab.svelte` -- quando `card.formato === 'anuncio'`:
  - Esconde campos de copy editavel.
  - Exibe `AnuncioCopyDisplay` (readonly, reuso de `components/anuncio/`).
  - Exibe `AnuncioDimensoesGrid` (readonly, reuso).
  - Exibe link "Abrir no modulo Anuncios" -> `/anuncios/[id]`.
- `src/lib/dtos/CardDTO.ts` -- se nao ha campo `formato`, acrescentar `readonly formato` + `readonly anuncio_id` (opcional). Avaliar no checkpoint com Agente 03 (backend).

### 9.5 Pipeline AP-4 (`routes/pipeline/[id]/imagem/+page.svelte`)

Alteracoes na pagina:
- Branch `if (pipeline.formato === 'anuncio')`: renderiza `AnuncioDimensoesGrid` (reuso de `components/anuncio/`) ao inves do grid de slides/variacoes.
- Botoes de aprovacao usam a mesma API ja existente (`PipelineService.aprovar`, `rejeitar`, `regerar`). Reutiliza.
- Se alguma dimensao esta em `falhou` apos 2 retries, o botao muda para "Aprovar mesmo assim (parcial)" (RN-019 / DT-A06).

### 9.6 Pipeline Export (`routes/pipeline/[id]/export/+page.svelte`)

Alteracoes:
- Branch `if (pipeline.formato === 'anuncio')`:
  - Oculta "Exportar PDF".
  - Mostra `AnuncioDriveActions` (botoes "Baixar ZIP" e "Salvar no Drive").
  - Mostra `AnuncioCopyDisplay` + `AnuncioDimensoesGrid` (readonly).
  - Mostra preview do `copy.txt` (usando `AnuncioCopyDTO.copyTxtPreview`).

### 9.7 Configuracoes (`routes/configuracoes/+page.svelte`)

Arquivos a tocar:
- `src/lib/components/config/PlatformRulesForm.svelte` -- passa a listar "Google Ads Display" com campos readonly: `headline_max=30`, `descricao_max=90`, `dimensoes=[1200x628, 1080x1080, 300x600, 300x250]`.
- `src/lib/dtos/PlatformRuleDTO.ts` -- aceitar campo `dimensoes: string[]` (array) quando plataforma for Google Ads (RN-011).

### 9.8 Sidebar (`src/lib/components/layout/Sidebar.svelte`)

Alteracao:
- Adicionar item `{ label: 'Anuncios', rota: '/anuncios', icone: 'megaphone' }` entre Kanban e Historico.
- Visivel para perfis Marketing e Admin (RN-022 -- ja abrangido pelo auth guard existente).

---

## 10. Fluxos de Dados por Caso de Uso

### 10.1 CriarAnuncio (avulso)

```
/anuncios/novo (+page.svelte)
  │  user preenche form -> $state: CriarAnuncioDTO
  │  submit:
  ↓
AnuncioService.criar(dto)
  │  valida dto.isValid() -> throw se invalido
  ↓
AnuncioRepository.criar(dto)
  │  if USE_MOCK: sleep + retorna UUIDs fake
  │  else: fetch POST /api/anuncios + dto.toPayload()
  ↓
retorna { anuncio_id, pipeline_id }
  │
  ↓
goto(`/pipeline/${pipeline_id}`)    // SvelteKit navigation
```

### 10.2 ListarAnuncios

```
/anuncios (+page.svelte)
  │  onMount + $effect([anuncioStore.filtro]):
  ↓
AnuncioService.listar(anuncioStore.filtro)
  ↓
AnuncioRepository.listar(filtro)
  │  if USE_MOCK: filtrarAnunciosMock(filtro.toPayload()).map(new AnuncioDTO)
  │  else: fetch GET /api/anuncios?{filtro.queryString} -> .map(new AnuncioDTO)
  ↓
service filtra por .isValid() -> retorna AnuncioDTO[]
  │
  ↓
<AnuncioCard anuncio={dto} /> (por item)
  │  $derived: dto.statusLabel, dto.thumbnailUrl, dto.dimensoesOkCount
```

### 10.3 ObterAnuncio

```
/anuncios/[id] (+page.svelte)
  │  $effect -> AnuncioService.obter(params.id)
  ↓
AnuncioRepository.obterPorId(id)
  │  mock: buscarAnuncioMockPorId(id); else: fetch GET /api/anuncios/{id}
  ↓
new AnuncioDTO(data)
  │
  ↓
<AnuncioCopyDisplay copy={dto.copy} />
<AnuncioDimensoesGrid dimensoes={dto.dimensoes} readonly={true} />
<AnuncioDriveActions anuncio={dto} />
```

### 10.4 EditarAnuncio -- Salvar Copy

```
/anuncios/[id]/editar (+page.svelte)
  │  <AnuncioCopyEditor dto={editDto} onSalvar={handleSalvar} />
  │  handleSalvar(novoDto):
  ↓
AnuncioService.editarCopy(novoDto)
  │  valida novoDto.isValid() (titulo >= 3, headline 1-30, descricao 1-90)
  ↓
AnuncioRepository.editarCopy(dto)
  │  mock: atualiza em memoria e retorna novo DTO
  │  else: PUT /api/anuncios/{id}/copy
  ↓
retorna AnuncioDTO atualizado
  │
  ↓
toast "Copy salva" + atualiza local state
```

### 10.5 EditarAnuncio -- Regerar Dimensoes (RN-018)

```
/anuncios/[id]/editar (+page.svelte)
  │  user marca checkboxes -> $state: selecionadas: DimensaoId[]
  │  clica "Regerar dimensoes selecionadas"
  ↓
<AnuncioRegenerarModal aberto={true} dimensoesAlvo={selecionadas} />
  │  user escreve feedback + confirma
  ↓
AnuncioService.regerarDimensoes(new RegerarDimensaoDTO({ anuncio_id, dimensoes_alvo, feedback_livre }))
  ↓
AnuncioRepository.regerarDimensoes(dto)
  │  mock: retorna job_id fake
  │  else: POST /api/anuncios/{id}/regenerar
  ↓
anuncioStore.marcarRegenerando(anuncio_id, dimensoes_alvo)
  │  UI refleteimediatamente: cada dimensao-alvo mostra spinner
  ↓
(backend processa e atualiza async)
  │
  ↓
$effect polling (ou refetch no mount) -> AnuncioService.obter(id)
  │  atualiza DTO, anuncioStore.marcarRegenerado(id, dim)
  ↓
toast "Dimensao 300x600 regenerada"
```

### 10.6 ExcluirAnuncio (Soft Delete, RN-013)

```
qualquer tela (lista/detalhe/editar)
  │  clique em Excluir
  ↓
<AnuncioExcluirModal aberto />
  │  user confirma
  ↓
AnuncioService.excluir(id)
  ↓
AnuncioRepository.excluir(id)
  │  mock: sleep; else: DELETE /api/anuncios/{id}
  ↓
origin === lista: refetch + remove card
origin === detalhe/editar: goto('/anuncios')
toast "Anuncio excluido"
```

### 10.7 Export Drive / ZIP

```
/anuncios/[id] ou /pipeline/[id]/export
  │  user clica "Salvar no Drive"
  ↓
AnuncioService.salvarNoDrive(id)
  ↓
AnuncioRepository.salvarNoDrive(id)
  │  mock: retorna link fake; else: POST /api/anuncios/{id}/drive
  ↓
retorna { drive_folder_link }
  │
  ↓
atualiza local state + toast com link
```

---

## 11. Codigo-Base por Modulo -- Esqueleto

Assinaturas prontas para o Agente 06 (Dev Mockado) e Agente 09 (Dev Frontend) implementarem. Imports + interfaces, sem implementacao.

### 11.1 DTOs -- esqueleto

```typescript
// src/lib/dtos/AnuncioDimensaoDTO.ts
export type DimensaoId = '1200x628' | '1080x1080' | '300x600' | '300x250';
export type BrandGateStatus = 'valido' | 'revisao_manual' | 'falhou' | 'nao_gerada';
export type OverlayTipo = 'foto+logo' | 'so_logo';
export type ModeloGemini = 'gemini-pro' | 'gemini-flash';

export class AnuncioDimensaoDTO {
  readonly dimensao_id: DimensaoId;
  readonly imagem_url: string;
  readonly brand_gate_status: BrandGateStatus;
  readonly brand_gate_retries: number;
  readonly modelo_usado: ModeloGemini;
  readonly overlay_tipo: OverlayTipo;
  readonly largura: number;
  readonly altura: number;
  readonly regenerada_em: string;

  constructor(data: Record<string, any>) {
    this.dimensao_id = data.dimensao_id ?? '1200x628';
    this.imagem_url = data.imagem_url ?? '';
    this.brand_gate_status = data.brand_gate_status ?? 'nao_gerada';
    this.brand_gate_retries = data.brand_gate_retries ?? 0;
    this.modelo_usado = data.modelo_usado ?? 'gemini-flash';
    this.overlay_tipo = data.overlay_tipo ?? 'so_logo';
    this.largura = data.largura ?? 0;
    this.altura = data.altura ?? 0;
    this.regenerada_em = data.regenerada_em ?? '';
  }

  get aspectRatio(): string {
    if (this.largura === 0 || this.altura === 0) return '';
    const gcd = (a: number, b: number): number => b === 0 ? a : gcd(b, a % b);
    const g = gcd(this.largura, this.altura);
    return `${this.largura / g}:${this.altura / g}`;
  }

  get isValida(): boolean {
    return this.brand_gate_status === 'valido' && this.imagem_url.length > 0;
  }

  get isFalha(): boolean {
    return this.brand_gate_status === 'falhou';
  }

  get isNaoGerada(): boolean {
    return this.brand_gate_status === 'nao_gerada';
  }

  get temOverlayFoto(): boolean {
    return this.overlay_tipo === 'foto+logo';
  }

  get statusLabel(): string {
    const labels: Record<BrandGateStatus, string> = {
      valido: 'Brand Gate OK',
      revisao_manual: 'Revisao manual',
      falhou: 'Falhou',
      nao_gerada: 'Aguardando'
    };
    return labels[this.brand_gate_status];
  }

  get labelCompleto(): string {
    const kindByDim: Record<DimensaoId, string> = {
      '1200x628': 'landscape',
      '1080x1080': 'square',
      '300x600': 'half page',
      '300x250': 'medium rectangle'
    };
    const modelo = this.modelo_usado === 'gemini-pro' ? 'Gemini Pro' : 'Gemini Flash';
    return `${this.dimensao_id} (${kindByDim[this.dimensao_id]}) - ${modelo}`;
  }

  get estiloGrid(): string {
    // Mapeamento para classes Tailwind do grid 2x2 responsivo.
    // Detalhes finais ficam com o Agente 05 (Designer).
    const map: Record<DimensaoId, string> = {
      '1200x628': 'col-span-2 aspect-[1200/628]',
      '1080x1080': 'col-span-1 aspect-square',
      '300x600': 'col-span-1 aspect-[300/600]',
      '300x250': 'col-span-1 aspect-[300/250]'
    };
    return map[this.dimensao_id];
  }

  isValid(): boolean {
    return (['1200x628', '1080x1080', '300x600', '300x250'] as DimensaoId[]).includes(this.dimensao_id);
  }

  toPayload(): Record<string, any> {
    return {
      dimensao_id: this.dimensao_id,
      imagem_url: this.imagem_url,
      brand_gate_status: this.brand_gate_status,
      brand_gate_retries: this.brand_gate_retries,
      modelo_usado: this.modelo_usado,
      overlay_tipo: this.overlay_tipo,
      largura: this.largura,
      altura: this.altura
    };
  }
}
```

```typescript
// src/lib/dtos/AnuncioCopyDTO.ts
export const HEADLINE_MAX = 30;
export const DESCRICAO_MAX = 90;

export class AnuncioCopyDTO {
  readonly headline: string;
  readonly descricao: string;

  constructor(data: Record<string, any>) {
    this.headline = data.headline ?? '';
    this.descricao = data.descricao ?? '';
  }

  get headlineLength(): number { return this.headline.length; }
  get descricaoLength(): number { return this.descricao.length; }
  get headlineExcedido(): boolean { return this.headlineLength > HEADLINE_MAX; }
  get descricaoExcedido(): boolean { return this.descricaoLength > DESCRICAO_MAX; }
  get headlineRestante(): number { return HEADLINE_MAX - this.headlineLength; }
  get descricaoRestante(): number { return DESCRICAO_MAX - this.descricaoLength; }

  get copyTxtPreview(): string {
    return `Headline: ${this.headline}\nDescricao: ${this.descricao}\n`;
  }

  isValid(): boolean {
    return this.headlineLength >= 1 && this.headlineLength <= HEADLINE_MAX
      && this.descricaoLength >= 1 && this.descricaoLength <= DESCRICAO_MAX;
  }

  toPayload(): Record<string, any> {
    return { headline: this.headline, descricao: this.descricao };
  }
}
```

```typescript
// src/lib/dtos/AnuncioDTO.ts
import { AnuncioDimensaoDTO, type DimensaoId } from './AnuncioDimensaoDTO';
import { AnuncioCopyDTO } from './AnuncioCopyDTO';

export type AnuncioStatus = 'em_andamento' | 'concluido' | 'parcial' | 'erro' | 'cancelado';
export type EtapaFunil = 'topo' | 'meio' | 'fundo' | 'avulso';

export class AnuncioDTO {
  readonly id: string;
  readonly tenant_id: string;
  readonly titulo: string;
  readonly copy: AnuncioCopyDTO;
  readonly status: AnuncioStatus;
  readonly etapa_funil: EtapaFunil;
  readonly pipeline_id: string;
  readonly pipeline_funil_id: string;
  readonly dimensoes: AnuncioDimensaoDTO[];
  readonly drive_folder_link: string;
  readonly criado_por: string;
  readonly created_at: string;
  readonly updated_at: string;
  readonly deleted_at: string;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? '';
    this.tenant_id = data.tenant_id ?? '';
    this.titulo = data.titulo ?? '';
    this.copy = new AnuncioCopyDTO(data.copy ?? {});
    this.status = data.status ?? 'em_andamento';
    this.etapa_funil = data.etapa_funil ?? 'avulso';
    this.pipeline_id = data.pipeline_id ?? '';
    this.pipeline_funil_id = data.pipeline_funil_id ?? '';
    this.dimensoes = (data.dimensoes ?? []).map((d: any) => new AnuncioDimensaoDTO(d));
    this.drive_folder_link = data.drive_folder_link ?? '';
    this.criado_por = data.criado_por ?? '';
    this.created_at = data.created_at ?? '';
    this.updated_at = data.updated_at ?? '';
    this.deleted_at = data.deleted_at ?? '';
  }

  get isConcluido(): boolean { return this.status === 'concluido'; }
  get isParcial(): boolean { return this.status === 'parcial'; }
  get isEmAndamento(): boolean { return this.status === 'em_andamento'; }
  get isErro(): boolean { return this.status === 'erro'; }
  get isDeletado(): boolean { return this.deleted_at.length > 0; }

  get dimensoesOkCount(): number {
    return this.dimensoes.filter(d => d.isValida).length;
  }

  get dimensoesTotalCount(): number {
    return 4;  // RN-001 no MVP
  }

  get statusLabel(): string {
    const labels: Record<AnuncioStatus, string> = {
      em_andamento: 'Em andamento',
      concluido: 'Concluido',
      parcial: `Parcial (${this.dimensoesOkCount}/${this.dimensoesTotalCount})`,
      erro: 'Erro',
      cancelado: 'Cancelado'
    };
    return labels[this.status];
  }

  get etapaFunilLabel(): string {
    const labels: Record<EtapaFunil, string> = {
      topo: 'Topo', meio: 'Meio', fundo: 'Fundo', avulso: 'Avulso'
    };
    return labels[this.etapa_funil];
  }

  get thumbnailUrl(): string {
    const square = this.dimensoes.find(d => d.dimensao_id === '1080x1080');
    return square?.imagem_url ?? '';
  }

  get tituloTruncado(): string {
    return this.titulo.length > 50 ? this.titulo.slice(0, 47) + '...' : this.titulo;
  }

  get driveFolderName(): string {
    const date = this.created_at.slice(0, 10);  // YYYY-MM-DD
    return `${this.titulo} - ${date}`;
  }

  get hasDriveLink(): boolean { return this.drive_folder_link.length > 0; }

  get podeExportar(): boolean {
    return this.isConcluido || this.isParcial;
  }

  dimensaoPorId(id: DimensaoId): AnuncioDimensaoDTO | undefined {
    return this.dimensoes.find(d => d.dimensao_id === id);
  }

  isValid(): boolean {
    return this.id.length > 0
      && this.titulo.length >= 3
      && this.dimensoes.length === 4
      && this.copy.isValid();
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      tenant_id: this.tenant_id,
      titulo: this.titulo,
      copy: this.copy.toPayload(),
      status: this.status,
      etapa_funil: this.etapa_funil,
      pipeline_id: this.pipeline_id,
      pipeline_funil_id: this.pipeline_funil_id,
      dimensoes: this.dimensoes.map(d => d.toPayload()),
      drive_folder_link: this.drive_folder_link
    };
  }
}
```

```typescript
// src/lib/dtos/CriarAnuncioDTO.ts
import type { EtapaFunil } from './AnuncioDTO';

export type ModoEntrada = 'texto' | 'disciplina';

export class CriarAnuncioDTO {
  readonly titulo: string;
  readonly tema_ou_briefing: string;
  readonly modo_entrada: ModoEntrada;
  readonly disciplina: string;
  readonly tecnologia: string;
  readonly etapa_funil: EtapaFunil;
  readonly pipeline_funil_id: string;
  readonly foto_criador_id: string;

  constructor(data: Record<string, any>) {
    this.titulo = (data.titulo ?? '').trim();
    this.tema_ou_briefing = (data.tema_ou_briefing ?? '').trim();
    this.modo_entrada = data.modo_entrada ?? 'texto';
    this.disciplina = data.disciplina ?? '';
    this.tecnologia = data.tecnologia ?? '';
    this.etapa_funil = data.etapa_funil ?? 'avulso';
    this.pipeline_funil_id = data.pipeline_funil_id ?? '';
    this.foto_criador_id = data.foto_criador_id ?? '';
  }

  get tituloValido(): boolean { return this.titulo.length >= 3; }
  get temaValido(): boolean { return this.tema_ou_briefing.length >= 20; }
  get precisaDisciplina(): boolean { return this.modo_entrada === 'disciplina'; }
  get vindoDoFunil(): boolean { return this.pipeline_funil_id.length > 0; }

  isValid(): boolean {
    if (!this.tituloValido) return false;
    if (!this.temaValido) return false;
    if (this.precisaDisciplina && (this.disciplina === '' || this.tecnologia === '')) return false;
    return true;
  }

  toPayload(): Record<string, any> {
    return {
      titulo: this.titulo,
      tema_ou_briefing: this.tema_ou_briefing,
      modo_entrada: this.modo_entrada,
      disciplina: this.disciplina,
      tecnologia: this.tecnologia,
      etapa_funil: this.etapa_funil,
      pipeline_funil_id: this.pipeline_funil_id,
      foto_criador_id: this.foto_criador_id,
      formato: 'anuncio'  // explicito para o pipeline
    };
  }
}
```

```typescript
// src/lib/dtos/ListarAnunciosFiltroDTO.ts
import type { AnuncioStatus, EtapaFunil } from './AnuncioDTO';

export class ListarAnunciosFiltroDTO {
  readonly busca: string;
  readonly status: AnuncioStatus | 'todos';
  readonly etapa_funil: EtapaFunil | 'todas';
  readonly data_inicio: string;
  readonly data_fim: string;
  readonly incluir_excluidos: boolean;

  constructor(data: Record<string, any>) {
    this.busca = data.busca ?? '';
    this.status = data.status ?? 'todos';
    this.etapa_funil = data.etapa_funil ?? 'todas';
    this.data_inicio = data.data_inicio ?? '';
    this.data_fim = data.data_fim ?? '';
    this.incluir_excluidos = data.incluir_excluidos ?? false;
  }

  get temFiltroAtivo(): boolean {
    return this.busca !== ''
      || this.status !== 'todos'
      || this.etapa_funil !== 'todas'
      || this.data_inicio !== ''
      || this.data_fim !== ''
      || this.incluir_excluidos;
  }

  get queryString(): string {
    const p = new URLSearchParams();
    if (this.busca) p.set('q', this.busca);
    if (this.status !== 'todos') p.set('status', this.status);
    if (this.etapa_funil !== 'todas') p.set('etapa_funil', this.etapa_funil);
    if (this.data_inicio) p.set('data_inicio', this.data_inicio);
    if (this.data_fim) p.set('data_fim', this.data_fim);
    if (this.incluir_excluidos) p.set('incluir_excluidos', '1');
    return p.toString();
  }

  isValid(): boolean { return true; }

  toPayload(): Record<string, any> {
    return {
      busca: this.busca,
      status: this.status,
      etapa_funil: this.etapa_funil,
      data_inicio: this.data_inicio,
      data_fim: this.data_fim,
      incluir_excluidos: this.incluir_excluidos
    };
  }
}
```

```typescript
// src/lib/dtos/EditarAnuncioCopyDTO.ts
import type { EtapaFunil } from './AnuncioDTO';
import { HEADLINE_MAX, DESCRICAO_MAX } from './AnuncioCopyDTO';

export class EditarAnuncioCopyDTO {
  readonly id: string;
  readonly titulo: string;
  readonly headline: string;
  readonly descricao: string;
  readonly etapa_funil: EtapaFunil;

  constructor(data: Record<string, any>) {
    this.id = data.id ?? '';
    this.titulo = (data.titulo ?? '').trim();
    this.headline = data.headline ?? '';
    this.descricao = data.descricao ?? '';
    this.etapa_funil = data.etapa_funil ?? 'avulso';
  }

  get tituloValido(): boolean { return this.titulo.length >= 3; }
  get headlineValido(): boolean { return this.headline.length >= 1 && this.headline.length <= HEADLINE_MAX; }
  get descricaoValido(): boolean { return this.descricao.length >= 1 && this.descricao.length <= DESCRICAO_MAX; }

  isValid(): boolean {
    return this.id.length > 0 && this.tituloValido && this.headlineValido && this.descricaoValido;
  }

  toPayload(): Record<string, any> {
    return {
      id: this.id,
      titulo: this.titulo,
      headline: this.headline,
      descricao: this.descricao,
      etapa_funil: this.etapa_funil
    };
  }
}
```

```typescript
// src/lib/dtos/RegerarDimensaoDTO.ts
import type { DimensaoId } from './AnuncioDimensaoDTO';

export class RegerarDimensaoDTO {
  readonly anuncio_id: string;
  readonly dimensoes_alvo: DimensaoId[];
  readonly feedback_livre: string;
  readonly manter_prompt_base: boolean;

  constructor(data: Record<string, any>) {
    this.anuncio_id = data.anuncio_id ?? '';
    this.dimensoes_alvo = data.dimensoes_alvo ?? [];
    this.feedback_livre = (data.feedback_livre ?? '').trim();
    this.manter_prompt_base = data.manter_prompt_base ?? true;
  }

  get feedbackDentroLimite(): boolean { return this.feedback_livre.length <= 500; }
  get dimensoesValidas(): boolean {
    return this.dimensoes_alvo.length >= 1 && this.dimensoes_alvo.length <= 4;
  }

  isValid(): boolean {
    return this.anuncio_id.length > 0 && this.dimensoesValidas && this.feedbackDentroLimite;
  }

  toPayload(): Record<string, any> {
    return {
      anuncio_id: this.anuncio_id,
      dimensoes_alvo: this.dimensoes_alvo,
      feedback_livre: this.feedback_livre,
      manter_prompt_base: this.manter_prompt_base
    };
  }
}
```

### 11.2 Service -- esqueleto

```typescript
// src/lib/services/AnuncioService.ts
import { AnuncioRepository } from '$lib/repositories/AnuncioRepository';
import type { AnuncioDTO } from '$lib/dtos/AnuncioDTO';
import type { CriarAnuncioDTO } from '$lib/dtos/CriarAnuncioDTO';
import type { EditarAnuncioCopyDTO } from '$lib/dtos/EditarAnuncioCopyDTO';
import type { ListarAnunciosFiltroDTO } from '$lib/dtos/ListarAnunciosFiltroDTO';
import type { RegerarDimensaoDTO } from '$lib/dtos/RegerarDimensaoDTO';

export class AnuncioService {
  static async listar(filtro: ListarAnunciosFiltroDTO): Promise<AnuncioDTO[]> {
    if (!filtro.isValid()) throw new Error('Filtro invalido');
    const anuncios = await AnuncioRepository.listar(filtro);
    return anuncios.filter(a => a.isValid());
  }

  static async obter(id: string): Promise<AnuncioDTO> {
    if (!id || id.length === 0) throw new Error('ID invalido');
    return AnuncioRepository.obterPorId(id);
  }

  static async criar(dto: CriarAnuncioDTO): Promise<{ anuncio_id: string; pipeline_id: string }> {
    if (!dto.isValid()) throw new Error('Dados de criacao invalidos');
    return AnuncioRepository.criar(dto);
  }

  static async editarCopy(dto: EditarAnuncioCopyDTO): Promise<AnuncioDTO> {
    if (!dto.isValid()) throw new Error('Copy invalida (limites 30/90 violados ou titulo curto)');
    return AnuncioRepository.editarCopy(dto);
  }

  static async regerarDimensoes(dto: RegerarDimensaoDTO): Promise<{ anuncio_id: string; job_id: string }> {
    if (!dto.isValid()) throw new Error('Parametros de regeneracao invalidos');
    return AnuncioRepository.regerarDimensoes(dto);
  }

  static async excluir(id: string): Promise<void> {
    if (!id || id.length === 0) throw new Error('ID invalido');
    return AnuncioRepository.excluir(id);
  }

  static async baixarZip(id: string): Promise<Blob> {
    if (!id || id.length === 0) throw new Error('ID invalido');
    return AnuncioRepository.baixarZip(id);
  }

  static async salvarNoDrive(id: string): Promise<{ drive_folder_link: string }> {
    if (!id || id.length === 0) throw new Error('ID invalido');
    return AnuncioRepository.salvarNoDrive(id);
  }
}
```

### 11.3 Store -- esqueleto

```typescript
// src/lib/stores/anuncio.svelte.ts
import { ListarAnunciosFiltroDTO } from '$lib/dtos/ListarAnunciosFiltroDTO';
import type { DimensaoId } from '$lib/dtos/AnuncioDimensaoDTO';

class AnuncioStore {
  filtro = $state(new ListarAnunciosFiltroDTO({}));
  regeracoesEmAndamento = $state<Record<string, Set<DimensaoId>>>({});

  resetFiltros(): void {
    this.filtro = new ListarAnunciosFiltroDTO({});
  }

  aplicarFiltros(novo: ListarAnunciosFiltroDTO): void {
    this.filtro = novo;
  }

  marcarRegenerando(anuncioId: string, dims: DimensaoId[]): void {
    const atual = this.regeracoesEmAndamento[anuncioId] ?? new Set<DimensaoId>();
    dims.forEach(d => atual.add(d));
    this.regeracoesEmAndamento = { ...this.regeracoesEmAndamento, [anuncioId]: atual };
  }

  marcarRegenerado(anuncioId: string, dim: DimensaoId): void {
    const atual = this.regeracoesEmAndamento[anuncioId];
    if (!atual) return;
    atual.delete(dim);
    this.regeracoesEmAndamento = { ...this.regeracoesEmAndamento, [anuncioId]: atual };
  }

  estaRegerando(anuncioId: string, dim: DimensaoId): boolean {
    return this.regeracoesEmAndamento[anuncioId]?.has(dim) ?? false;
  }

  limparRegeracoes(anuncioId: string): void {
    const { [anuncioId]: _, ...resto } = this.regeracoesEmAndamento;
    this.regeracoesEmAndamento = resto;
  }
}

export const anuncioStore = new AnuncioStore();
```

### 11.4 Componentes -- esqueletos selecionados

```svelte
<!-- src/lib/components/anuncio/AnuncioCard.svelte -->
<script lang="ts">
  import type { AnuncioDTO } from '$lib/dtos/AnuncioDTO';
  import AnuncioStatusBadge from './AnuncioStatusBadge.svelte';
  import AnuncioExportBadge from './AnuncioExportBadge.svelte';

  let { anuncio, onClick, onEditar, onExcluir, onAbrirDrive, onAbrirPipeline }: {
    anuncio: AnuncioDTO;
    onClick: (id: string) => void;
    onEditar: (id: string) => void;
    onExcluir: (id: string) => void;
    onAbrirDrive: (url: string) => void;
    onAbrirPipeline: (pipelineId: string) => void;
  } = $props();

  const thumb = $derived(anuncio.thumbnailUrl);
  const classe = $derived(anuncio.isDeletado ? 'opacity-50' : '');
</script>

<!-- layout: thumbnail + titulo + headline + badges + acoes -->
```

```svelte
<!-- src/lib/components/anuncio/AnuncioCopyEditor.svelte -->
<script lang="ts">
  import { EditarAnuncioCopyDTO } from '$lib/dtos/EditarAnuncioCopyDTO';
  import { HEADLINE_MAX, DESCRICAO_MAX } from '$lib/dtos/AnuncioCopyDTO';

  let { dto, onChange, onSalvar }: {
    dto: EditarAnuncioCopyDTO;
    onChange: (dto: EditarAnuncioCopyDTO) => void;
    onSalvar: (dto: EditarAnuncioCopyDTO) => void;
  } = $props();

  let titulo = $state(dto.toPayload().titulo);
  let headline = $state(dto.toPayload().headline);
  let descricao = $state(dto.toPayload().descricao);
  let etapa_funil = $state(dto.toPayload().etapa_funil);

  const dtoAtual = $derived(new EditarAnuncioCopyDTO({
    id: dto.toPayload().id, titulo, headline, descricao, etapa_funil
  }));
  const headlineCor = $derived(dtoAtual.headlineValido ? 'text-green-400' : 'text-red-400');
  const descricaoCor = $derived(dtoAtual.descricaoValido ? 'text-green-400' : 'text-red-400');
  const podeSalvar = $derived(dtoAtual.isValid());

  $effect(() => onChange(dtoAtual));
</script>

<!-- inputs + contadores + select etapa + botao Salvar copy -->
```

```svelte
<!-- src/lib/components/anuncio/AnuncioDimensoesGrid.svelte -->
<script lang="ts">
  import type { AnuncioDimensaoDTO, DimensaoId } from '$lib/dtos/AnuncioDimensaoDTO';
  import AnuncioDimensaoCard from './AnuncioDimensaoCard.svelte';

  let { dimensoes, readonly, regeracoes, selecionadas, onAmpliar, onToggleSelecao, onRegerar }: {
    dimensoes: AnuncioDimensaoDTO[];
    readonly: boolean;
    regeracoes?: Set<DimensaoId>;
    selecionadas?: Set<DimensaoId>;
    onAmpliar: (dim: AnuncioDimensaoDTO) => void;
    onToggleSelecao?: (id: DimensaoId) => void;
    onRegerar?: (id: DimensaoId) => void;
  } = $props();
</script>

<!-- grid 2 colunas em mobile, 2 em desktop mas com dimensao 1200x628 col-span-2 -->
```

```svelte
<!-- src/lib/components/anuncio/AnuncioRegenerarModal.svelte -->
<script lang="ts">
  import type { DimensaoId } from '$lib/dtos/AnuncioDimensaoDTO';
  import Modal from '$lib/components/ui/Modal.svelte';

  let { dimensoesAlvo, aberto, onConfirmar, onCancelar }: {
    dimensoesAlvo: DimensaoId[];
    aberto: boolean;
    onConfirmar: (feedback: string) => void;
    onCancelar: () => void;
  } = $props();

  let feedback = $state('');
  const feedbackValido = $derived(feedback.length <= 500);

  function modeloDaDimensao(d: DimensaoId): string {
    return d === '1200x628' ? 'Gemini Pro' : 'Gemini Flash';
  }
</script>

<!-- Modal com lista readonly das dimensoes + textarea feedback + botoes -->
```

```svelte
<!-- src/lib/components/anuncio/AnuncioExcluirModal.svelte -->
<script lang="ts">
  import type { AnuncioDTO } from '$lib/dtos/AnuncioDTO';
  import Modal from '$lib/components/ui/Modal.svelte';

  let { anuncio, aberto, onConfirmar, onCancelar }: {
    anuncio: AnuncioDTO;
    aberto: boolean;
    onConfirmar: () => void;
    onCancelar: () => void;
  } = $props();
</script>

<!-- Mensagem: "Excluir anuncio '{titulo}'? Arquivos no Drive permanecem." -->
```

### 11.5 Pagina -- esqueleto

```svelte
<!-- src/routes/anuncios/+page.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { AnuncioService } from '$lib/services/AnuncioService';
  import type { AnuncioDTO } from '$lib/dtos/AnuncioDTO';
  import { anuncioStore } from '$lib/stores/anuncio.svelte';
  import AnuncioFiltros from '$lib/components/anuncio/AnuncioFiltros.svelte';
  import AnuncioCard from '$lib/components/anuncio/AnuncioCard.svelte';
  import AnuncioExcluirModal from '$lib/components/anuncio/AnuncioExcluirModal.svelte';

  let anuncios = $state<AnuncioDTO[]>([]);
  let carregando = $state(true);
  let erro = $state('');
  let anuncioParaExcluir = $state<AnuncioDTO | null>(null);

  async function carregar() {
    try {
      carregando = true;
      erro = '';
      anuncios = await AnuncioService.listar(anuncioStore.filtro);
    } catch (e) {
      erro = e instanceof Error ? e.message : 'Erro ao carregar';
    } finally {
      carregando = false;
    }
  }

  onMount(carregar);
  $effect(() => { anuncioStore.filtro; carregar(); });

  async function confirmarExclusao() {
    if (!anuncioParaExcluir) return;
    await AnuncioService.excluir(anuncioParaExcluir.id);
    anuncioParaExcluir = null;
    await carregar();
  }
</script>

<!-- header + filtros + grid de cards + modal exclusao -->
```

```svelte
<!-- src/routes/anuncios/[id]/editar/+page.svelte -->
<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import { AnuncioService } from '$lib/services/AnuncioService';
  import { AnuncioDTO } from '$lib/dtos/AnuncioDTO';
  import { EditarAnuncioCopyDTO } from '$lib/dtos/EditarAnuncioCopyDTO';
  import { RegerarDimensaoDTO } from '$lib/dtos/RegerarDimensaoDTO';
  import type { DimensaoId } from '$lib/dtos/AnuncioDimensaoDTO';
  import { anuncioStore } from '$lib/stores/anuncio.svelte';
  import AnuncioCopyEditor from '$lib/components/anuncio/AnuncioCopyEditor.svelte';
  import AnuncioDimensoesGrid from '$lib/components/anuncio/AnuncioDimensoesGrid.svelte';
  import AnuncioRegenerarModal from '$lib/components/anuncio/AnuncioRegenerarModal.svelte';
  import AnuncioExcluirModal from '$lib/components/anuncio/AnuncioExcluirModal.svelte';

  let anuncio = $state<AnuncioDTO | null>(null);
  let carregando = $state(true);
  let selecionadas = $state<Set<DimensaoId>>(new Set());
  let modalRegerarAberto = $state(false);
  let modalExcluirAberto = $state(false);

  // ... handleSalvarCopy, handleRegerar, handleConfirmarRegerar, etc.
</script>
```

---

## 12. Checklist de Entrega por Caso de Uso

Para cada caso de uso, o dev feature entrega:

| Caso de Uso | DTO | Service | Repository | Mock | Componente | Rota |
|------------|-----|---------|-----------|------|-----------|------|
| CriarAnuncio | `CriarAnuncioDTO` | `criar()` | `criar()` | -- | `AnuncioBriefingForm` | `/anuncios/novo` |
| ListarAnuncios | `ListarAnunciosFiltroDTO`, `AnuncioDTO` | `listar()` | `listar()` + `filtrarAnunciosMock` | `anunciosMock` | `AnuncioCard`, `AnuncioFiltros`, `AnuncioStatusBadge`, `AnuncioExportBadge` | `/anuncios` |
| ObterAnuncio | `AnuncioDTO`, `AnuncioDimensaoDTO`, `AnuncioCopyDTO` | `obter()` | `obterPorId()` + `buscarAnuncioMockPorId` | idem | `AnuncioCopyDisplay`, `AnuncioDimensoesGrid`, `AnuncioDimensaoCard`, `AnuncioImageZoomModal`, `AnuncioDriveActions` | `/anuncios/[id]` |
| EditarAnuncio (copy) | `EditarAnuncioCopyDTO` | `editarCopy()` | `editarCopy()` | idem | `AnuncioCopyEditor` | `/anuncios/[id]/editar` |
| RegerarDimensao | `RegerarDimensaoDTO` | `regerarDimensoes()` | `regerarDimensoes()` | job fake | `AnuncioRegenerarModal` | modal em `/anuncios/[id]/editar` |
| ExcluirAnuncio | -- (id) | `excluir()` | `excluir()` | update mock | `AnuncioExcluirModal` | modal global |
| SalvarNoDrive | -- (id) | `salvarNoDrive()` | `salvarNoDrive()` | link fake | `AnuncioDriveActions` | acao em Detalhe e Export |
| BaixarZip | -- (id) | `baixarZip()` | `baixarZip()` | Blob fake | `AnuncioDriveActions` | acao em Detalhe e Export |

---

## 13. Duvidas em Aberto (para validacao com o P.O.)

Nenhuma duvida bloqueante. A cliente confirmou todas as decisoes no PRD (DA-001 a DA-010) e nas telas (DT-A01 a DT-A06). Pontos apenas de alinhamento com outros agentes (nao sao bloqueadores):

| ID | Ponto | Pra quem |
|----|-------|----------|
| FA-001 | `CardDTO` tera campo novo `formato: 'carrossel' \| 'post_unico' \| 'thumbnail_youtube' \| 'anuncio'` + `anuncio_id`? Ou o Kanban deduz o formato via join com pipeline? | Agente 03 (Backend) |
| FA-002 | Endpoint `/api/anuncios/{id}/zip` devolve ZIP do backend, ou o frontend gera localmente com JSZip? Implicacao: perf + dependencia. | Agente 03 (Backend) |
| FA-003 | Polling para acompanhar regeneracao de dimensao: o backend tera WebSocket ou o frontend faz polling GET a cada N segundos? | Agente 03 (Backend) |
| FA-004 | Imagens nas dimensoes do grid podem ter aspect ratio bem distinto (1200x628 largo vs 300x600 alto). O Designer decidira se o grid e 2x2 livre ou 2 colunas com 1200x628 ocupando largura total + 3 outras abaixo. | Agente 05 (Designer) |
| FA-005 | Icone do item "Anuncios" na Sidebar: megaphone, target, ad-fill? Decisao visual. | Agente 05 (Designer) |
| FA-006 | Badge "Anuncio" no Kanban precisa de cor nova (diferente de carrossel/post/thumbnail). | Agente 05 (Designer) |

Estes pontos nao bloqueiam o Dev Mockado (Agente 06) nem o Dev Frontend (Agente 09), que podem usar defaults razoaveis ate as decisoes saírem.

---

*Documento gerado pelo Agente 04 (Arquiteto IT Valley Frontend) da esteira IT Valley.*
*Fonte: `docs/prd-anuncios.md` + `docs/telas-anuncios.md` + `docs/ARQUITETURA_FRONTEND.md` + `docs/arquitetura-frontend-kanban.md`.*
*Proximo: Agente 06 (Dev Mockado) para mocks prontos + Agente 09 (Dev Frontend) para implementacao real apos Agente 10 (Dev Backend) subir as rotas.*
