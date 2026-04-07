# DEV FEATURES -- Content Factory v3

Documento gerado pelo Agente 08 (P.O. / Product Owner) da esteira IT Valley.
Base: PRD (Agente 01) + TELAS (Agente 02) + ARQUITETURA_BACKEND (Agente 03) + ARQUITETURA_FRONTEND (Agente 04).

---

## MAPA DE DOMINIOS E DEPENDENCIAS

```
Dominios identificados:
  Pipeline          (central -- depende de: Config, Agente, Skill)
  Config            (base -- sem dependencias)
  Agente            (base -- sem dependencias de dominio)
  Skill             (base -- sem dependencias de dominio)
  Conteudo          (legado -- sem dependencias novas)
  Imagem            (legado -- sem dependencias novas)
  Drive             (depende de: Conteudo, Imagem)
  Historico         (depende de: Pipeline, Conteudo)
  Score             (depende de: Pipeline, Conteudo)
  VisualPreference  (depende de: Pipeline)
  Briefing*         (sub-dominio de Pipeline -- AP-1)
  Copy*             (sub-dominio de Pipeline -- AP-2)
  Visual*           (sub-dominio de Pipeline -- AP-3)
  ImagemAprovacao*  (sub-dominio de Pipeline -- AP-4)
  Export*           (sub-dominio de Pipeline -- final)

  * Sub-dominios do Pipeline no frontend. No backend sao rotas do dominio Pipeline.

Ordem de implementacao:
  Nivel 0 (base):         Pacote Base (frontend + backend)
  Nivel 1 (sem dep):      Config, Agente (back) | Config, Agente (front)
  Nivel 2 (legado):       Conteudo legado, Imagem legado, Drive legado (manter, refatorar)
  Nivel 3 (pipeline):     Pipeline core (criar, buscar, listar, cancelar)
  Nivel 4 (aprovacoes):   AP-1 Briefing, AP-2 Copy+Hook, AP-3 Visual, AP-4 Imagem
  Nivel 5 (finalizacao):  Export, Score, VisualPreference, Historico refatorado
```

---

## PACOTE BASE -- Frontend + Backend (obrigatorio primeiro)

**Ninguem comeca sem este pacote estar pronto.**

### Backend Base

**O que o dev CRIA:**
- `config.py` -- Settings (Pydantic BaseSettings) com variaveis de ambiente
- `models/base.py` -- Base (DeclarativeBase) + TenantMixin (id, tenant_id, timestamps, soft delete)
- `data/interfaces/base_repository.py` -- contrato abstrato puro (ABC com create, get, list, update, delete)
- `data/repositories/sql/base_sql_repository.py` -- CRUD generico SQLAlchemy (implementa base_repository)
- `data/connections/sql_connection.py` -- engine + async session factory (MSSQL via pyodbc)
- `data/connections/database.py` -- Depends: get_sql_session
- `requirements.txt` -- atualizar com sqlalchemy, asyncio, pyodbc

**O que o dev VERIFICA (existente):**
- `main.py` -- ja existe, confirmar que registra routers com prefix `/api`
- `.env` -- ja existe, nao commitar

**Criterio de pronto:**
1. `python -c "from models.base import Base, TenantMixin"` executa sem erro
2. `python -c "from data.connections.database import get_sql_session"` executa sem erro
3. `python -c "from data.repositories.sql.base_sql_repository import BaseSqlRepository"` executa sem erro
4. `uvicorn main:app --reload` inicia sem erro (porta 8000)

---

### Frontend Base

**O que o dev CRIA:**
- `src/lib/components/ui/Modal.svelte` -- modal generico com overlay, close, slot
- `src/lib/components/ui/Spinner.svelte` -- loading spinner animado
- `src/lib/components/ui/Skeleton.svelte` -- placeholder de carregamento
- `src/lib/components/ui/Toggle.svelte` -- toggle on/off
- `src/lib/components/ui/Tabs.svelte` -- tabs com slot por aba
- `src/lib/components/ui/Banner.svelte` -- feedback sucesso/erro/warning
- `src/lib/components/layout/Sidebar.svelte` -- menu lateral com itens de navegacao
- `src/lib/utils/formatters.ts` -- formatDate, formatScore, truncate
- `src/lib/utils/validators.ts` -- isValidUrl, isValidHex, isMinLength

**O que o dev VERIFICA (existente):**
- `src/lib/components/ui/Badge.svelte` -- existe
- `src/lib/components/ui/Button.svelte` -- existe
- `src/lib/components/ui/Card.svelte` -- existe
- `src/app.css` -- existe, design tokens dark mode
- `src/routes/+layout.svelte` -- existe (refatorar header para usar Sidebar)

**O que o dev REFATORA:**
- `src/routes/+layout.svelte` -- substituir header horizontal por Sidebar.svelte

**Criterio de pronto:**
1. `npm run dev` inicia sem erro (porta 5173)
2. Sidebar renderiza com itens: Home, Pipeline, Historico, Agentes, Config
3. Todos os componentes UI novos renderizam isoladamente
4. `VITE_USE_MOCK=true` funciona (environment.js configurado)

---

## PACOTE BACK-1 -- Dominio: Config (refatorar)

**Pode comecar apos:** Pacote Base Backend
**Outros devs trabalhando em paralelo:** Front-1 (Config frontend), Back-2 (Agente)

### Dev Feature 1: SalvarBrandPalette

**O que o dev CRIA:**
- `dtos/config/salvar_brand_palette/request.py` -- SalvarBrandPaletteRequest (cores, fonte, elementos_obrigatorios, estilo)
- `dtos/config/salvar_brand_palette/response.py` -- SalvarBrandPaletteResponse (sucesso + dados salvos)

**O que o dev ADICIONA:**
- `services/config_service.py` -- salvar_brand_palette()
- `routers/config.py` -- PUT /api/config/brand-palette
- `factories/config_factory.py` -- to_brand_palette_file() (valida e salva JSON)

**Dependencias:** Nenhuma dev feature anterior
**Criterio de pronto:** PUT /api/config/brand-palette recebe SalvarBrandPaletteRequest e salva em configs/brand_palette.json. Retorna 200 com dados salvos.

---

### Dev Feature 2: BuscarBrandPalette

**O que o dev CRIA:**
- `dtos/config/buscar_brand_palette/response.py` -- BuscarBrandPaletteResponse

**O que o dev ADICIONA:**
- `services/config_service.py` -- buscar_brand_palette()
- `routers/config.py` -- GET /api/config/brand-palette

**Dependencias:** Dev Feature 1 (SalvarBrandPalette -- precisa do arquivo existir)
**Criterio de pronto:** GET /api/config/brand-palette retorna BuscarBrandPaletteResponse com dados do configs/brand_palette.json.

---

### Dev Feature 3: SalvarCreatorRegistry

**O que o dev CRIA:**
- `dtos/config/salvar_creator_registry/request.py` -- SalvarCreatorRegistryRequest (lista de criadores com nome, funcao, plataforma, url)
- `dtos/config/salvar_creator_registry/response.py` -- SalvarCreatorRegistryResponse

**O que o dev ADICIONA:**
- `services/config_service.py` -- salvar_creator_registry()
- `routers/config.py` -- PUT /api/config/creator-registry
- `factories/config_factory.py` -- to_creator_registry_file()

**Dependencias:** Nenhuma
**Criterio de pronto:** PUT /api/config/creator-registry recebe lista de criadores e salva em configs/creator_registry.json. Retorna 200.

---

### Dev Feature 4: BuscarCreatorRegistry + SalvarPlatformRules + BuscarPlatformRules

**O que o dev CRIA:**
- `dtos/config/buscar_creator_registry/response.py` -- BuscarCreatorRegistryResponse
- `dtos/config/salvar_platform_rules/request.py` -- SalvarPlatformRulesRequest
- `dtos/config/salvar_platform_rules/response.py` -- SalvarPlatformRulesResponse
- `dtos/config/buscar_platform_rules/response.py` -- BuscarPlatformRulesResponse

**O que o dev ADICIONA:**
- `services/config_service.py` -- buscar_creator_registry(), salvar_platform_rules(), buscar_platform_rules()
- `routers/config.py` -- GET /api/config/creator-registry, PUT /api/config/platform-rules, GET /api/config/platform-rules
- `factories/config_factory.py` -- to_platform_rules_file()

**Dependencias:** Dev Feature 3
**Criterio de pronto:** Todas as 3 rotas retornam dados corretos. JSON salvo em configs/.

---

## PACOTE BACK-2 -- Dominio: Agente

**Pode comecar apos:** Pacote Base Backend
**Outros devs trabalhando em paralelo:** Back-1 (Config), Front-1, Front-2

### Dev Feature 1: ListarAgentes

**O que o dev CRIA:**
- `dtos/agente/listar_agentes/response.py` -- ListarAgentesResponse (lista de AgenteBase)
- `dtos/agente/base.py` -- AgenteBase (slug, nome, tipo, descricao, status)
- `routers/agente.py` -- novo router (refatorar de agentes.py)
- `services/agente_service.py` -- listar()
- `mappers/agente_mapper.py` -- to_list_response()
- `factories/agente_factory.py` -- build_agente_list() (monta lista dos 6 agentes + 6 skills)

**Dependencias:** Nenhuma
**Criterio de pronto:** GET /api/agentes retorna ListarAgentesResponse com 12 itens (6 agentes LLM + 6 skills). Status 200.

---

### Dev Feature 2: BuscarAgente

**O que o dev CRIA:**
- `dtos/agente/buscar_agente/response.py` -- BuscarAgenteResponse (AgenteBase + system_prompt)

**O que o dev ADICIONA:**
- `services/agente_service.py` -- buscar(slug)
- `routers/agente.py` -- GET /api/agentes/{slug}
- `mappers/agente_mapper.py` -- to_detail_response()

**Dependencias:** Dev Feature 1 (ListarAgentes)
**Criterio de pronto:** GET /api/agentes/strategist retorna BuscarAgenteResponse com system prompt. Status 200. Slug invalido retorna 404.

---

### Dev Feature 3: ExecutarAgente (debug)

**O que o dev CRIA:**
- `dtos/agente/executar_agente/request.py` -- ExecutarAgenteRequest (entrada JSON livre)
- `dtos/agente/executar_agente/response.py` -- ExecutarAgenteResponse (saida JSON + duracao_ms)
- `agents/strategist.py` -- executar(entrada) -> saida (Claude API)
- `agents/copywriter.py` -- executar(entrada) -> saida (Claude API)
- `agents/hook_specialist.py` -- executar(entrada) -> saida (Claude API)
- `agents/art_director.py` -- executar(entrada) -> saida (Claude API)
- `agents/image_generator.py` -- executar(entrada) -> saida (Gemini API)
- `agents/content_critic.py` -- executar(entrada) -> saida (Claude API)

**O que o dev ADICIONA:**
- `services/agente_service.py` -- executar(slug, entrada)
- `routers/agente.py` -- POST /api/agentes/{slug}/executar

**Dependencias:** Dev Feature 2 (BuscarAgente)
**Criterio de pronto:** POST /api/agentes/strategist/executar com entrada JSON retorna saida do agente. Status 200. Slug invalido retorna 404.

---

## PACOTE BACK-3 -- Dominio: Pipeline (core) + Skills

**Pode comecar apos:** Pacote Base Backend + Back-1 (Config precisa existir para brand_palette)
**Outros devs trabalhando em paralelo:** Front-2 (Pipeline), Back-2 pode ja estar pronto

### Dev Feature 1: CriarPipeline

**O que o dev CRIA:**
- `dtos/pipeline/criar_pipeline/request.py` -- CriarPipelineRequest (tema, formato, modo_funil, modo_entrada, disciplina, tecnologia, foto_criador)
- `dtos/pipeline/criar_pipeline/response.py` -- CriarPipelineResponse (id, status, etapa_atual, created_at)
- `dtos/pipeline/base.py` -- PipelineBase, EtapaBase
- `models/pipeline.py` -- PipelineModel + PipelineStepModel (SQLAlchemy)
- `factories/pipeline_factory.py` -- to_model() (cria pipeline + 7 etapas com status "pendente")
- `mappers/pipeline_mapper.py` -- to_create_response()
- `services/pipeline_service.py` -- criar()
- `routers/pipeline.py` -- POST /api/pipelines
- `data/repositories/sql/pipeline_repository.py` -- create, get, list

**Dependencias:** Nenhuma dev feature de pipeline anterior
**Criterio de pronto:** POST /api/pipelines com tema >= 20 chars e formato valido retorna CriarPipelineResponse com status 201. Pipeline e 7 steps persistidos no banco.

---

### Dev Feature 2: BuscarPipeline + ListarPipelines

**O que o dev CRIA:**
- `dtos/pipeline/buscar_pipeline/response.py` -- BuscarPipelineResponse (pipeline + lista de etapas com status)
- `dtos/pipeline/listar_pipelines/request.py` -- ListarPipelinesFiltros (formato, status, data_inicio, data_fim)
- `dtos/pipeline/listar_pipelines/response.py` -- ListarPipelinesResponse (lista paginada)

**O que o dev ADICIONA:**
- `services/pipeline_service.py` -- buscar(id), listar(filtros)
- `routers/pipeline.py` -- GET /api/pipelines/{id}, GET /api/pipelines
- `mappers/pipeline_mapper.py` -- to_detail_response(), to_list_response()

**Dependencias:** Dev Feature 1 (CriarPipeline)
**Criterio de pronto:** GET /api/pipelines/{id} retorna pipeline com 7 etapas. GET /api/pipelines retorna lista filtrada por tenant_id. ID invalido retorna 404.

---

### Dev Feature 3: CancelarPipeline + RetomarPipeline

**O que o dev CRIA:**
- `dtos/pipeline/base.py` -- adicionar CancelarPipelineResponse, RetomarPipelineResponse (se necessario)

**O que o dev ADICIONA:**
- `services/pipeline_service.py` -- cancelar(id), retomar(id)
- `routers/pipeline.py` -- POST /api/pipelines/{id}/cancelar, POST /api/pipelines/{id}/retomar
- `factories/pipeline_factory.py` -- validar_cancelamento(), validar_retomada()

**Dependencias:** Dev Feature 2 (BuscarPipeline)
**Criterio de pronto:** Cancelar muda status para "cancelado". Retomar re-executa etapa com status "erro". Pipeline ja cancelado nao pode ser retomado (400).

---

### Dev Feature 4: Skills deterministicas (6)

**O que o dev CRIA:**
- `skills/brand_overlay.py` -- aplica foto redonda + logo via Pillow
- `skills/brand_validator.py` -- valida cores, aspect ratio, elementos obrigatorios
- `skills/visual_memory.py` -- persiste preferencias visuais em banco
- `skills/variation_engine.py` -- gera 3 variacoes de prompt (manipulacao de string, zero LLM)
- `skills/tone_guide.py` -- valida vocabulario IT Valley (termos proibidos, tom de voz)
- `skills/trend_scanner.py` -- busca tendencias (dev.to + HN + YouTube RSS, cache 1h)

**Dependencias:** Nenhuma (skills sao independentes)
**Criterio de pronto:**
1. `brand_validator` recebe imagem e retorna {valido: bool, erros: []}
2. `brand_overlay` recebe imagem e retorna imagem com foto + logo aplicados
3. `variation_engine` recebe 1 prompt e retorna 3 variacoes
4. `tone_guide` recebe texto e retorna {aprovado: bool, correcoes: []}
5. `trend_scanner` retorna lista de tendencias com cache de 1h
6. `visual_memory` persiste e recupera preferencias do banco

---

## PACOTE BACK-4 -- Dominio: Pipeline (aprovacoes AP-1 a AP-4)

**Pode comecar apos:** Back-3 (Pipeline core + Skills + Agentes criados em Back-2)
**Outros devs trabalhando em paralelo:** Front-3 (Aprovacoes), Front-4

### Dev Feature 1: ExecutarProximaEtapa + AprovarEtapa (AP-1 Strategist)

**O que o dev CRIA:**
- `dtos/pipeline/aprovar_etapa/request.py` -- AprovarEtapaRequest (dados_editados: JSON, etapa: str)
- `dtos/pipeline/aprovar_etapa/response.py` -- AprovarEtapaResponse (pipeline atualizado)
- `dtos/pipeline/buscar_etapa/response.py` -- BuscarEtapaResponse (entrada, saida, status)

**O que o dev ADICIONA:**
- `services/pipeline_service.py` -- executar_proxima_etapa(id), aprovar_etapa(id, etapa, dados)
- `routers/pipeline.py` -- POST /api/pipelines/{id}/executar, POST /api/pipelines/{id}/etapas/{etapa}/aprovar, GET /api/pipelines/{id}/etapas/{etapa}
- `factories/pipeline_factory.py` -- validar_aprovacao(), preparar_entrada_proxima_etapa()

**O que o dev INTEGRA:**
- `agents/strategist.py` -- chamado por pipeline_service ao executar etapa "strategist"
- `skills/trend_scanner.py` -- alimenta o Strategist com tendencias

**Dependencias:** Back-3 Dev Feature 1-3 + Back-2 Dev Feature 3 (agentes)
**Criterio de pronto:**
1. POST /api/pipelines/{id}/executar executa o Strategist e muda status da etapa para "aguardando_aprovacao"
2. GET /api/pipelines/{id}/etapas/strategist retorna saida do Strategist (briefing)
3. POST /api/pipelines/{id}/etapas/strategist/aprovar com briefing editado avanca pipeline para proxima etapa

---

### Dev Feature 2: RejeitarEtapa + Fluxo AP-2 (Copy + Hook)

**O que o dev CRIA:**
- `dtos/pipeline/rejeitar_etapa/request.py` -- RejeitarEtapaRequest (feedback: str)
- `dtos/pipeline/rejeitar_etapa/response.py` -- RejeitarEtapaResponse

**O que o dev ADICIONA:**
- `services/pipeline_service.py` -- rejeitar_etapa(id, etapa, feedback)
- `routers/pipeline.py` -- POST /api/pipelines/{id}/etapas/{etapa}/rejeitar

**O que o dev INTEGRA:**
- `agents/copywriter.py` -- executado apos AP-1 aprovado
- `agents/hook_specialist.py` -- executado apos Copywriter
- `skills/tone_guide.py` -- valida vocabulario apos Copywriter

**Dependencias:** Dev Feature 1 (ExecutarProximaEtapa)
**Criterio de pronto:**
1. Rejeitar re-executa agente com feedback. Status volta para "em_execucao"
2. Apos AP-1 aprovado, Copywriter + Hook Specialist executam em sequencia
3. Etapa "hook_specialist" fica "aguardando_aprovacao" com 3 hooks A/B/C na saida
4. tone_guide roda apos Copywriter e correcoes aparecem na saida

---

### Dev Feature 3: Fluxo AP-3 (Art Director + Visual) + AP-4 (Image Generator + Brand Gate)

**O que o dev INTEGRA:**
- `agents/art_director.py` -- executado apos AP-2 aprovado
- `agents/image_generator.py` -- executado apos AP-3 aprovado (3 variacoes)
- `skills/variation_engine.py` -- gera 3 variacoes de prompt antes do Image Generator
- `skills/brand_validator.py` -- valida imagem apos geracao
- `skills/brand_overlay.py` -- aplica foto + logo se valido
- `skills/visual_memory.py` -- consultada pelo Art Director

**O que o dev ADICIONA:**
- `services/pipeline_service.py` -- logica de retry do Brand Gate (max 2x)
- `factories/pipeline_factory.py` -- preparar_entrada_art_director(), preparar_entrada_image_generator()

**Dependencias:** Dev Feature 2 (fluxo AP-2 completo)
**Criterio de pronto:**
1. Apos AP-2 aprovado, Art Director executa e etapa fica "aguardando_aprovacao"
2. Apos AP-3 aprovado, Image Generator gera 3 variacoes por slide
3. Brand Gate valida e aplica overlay automaticamente
4. Se invalido, retry automatico (max 2x). Se falha, marca "revisao_manual"
5. Etapa "brand_gate" fica "aguardando_aprovacao" com variacoes de imagem

---

### Dev Feature 4: Fluxo final (Content Critic + Score)

**O que o dev CRIA:**
- `models/conteudo.py` -- ConteudoModel (SQLAlchemy)
- `models/imagem.py` -- ImagemModel (SQLAlchemy)
- `models/score.py` -- ScoreModel (SQLAlchemy)
- `dtos/score/buscar_score/response.py` -- BuscarScoreResponse
- `dtos/score/base.py` -- ScoreBase
- `data/repositories/sql/conteudo_repository.py`
- `data/repositories/sql/imagem_repository.py`
- `data/repositories/sql/score_repository.py`
- `mappers/score_mapper.py` -- to_response()

**O que o dev INTEGRA:**
- `agents/content_critic.py` -- executa apos AP-4, gera score
- `skills/visual_memory.py` -- salva preferencia apos AP-4

**O que o dev ADICIONA:**
- `services/pipeline_service.py` -- finalizar_pipeline()
- `routers/pipeline.py` -- GET /api/pipelines/{pipeline_id}/score

**Dependencias:** Dev Feature 3 (fluxo AP-3 + AP-4)
**Criterio de pronto:**
1. Apos AP-4, Content Critic executa e gera score com 6 dimensoes
2. Score persiste no banco (ScoreModel)
3. Conteudo final persiste no banco (ConteudoModel + ImagemModel)
4. GET /api/pipelines/{id}/score retorna BuscarScoreResponse
5. Pipeline status muda para "completo"
6. visual_memory salva preferencias das variacoes aprovadas/rejeitadas

---

## PACOTE BACK-5 -- Dominios: Historico (refatorar) + VisualPreference + Drive (v3)

**Pode comecar apos:** Back-4 (Pipeline completo)
**Outros devs trabalhando em paralelo:** Front-4 (Export), Front-5

### Dev Feature 1: ListarHistorico refatorado

**O que o dev CRIA:**
- `models/historico.py` -- HistoricoModel (SQLAlchemy, refatorar de db_service)
- `dtos/historico/listar_historico/request.py` -- ListarHistoricoFiltros (formato, status, data_inicio, data_fim, busca)
- `dtos/historico/listar_historico/response.py` -- ListarHistoricoResponse (lista paginada)
- `dtos/historico/buscar_historico/response.py` -- BuscarHistoricoResponse
- `dtos/historico/base.py` -- HistoricoItemBase
- `data/repositories/sql/historico_repository.py`
- `factories/historico_factory.py` -- to_model()
- `mappers/historico_mapper.py` -- to_list_response(), to_detail_response()
- `services/historico_service.py` -- listar(filtros), buscar(id), deletar(id)

**O que o dev REFATORA:**
- `routers/historico.py` -- GET /api/historico (adicionar filtros), GET /api/historico/{id}, DELETE /api/historico/{id}

**Dependencias:** Nenhuma dev feature deste pacote
**Criterio de pronto:**
1. GET /api/historico aceita filtros por formato, status, data. Retorna lista paginada
2. GET /api/historico/{id} retorna item individual com pipeline_id linkado
3. DELETE /api/historico/{id} faz soft delete

---

### Dev Feature 2: VisualPreference (CRUD)

**O que o dev CRIA:**
- `models/visual_preference.py` -- VisualPreferenceModel (SQLAlchemy)
- `dtos/visual_preference/salvar_preferencia/request.py` -- SalvarPreferenciaRequest
- `dtos/visual_preference/salvar_preferencia/response.py` -- SalvarPreferenciaResponse
- `dtos/visual_preference/listar_preferencias/response.py` -- ListarPreferenciasResponse
- `dtos/visual_preference/base.py` -- VisualPreferenceBase
- `data/repositories/sql/visual_preference_repository.py`
- `factories/visual_preference_factory.py` -- to_model()
- `mappers/visual_preference_mapper.py` -- to_response(), to_list_response()
- `services/visual_preference_service.py` -- salvar(), listar()
- `routers/visual_preference.py` -- POST /api/visual-preferences, GET /api/visual-preferences

**Dependencias:** Nenhuma
**Criterio de pronto:**
1. POST /api/visual-preferences salva preferencia com estilo + aprovado + contexto
2. GET /api/visual-preferences lista preferencias do tenant

---

### Dev Feature 3: SalvarConteudoDrive (v3)

**O que o dev CRIA:**
- `dtos/drive/salvar_conteudo_drive/request.py` -- SalvarConteudoDriveRequest (pipeline_id, imagens)
- `dtos/drive/salvar_conteudo_drive/response.py` -- SalvarConteudoDriveResponse (link_drive, pasta)

**O que o dev ADICIONA:**
- `services/drive_service.py` -- salvar_conteudo_v3() (cria subpasta, salva PDF + PNGs)
- `routers/drive.py` -- POST /api/google-drive/conteudo

**Dependencias:** Dev Feature 1 (Historico -- para registrar link do Drive)
**Criterio de pronto:** POST /api/google-drive/conteudo cria subpasta no Drive, salva arquivos, retorna link. Atualiza historico com google_drive_link.

---

## PACOTE FRONT-1 -- Dominio: Config (refatorar) + Agente

**Pode comecar apos:** Pacote Base Frontend
**Outros devs trabalhando em paralelo:** Back-1 (Config backend), Back-2 (Agente backend)

### Dev Feature 1: SalvarApiKeys (refatorar)

**O que o dev VERIFICA (existente):**
- `src/lib/services/config-service.ts` -- existe
- `src/lib/repositories/config-repository.ts` -- existe
- `src/routes/configuracoes/+page.svelte` -- existe

**O que o dev CRIA:**
- `src/lib/dtos/BrandPaletteDTO.ts` -- readonly, constructor, isValid(), toPayload()
- `src/lib/dtos/CreatorEntryDTO.ts` -- readonly, constructor, isValid(), toPayload()
- `src/lib/dtos/PlatformRuleDTO.ts` -- readonly, constructor, isValid(), toPayload()
- `src/lib/mocks/config-brand.mock.ts` -- brand palette realista (dark mode IT Valley)
- `src/lib/mocks/config-creators.mock.ts` -- 11 criadores confirmados no PRD
- `src/lib/mocks/config-platform.mock.ts` -- regras LinkedIn, Instagram, YouTube
- `src/lib/services/ConfigService.ts` -- novo (metodos static: salvarBrandPalette, buscarBrandPalette, salvarCreatorRegistry, buscarCreatorRegistry, salvarPlatformRules, buscarPlatformRules)
- `src/lib/repositories/ConfigRepository.ts` -- novo (mock/real via VITE_USE_MOCK)

**Dependencias:** Nenhuma
**Criterio de pronto:** Com VITE_USE_MOCK=true, ConfigService.buscarBrandPalette() retorna dados do mock. DTOs validam campos obrigatorios.

---

### Dev Feature 2: BrandPaletteForm

**O que o dev CRIA:**
- `src/lib/components/config/BrandPaletteForm.svelte` -- editor de cores, fonte, elementos obrigatorios. Color pickers para cada cor. Preview visual do resultado.
- `src/lib/components/config/ApiKeysForm.svelte` -- refatorar formulario de chaves existente para componente isolado

**O que o dev ADICIONA:**
- `src/routes/configuracoes/+page.svelte` -- tabs: API Keys | Brand Palette | Creator Registry | Platform Rules

**Dependencias:** Dev Feature 1
**Criterio de pronto:** Tela de configuracoes tem 4 tabs. BrandPaletteForm exibe paleta, permite editar cores, salva via mock. Valida que todas as cores sao hex validos.

---

### Dev Feature 3: CreatorRegistryForm + PlatformRulesForm

**O que o dev CRIA:**
- `src/lib/components/config/CreatorRegistryForm.svelte` -- CRUD de criadores (tabela editavel, adicionar/remover, funcao por select)
- `src/lib/components/config/PlatformRulesForm.svelte` -- editor de regras por plataforma (limites de caracteres, hashtags)

**O que o dev ADICIONA:**
- `src/routes/configuracoes/+page.svelte` -- conteudo das tabs Creator Registry e Platform Rules

**Dependencias:** Dev Feature 2 (tabs ja existem)
**Criterio de pronto:** CreatorRegistryForm lista criadores, permite adicionar/editar/remover com mock. PlatformRulesForm exibe regras por plataforma, permite editar.

---

### Dev Feature 4: ListarAgentes + VisualizarAgente

**O que o dev CRIA:**
- `src/lib/dtos/AgenteDTO.ts` -- readonly, constructor, isValid(), toPayload()
- `src/lib/components/agente/AgenteCard.svelte` -- card de agente/skill (nome, tipo, descricao, status)
- `src/lib/components/agente/AgenteDetalhe.svelte` -- painel com system prompt completo
- `src/lib/components/agente/PipelineVisual.svelte` -- diagrama visual do pipeline (7 etapas conectadas)
- `src/lib/mocks/agente.mock.ts` -- 6 agentes LLM + 6 skills com dados realistas
- `src/lib/services/AgenteService.ts` -- listar(), buscar(slug)
- `src/lib/repositories/AgenteRepository.ts` -- mock/real

**O que o dev REFATORA:**
- `src/routes/agentes/+page.svelte` -- grid de AgenteCard + diagrama PipelineVisual. Clique abre AgenteDetalhe.

**Dependencias:** Nenhuma
**Criterio de pronto:** Tela /agentes mostra 12 cards (6 agentes + 6 skills) com mock. Clique abre detalhe com system prompt. Diagrama do pipeline e visual.

---

## PACOTE FRONT-2 -- Dominio: Pipeline (Home + Wizard)

**Pode comecar apos:** Pacote Base Frontend
**Outros devs trabalhando em paralelo:** Back-3 (Pipeline backend), Front-1

### Dev Feature 1: IniciarPipeline (Home refatorada)

**O que o dev CRIA:**
- `src/lib/dtos/IniciarPipelineDTO.ts` -- readonly, constructor, isValid(), toPayload() (tema, formatos[], modo_funil, modo_entrada, disciplina, tecnologia, foto_criador_id)
- `src/lib/dtos/PipelineDTO.ts` -- readonly, constructor, isValid(), toPayload()
- `src/lib/components/home/FormatoSelector.svelte` -- 3 cards selecionaveis (Carrossel, Post Unico, Thumbnail YouTube) com dimensoes e plataformas
- `src/lib/components/home/FotoCriadorGaleria.svelte` -- galeria de fotos do criador (miniaturas clicaveis)
- `src/lib/mocks/pipeline.mock.ts` -- pipeline mockado com 7 etapas
- `src/lib/services/PipelineService.ts` -- iniciar()
- `src/lib/repositories/PipelineRepository.ts` -- mock/real

**O que o dev REFATORA:**
- `src/routes/+page.svelte` -- substituir formulario antigo (so carrossel) por novo: tema (textarea) + FormatoSelector + toggle modo_funil + tabs texto/disciplina + DisciplinaSelector (mover do carrossel) + FotoCriadorGaleria + botao "Criar Conteudo"

**O que o dev MOVE:**
- `src/lib/components/carrossel/DisciplinaSelector.svelte` -> `src/lib/components/home/DisciplinaSelector.svelte` (copiar, nao remover original)

**Dependencias:** Nenhuma
**Criterio de pronto:**
1. Home exibe formulario com tema + formatos + modo funil + tabs texto/disciplina
2. Botao desabilitado ate preencher tema (>= 20 chars) + selecionar formato
3. Submit cria pipeline via mock e redireciona para /pipeline/[id]
4. VITE_USE_MOCK=true funciona

---

### Dev Feature 2: AcompanharPipeline (Wizard)

**O que o dev CRIA:**
- `src/lib/dtos/PipelineStepDTO.ts` -- readonly, constructor, isValid(), toPayload()
- `src/lib/components/pipeline/PipelineWizard.svelte` -- wizard vertical/horizontal com 7 etapas. Cada etapa: nome do agente, status (badge colorido), tempo, acoes
- `src/lib/components/pipeline/PipelineStepCard.svelte` -- card de 1 etapa (clique expande detalhes)
- `src/lib/components/pipeline/PipelineStatusBadge.svelte` -- badge: pendente (cinza), em_execucao (azul+spinner), aguardando_aprovacao (amarelo piscante), aprovado (verde), rejeitado (vermelho), erro (vermelho)
- `src/routes/pipeline/[id]/+page.svelte` -- nova rota. Carrega pipeline por ID, renderiza PipelineWizard. Botoes para navegar para sub-telas de aprovacao.

**O que o dev ADICIONA:**
- `src/lib/services/PipelineService.ts` -- buscar(id)
- `src/lib/repositories/PipelineRepository.ts` -- buscar(id)
- `src/lib/mocks/pipeline.mock.ts` -- pipeline com etapas em diferentes status

**Dependencias:** Dev Feature 1 (IniciarPipeline -- cria o pipeline que sera buscado)
**Criterio de pronto:**
1. /pipeline/[id] renderiza wizard com 7 etapas com status do mock
2. Etapa "aguardando_aprovacao" mostra botao para ir a sub-tela de aprovacao
3. Etapa "em_execucao" mostra spinner
4. Etapa "erro" mostra botao "Retomar"
5. Pipeline concluido mostra botao "Ver Resultado"

---

## PACOTE FRONT-3 -- Dominio: Aprovacoes (AP-1, AP-2, AP-3, AP-4)

**Pode comecar apos:** Front-2 (Pipeline Wizard precisa existir para navegar)
**Outros devs trabalhando em paralelo:** Back-4 (Pipeline aprovacoes), Front-4

### Dev Feature 1: AP-1 Aprovacao de Briefing

**O que o dev CRIA:**
- `src/lib/dtos/BriefingDTO.ts` -- readonly, constructor, isValid(), toPayload() (briefing_completo, tema_original, formato_alvo, pecas_funil[], tendencias_usadas[])
- `src/lib/components/briefing/BriefingEditor.svelte` -- textarea editavel do briefing completo, com modo leitura e modo edicao
- `src/lib/components/briefing/FunilPlanner.svelte` -- lista de pecas do funil (titulo, etapa_funil, formato). Editavel se modo funil ativo.
- `src/lib/mocks/briefing.mock.ts` -- briefing realista com funil de 5 pecas
- `src/lib/services/BriefingService.ts` -- buscar(pipeline_id), aprovar(pipeline_id, dados), rejeitar(pipeline_id, feedback)
- `src/lib/repositories/BriefingRepository.ts` -- mock/real
- `src/routes/pipeline/[id]/briefing/+page.svelte` -- tela AP-1

**Dependencias:** Nenhuma deste pacote (mas Front-2 precisa estar pronto para navegar)
**Criterio de pronto:**
1. /pipeline/[id]/briefing exibe briefing do Strategist (mock)
2. Briefing e editavel inline (textarea)
3. Se modo funil: mostra lista de pecas editavel
4. "Aprovar e Continuar" envia dados e redireciona para /pipeline/[id]
5. "Rejeitar e Regerar" exibe campo de feedback e re-submete

---

### Dev Feature 2: AP-2 Aprovacao de Copy + Hook

**O que o dev CRIA:**
- `src/lib/dtos/CopyDTO.ts` -- readonly, constructor, isValid(), toPayload()
- `src/lib/dtos/HookDTO.ts` -- readonly, constructor, isValid(), toPayload()
- `src/lib/components/copy/CopyEditor.svelte` -- edicao de headline, narrativa, CTA (inline editavel)
- `src/lib/components/copy/HookSelector.svelte` -- 3 cards A/B/C com radio selection. Cada card mostra texto do hook.
- `src/lib/components/copy/SlideSequenceEditor.svelte` -- lista de slides editavel, reordenavel (drag-and-drop), adicionar/remover
- `src/lib/components/copy/ToneGuideAlerts.svelte` -- lista de correcoes do tone_guide (badge amarelo por correcao)
- `src/lib/mocks/copy.mock.ts` -- copy com 7 slides + 3 hooks + 2 correcoes tone_guide
- `src/lib/services/CopyService.ts` -- buscar(pipeline_id), aprovar(pipeline_id, copy, hook), rejeitar(pipeline_id, feedback)
- `src/lib/repositories/CopyRepository.ts` -- mock/real
- `src/routes/pipeline/[id]/copy/+page.svelte` -- tela AP-2

**Dependencias:** Nenhuma deste pacote
**Criterio de pronto:**
1. /pipeline/[id]/copy exibe headline, narrativa, CTA, sequencia de slides (mock)
2. 3 hooks A/B/C renderizam como cards selecionaveis
3. Slide sequence e editavel, reordenavel, com adicionar/remover
4. Correcoes do tone_guide aparecem como alertas
5. Aprovar requer hook selecionado

---

### Dev Feature 3: AP-3 Aprovacao de Prompt Visual

**O que o dev CRIA:**
- `src/lib/dtos/PromptVisualDTO.ts` -- readonly, constructor, isValid(), toPayload()
- `src/lib/components/visual/PromptEditor.svelte` -- textarea de prompt por slide (editavel)
- `src/lib/components/visual/PromptSlideList.svelte` -- accordion com todos os prompts (um por slide)
- `src/lib/components/visual/BrandPalettePreview.svelte` -- preview inline da paleta (cores + fonte + estilo)
- `src/lib/components/visual/VisualMemoryPanel.svelte` -- lista de preferencias visuais anteriores (aprovadas/rejeitadas)
- `src/lib/mocks/visual.mock.ts` -- prompts por slide + preferencias visuais
- `src/lib/services/VisualService.ts` -- buscar(pipeline_id), aprovar(pipeline_id, prompts), rejeitar(pipeline_id, feedback)
- `src/lib/repositories/VisualRepository.ts` -- mock/real
- `src/routes/pipeline/[id]/visual/+page.svelte` -- tela AP-3

**Dependencias:** Nenhuma deste pacote
**Criterio de pronto:**
1. /pipeline/[id]/visual exibe prompts por slide em accordion (mock)
2. Cada prompt e editavel (textarea com minimo 50 chars)
3. Brand palette preview mostra cores e elementos
4. Visual memory mostra estilos aprovados/rejeitados anteriores
5. Aprovar envia prompts editados

---

### Dev Feature 4: AP-4 Aprovacao de Imagem

**O que o dev CRIA:**
- `src/lib/dtos/ImagemVariacaoDTO.ts` -- readonly, constructor, isValid(), toPayload()
- `src/lib/components/imagem/ImageVariationGrid.svelte` -- grid 3 colunas de variacoes por slide (radio selection)
- `src/lib/components/imagem/ImageSlideAccordion.svelte` -- accordion por slide (abre/fecha)
- `src/lib/components/imagem/ImageZoomModal.svelte` -- modal fullscreen de imagem (zoom)
- `src/lib/components/imagem/BrandGateStatus.svelte` -- badge "valido" (verde) ou "revisao manual" (amarelo) por slide
- `src/lib/mocks/imagem.mock.ts` -- 7 slides x 3 variacoes (placeholders) + brand gate status
- `src/lib/services/ImagemService.ts` -- buscar(pipeline_id), aprovar(pipeline_id, selecoes), rejeitar(pipeline_id), regerar(pipeline_id, slide_index)
- `src/lib/repositories/ImagemRepository.ts` -- mock/real
- `src/routes/pipeline/[id]/imagem/+page.svelte` -- tela AP-4

**Dependencias:** Nenhuma deste pacote
**Criterio de pronto:**
1. /pipeline/[id]/imagem exibe grid de variacoes por slide (mock)
2. Cada slide tem 3 imagens selecionaveis (radio)
3. Duplo-clique abre zoom modal
4. Brand Gate status visivel por slide
5. "Regerar" funciona para 1 variacao
6. Aprovar requer 1 variacao selecionada por slide

---

## PACOTE FRONT-4 -- Dominio: Export + Score + Historico

**Pode comecar apos:** Front-3 (aprovacoes precisam existir para chegar no export)
**Outros devs trabalhando em paralelo:** Back-5 (Historico + Drive)

### Dev Feature 1: VisualizarScore + ExportarPdf

**O que o dev CRIA:**
- `src/lib/dtos/ScoreDTO.ts` -- readonly, constructor, isValid(), toPayload()
- `src/lib/components/export/ScoreRadar.svelte` -- radar chart com 6 dimensoes (clarity, impact, originality, scroll_stop, cta_strength, final_score). SVG ou canvas.
- `src/lib/components/export/ScoreCard.svelte` -- card de 1 dimensao (nome + valor 0-10 + barra de progresso)
- `src/lib/components/export/SlidePreviewCarousel.svelte` -- carousel de slides finais (dots + setas + swipe)
- `src/lib/components/export/ExportActions.svelte` -- botoes: Exportar PDF, Download PNG, Salvar no Drive, Copiar Legenda, Novo Conteudo
- `src/lib/mocks/score.mock.ts` -- score realista (6 dimensoes, decision, best_variation)
- `src/lib/services/ExportService.ts` -- buscarScore(pipeline_id), exportarPdf(slides), salvarDrive(pipeline_id)
- `src/lib/repositories/ExportRepository.ts` -- mock/real
- `src/routes/pipeline/[id]/export/+page.svelte` -- tela final

**Dependencias:** Nenhuma deste pacote
**Criterio de pronto:**
1. /pipeline/[id]/export exibe score radar + 6 score cards (mock)
2. Carousel navega entre slides finais
3. Badge verde "Aprovado" se final_score >= 7, amarelo "Recomenda ajustes" se < 7
4. "Exportar PDF" gera PDF via jsPDF e faz download
5. "Copiar Legenda" copia para clipboard
6. "Novo Conteudo" navega para /

---

### Dev Feature 2: ListarHistorico refatorado

**O que o dev CRIA:**
- `src/lib/dtos/HistoricoItemDTO.ts` -- readonly, constructor, isValid(), toPayload()
- `src/lib/components/historico/HistoricoCard.svelte` -- card de item (titulo, formato badge, data, score, status)
- `src/lib/components/historico/HistoricoFiltros.svelte` -- filtros: formato (select), status (select), periodo (date range), busca (text)
- `src/lib/mocks/historico.mock.ts` -- 10 itens variados (carrossel, post, thumbnail, diferentes status e scores)
- `src/lib/services/HistoricoService.ts` -- listar(filtros), deletar(id)
- `src/lib/repositories/HistoricoRepository.ts` -- mock/real

**O que o dev REFATORA:**
- `src/routes/historico/+page.svelte` -- grid de HistoricoCard + HistoricoFiltros. Clique no card abre /pipeline/[id] ou detalhe.

**Dependencias:** Dev Feature 1 (ExportService para reabrir pipeline)
**Criterio de pronto:**
1. /historico exibe grid de cards multi-formato (mock)
2. Filtros por formato, status, periodo funcionam
3. Cada card mostra formato (badge), score, data
4. "Remover" faz soft delete com confirmacao via modal

---

## PACOTE FRONT-5 -- Dominio: Carrossel legado (manter) + Config extras

**Pode comecar apos:** Front-1
**Outros devs trabalhando em paralelo:** Back-5

### Dev Feature 1: DesignSystemManager + FotoManager

**O que o dev CRIA:**
- `src/lib/components/config/DesignSystemManager.svelte` -- upload/preview/delete de design systems (integra com Drive)
- `src/lib/components/config/FotoManager.svelte` -- upload/selecao/preview de fotos do criador

**O que o dev ADICIONA:**
- `src/routes/configuracoes/+page.svelte` -- tabs: Design Systems, Fotos (adicionais as 4 existentes)

**Dependencias:** Front-1 Dev Feature 2 (tabs de config ja existem)
**Criterio de pronto:**
1. Tab Design Systems permite upload, lista, preview e delete
2. Tab Fotos permite upload, selecao e preview de fotos
3. Funciona com VITE_USE_MOCK=true

---

## RESUMO DE PACOTES E CRONOGRAMA

```
SEMANA 1:
  Pacote Base Frontend .......... 1 dev, ~2 dias
  Pacote Base Backend ........... 1 dev, ~2 dias
  Back-1 (Config) ............... 1 dev, ~2 dias (apos base)
  Back-2 (Agente) ............... 1 dev, ~2 dias (apos base, paralelo com Back-1)
  Front-1 (Config + Agente) .... 1 dev, ~3 dias (apos base front)

SEMANA 2:
  Back-3 (Pipeline core + Skills) ... 1 dev, ~3 dias
  Front-2 (Home + Wizard) .......... 1 dev, ~3 dias

SEMANA 3:
  Back-4 (Pipeline aprovacoes) ..... 1 dev, ~4 dias
  Front-3 (Aprovacoes AP1-AP4) ..... 1 dev, ~4 dias (paralelo com Back-4)

SEMANA 4:
  Back-5 (Historico + Visual + Drive) ... 1 dev, ~2 dias
  Front-4 (Export + Score + Historico) .. 1 dev, ~3 dias
  Front-5 (Config extras) .............. 1 dev, ~1 dia
```

---

## REGRAS DE COORDENACAO

1. **Dev Front trabalha com VITE_USE_MOCK=true** ate o backend correspondente estar pronto. Nunca depender do backend para comecar.

2. **Conflitos de arquivo zero:** Nenhuma dev feature de frontend toca o mesmo arquivo que outra dev feature de frontend no mesmo pacote (exceto +page.svelte de configuracoes, que e por tabs isoladas). Nenhuma dev feature de backend toca o mesmo router simultaneamente (services podem ser tocados em sequencia dentro do mesmo pacote).

3. **Integracao front+back:** Apos cada pacote de backend ficar pronto, o dev front troca `VITE_USE_MOCK=false` para o dominio correspondente e integra. Integracao e testada por dominio, nao tudo de uma vez.

4. **Criterio de aceite final de um pacote:** Todas as dev features do pacote passam nos criterios individuais + testes de integracao entre features do mesmo pacote (ex: CriarPipeline + BuscarPipeline funcionam em sequencia).

5. **Comunicacao entre devs:** Todo dev sabe o que os outros estao fazendo (informado nos pacotes acima). Se precisar alterar arquivo que outro dev esta usando, comunicar antes.

---

## TABELA DE REFERENCIA RAPIDA

| Pacote | Dominio | Dev Features | Depende de |
|--------|---------|-------------|------------|
| Base Backend | Infraestrutura | models/base, data layer, connections | - |
| Base Frontend | Infraestrutura | UI components, Sidebar, utils | - |
| Back-1 | Config | 4: BrandPalette (save/get), CreatorRegistry (save/get), PlatformRules (save/get) | Base Back |
| Back-2 | Agente | 3: Listar, Buscar, Executar (debug) | Base Back |
| Back-3 | Pipeline + Skills | 4: CriarPipeline, Buscar+Listar, Cancelar+Retomar, 6 Skills | Base Back, Back-1 |
| Back-4 | Pipeline (aprovacoes) | 4: AP-1 Strategist, AP-2 Copy+Hook, AP-3+AP-4 Visual+Imagem, Final (Score) | Back-3, Back-2 |
| Back-5 | Historico + VisualPref + Drive | 3: Historico refatorado, VisualPreference CRUD, Drive v3 | Back-4 |
| Front-1 | Config + Agente | 4: DTOs+mocks, BrandPaletteForm, CreatorRegistry+PlatformRules, Agentes | Base Front |
| Front-2 | Pipeline (Home + Wizard) | 2: IniciarPipeline (Home), AcompanharPipeline (Wizard) | Base Front |
| Front-3 | Aprovacoes | 4: AP-1 Briefing, AP-2 Copy+Hook, AP-3 Visual, AP-4 Imagem | Front-2 |
| Front-4 | Export + Score + Historico | 2: Export+Score, Historico refatorado | Front-3 |
| Front-5 | Config extras | 1: DesignSystemManager + FotoManager | Front-1 |

**Total: 31 dev features em 11 pacotes (2 base + 5 back + 4 front).**

---

*Documento gerado pelo Agente 08 (P.O. / Product Owner) da esteira IT Valley.*
*Proximo: Dev Front (Agente 09) e Dev Back (Agente 10) -- em paralelo.*
