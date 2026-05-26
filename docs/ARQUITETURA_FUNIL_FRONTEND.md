# Arquitetura Frontend — Modulo Funil

> Documento de arquitetura gerado pelo Agente 04 (Arquiteto IT Valley Frontend).
> Entrada: PRD-funil.md + contratos backend + codebase existente.
> Saida para: Dev Mockado (06) + Dev Frontend (09).

---

## 1. Dominios Identificados

### Dominio: Funil

Casos de uso:

| Caso de Uso | Rota | Endpoint Backend |
|---|---|---|
| VisualizarPlano | `/pipeline/{id}/funil-plano` | GET `/api/pipelines/{id}/funil/plano` |
| EditarPlano | `/pipeline/{id}/funil-plano` | PUT `/api/pipelines/{id}/funil/plano` |
| AprovarPlano | `/pipeline/{id}/funil-plano` | POST `/api/pipelines/{id}/funil/plano/aprovar` |
| RejeitarPlano | `/pipeline/{id}/funil-plano` | POST `/api/pipelines/{id}/funil/plano/rejeitar` |
| AcompanharPecas | `/pipeline/{id}/funil` | GET `/api/pipelines/{id}/funil/status` |
| ExportarFunil | `/pipeline/{id}/funil-export` | POST `/api/pipelines/{id}/funil/exportar` |

Dominios reutilizados (sem alteracao):
- **Pipeline** — PipelineDTO, PipelineService, PipelineRepository (ja existem)
- **UI** — Button, Badge, Modal, Spinner, Skeleton, Banner (ja existem)

---

## 2. Estrutura de Pastas

```
src/lib/
├── components/
│   ├── ui/                          # (existente — sem alteracao)
│   ├── pipeline/                    # (existente — sem alteracao)
│   └── funil/                       # NOVO — dominio funil
│       ├── FunilPecaCard.svelte     # Card de 1 peca (plano e painel)
│       ├── FunilProgressBar.svelte  # Barra de progresso geral (X de Y completas)
│       ├── FunilPecaTracker.svelte  # Status tracker de 1 peca no painel
│       ├── FunilExportCard.svelte   # Preview de 1 peca na tela de export
│       └── FunilExportBar.svelte    # Barra de acoes do export (Drive + Download)
│
├── dtos/
│   ├── FunilPlanoDTO.ts             # NOVO — plano completo do funil
│   ├── FunilPecaDTO.ts              # NOVO — 1 peca dentro do plano
│   └── FunilStatusDTO.ts            # NOVO — status de todas as pecas (polling)
│
├── services/
│   └── FunilService.ts              # NOVO — logica de negocio do funil
│
├── repositories/
│   └── FunilRepository.ts           # NOVO — acesso a dados (mock + real)
│
├── mocks/
│   └── funil.mock.ts                # NOVO — dados falsos realistas
│
src/routes/pipeline/[id]/
├── funil-plano/+page.svelte         # NOVO — revisar/editar/aprovar plano
├── funil/+page.svelte               # NOVO — painel de acompanhamento
└── funil-export/+page.svelte        # NOVO — export de todas as pecas
```

---

## 3. DTOs

### 3.1 FunilPecaDTO

Representa 1 peca dentro do plano do funil. Usada tanto na tela de plano (editavel) quanto no painel (somente leitura).

```typescript
// src/lib/dtos/FunilPecaDTO.ts

export type EtapaFunil = 'topo' | 'meio' | 'fundo' | 'conversao';
export type FormatoPeca = 'carrossel' | 'post_unico' | 'thumbnail_youtube' | 'capa_reels';
export type StatusPeca = 'pendente' | 'executando' | 'aguardando_aprovacao' | 'completo' | 'erro';

export class FunilPecaDTO {
  readonly ordem: number;
  readonly titulo: string;
  readonly etapa_funil: EtapaFunil;
  readonly formato: FormatoPeca;
  readonly angulo: string;
  readonly resumo: string;
  readonly gancho: string;
  readonly conexao_anterior: string | null;
  readonly cta_para_proxima: string | null;

  // Campos de acompanhamento (preenchidos pelo polling, nao pelo plano)
  readonly pipeline_id: string | null;
  readonly status: StatusPeca;
  readonly etapa_atual: string;
  readonly progresso_imagem: number; // 0-100

  constructor(data: Record<string, any>) {
    this.ordem = data.ordem ?? 0;
    this.titulo = data.titulo ?? '';
    this.etapa_funil = data.etapa_funil ?? 'topo';
    this.formato = data.formato ?? 'carrossel';
    this.angulo = data.angulo ?? '';
    this.resumo = data.resumo ?? '';
    this.gancho = data.gancho ?? '';
    this.conexao_anterior = data.conexao_anterior ?? null;
    this.cta_para_proxima = data.cta_para_proxima ?? null;
    this.pipeline_id = data.pipeline_id ?? null;
    this.status = data.status ?? 'pendente';
    this.etapa_atual = data.etapa_atual ?? '';
    this.progresso_imagem = data.progresso_imagem ?? 0;
  }

  // --- Getters derivados ---

  get etapaFunilLabel(): string {
    const labels: Record<EtapaFunil, string> = {
      topo: 'Topo de Funil',
      meio: 'Meio de Funil',
      fundo: 'Fundo de Funil',
      conversao: 'Conversao'
    };
    return labels[this.etapa_funil];
  }

  get etapaFunilAbreviada(): string {
    const labels: Record<EtapaFunil, string> = {
      topo: 'ToFu', meio: 'MoFu', fundo: 'BoFu', conversao: 'CTA'
    };
    return labels[this.etapa_funil];
  }

  get formatoLabel(): string {
    const labels: Record<FormatoPeca, string> = {
      carrossel: 'Carrossel',
      post_unico: 'Post Unico',
      thumbnail_youtube: 'Thumbnail YouTube',
      capa_reels: 'Capa Reels'
    };
    return labels[this.formato] ?? this.formato;
  }

  get isAguardandoAprovacao(): boolean {
    return this.status === 'aguardando_aprovacao';
  }

  get isCompleto(): boolean {
    return this.status === 'completo';
  }

  get isErro(): boolean {
    return this.status === 'erro';
  }

  get temSubPipeline(): boolean {
    return this.pipeline_id !== null && this.pipeline_id.length > 0;
  }

  // --- Metodos obrigatorios ---

  isValid(): boolean {
    return (
      this.ordem > 0 &&
      this.titulo.trim().length > 0 &&
      this.angulo.trim().length > 0 &&
      this.resumo.trim().length > 0
    );
  }

  toPayload(): Record<string, any> {
    return {
      ordem: this.ordem,
      titulo: this.titulo,
      etapa_funil: this.etapa_funil,
      formato: this.formato,
      angulo: this.angulo,
      resumo: this.resumo,
      gancho: this.gancho,
      conexao_anterior: this.conexao_anterior,
      cta_para_proxima: this.cta_para_proxima
    };
  }
}
```

### 3.2 FunilPlanoDTO

Representa o plano completo do funil (wrapper das pecas + metadados da narrativa).

```typescript
// src/lib/dtos/FunilPlanoDTO.ts

import { FunilPecaDTO } from './FunilPecaDTO';

export type StatusFunil = 'pendente_plano' | 'plano_aprovado' | 'executando' | 'completo' | 'cancelado';

export class FunilPlanoDTO {
  readonly funil_id: string;
  readonly pipeline_id: string;
  readonly tema_principal: string;
  readonly objetivo_campanha: string;
  readonly narrativa_geral: string;
  readonly pecas: FunilPecaDTO[];
  readonly status: StatusFunil;
  readonly created_at: string;
  readonly approved_at: string | null;

  constructor(data: Record<string, any>) {
    this.funil_id = data.funil_id ?? data.id ?? '';
    this.pipeline_id = data.pipeline_id ?? '';
    this.tema_principal = data.tema_principal ?? data.plano?.tema_principal ?? '';
    this.objetivo_campanha = data.objetivo_campanha ?? data.plano?.objetivo_campanha ?? '';
    this.narrativa_geral = data.narrativa_geral ?? data.plano?.narrativa_geral ?? '';
    this.status = data.status ?? 'pendente_plano';
    this.created_at = data.created_at ?? '';
    this.approved_at = data.approved_at ?? null;

    const rawPecas = data.pecas ?? data.plano?.pecas ?? [];
    this.pecas = rawPecas.map((p: any) => new FunilPecaDTO(p));
  }

  // --- Getters derivados ---

  get totalPecas(): number {
    return this.pecas.length;
  }

  get pecasCompletas(): number {
    return this.pecas.filter(p => p.isCompleto).length;
  }

  get pecasComErro(): number {
    return this.pecas.filter(p => p.isErro).length;
  }

  get pecasAguardando(): number {
    return this.pecas.filter(p => p.isAguardandoAprovacao).length;
  }

  get progressoLabel(): string {
    return `${this.pecasCompletas} de ${this.totalPecas} pecas completas`;
  }

  get progressoPct(): number {
    if (this.totalPecas === 0) return 0;
    return Math.round((this.pecasCompletas / this.totalPecas) * 100);
  }

  get isPendentePlano(): boolean {
    return this.status === 'pendente_plano';
  }

  get isPlanoAprovado(): boolean {
    return this.status === 'plano_aprovado' || this.status === 'executando' || this.status === 'completo';
  }

  get isTudoCompleto(): boolean {
    return this.totalPecas > 0 && this.pecas.every(p => p.isCompleto);
  }

  get etapasFunilCobertas(): string[] {
    return [...new Set(this.pecas.map(p => p.etapa_funil))];
  }

  // --- Metodos obrigatorios ---

  isValid(): boolean {
    return (
      this.funil_id.length > 0 &&
      this.tema_principal.trim().length > 0 &&
      this.pecas.length >= 2 &&
      this.pecas.length <= 5 &&
      this.pecas.every(p => p.isValid()) &&
      this.etapasFunilCobertas.length >= 2
    );
  }

  toPayload(): Record<string, any> {
    return {
      funil_id: this.funil_id,
      pipeline_id: this.pipeline_id,
      tema_principal: this.tema_principal,
      objetivo_campanha: this.objetivo_campanha,
      narrativa_geral: this.narrativa_geral,
      pecas: this.pecas.map(p => p.toPayload())
    };
  }
}
```

### 3.3 FunilStatusDTO

Resposta do polling. Wrapper leve que recebe o array de pecas com status atualizado.

```typescript
// src/lib/dtos/FunilStatusDTO.ts

import { FunilPecaDTO } from './FunilPecaDTO';

export class FunilStatusDTO {
  readonly funil_id: string;
  readonly status: string;
  readonly pecas: FunilPecaDTO[];

  constructor(data: Record<string, any>) {
    this.funil_id = data.funil_id ?? data.id ?? '';
    this.status = data.status ?? 'executando';
    const rawPecas = data.pecas ?? [];
    this.pecas = rawPecas.map((p: any) => new FunilPecaDTO(p));
  }

  get totalPecas(): number {
    return this.pecas.length;
  }

  get pecasCompletas(): number {
    return this.pecas.filter(p => p.isCompleto).length;
  }

  get temPecaAguardando(): boolean {
    return this.pecas.some(p => p.isAguardandoAprovacao);
  }

  get isTudoCompleto(): boolean {
    return this.totalPecas > 0 && this.pecas.every(p => p.isCompleto);
  }

  isValid(): boolean {
    return this.funil_id.length > 0 && this.pecas.length > 0;
  }

  toPayload(): Record<string, any> {
    return {
      funil_id: this.funil_id,
      status: this.status
    };
  }
}
```

---

## 4. Repository

```typescript
// src/lib/repositories/FunilRepository.ts

import { browser } from '$app/environment';
import { API_BASE } from '$lib/api';
import { FunilPlanoDTO } from '$lib/dtos/FunilPlanoDTO';
import { FunilStatusDTO } from '$lib/dtos/FunilStatusDTO';

const USE_MOCK = browser && import.meta.env.VITE_USE_MOCK === 'true';

export class FunilRepository {

  /** Busca o plano do funil (gerado pelo Funnel Architect) */
  static async buscarPlano(pipelineId: string): Promise<FunilPlanoDTO> {
    if (USE_MOCK) {
      const { funilPlanoMock, simularDelay } = await import('$lib/mocks/funil.mock');
      await simularDelay(500);
      return new FunilPlanoDTO({ ...funilPlanoMock, pipeline_id: pipelineId });
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/funil/plano`);
    if (!res.ok) throw new Error('Erro ao carregar plano do funil');
    return new FunilPlanoDTO(await res.json());
  }

  /** Salva edicoes do plano (antes de aprovar) */
  static async salvarPlano(pipelineId: string, payload: Record<string, any>): Promise<FunilPlanoDTO> {
    if (USE_MOCK) {
      const { funilPlanoMock, simularDelay } = await import('$lib/mocks/funil.mock');
      await simularDelay(400);
      return new FunilPlanoDTO({ ...funilPlanoMock, ...payload, pipeline_id: pipelineId });
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/funil/plano`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error('Erro ao salvar plano');
    return new FunilPlanoDTO(await res.json());
  }

  /** Aprova plano — backend cria N sub-pipelines */
  static async aprovarPlano(pipelineId: string): Promise<void> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/funil.mock');
      await simularDelay(1000);
      return;
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/funil/plano/aprovar`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Erro ao aprovar plano');
  }

  /** Rejeita plano com feedback — backend regenera via Funnel Architect */
  static async rejeitarPlano(pipelineId: string, feedback: string): Promise<FunilPlanoDTO> {
    if (USE_MOCK) {
      const { funilPlanoMock, simularDelay } = await import('$lib/mocks/funil.mock');
      await simularDelay(2000); // simula re-geracao
      return new FunilPlanoDTO({
        ...funilPlanoMock,
        pipeline_id: pipelineId,
        narrativa_geral: 'Plano regenerado com base no feedback: ' + feedback
      });
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/funil/plano/rejeitar`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ feedback })
    });
    if (!res.ok) throw new Error('Erro ao rejeitar plano');
    return new FunilPlanoDTO(await res.json());
  }

  /** Polling — status de todas as pecas */
  static async buscarStatus(pipelineId: string): Promise<FunilStatusDTO> {
    if (USE_MOCK) {
      const { funilStatusMock, simularDelay } = await import('$lib/mocks/funil.mock');
      await simularDelay(200);
      return new FunilStatusDTO({ ...funilStatusMock, funil_id: pipelineId });
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/funil/status`);
    if (!res.ok) throw new Error('Erro ao carregar status do funil');
    return new FunilStatusDTO(await res.json());
  }

  /** Exporta todas as pecas (Drive + gera PDFs) */
  static async exportar(pipelineId: string): Promise<{ drive_url: string }> {
    if (USE_MOCK) {
      const { simularDelay } = await import('$lib/mocks/funil.mock');
      await simularDelay(3000); // simula upload ao Drive
      return { drive_url: 'https://drive.google.com/drive/folders/mock-funil-folder' };
    }
    const res = await fetch(`${API_BASE}/api/pipelines/${pipelineId}/funil/exportar`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error('Erro ao exportar funil');
    return await res.json();
  }
}
```

---

## 5. Service

```typescript
// src/lib/services/FunilService.ts

import { FunilRepository } from '$lib/repositories/FunilRepository';
import type { FunilPlanoDTO } from '$lib/dtos/FunilPlanoDTO';
import type { FunilStatusDTO } from '$lib/dtos/FunilStatusDTO';

export class FunilService {

  /** Busca plano do funil */
  static async buscarPlano(pipelineId: string): Promise<FunilPlanoDTO> {
    if (!pipelineId) throw new Error('Pipeline ID obrigatorio');
    return FunilRepository.buscarPlano(pipelineId);
  }

  /** Salva edicoes do plano — recebe DTO, usa toPayload() */
  static async salvarPlano(pipelineId: string, plano: FunilPlanoDTO): Promise<FunilPlanoDTO> {
    if (!pipelineId) throw new Error('Pipeline ID obrigatorio');
    if (!plano.isValid()) throw new Error('Plano invalido — verifique os campos');
    return FunilRepository.salvarPlano(pipelineId, plano.toPayload());
  }

  /** Aprova plano — delega para repository */
  static async aprovarPlano(pipelineId: string, plano: FunilPlanoDTO): Promise<void> {
    if (!pipelineId) throw new Error('Pipeline ID obrigatorio');
    if (!plano.isValid()) throw new Error('Plano invalido — nao pode aprovar');
    // Salvar antes de aprovar (garante que edicoes foram persistidas)
    await FunilRepository.salvarPlano(pipelineId, plano.toPayload());
    return FunilRepository.aprovarPlano(pipelineId);
  }

  /** Rejeita plano com feedback — valida feedback antes */
  static async rejeitarPlano(pipelineId: string, feedback: string): Promise<FunilPlanoDTO> {
    if (!pipelineId) throw new Error('Pipeline ID obrigatorio');
    if (!feedback || feedback.trim().length < 10) {
      throw new Error('Feedback deve ter pelo menos 10 caracteres');
    }
    return FunilRepository.rejeitarPlano(pipelineId, feedback.trim());
  }

  /** Polling — busca status atualizado */
  static async buscarStatus(pipelineId: string): Promise<FunilStatusDTO> {
    if (!pipelineId) throw new Error('Pipeline ID obrigatorio');
    return FunilRepository.buscarStatus(pipelineId);
  }

  /** Exporta funil completo — valida se tudo esta completo via DTO */
  static async exportar(pipelineId: string, status: FunilStatusDTO): Promise<{ drive_url: string }> {
    if (!pipelineId) throw new Error('Pipeline ID obrigatorio');
    if (!status.isTudoCompleto) {
      throw new Error('Todas as pecas devem estar completas para exportar');
    }
    return FunilRepository.exportar(pipelineId);
  }
}
```

**Observacao sobre opacidade:** O Service NUNCA acessa `plano.tema_principal` ou `plano.pecas[0].titulo` diretamente. Ele usa `plano.isValid()`, `plano.toPayload()`, `status.isTudoCompleto`. Quando um campo muda no DTO, o Service nao precisa mudar.

---

## 6. Mocks

```typescript
// src/lib/mocks/funil.mock.ts

export const funilPlanoMock = {
  id: 'funil-001',
  funil_id: 'funil-001',
  pipeline_id: 'pip-funil-001',
  status: 'pendente_plano',
  created_at: '2026-04-05T10:00:00Z',
  approved_at: null,
  tema_principal: 'RAG na pratica: como montar um pipeline de Retrieval-Augmented Generation do zero',
  objetivo_campanha: 'Educar devs sobre RAG e gerar leads para o curso de IA Generativa da IT Valley',
  narrativa_geral: 'Funil que comecar despertando curiosidade sobre RAG, aprofunda com implementacao real, e fecha com convite para o curso.',
  pecas: [
    {
      ordem: 1,
      titulo: 'Voce esta usando ChatGPT errado se nao conhece RAG',
      etapa_funil: 'topo',
      formato: 'carrossel',
      angulo: 'Desmistificar o que e RAG e por que todo dev precisa conhecer',
      resumo: 'Carrossel de 7 slides mostrando o problema de alucinacao em LLMs e como RAG resolve isso de forma elegante.',
      gancho: 'O ChatGPT inventou dados no seu projeto? A culpa nao e dele.',
      conexao_anterior: null,
      cta_para_proxima: 'Quer ver como montar isso na pratica? Veja o proximo post.'
    },
    {
      ordem: 2,
      titulo: 'Arquitetura RAG em 1 imagem: LangChain + ChromaDB + Claude',
      etapa_funil: 'meio',
      formato: 'post_unico',
      angulo: 'Diagrama tecnico da arquitetura RAG com stack moderna',
      resumo: 'Post unico com diagrama visual da arquitetura completa, mostrando cada componente e como se conectam.',
      gancho: 'Toda a arquitetura RAG em 1 imagem. Salve isso.',
      conexao_anterior: 'Aprofunda o conceito introduzido no carrossel anterior',
      cta_para_proxima: 'Agora que voce entendeu a arquitetura, veja o codigo funcionando.'
    },
    {
      ordem: 3,
      titulo: 'RAG em 50 linhas de Python: tutorial completo',
      etapa_funil: 'meio',
      formato: 'carrossel',
      angulo: 'Codigo real e funcional de um pipeline RAG minimo',
      resumo: 'Carrossel de 10 slides com codigo Python passo a passo, do setup ao primeiro resultado.',
      gancho: 'RAG completo em 50 linhas. Sem framework magico, so Python puro.',
      conexao_anterior: 'Implementa a arquitetura mostrada no post anterior',
      cta_para_proxima: 'Quer ir alem do basico? Veja as armadilhas que ninguem conta.'
    },
    {
      ordem: 4,
      titulo: '5 erros que destroem seu RAG em producao',
      etapa_funil: 'fundo',
      formato: 'thumbnail_youtube',
      angulo: 'Erros reais de producao que so quem implementou RAG conhece',
      resumo: 'Thumbnail para video sobre os 5 erros mais comuns ao colocar RAG em producao e como evita-los.',
      gancho: 'Seu RAG funciona no notebook mas falha em producao? Leia isso.',
      conexao_anterior: 'Complementa o tutorial mostrando o que pode dar errado',
      cta_para_proxima: 'Quer dominar RAG de verdade? Conheca o curso.'
    },
    {
      ordem: 5,
      titulo: 'Domine RAG, Agentes e LangChain no curso de IA Gen da IT Valley',
      etapa_funil: 'conversao',
      formato: 'capa_reels',
      angulo: 'CTA direto para o curso de IA Generativa com RAG como destaque',
      resumo: 'Capa de Reels com CTA claro para o curso, mencionando RAG, Agentes e LangChain como modulos.',
      gancho: 'De "o que e RAG" a "RAG em producao" em 8 semanas.',
      conexao_anterior: 'Fecha o funil convertendo quem acompanhou a jornada',
      cta_para_proxima: null
    }
  ]
};

export const funilStatusMock = {
  funil_id: 'funil-001',
  status: 'executando',
  pecas: [
    {
      ordem: 1,
      titulo: 'Voce esta usando ChatGPT errado se nao conhece RAG',
      etapa_funil: 'topo',
      formato: 'carrossel',
      angulo: 'Desmistificar o que e RAG',
      resumo: 'Carrossel de 7 slides sobre RAG.',
      gancho: 'O ChatGPT inventou dados no seu projeto?',
      conexao_anterior: null,
      cta_para_proxima: 'Veja o proximo post.',
      pipeline_id: 'pip-peca-001',
      status: 'completo',
      etapa_atual: 'content_critic',
      progresso_imagem: 100
    },
    {
      ordem: 2,
      titulo: 'Arquitetura RAG em 1 imagem',
      etapa_funil: 'meio',
      formato: 'post_unico',
      angulo: 'Diagrama tecnico da arquitetura RAG',
      resumo: 'Post unico com diagrama visual.',
      gancho: 'Toda a arquitetura RAG em 1 imagem.',
      conexao_anterior: 'Aprofunda o carrossel anterior',
      cta_para_proxima: 'Veja o codigo funcionando.',
      pipeline_id: 'pip-peca-002',
      status: 'aguardando_aprovacao',
      etapa_atual: 'copywriter',
      progresso_imagem: 0
    },
    {
      ordem: 3,
      titulo: 'RAG em 50 linhas de Python',
      etapa_funil: 'meio',
      formato: 'carrossel',
      angulo: 'Codigo real de pipeline RAG',
      resumo: 'Carrossel de 10 slides com codigo.',
      gancho: 'RAG completo em 50 linhas.',
      conexao_anterior: 'Implementa a arquitetura anterior',
      cta_para_proxima: 'Veja as armadilhas.',
      pipeline_id: 'pip-peca-003',
      status: 'executando',
      etapa_atual: 'art_director',
      progresso_imagem: 0
    },
    {
      ordem: 4,
      titulo: '5 erros que destroem seu RAG',
      etapa_funil: 'fundo',
      formato: 'thumbnail_youtube',
      angulo: 'Erros reais de producao',
      resumo: 'Thumbnail para video sobre erros.',
      gancho: 'Seu RAG falha em producao?',
      conexao_anterior: 'Complementa o tutorial',
      cta_para_proxima: 'Conheca o curso.',
      pipeline_id: 'pip-peca-004',
      status: 'pendente',
      etapa_atual: '',
      progresso_imagem: 0
    },
    {
      ordem: 5,
      titulo: 'Domine RAG no curso IT Valley',
      etapa_funil: 'conversao',
      formato: 'capa_reels',
      angulo: 'CTA para o curso',
      resumo: 'Capa de Reels com CTA.',
      gancho: 'De zero a RAG em producao em 8 semanas.',
      conexao_anterior: 'Fecha o funil',
      cta_para_proxima: null,
      pipeline_id: 'pip-peca-005',
      status: 'pendente',
      etapa_atual: '',
      progresso_imagem: 0
    }
  ]
};

export function simularDelay(ms: number = 300): Promise<void> {
  return new Promise(r => setTimeout(r, ms));
}
```

---

## 7. Componentes

### 7.1 FunilPecaCard.svelte

Card reutilizado na tela de plano (editavel) e no painel (somente leitura).

```
Props:
  peca: FunilPecaDTO           — dados da peca
  editavel: boolean            — true na tela de plano, false no painel
  onremover?: () => void       — callback para remover peca (so no plano)
  oneditar?: (campo: string, valor: string) => void  — callback para edicao inline
  onclick?: () => void         — callback ao clicar (navegar no painel)

Responsabilidades:
  - Exibir titulo, etapa_funil (badge colorido), formato (icone), angulo, resumo, gancho
  - No modo editavel: inputs inline para titulo, angulo, resumo; dropdowns para formato e etapa_funil
  - No modo painel: exibir status com cor + etapa_atual + progresso de imagem
  - Badge "aguardando_aprovacao" com animate-pulse quando aplicavel
  - Botao remover com confirmacao (dialog nativo ou Modal)

$derived:
  - etapaCor: topo=purple, meio=amber, fundo=green, conversao=red
  - statusCor: pendente=text-muted, executando=purple+pulse, aguardando=amber+pulse, completo=green, erro=red
  - formatoIcone: carrossel=grid, post_unico=square, thumbnail=play, capa_reels=smartphone
```

### 7.2 FunilProgressBar.svelte

Barra de progresso geral do funil.

```
Props:
  total: number         — total de pecas
  completas: number     — pecas completas
  aguardando: number    — pecas aguardando aprovacao
  erros: number         — pecas com erro

Responsabilidades:
  - Barra horizontal segmentada (cada peca = 1 segmento)
  - Cores por status: verde (completo), amarelo (aguardando), azul pulsante (executando), cinza (pendente), vermelho (erro)
  - Label: "3 de 5 pecas completas"
  - Icone de check quando 100%

$derived:
  - pct: Math.round((completas / total) * 100)
  - label: "{completas} de {total} pecas completas"
  - corBarra: baseada no progresso geral
```

### 7.3 FunilPecaTracker.svelte

Mini-tracker de etapas dentro de 1 peca no painel (mostra em qual etapa do pipeline de 6 passos a peca esta).

```
Props:
  etapa_atual: string          — agente atual (strategist, copywriter, etc.)
  status: StatusPeca           — status da peca
  progresso_imagem: number     — 0-100

Responsabilidades:
  - 6 dots horizontais representando as etapas do pipeline
  - Dot ativo pulsa na cor do status
  - Dots anteriores verdes (concluidos)
  - Dots futuros cinza
  - Se etapa = image_generator, mostra barra de progresso abaixo

$derived:
  - etapaIndex: indice da etapa atual na lista de 6 agentes
  - etapasCompletas: etapas antes do index atual
```

### 7.4 FunilExportCard.svelte

Preview de 1 peca na tela de export.

```
Props:
  peca: FunilPecaDTO          — dados da peca
  previewUrl: string          — URL da imagem de preview (primeiro slide)

Responsabilidades:
  - Miniatura do primeiro slide (aspect ratio correto via getDims)
  - Titulo + formato + etapa_funil
  - Botao "Download PDF" individual
  - Badge "Pronto para exportar"
```

### 7.5 FunilExportBar.svelte

Barra de acoes fixa no rodape da tela de export.

```
Props:
  total: number               — total de pecas
  exportando: boolean         — estado de loading
  onexportardrive: () => void — callback export Drive
  ondownloadzip: () => void   — callback download ZIP

Responsabilidades:
  - Sticky no bottom
  - Botao primario "Exportar para Drive" (icone Drive)
  - Botao secundario "Download ZIP" (icone download)
  - Spinner quando exportando
  - Label "5 pecas prontas para exportar"
```

---

## 8. Rotas — Estrutura das Paginas

### 8.1 `/pipeline/{id}/funil-plano/+page.svelte`

Tela de revisao, edicao e aprovacao do plano.

```
Estados:
  - plano: FunilPlanoDTO | null
  - carregando: boolean
  - salvando: boolean
  - aprovando: boolean
  - rejeitando: boolean
  - feedbackRejeicao: string
  - showRejectModal: boolean
  - erro: string

onMount:
  1. FunilService.buscarPlano(pipelineId) → plano
  2. Se plano.isPlanoAprovado → goto(`/pipeline/${id}/funil`)

Fluxo de edicao:
  - Edicoes modificam um state local (copia editavel das pecas)
  - "Salvar" chama FunilService.salvarPlano() com novo FunilPlanoDTO construido a partir do state
  - Validacao inline (minimo 2 pecas, pelo menos 2 etapas diferentes)

Aprovar:
  1. FunilService.aprovarPlano(pipelineId, plano)
  2. goto(`/pipeline/${id}/funil`)

Rejeitar:
  1. Abre modal com textarea para feedback (minimo 10 chars)
  2. FunilService.rejeitarPlano(pipelineId, feedback)
  3. Atualiza plano com o retorno

Layout:
  - PipelineBreadcrumb (existente) → "Pipeline > Plano do Funil"
  - Narrativa geral no topo (texto editavel)
  - Grid de FunilPecaCard (editavel=true) — 1 coluna em mobile, 2 em desktop
  - Barra fixa no rodape: "Rejeitar e Regenerar" | "Aprovar Plano"
```

### 8.2 `/pipeline/{id}/funil/+page.svelte`

Painel de acompanhamento com polling.

```
Estados:
  - status: FunilStatusDTO | null
  - carregando: boolean
  - erro: string
  - pollingInterval: ReturnType<typeof setInterval> | null

onMount:
  1. FunilService.buscarStatus(pipelineId) → status
  2. Iniciar polling a cada 3s
  3. Parar polling quando isTudoCompleto

Polling:
  - Chama FunilService.buscarStatus(pipelineId)
  - Atualiza status reativo
  - Para quando isTudoCompleto ou todas em aguardando_aprovacao humana

Navegacao:
  - Clicar em peca com aguardando_aprovacao → goto(`/pipeline/${peca.pipeline_id}/copy`)
  - Clicar em peca completa → goto(`/pipeline/${peca.pipeline_id}/export`)

Layout:
  - PipelineBreadcrumb → "Pipeline > Funil"
  - FunilProgressBar no topo
  - Lista vertical de FunilPecaCard (editavel=false) com FunilPecaTracker dentro
  - Quando isTudoCompleto: botao "Exportar Funil" → goto(`/pipeline/${id}/funil-export`)
```

### 8.3 `/pipeline/{id}/funil-export/+page.svelte`

Export de todas as pecas.

```
Estados:
  - status: FunilStatusDTO | null
  - carregando: boolean
  - exportando: boolean
  - driveUrl: string
  - erro: string

onMount:
  1. FunilService.buscarStatus(pipelineId) → status
  2. Se !status.isTudoCompleto → goto(`/pipeline/${id}/funil`) com aviso

Export Drive:
  1. FunilService.exportar(pipelineId, status)
  2. Exibe link do Drive retornado

Download ZIP:
  1. Fetch para endpoint de download (ou gerar client-side via jsPDF existente)

Layout:
  - PipelineBreadcrumb → "Pipeline > Funil > Exportar"
  - Grid de FunilExportCard (1-2 colunas)
  - FunilExportBar fixa no rodape
  - Apos export: banner de sucesso com link do Drive
```

---

## 9. Design Tokens Necessarios

Tokens que ja existem no `app.css` e serao reutilizados:

| Token | Uso |
|---|---|
| `--color-purple` | Badges topo de funil, botoes primarios |
| `--color-amber` | Badges meio de funil, status aguardando |
| `--color-green` | Badges fundo de funil, status completo |
| `--color-red` | Badges conversao, status erro |
| `--color-bg-card` | Fundo dos cards |
| `--color-border-default` | Borda dos cards |

**Nenhum novo token e necessario.** As cores das etapas do funil (topo, meio, fundo, conversao) mapeiam diretamente para as cores existentes (purple, amber, green, red). Os componentes usam classes Tailwind geradas pelo `@theme`.

---

## 10. Fluxo de Dados Completo

```
+page.svelte (funil-plano)
  ├── FunilService.buscarPlano(id)
  │   └── FunilRepository.buscarPlano(id)
  │       └── new FunilPlanoDTO(data) ← contem N FunilPecaDTO
  │
  ├── [usuario edita] → monta novo FunilPlanoDTO local
  │
  ├── FunilService.aprovarPlano(id, plano)
  │   ├── plano.isValid() ← validacao via metodo
  │   ├── plano.toPayload() ← serializa via metodo
  │   └── FunilRepository.aprovarPlano(id)
  │
  └── <FunilPecaCard peca={peca} editavel={true}>
      └── $derived(etapaCor, formatoIcone)

+page.svelte (funil — painel)
  ├── FunilService.buscarStatus(id)
  │   └── FunilRepository.buscarStatus(id)
  │       └── new FunilStatusDTO(data) ← contem N FunilPecaDTO com status
  │
  ├── [polling 3s] → atualiza status reativo
  │
  └── <FunilPecaCard peca={peca} editavel={false} onclick={navegar}>
      └── <FunilPecaTracker etapa_atual={peca.etapa_atual}>

+page.svelte (funil-export)
  ├── FunilService.buscarStatus(id) → valida isTudoCompleto
  ├── FunilService.exportar(id, status)
  │   └── status.isTudoCompleto ← validacao via metodo
  │
  └── <FunilExportCard peca={peca}>
      └── <FunilExportBar onexportardrive={...}>
```

---

## 11. Dev Features (Unidades de Trabalho)

Ordem sugerida de implementacao:

### Feature 1: VisualizarPlano
```
CRIA:     dtos/FunilPecaDTO.ts
CRIA:     dtos/FunilPlanoDTO.ts
CRIA:     mocks/funil.mock.ts
CRIA:     repositories/FunilRepository.ts     ← buscarPlano()
CRIA:     services/FunilService.ts            ← buscarPlano()
CRIA:     components/funil/FunilPecaCard.svelte
CRIA:     routes/pipeline/[id]/funil-plano/+page.svelte
```

### Feature 2: EditarPlano + AprovarPlano + RejeitarPlano
```
ADICIONA: repositories/FunilRepository.ts     ← salvarPlano(), aprovarPlano(), rejeitarPlano()
ADICIONA: services/FunilService.ts            ← salvarPlano(), aprovarPlano(), rejeitarPlano()
MODIFICA: routes/pipeline/[id]/funil-plano/+page.svelte  ← edicao inline + botoes aprovar/rejeitar
```

### Feature 3: AcompanharPecas
```
CRIA:     dtos/FunilStatusDTO.ts
ADICIONA: repositories/FunilRepository.ts     ← buscarStatus()
ADICIONA: services/FunilService.ts            ← buscarStatus()
CRIA:     components/funil/FunilProgressBar.svelte
CRIA:     components/funil/FunilPecaTracker.svelte
CRIA:     routes/pipeline/[id]/funil/+page.svelte
```

### Feature 4: ExportarFunil
```
ADICIONA: repositories/FunilRepository.ts     ← exportar()
ADICIONA: services/FunilService.ts            ← exportar()
CRIA:     components/funil/FunilExportCard.svelte
CRIA:     components/funil/FunilExportBar.svelte
CRIA:     routes/pipeline/[id]/funil-export/+page.svelte
```

---

## 12. Notas para o Dev Mockado (Agente 06)

1. **funilPlanoMock** deve ter 5 pecas com variedade de formatos (carrossel, post_unico, thumbnail_youtube, capa_reels) e etapas (topo, meio, fundo, conversao). O tema deve ser tecnico IT Valley (RAG, MLOps, Deep Learning).

2. **funilStatusMock** deve simular um funil em progresso: 1 peca completa, 1 aguardando_aprovacao, 1 executando, 2 pendentes. Cada peca deve ter `pipeline_id` preenchido (referencia ao sub-pipeline).

3. Os mocks devem ser importados via `await import()` (lazy) dentro do `if (USE_MOCK)` — padrao do projeto.

4. A funcao `simularDelay()` deve existir no mock para simular latencia de rede.

5. Os dados devem ser realistas o suficiente para validar: badges de etapa_funil, tracker de etapas, progresso de imagem, navegacao entre pecas.

---

## 13. Checklist — Dominio Funil

- [ ] Criar `dtos/FunilPecaDTO.ts` com constructor, readonly, getters, isValid, toPayload
- [ ] Criar `dtos/FunilPlanoDTO.ts` com constructor, readonly, getters, isValid, toPayload
- [ ] Criar `dtos/FunilStatusDTO.ts` com constructor, readonly, getters, isValid, toPayload
- [ ] Criar `repositories/FunilRepository.ts` com VITE_USE_MOCK e todos os endpoints
- [ ] Criar `mocks/funil.mock.ts` com dados realistas (5 pecas, status variados)
- [ ] Criar `services/FunilService.ts` com metodos estaticos opacos
- [ ] Criar `components/funil/FunilPecaCard.svelte`
- [ ] Criar `components/funil/FunilProgressBar.svelte`
- [ ] Criar `components/funil/FunilPecaTracker.svelte`
- [ ] Criar `components/funil/FunilExportCard.svelte`
- [ ] Criar `components/funil/FunilExportBar.svelte`
- [ ] Criar `routes/pipeline/[id]/funil-plano/+page.svelte`
- [ ] Criar `routes/pipeline/[id]/funil/+page.svelte`
- [ ] Criar `routes/pipeline/[id]/funil-export/+page.svelte`
- [ ] Nenhum novo token no app.css (cores existentes cobrem tudo)

---

*Arquitetura gerada em 2026-04-05 pelo Agente 04 (Arquiteto IT Valley Frontend).*
*Fonte de verdade para: Dev Mockado (06) e Dev Frontend (09).*
