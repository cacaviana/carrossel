# Gestao de Projeto -- Content Factory v3

**Data de criacao:** 2026-04-02
**Space:** Sistemas IT Valley
**Projeto (Folder):** Content Factory v3 -- Fabrica de Conteudo Visual
**Total de dominios (Lists):** 11
**Total de dev features (Tasks):** 31
**Niveis de implementacao:** 5 (0 a 4)
**Workflow de status:** A FAZER -> FEITO IA -> REVISAO DEV -> FEITO DEV -> QA -> FINALIZADA

---

## Mapa de Dominios

| # | List no ClickUp | Dev Features | Depende de | Nivel |
|---|----------------|-------------|------------|-------|
| 1 | Dominio Base Backend | 1 | -- | 0 |
| 2 | Dominio Base Frontend | 1 | -- | 0 |
| 3 | Dominio Config Backend | 4 | Dominio Base Backend | 1 |
| 4 | Dominio Agente Backend | 3 | Dominio Base Backend | 1 |
| 5 | Dominio Config Frontend | 4 | Dominio Base Frontend | 1 |
| 6 | Dominio Pipeline Backend | 4 | Dominio Base Backend, Dominio Config Backend | 2 |
| 7 | Dominio Pipeline Frontend | 2 | Dominio Base Frontend | 2 |
| 8 | Dominio Aprovacoes Backend | 4 | Dominio Pipeline Backend, Dominio Agente Backend | 3 |
| 9 | Dominio Aprovacoes Frontend | 4 | Dominio Pipeline Frontend | 3 |
| 10 | Dominio Finalizacao Backend | 3 | Dominio Aprovacoes Backend | 4 |
| 11 | Dominio Finalizacao Frontend | 1 | Dominio Aprovacoes Frontend | 4 |

---

## Dominio Base Backend

**O que e:** Infraestrutura base do backend -- models, repositorio generico, conexao com banco MSSQL e configuracoes de ambiente. Sem este dominio pronto, nenhum outro dominio backend pode comecar.
**Depende de:** nenhum (Nivel 0)
**Libera:** Dominio Config Backend, Dominio Agente Backend, Dominio Pipeline Backend
**Status customizados:** A FAZER | FEITO IA | REVISAO DEV | FEITO DEV | QA | FINALIZADA

### Tasks (Dev Features)

| # | Task no ClickUp | Descricao GP | Criterios de Aceite | Depende de | Status |
|---|----------------|-------------|---------------------|------------|--------|
| 1 | Criar Infraestrutura Base (CriarBaseBackendRequest) | Criar a base de dados, conexao com banco, modelo generico com suporte a multitenancia e repositorio reutilizavel | 1. Comando de importacao do modelo base executa sem erro 2. Conexao com banco MSSQL funciona 3. Repositorio generico permite criar, buscar, listar, atualizar e deletar 4. Servidor inicia na porta 8000 sem erro | -- | A FAZER |

### Arquivos do Dominio

| Arquivo | Criado na Task |
|---------|---------------|
| config.py | Criar Infraestrutura Base |
| models/base.py | Criar Infraestrutura Base |
| data/interfaces/base_repository.py | Criar Infraestrutura Base |
| data/repositories/sql/base_sql_repository.py | Criar Infraestrutura Base |
| data/connections/sql_connection.py | Criar Infraestrutura Base |
| data/connections/database.py | Criar Infraestrutura Base |

---

## Dominio Base Frontend

**O que e:** Componentes de interface reutilizaveis (modal, spinner, skeleton, toggle, tabs, banner), menu lateral de navegacao e funcoes utilitarias. Sem este dominio pronto, nenhum outro dominio frontend pode comecar.
**Depende de:** nenhum (Nivel 0)
**Libera:** Dominio Config Frontend, Dominio Pipeline Frontend, Dominio Aprovacoes Frontend
**Status customizados:** A FAZER | FEITO IA | REVISAO DEV | FEITO DEV | QA | FINALIZADA

### Tasks (Dev Features)

| # | Task no ClickUp | Descricao GP | Criterios de Aceite | Depende de | Status |
|---|----------------|-------------|---------------------|------------|--------|
| 1 | Criar Componentes Base e Sidebar (CriarBaseFrontendRequest) | Criar componentes visuais genericos (modal, spinner, skeleton, toggle, tabs, banner), menu lateral de navegacao e funcoes utilitarias | 1. Aplicacao inicia na porta 5173 sem erro 2. Menu lateral renderiza com itens: Home, Pipeline, Historico, Agentes, Config 3. Todos os componentes novos renderizam isoladamente 4. Modo mock (VITE_USE_MOCK=true) funciona | -- | A FAZER |

### Arquivos do Dominio

| Arquivo | Criado na Task |
|---------|---------------|
| src/lib/components/ui/Modal.svelte | Criar Componentes Base e Sidebar |
| src/lib/components/ui/Spinner.svelte | Criar Componentes Base e Sidebar |
| src/lib/components/ui/Skeleton.svelte | Criar Componentes Base e Sidebar |
| src/lib/components/ui/Toggle.svelte | Criar Componentes Base e Sidebar |
| src/lib/components/ui/Tabs.svelte | Criar Componentes Base e Sidebar |
| src/lib/components/ui/Banner.svelte | Criar Componentes Base e Sidebar |
| src/lib/components/layout/Sidebar.svelte | Criar Componentes Base e Sidebar |
| src/lib/utils/formatters.ts | Criar Componentes Base e Sidebar |
| src/lib/utils/validators.ts | Criar Componentes Base e Sidebar |

---

## Dominio Config Backend

**O que e:** Gerenciamento das configuracoes do sistema -- paleta de cores da marca, registro de criadores de conteudo e regras por plataforma (LinkedIn, Instagram, YouTube). Sao arquivos JSON salvos no servidor.
**Depende de:** Dominio Base Backend (Nivel 1)
**Libera:** Dominio Pipeline Backend (precisa da brand palette para o Brand Gate)
**Status customizados:** A FAZER | FEITO IA | REVISAO DEV | FEITO DEV | QA | FINALIZADA

### Tasks (Dev Features)

| # | Task no ClickUp | Descricao GP | Criterios de Aceite | Depende de | Status |
|---|----------------|-------------|---------------------|------------|--------|
| 1 | Salvar Paleta de Cores (SalvarBrandPaletteRequest) | Permitir que o administrador salve as cores, fonte e elementos visuais obrigatorios da marca | 1. Paleta salva no servidor em arquivo JSON 2. Retorna dados salvos com confirmacao 3. Valida que todas as cores sao hexadecimais validos | -- | A FAZER |
| 2 | Buscar Paleta de Cores (BuscarBrandPaletteRequest) | Consultar a paleta de cores atual da marca | 1. Retorna paleta completa com cores, fonte e estilo 2. Retorna erro amigavel se paleta ainda nao foi configurada | Task 1 | A FAZER |
| 3 | Salvar Registro de Criadores (SalvarCreatorRegistryRequest) | Cadastrar a lista de criadores de conteudo que alimentam o scanner de tendencias | 1. Lista de criadores salva no servidor em arquivo JSON 2. Cada criador tem nome, funcao, plataforma e URL 3. Retorna confirmacao com total de criadores salvos | -- | A FAZER |
| 4 | Buscar Registro de Criadores e Gerenciar Regras de Plataforma (BuscarCreatorRegistryRequest) | Consultar criadores cadastrados e gerenciar regras por plataforma (limites de caracteres, hashtags) | 1. Retorna lista de criadores cadastrados 2. Salva e retorna regras por plataforma 3. Arquivos JSON gravados corretamente | Task 3 | A FAZER |

### Arquivos do Dominio

| Arquivo | Criado na Task |
|---------|---------------|
| dtos/config/salvar_brand_palette/request.py | Salvar Paleta de Cores |
| dtos/config/salvar_brand_palette/response.py | Salvar Paleta de Cores |
| dtos/config/buscar_brand_palette/response.py | Buscar Paleta de Cores |
| dtos/config/salvar_creator_registry/request.py | Salvar Registro de Criadores |
| dtos/config/salvar_creator_registry/response.py | Salvar Registro de Criadores |
| dtos/config/buscar_creator_registry/response.py | Buscar Registro de Criadores |
| dtos/config/salvar_platform_rules/request.py | Buscar Registro de Criadores |
| dtos/config/salvar_platform_rules/response.py | Buscar Registro de Criadores |
| dtos/config/buscar_platform_rules/response.py | Buscar Registro de Criadores |
| services/config_service.py | Salvar Paleta de Cores |
| routers/config.py | Salvar Paleta de Cores |
| factories/config_factory.py | Salvar Paleta de Cores |

---

## Dominio Agente Backend

**O que e:** Gerenciamento dos 6 agentes de inteligencia artificial (Strategist, Copywriter, Hook Specialist, Art Director, Image Generator, Content Critic) e 6 funcoes automaticas (brand overlay, brand validator, visual memory, variation engine, tone guide, trend scanner). Permite listar, consultar detalhes e testar cada agente individualmente.
**Depende de:** Dominio Base Backend (Nivel 1)
**Libera:** Dominio Aprovacoes Backend (agentes sao chamados pelo pipeline)
**Status customizados:** A FAZER | FEITO IA | REVISAO DEV | FEITO DEV | QA | FINALIZADA

### Tasks (Dev Features)

| # | Task no ClickUp | Descricao GP | Criterios de Aceite | Depende de | Status |
|---|----------------|-------------|---------------------|------------|--------|
| 1 | Listar Agentes (ListarAgentesRequest) | Mostrar todos os agentes e funcoes automaticas do sistema com nome, tipo e descricao | 1. Retorna lista com 12 itens (6 agentes + 6 funcoes) 2. Cada item tem nome, tipo (LLM ou deterministico) e descricao 3. Retorna status 200 | -- | A FAZER |
| 2 | Buscar Agente (BuscarAgenteRequest) | Consultar detalhes de um agente especifico, incluindo suas instrucoes de funcionamento | 1. Retorna agente com instrucoes completas 2. Retorna erro 404 se agente nao existe | Task 1 | A FAZER |
| 3 | Executar Agente em Modo Teste (ExecutarAgenteRequest) | Permitir testar um agente individualmente com uma entrada livre, para fins de debug | 1. Recebe entrada em formato livre e retorna saida do agente 2. Registra tempo de execucao 3. Retorna erro 404 se agente nao existe | Task 2 | A FAZER |

### Arquivos do Dominio

| Arquivo | Criado na Task |
|---------|---------------|
| dtos/agente/listar_agentes/response.py | Listar Agentes |
| dtos/agente/base.py | Listar Agentes |
| dtos/agente/buscar_agente/response.py | Buscar Agente |
| dtos/agente/executar_agente/request.py | Executar Agente em Modo Teste |
| dtos/agente/executar_agente/response.py | Executar Agente em Modo Teste |
| routers/agente.py | Listar Agentes |
| services/agente_service.py | Listar Agentes |
| mappers/agente_mapper.py | Listar Agentes |
| factories/agente_factory.py | Listar Agentes |
| agents/strategist.py | Executar Agente em Modo Teste |
| agents/copywriter.py | Executar Agente em Modo Teste |
| agents/hook_specialist.py | Executar Agente em Modo Teste |
| agents/art_director.py | Executar Agente em Modo Teste |
| agents/image_generator.py | Executar Agente em Modo Teste |
| agents/content_critic.py | Executar Agente em Modo Teste |

---

## Dominio Config Frontend

**O que e:** Telas de configuracao do sistema -- edicao da paleta de cores da marca, gerenciamento de criadores de conteudo, regras por plataforma, visualizacao dos agentes e funcoes. Tudo funciona inicialmente com dados simulados (mock).
**Depende de:** Dominio Base Frontend (Nivel 1)
**Libera:** Dominio Finalizacao Frontend (config extras)
**Status customizados:** A FAZER | FEITO IA | REVISAO DEV | FEITO DEV | QA | FINALIZADA

### Tasks (Dev Features)

| # | Task no ClickUp | Descricao GP | Criterios de Aceite | Depende de | Status |
|---|----------------|-------------|---------------------|------------|--------|
| 1 | Criar DTOs e Mocks de Configuracao (SalvarApiKeysRequest) | Criar estrutura de dados e dados simulados para paleta de cores, criadores e regras de plataforma | 1. DTOs validam campos obrigatorios 2. Mocks retornam dados realistas de paleta, 11 criadores e regras para 3 plataformas 3. Servicos funcionam com modo mock ativo | -- | A FAZER |
| 2 | Criar Formulario de Paleta de Cores (CriarBrandPaletteFormRequest) | Criar formulario visual para editar cores, fonte e elementos da marca com seletores de cor e pre-visualizacao | 1. Tela de configuracoes tem 4 abas: Chaves API, Paleta, Criadores, Regras 2. Formulario exibe paleta com seletores de cor 3. Valida que todas as cores sao hexadecimais validos 4. Salva alteracoes via mock | Task 1 | A FAZER |
| 3 | Criar Formularios de Criadores e Regras (CriarCreatorRegistryFormRequest) | Criar formularios para gerenciar criadores de conteudo (adicionar, editar, remover) e regras por plataforma | 1. Aba Criadores lista criadores em tabela editavel 2. Permite adicionar, editar e remover criadores 3. Aba Regras exibe regras por plataforma 4. Funciona com modo mock ativo | Task 2 | A FAZER |
| 4 | Listar e Visualizar Agentes (ListarAgentesVisualizarRequest) | Mostrar todos os 12 componentes do pipeline (agentes + funcoes) com detalhes e diagrama visual do fluxo | 1. Tela de agentes mostra 12 cards com dados simulados 2. Clique no card abre detalhes com instrucoes 3. Diagrama visual do pipeline e apresentado | -- | A FAZER |

### Arquivos do Dominio

| Arquivo | Criado na Task |
|---------|---------------|
| src/lib/dtos/BrandPaletteDTO.ts | Criar DTOs e Mocks de Configuracao |
| src/lib/dtos/CreatorEntryDTO.ts | Criar DTOs e Mocks de Configuracao |
| src/lib/dtos/PlatformRuleDTO.ts | Criar DTOs e Mocks de Configuracao |
| src/lib/mocks/config-brand.mock.ts | Criar DTOs e Mocks de Configuracao |
| src/lib/mocks/config-creators.mock.ts | Criar DTOs e Mocks de Configuracao |
| src/lib/mocks/config-platform.mock.ts | Criar DTOs e Mocks de Configuracao |
| src/lib/services/ConfigService.ts | Criar DTOs e Mocks de Configuracao |
| src/lib/repositories/ConfigRepository.ts | Criar DTOs e Mocks de Configuracao |
| src/lib/components/config/BrandPaletteForm.svelte | Criar Formulario de Paleta de Cores |
| src/lib/components/config/ApiKeysForm.svelte | Criar Formulario de Paleta de Cores |
| src/lib/components/config/CreatorRegistryForm.svelte | Criar Formularios de Criadores e Regras |
| src/lib/components/config/PlatformRulesForm.svelte | Criar Formularios de Criadores e Regras |
| src/lib/dtos/AgenteDTO.ts | Listar e Visualizar Agentes |
| src/lib/components/agente/AgenteCard.svelte | Listar e Visualizar Agentes |
| src/lib/components/agente/AgenteDetalhe.svelte | Listar e Visualizar Agentes |
| src/lib/components/agente/PipelineVisual.svelte | Listar e Visualizar Agentes |
| src/lib/mocks/agente.mock.ts | Listar e Visualizar Agentes |
| src/lib/services/AgenteService.ts | Listar e Visualizar Agentes |
| src/lib/repositories/AgenteRepository.ts | Listar e Visualizar Agentes |

---

## Dominio Pipeline Backend

**O que e:** Nucleo do sistema v3 -- criacao, acompanhamento, cancelamento e retomada do pipeline de geracao de conteudo. Inclui tambem as 6 funcoes automaticas (skills) que atuam dentro do pipeline. Cada pipeline tem 7 etapas e persiste estado no banco para retomada a qualquer momento.
**Depende de:** Dominio Base Backend, Dominio Config Backend (Nivel 2)
**Libera:** Dominio Aprovacoes Backend
**Status customizados:** A FAZER | FEITO IA | REVISAO DEV | FEITO DEV | QA | FINALIZADA

### Tasks (Dev Features)

| # | Task no ClickUp | Descricao GP | Criterios de Aceite | Depende de | Status |
|---|----------------|-------------|---------------------|------------|--------|
| 1 | Criar Pipeline (CriarPipelineRequest) | Iniciar um novo pipeline de geracao de conteudo com tema, formato e configuracoes | 1. Pipeline criado com status "pendente" e 7 etapas 2. Tema deve ter minimo 20 caracteres 3. Formato deve ser valido (carrossel, post unico ou thumbnail YouTube) 4. Retorna identificador do pipeline e status 201 | -- | A FAZER |
| 2 | Buscar e Listar Pipelines (BuscarPipelineRequest) | Consultar um pipeline por identificador ou listar todos os pipelines com filtros | 1. Busca retorna pipeline com 7 etapas e seus status 2. Listagem aceita filtros por formato, status e periodo 3. Retorna erro 404 se pipeline nao existe 4. Resultados isolados por empresa (tenant) | Task 1 | A FAZER |
| 3 | Cancelar e Retomar Pipeline (CancelarPipelineRequest) | Cancelar um pipeline em andamento ou retomar um pipeline que falhou | 1. Cancelar muda status para "cancelado" 2. Retomar re-executa a etapa que falhou 3. Pipeline ja cancelado nao pode ser retomado (erro 400) 4. Pipeline ja completo nao pode ser cancelado | Task 2 | A FAZER |
| 4 | Criar Funcoes Automaticas do Pipeline (CriarSkillsRequest) | Implementar as 6 funcoes automaticas: aplicar marca na imagem, validar cores, memoria visual, gerador de variacoes, validador de vocabulario e scanner de tendencias | 1. Validador de marca recebe imagem e retorna se esta valida com lista de erros 2. Aplicador de marca insere foto redonda e logo na imagem 3. Gerador de variacoes recebe 1 descricao e retorna 3 variacoes 4. Validador de vocabulario checa tom de voz e retorna correcoes 5. Scanner de tendencias retorna artigos recentes com cache de 1 hora 6. Memoria visual salva e recupera preferencias do banco | -- | A FAZER |

### Arquivos do Dominio

| Arquivo | Criado na Task |
|---------|---------------|
| dtos/pipeline/criar_pipeline/request.py | Criar Pipeline |
| dtos/pipeline/criar_pipeline/response.py | Criar Pipeline |
| dtos/pipeline/base.py | Criar Pipeline |
| models/pipeline.py | Criar Pipeline |
| factories/pipeline_factory.py | Criar Pipeline |
| mappers/pipeline_mapper.py | Criar Pipeline |
| services/pipeline_service.py | Criar Pipeline |
| routers/pipeline.py | Criar Pipeline |
| data/repositories/sql/pipeline_repository.py | Criar Pipeline |
| dtos/pipeline/buscar_pipeline/response.py | Buscar e Listar Pipelines |
| dtos/pipeline/listar_pipelines/request.py | Buscar e Listar Pipelines |
| dtos/pipeline/listar_pipelines/response.py | Buscar e Listar Pipelines |
| skills/brand_overlay.py | Criar Funcoes Automaticas do Pipeline |
| skills/brand_validator.py | Criar Funcoes Automaticas do Pipeline |
| skills/visual_memory.py | Criar Funcoes Automaticas do Pipeline |
| skills/variation_engine.py | Criar Funcoes Automaticas do Pipeline |
| skills/tone_guide.py | Criar Funcoes Automaticas do Pipeline |
| skills/trend_scanner.py | Criar Funcoes Automaticas do Pipeline |

---

## Dominio Pipeline Frontend

**O que e:** Tela de inicio do pipeline (Home refatorada com selecao de formato, modo funil, texto ou disciplina) e tela de acompanhamento do pipeline como um assistente passo a passo (wizard) com 7 etapas visuais.
**Depende de:** Dominio Base Frontend (Nivel 2)
**Libera:** Dominio Aprovacoes Frontend
**Status customizados:** A FAZER | FEITO IA | REVISAO DEV | FEITO DEV | QA | FINALIZADA

### Tasks (Dev Features)

| # | Task no ClickUp | Descricao GP | Criterios de Aceite | Depende de | Status |
|---|----------------|-------------|---------------------|------------|--------|
| 1 | Iniciar Pipeline na Home (IniciarPipelineRequest) | Refatorar a tela inicial para suportar selecao de formato (carrossel, post unico, thumbnail), modo funil, texto livre ou disciplina, e foto do criador | 1. Home exibe formulario com tema + formatos + modo funil + abas texto/disciplina 2. Botao desabilitado ate preencher tema (minimo 20 caracteres) e selecionar formato 3. Submissao cria pipeline e redireciona para acompanhamento 4. Funciona com modo mock ativo | -- | A FAZER |
| 2 | Acompanhar Pipeline no Wizard (AcompanharPipelineRequest) | Criar tela de acompanhamento do pipeline com 7 etapas visuais, status coloridos e botoes para aprovar, retomar ou ver resultado | 1. Wizard exibe 7 etapas com status do mock (cores diferentes por status) 2. Etapa aguardando aprovacao mostra botao para sub-tela correspondente 3. Etapa em execucao mostra indicador de carregamento 4. Etapa com erro mostra botao "Retomar" 5. Pipeline concluido mostra botao "Ver Resultado" | Task 1 | A FAZER |

### Arquivos do Dominio

| Arquivo | Criado na Task |
|---------|---------------|
| src/lib/dtos/IniciarPipelineDTO.ts | Iniciar Pipeline na Home |
| src/lib/dtos/PipelineDTO.ts | Iniciar Pipeline na Home |
| src/lib/components/home/FormatoSelector.svelte | Iniciar Pipeline na Home |
| src/lib/components/home/FotoCriadorGaleria.svelte | Iniciar Pipeline na Home |
| src/lib/mocks/pipeline.mock.ts | Iniciar Pipeline na Home |
| src/lib/services/PipelineService.ts | Iniciar Pipeline na Home |
| src/lib/repositories/PipelineRepository.ts | Iniciar Pipeline na Home |
| src/lib/dtos/PipelineStepDTO.ts | Acompanhar Pipeline no Wizard |
| src/lib/components/pipeline/PipelineWizard.svelte | Acompanhar Pipeline no Wizard |
| src/lib/components/pipeline/PipelineStepCard.svelte | Acompanhar Pipeline no Wizard |
| src/lib/components/pipeline/PipelineStatusBadge.svelte | Acompanhar Pipeline no Wizard |
| src/routes/pipeline/[id]/+page.svelte | Acompanhar Pipeline no Wizard |

---

## Dominio Aprovacoes Backend

**O que e:** Logica de aprovacao humana nas 4 etapas do pipeline: briefing (AP-1), copy e gancho (AP-2), prompt visual (AP-3), imagem (AP-4) e finalizacao com avaliacao de qualidade. Integra agentes, funcoes automaticas e persiste conteudo, imagens e scores no banco.
**Depende de:** Dominio Pipeline Backend, Dominio Agente Backend (Nivel 3)
**Libera:** Dominio Finalizacao Backend
**Status customizados:** A FAZER | FEITO IA | REVISAO DEV | FEITO DEV | QA | FINALIZADA

### Tasks (Dev Features)

| # | Task no ClickUp | Descricao GP | Criterios de Aceite | Depende de | Status |
|---|----------------|-------------|---------------------|------------|--------|
| 1 | Executar e Aprovar Briefing - AP-1 (AprovarEtapaRequest) | Executar o agente Strategist, exibir briefing para aprovacao humana e avancar pipeline | 1. Executar inicia o Strategist e muda status para "aguardando aprovacao" 2. Consulta retorna briefing gerado 3. Aprovar com briefing editado avanca para proxima etapa 4. Scanner de tendencias alimenta o Strategist | -- | A FAZER |
| 2 | Rejeitar Etapa e Aprovar Copy + Hook - AP-2 (RejeitarEtapaRequest) | Permitir rejeitar uma etapa (re-executa agente com feedback) e processar o fluxo de copy + selecao de gancho | 1. Rejeitar re-executa agente com feedback do usuario 2. Apos AP-1 aprovado, Copywriter e Hook Specialist executam em sequencia 3. Etapa fica aguardando aprovacao com 3 ganchos A/B/C 4. Validador de vocabulario roda apos Copywriter | Task 1 | A FAZER |
| 3 | Aprovar Prompt Visual AP-3 e Imagem AP-4 (AprovarVisualImagemRequest) | Processar fluxo do Art Director (prompt visual), Image Generator (3 variacoes de imagem) e Brand Gate (validacao e aplicacao de marca) | 1. Apos AP-2, Art Director executa e fica aguardando aprovacao 2. Apos AP-3, Image Generator gera 3 variacoes por slide 3. Brand Gate valida e aplica marca automaticamente 4. Se invalidado, tenta novamente automaticamente (maximo 2 vezes) 5. Se falha apos tentativas, marca como "revisao manual necessaria" | Task 2 | A FAZER |
| 4 | Finalizar Pipeline com Avaliacao de Qualidade (FinalizarPipelineRequest) | Executar avaliacao de qualidade (Content Critic), salvar conteudo final, imagens e scores no banco | 1. Content Critic gera avaliacao com 6 dimensoes (0 a 10) 2. Score salvo no banco 3. Conteudo final e imagens salvos no banco 4. Pipeline muda status para "completo" 5. Memoria visual salva preferencias das variacoes aprovadas e rejeitadas | Task 3 | A FAZER |

### Arquivos do Dominio

| Arquivo | Criado na Task |
|---------|---------------|
| dtos/pipeline/aprovar_etapa/request.py | Executar e Aprovar Briefing - AP-1 |
| dtos/pipeline/aprovar_etapa/response.py | Executar e Aprovar Briefing - AP-1 |
| dtos/pipeline/buscar_etapa/response.py | Executar e Aprovar Briefing - AP-1 |
| dtos/pipeline/rejeitar_etapa/request.py | Rejeitar Etapa e Aprovar Copy + Hook - AP-2 |
| dtos/pipeline/rejeitar_etapa/response.py | Rejeitar Etapa e Aprovar Copy + Hook - AP-2 |
| models/conteudo.py | Finalizar Pipeline com Avaliacao de Qualidade |
| models/imagem.py | Finalizar Pipeline com Avaliacao de Qualidade |
| models/score.py | Finalizar Pipeline com Avaliacao de Qualidade |
| dtos/score/buscar_score/response.py | Finalizar Pipeline com Avaliacao de Qualidade |
| dtos/score/base.py | Finalizar Pipeline com Avaliacao de Qualidade |
| data/repositories/sql/conteudo_repository.py | Finalizar Pipeline com Avaliacao de Qualidade |
| data/repositories/sql/imagem_repository.py | Finalizar Pipeline com Avaliacao de Qualidade |
| data/repositories/sql/score_repository.py | Finalizar Pipeline com Avaliacao de Qualidade |
| mappers/score_mapper.py | Finalizar Pipeline com Avaliacao de Qualidade |

---

## Dominio Aprovacoes Frontend

**O que e:** As 4 telas de aprovacao humana do pipeline: revisao de briefing (AP-1), escolha de gancho e edicao de copy (AP-2), revisao de prompt visual (AP-3) e selecao de variacao de imagem (AP-4). Cada tela permite aprovar, editar e rejeitar.
**Depende de:** Dominio Pipeline Frontend (Nivel 3)
**Libera:** Dominio Finalizacao Frontend
**Status customizados:** A FAZER | FEITO IA | REVISAO DEV | FEITO DEV | QA | FINALIZADA

### Tasks (Dev Features)

| # | Task no ClickUp | Descricao GP | Criterios de Aceite | Depende de | Status |
|---|----------------|-------------|---------------------|------------|--------|
| 1 | Aprovar Briefing - AP-1 (AprovarBriefingRequest) | Tela para revisar, editar e aprovar o briefing gerado pelo Strategist. Se modo funil ativo, mostra plano de 5-7 pecas editavel. | 1. Tela exibe briefing do Strategist (dados simulados) 2. Briefing e editavel (campo de texto) 3. Se modo funil: mostra lista de pecas editavel 4. "Aprovar e Continuar" envia dados e redireciona 5. "Rejeitar e Regerar" exibe campo de feedback | -- | A FAZER |
| 2 | Aprovar Copy e Escolher Gancho - AP-2 (AprovarCopyHookRequest) | Tela para editar headline, narrativa, chamada para acao, reordenar slides e escolher entre 3 ganchos (A/B/C) | 1. Tela exibe headline, narrativa, chamada para acao e slides (dados simulados) 2. 3 ganchos renderizam como cards selecionaveis 3. Sequencia de slides e editavel, reordenavel, com adicionar e remover 4. Correcoes de vocabulario aparecem como alertas 5. Aprovar requer gancho selecionado | -- | A FAZER |
| 3 | Aprovar Prompt Visual - AP-3 (AprovarPromptVisualRequest) | Tela para revisar e editar os prompts de imagem por slide antes da geracao, com pre-visualizacao da paleta e historico de preferencias visuais | 1. Tela exibe prompts por slide em formato expansivel (dados simulados) 2. Cada prompt e editavel (minimo 50 caracteres) 3. Paleta de cores e exibida com cores e elementos 4. Historico visual mostra estilos aprovados e rejeitados | -- | A FAZER |
| 4 | Aprovar Imagem - AP-4 (AprovarImagemRequest) | Tela para escolher a melhor variacao de imagem para cada slide (3 opcoes por slide), com zoom e status de validacao da marca | 1. Tela exibe grade de variacoes por slide (dados simulados) 2. Cada slide tem 3 imagens selecionaveis 3. Duplo-clique abre imagem em tela cheia 4. Status de validacao da marca visivel por slide 5. "Regerar" funciona para 1 variacao individualmente 6. Aprovar requer 1 variacao selecionada por slide | -- | A FAZER |

### Arquivos do Dominio

| Arquivo | Criado na Task |
|---------|---------------|
| src/lib/dtos/BriefingDTO.ts | Aprovar Briefing - AP-1 |
| src/lib/components/briefing/BriefingEditor.svelte | Aprovar Briefing - AP-1 |
| src/lib/components/briefing/FunilPlanner.svelte | Aprovar Briefing - AP-1 |
| src/lib/mocks/briefing.mock.ts | Aprovar Briefing - AP-1 |
| src/lib/services/BriefingService.ts | Aprovar Briefing - AP-1 |
| src/lib/repositories/BriefingRepository.ts | Aprovar Briefing - AP-1 |
| src/routes/pipeline/[id]/briefing/+page.svelte | Aprovar Briefing - AP-1 |
| src/lib/dtos/CopyDTO.ts | Aprovar Copy e Escolher Gancho - AP-2 |
| src/lib/dtos/HookDTO.ts | Aprovar Copy e Escolher Gancho - AP-2 |
| src/lib/components/copy/CopyEditor.svelte | Aprovar Copy e Escolher Gancho - AP-2 |
| src/lib/components/copy/HookSelector.svelte | Aprovar Copy e Escolher Gancho - AP-2 |
| src/lib/components/copy/SlideSequenceEditor.svelte | Aprovar Copy e Escolher Gancho - AP-2 |
| src/lib/components/copy/ToneGuideAlerts.svelte | Aprovar Copy e Escolher Gancho - AP-2 |
| src/lib/mocks/copy.mock.ts | Aprovar Copy e Escolher Gancho - AP-2 |
| src/lib/services/CopyService.ts | Aprovar Copy e Escolher Gancho - AP-2 |
| src/lib/repositories/CopyRepository.ts | Aprovar Copy e Escolher Gancho - AP-2 |
| src/routes/pipeline/[id]/copy/+page.svelte | Aprovar Copy e Escolher Gancho - AP-2 |
| src/lib/dtos/PromptVisualDTO.ts | Aprovar Prompt Visual - AP-3 |
| src/lib/components/visual/PromptEditor.svelte | Aprovar Prompt Visual - AP-3 |
| src/lib/components/visual/PromptSlideList.svelte | Aprovar Prompt Visual - AP-3 |
| src/lib/components/visual/BrandPalettePreview.svelte | Aprovar Prompt Visual - AP-3 |
| src/lib/components/visual/VisualMemoryPanel.svelte | Aprovar Prompt Visual - AP-3 |
| src/lib/mocks/visual.mock.ts | Aprovar Prompt Visual - AP-3 |
| src/lib/services/VisualService.ts | Aprovar Prompt Visual - AP-3 |
| src/lib/repositories/VisualRepository.ts | Aprovar Prompt Visual - AP-3 |
| src/routes/pipeline/[id]/visual/+page.svelte | Aprovar Prompt Visual - AP-3 |
| src/lib/dtos/ImagemVariacaoDTO.ts | Aprovar Imagem - AP-4 |
| src/lib/components/imagem/ImageVariationGrid.svelte | Aprovar Imagem - AP-4 |
| src/lib/components/imagem/ImageSlideAccordion.svelte | Aprovar Imagem - AP-4 |
| src/lib/components/imagem/ImageZoomModal.svelte | Aprovar Imagem - AP-4 |
| src/lib/components/imagem/BrandGateStatus.svelte | Aprovar Imagem - AP-4 |
| src/lib/mocks/imagem.mock.ts | Aprovar Imagem - AP-4 |
| src/lib/services/ImagemService.ts | Aprovar Imagem - AP-4 |
| src/lib/repositories/ImagemRepository.ts | Aprovar Imagem - AP-4 |
| src/routes/pipeline/[id]/imagem/+page.svelte | Aprovar Imagem - AP-4 |

---

## Dominio Finalizacao Backend

**O que e:** Historico refatorado (multi-formato, filtros, paginacao), preferencias visuais (salvar e listar) e integracao com Google Drive v3 (salvar conteudo do pipeline no Drive com subpasta automatica).
**Depende de:** Dominio Aprovacoes Backend (Nivel 4)
**Libera:** nenhum (dominio final)
**Status customizados:** A FAZER | FEITO IA | REVISAO DEV | FEITO DEV | QA | FINALIZADA

### Tasks (Dev Features)

| # | Task no ClickUp | Descricao GP | Criterios de Aceite | Depende de | Status |
|---|----------------|-------------|---------------------|------------|--------|
| 1 | Listar Historico Refatorado (ListarHistoricoRequest) | Refatorar o historico para suportar multiplos formatos, filtros por formato, status e periodo, e paginacao | 1. Listagem aceita filtros por formato, status e periodo 2. Retorna lista paginada com titulo, formato, score e data 3. Busca por identificador retorna item com pipeline vinculado 4. Deletar faz remocao logica (soft delete) | -- | A FAZER |
| 2 | Salvar e Listar Preferencias Visuais (SalvarPreferenciaRequest) | Criar cadastro de preferencias visuais (estilos aprovados e rejeitados) que alimenta geracoes futuras | 1. Salva preferencia com estilo, aprovacao e contexto 2. Lista preferencias filtradas por empresa (tenant) 3. Dados persistidos no banco MSSQL | -- | A FAZER |
| 3 | Salvar Conteudo no Google Drive v3 (SalvarConteudoDriveRequest) | Salvar conteudo do pipeline no Google Drive com subpasta automatica contendo PDF e imagens PNG | 1. Cria subpasta automatica no Drive com nome do conteudo 2. Salva PDF e imagens PNG na subpasta 3. Retorna link do Drive 4. Atualiza historico com link do Drive | Task 1 | A FAZER |

### Arquivos do Dominio

| Arquivo | Criado na Task |
|---------|---------------|
| models/historico.py | Listar Historico Refatorado |
| dtos/historico/listar_historico/request.py | Listar Historico Refatorado |
| dtos/historico/listar_historico/response.py | Listar Historico Refatorado |
| dtos/historico/buscar_historico/response.py | Listar Historico Refatorado |
| dtos/historico/base.py | Listar Historico Refatorado |
| data/repositories/sql/historico_repository.py | Listar Historico Refatorado |
| factories/historico_factory.py | Listar Historico Refatorado |
| mappers/historico_mapper.py | Listar Historico Refatorado |
| services/historico_service.py | Listar Historico Refatorado |
| models/visual_preference.py | Salvar e Listar Preferencias Visuais |
| dtos/visual_preference/salvar_preferencia/request.py | Salvar e Listar Preferencias Visuais |
| dtos/visual_preference/salvar_preferencia/response.py | Salvar e Listar Preferencias Visuais |
| dtos/visual_preference/listar_preferencias/response.py | Salvar e Listar Preferencias Visuais |
| dtos/visual_preference/base.py | Salvar e Listar Preferencias Visuais |
| data/repositories/sql/visual_preference_repository.py | Salvar e Listar Preferencias Visuais |
| factories/visual_preference_factory.py | Salvar e Listar Preferencias Visuais |
| mappers/visual_preference_mapper.py | Salvar e Listar Preferencias Visuais |
| services/visual_preference_service.py | Salvar e Listar Preferencias Visuais |
| routers/visual_preference.py | Salvar e Listar Preferencias Visuais |
| dtos/drive/salvar_conteudo_drive/request.py | Salvar Conteudo no Google Drive v3 |
| dtos/drive/salvar_conteudo_drive/response.py | Salvar Conteudo no Google Drive v3 |

---

## Dominio Finalizacao Frontend

**O que e:** Tela de resultado final com avaliacao de qualidade (radar chart com 6 dimensoes), exportacao de PDF, download de imagens, salvamento no Drive, historico refatorado com filtros e cards multi-formato, e telas extras de configuracao (design systems e fotos).
**Depende de:** Dominio Aprovacoes Frontend (Nivel 4)
**Libera:** nenhum (dominio final)
**Status customizados:** A FAZER | FEITO IA | REVISAO DEV | FEITO DEV | QA | FINALIZADA

### Tasks (Dev Features)

| # | Task no ClickUp | Descricao GP | Criterios de Aceite | Depende de | Status |
|---|----------------|-------------|---------------------|------------|--------|
| 1 | Visualizar Score, Exportar e Listar Historico (VisualizarScoreExportarRequest) | Tela final do pipeline com grafico radar de qualidade, exportacao PDF, salvamento no Drive, copia de legenda e historico refatorado com filtros por formato, status e periodo | 1. Tela de resultado exibe grafico radar com 6 dimensoes e cards de score 2. Carrossel navega entre slides finais 3. Badge verde "Aprovado" se nota >= 7, amarelo "Recomenda ajustes" se < 7 4. "Exportar PDF" gera arquivo e faz download 5. "Copiar Legenda" copia para area de transferencia 6. Historico exibe cards multi-formato com filtros funcionais 7. "Remover" faz remocao com confirmacao via modal | -- | A FAZER |

### Arquivos do Dominio

| Arquivo | Criado na Task |
|---------|---------------|
| src/lib/dtos/ScoreDTO.ts | Visualizar Score, Exportar e Listar Historico |
| src/lib/components/export/ScoreRadar.svelte | Visualizar Score, Exportar e Listar Historico |
| src/lib/components/export/ScoreCard.svelte | Visualizar Score, Exportar e Listar Historico |
| src/lib/components/export/SlidePreviewCarousel.svelte | Visualizar Score, Exportar e Listar Historico |
| src/lib/components/export/ExportActions.svelte | Visualizar Score, Exportar e Listar Historico |
| src/lib/mocks/score.mock.ts | Visualizar Score, Exportar e Listar Historico |
| src/lib/services/ExportService.ts | Visualizar Score, Exportar e Listar Historico |
| src/lib/repositories/ExportRepository.ts | Visualizar Score, Exportar e Listar Historico |
| src/routes/pipeline/[id]/export/+page.svelte | Visualizar Score, Exportar e Listar Historico |
| src/lib/dtos/HistoricoItemDTO.ts | Visualizar Score, Exportar e Listar Historico |
| src/lib/components/historico/HistoricoCard.svelte | Visualizar Score, Exportar e Listar Historico |
| src/lib/components/historico/HistoricoFiltros.svelte | Visualizar Score, Exportar e Listar Historico |
| src/lib/mocks/historico.mock.ts | Visualizar Score, Exportar e Listar Historico |
| src/lib/services/HistoricoService.ts | Visualizar Score, Exportar e Listar Historico |
| src/lib/repositories/HistoricoRepository.ts | Visualizar Score, Exportar e Listar Historico |
| src/lib/components/config/DesignSystemManager.svelte | Visualizar Score, Exportar e Listar Historico |
| src/lib/components/config/FotoManager.svelte | Visualizar Score, Exportar e Listar Historico |

---

## Hierarquia ClickUp

```
Space: Sistemas IT Valley
  Folder: Content Factory v3 -- Fabrica de Conteudo Visual
    List: Dominio Base Backend
      Task: Criar Infraestrutura Base (CriarBaseBackendRequest)
    List: Dominio Base Frontend
      Task: Criar Componentes Base e Sidebar (CriarBaseFrontendRequest)
    List: Dominio Config Backend
      Task: Salvar Paleta de Cores (SalvarBrandPaletteRequest)
      Task: Buscar Paleta de Cores (BuscarBrandPaletteRequest)
      Task: Salvar Registro de Criadores (SalvarCreatorRegistryRequest)
      Task: Buscar Registro de Criadores e Gerenciar Regras de Plataforma (BuscarCreatorRegistryRequest)
    List: Dominio Agente Backend
      Task: Listar Agentes (ListarAgentesRequest)
      Task: Buscar Agente (BuscarAgenteRequest)
      Task: Executar Agente em Modo Teste (ExecutarAgenteRequest)
    List: Dominio Config Frontend
      Task: Criar DTOs e Mocks de Configuracao (SalvarApiKeysRequest)
      Task: Criar Formulario de Paleta de Cores (CriarBrandPaletteFormRequest)
      Task: Criar Formularios de Criadores e Regras (CriarCreatorRegistryFormRequest)
      Task: Listar e Visualizar Agentes (ListarAgentesVisualizarRequest)
    List: Dominio Pipeline Backend
      Task: Criar Pipeline (CriarPipelineRequest)
      Task: Buscar e Listar Pipelines (BuscarPipelineRequest)
      Task: Cancelar e Retomar Pipeline (CancelarPipelineRequest)
      Task: Criar Funcoes Automaticas do Pipeline (CriarSkillsRequest)
    List: Dominio Pipeline Frontend
      Task: Iniciar Pipeline na Home (IniciarPipelineRequest)
      Task: Acompanhar Pipeline no Wizard (AcompanharPipelineRequest)
    List: Dominio Aprovacoes Backend
      Task: Executar e Aprovar Briefing - AP-1 (AprovarEtapaRequest)
      Task: Rejeitar Etapa e Aprovar Copy + Hook - AP-2 (RejeitarEtapaRequest)
      Task: Aprovar Prompt Visual AP-3 e Imagem AP-4 (AprovarVisualImagemRequest)
      Task: Finalizar Pipeline com Avaliacao de Qualidade (FinalizarPipelineRequest)
    List: Dominio Aprovacoes Frontend
      Task: Aprovar Briefing - AP-1 (AprovarBriefingRequest)
      Task: Aprovar Copy e Escolher Gancho - AP-2 (AprovarCopyHookRequest)
      Task: Aprovar Prompt Visual - AP-3 (AprovarPromptVisualRequest)
      Task: Aprovar Imagem - AP-4 (AprovarImagemRequest)
    List: Dominio Finalizacao Backend
      Task: Listar Historico Refatorado (ListarHistoricoRequest)
      Task: Salvar e Listar Preferencias Visuais (SalvarPreferenciaRequest)
      Task: Salvar Conteudo no Google Drive v3 (SalvarConteudoDriveRequest)
    List: Dominio Finalizacao Frontend
      Task: Visualizar Score, Exportar e Listar Historico (VisualizarScoreExportarRequest)
```

---

## Configuracao de Status por List (API ClickUp)

Cada List DEVE ser criada com `override_statuses: true` e os seguintes status customizados:

```json
{
  "override_statuses": true,
  "statuses": [
    { "status": "A FAZER",      "type": "open",   "color": "#d3d3d3" },
    { "status": "FEITO IA",     "type": "custom", "color": "#6b5bff" },
    { "status": "REVISAO DEV",  "type": "custom", "color": "#f9a825" },
    { "status": "FEITO DEV",    "type": "custom", "color": "#2196f3" },
    { "status": "QA",           "type": "custom", "color": "#ff9800" },
    { "status": "FINALIZADA",   "type": "closed", "color": "#4caf50" }
  ]
}
```

---

## Tags de Nivel (Prioridade Tecnica)

| Tag | Dominios | Significado |
|-----|----------|-------------|
| Nivel 0 | Base Backend, Base Frontend | Infraestrutura obrigatoria, ninguem comeca sem estes |
| Nivel 1 | Config Backend, Agente Backend, Config Frontend | Dominios sem dependencia alem da base |
| Nivel 2 | Pipeline Backend, Pipeline Frontend | Nucleo do sistema, depende da base e configs |
| Nivel 3 | Aprovacoes Backend, Aprovacoes Frontend | Fluxo de aprovacao humana, depende do pipeline |
| Nivel 4 | Finalizacao Backend, Finalizacao Frontend | Historico, exportacao e preferencias visuais |

---

## Cronograma Sugerido

| Semana | Dominios Backend | Dominios Frontend | Observacao |
|--------|-----------------|------------------|------------|
| 1 | Base Backend, Config Backend, Agente Backend | Base Frontend, Config Frontend | Backend e frontend em paralelo |
| 2 | Pipeline Backend (core + skills) | Pipeline Frontend (Home + Wizard) | Paralelismo back/front |
| 3 | Aprovacoes Backend (AP-1 a AP-4 + finalizacao) | Aprovacoes Frontend (AP-1 a AP-4) | Paralelismo back/front |
| 4 | Finalizacao Backend (historico + visual + drive) | Finalizacao Frontend (export + score + historico) | Integracao e testes finais |

---

## Regras de Coordenacao

1. **Dev Frontend trabalha com VITE_USE_MOCK=true** ate o backend correspondente estar pronto. Nunca depender do backend para comecar.
2. **Conflitos de arquivo zero:** Nenhuma task toca o mesmo arquivo que outra task no mesmo dominio (exceto configuracoes, que usa abas isoladas).
3. **Integracao front+back:** Apos cada dominio backend ficar pronto, o dev front troca VITE_USE_MOCK=false para o dominio correspondente e integra.
4. **Criterio de aceite final de um dominio:** Todas as tasks passam nos criterios individuais + testes de integracao entre tasks do mesmo dominio.
5. **tenant_id obrigatorio:** Toda query e todo INSERT inclui tenant_id, mesmo em modo single-user (valor padrao: "itvalley").

---

## Checklist do Gerente de Projetos

- [x] Todos os dominios identificados e listados como "Dominio {Nome}"
- [x] Todos os dev features com nome "Verbo Objeto (DTORequest)"
- [x] Cada task tem criterios de aceite verificaveis
- [x] Cada task tem descricao GP-friendly (sem jargao tecnico)
- [x] Dependencias entre dominios mapeadas
- [x] Dependencias entre tasks dentro do dominio mapeadas
- [x] Tabela de arquivos por dominio completa
- [x] Documento segue hierarquia: Space (escopo) -> Folder (projeto) -> List (dominio) -> Task (acao)
- [x] Workflow de status definido: A FAZER -> FEITO IA -> REVISAO DEV -> FEITO DEV -> QA -> FINALIZADA
- [x] Cada List usa override_statuses: true com status customizados
- [x] Tasks pendentes marcadas como "A FAZER" (nenhuma implementada pela IA ainda)
- [x] Nenhum status nativo do ClickUp usado (apenas o workflow customizado)
- [x] Status types corretos: open (A FAZER), custom (intermediarios), closed (FINALIZADA)

---

*Documento gerado pelo Agente 08-b (Gerente de Projetos) da esteira IT Valley.*
*Entrada: DEV_FEATURES.md (Agente 08) + PRD.md + TELAS.md + ARQUITETURA_BACKEND.md + ARQUITETURA_FRONTEND.md + DESIGN.md + BANCO.md.*
*Proximo: GPExport sobe para ClickUp automaticamente. Devs (09/10) consultam as tasks.*
