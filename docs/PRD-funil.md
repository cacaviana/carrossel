# PRD -- Modo Funil de Conteudo

## 1. Visao Geral

**Problema:** Hoje o sistema gera pecas de conteudo isoladas (1 carrossel, 1 post unico, 1 thumbnail). Quando o usuario quer criar uma campanha completa com pecas conectadas em diferentes etapas do funil de vendas (topo, meio, fundo, conversao), ele precisa criar cada pipeline manualmente, repetir o tema, e nao ha conexao narrativa entre as pecas. Isso consome tempo, gera inconsistencia de mensagem e impede estrategias de funil reais.

**Solucao:** Um modo "Funil" que, a partir de um unico tema, gera automaticamente um plano de 3-5 pecas conectadas em diferentes formatos e etapas do funil. Um agente novo (Funnel Architect) cria o plano estrategico. O usuario revisa, edita e aprova o plano. O sistema entao cria N sub-pipelines independentes (1 por peca) que executam em paralelo, reaproveitando todo o pipeline de 6 etapas ja existente (strategist -> copywriter -> art_director -> image_generator -> brand_gate -> content_critic).

**Usuarios-alvo:** Criadores de conteudo da IT Valley School (Carlos Viana) e marcas cadastradas no sistema.

**Multitenante:** Sim -- toda query usa tenant_id, toda tabela tem tenant_id. Mesmo modelo do pipeline atual.

---

## 2. Perfis de Usuario (ACL)

| Perfil | Descricao | Permissoes Principais |
|--------|-----------|----------------------|
| Criador | Usuario que cria conteudo (Carlos Viana, marcas) | Criar funil, editar plano, aprovar/rejeitar pecas, exportar |
| Sistema | Agentes automaticos (LLM + deterministicos) | Executar etapas dos sub-pipelines |

---

## 3. Modulos do Sistema

### Modulo: Funnel Architect (Agente Novo)

- **Descricao:** Agente LLM que recebe o tema e gera um plano estrategico de funil com 3-5 pecas distribuidas entre topo, meio, fundo e conversao.
- **Perfis com acesso:** Sistema (execucao automatica)
- **Funcionalidades:**
  - Receber tema + brand_slug + preferencias do usuario
  - Gerar plano com 3-5 pecas, cada uma com: titulo, etapa_funil, formato, angulo, resumo
  - Distribuir pecas estrategicamente pelo funil (nao repetir formatos quando possivel)
  - Respeitar identidade da marca (brand context)
  - Regenerar plano quando rejeitado com feedback

### Modulo: Plano do Funil (Tela Nova)

- **Descricao:** Tela onde o usuario visualiza, edita e aprova o plano gerado pelo Funnel Architect antes da execucao das pecas.
- **Perfis com acesso:** Criador
- **Funcionalidades:**
  - Visualizar plano completo com cards por peca
  - Editar titulo, formato, angulo e resumo de cada peca
  - Remover pecas do plano
  - Trocar etapa do funil de uma peca
  - Trocar formato de uma peca (carrossel, post_unico, thumbnail_youtube, capa_reels)
  - Aprovar plano (dispara criacao dos sub-pipelines)
  - Rejeitar plano com feedback (regenera via Funnel Architect)

### Modulo: Painel do Funil (Tela Nova)

- **Descricao:** Tela de acompanhamento que mostra todas as pecas do funil com seus status em tempo real.
- **Perfis com acesso:** Criador
- **Funcionalidades:**
  - Visualizar todas as pecas com status (pendente, executando, aguardando_aprovacao, completo, erro)
  - Clicar em uma peca para ir ao fluxo de aprovacao existente (/pipeline/{pecaId}/copy, /visual, etc)
  - Ver progresso individual de cada peca (etapa atual, progresso de geracao de imagem)
  - Polling unico para atualizar status de todas as pecas
  - Indicador visual de quantas pecas estao prontas vs total

### Modulo: Export do Funil (Tela Nova)

- **Descricao:** Tela final que permite exportar todas as pecas do funil de uma vez.
- **Perfis com acesso:** Criador
- **Funcionalidades:**
  - Preview de todas as pecas finalizadas
  - Exportar 1 PDF por peca
  - Salvar no Google Drive em subpasta do funil (nome: "{tema} - Funil - {data}")
  - Download local de todos os PDFs

### Modulo: Pipeline Existente (Reutilizado)

- **Descricao:** Pipeline de 6 etapas ja existente. Cada peca do funil roda como um sub-pipeline independente.
- **Perfis com acesso:** Sistema, Criador (aprovacao/rejeicao)
- **Etapas reutilizadas:**
  - strategist (briefing individual da peca)
  - copywriter (copy dos slides)
  - art_director (direcao visual)
  - image_generator (geracao Gemini)
  - brand_gate (validacao + overlay)
  - content_critic (avaliacao final)

---

## 4. Regras de Negocio

| ID | Regra | Modulo |
|----|-------|--------|
| RN-001 | Um funil sempre usa UMA unica marca (brand_slug). Todas as pecas herdam a mesma identidade visual. | Funnel Architect |
| RN-002 | O plano do funil deve ter entre 3 e 5 pecas. | Funnel Architect |
| RN-003 | Cada peca tem uma etapa_funil: topo, meio, fundo ou conversao. O plano deve cobrir pelo menos 2 etapas diferentes. | Funnel Architect |
| RN-004 | O usuario DEVE aprovar o plano antes da criacao dos sub-pipelines. O plano e o primeiro ponto de aprovacao. | Plano do Funil |
| RN-005 | O usuario pode editar qualquer campo do plano (titulo, formato, angulo, resumo, etapa_funil) e pode remover pecas. | Plano do Funil |
| RN-006 | Cada peca e um sub-pipeline INDEPENDENTE. Executa seu proprio pipeline completo de 6 etapas. | Pipeline |
| RN-007 | Pecas executam em paralelo, com limite de 2 sub-pipelines simultaneos (para nao estourar rate limits de API). | Pipeline |
| RN-008 | O usuario aprova cada peca no seu ritmo. Uma peca pode estar pronta enquanto outra ainda esta sendo gerada. | Painel do Funil |
| RN-009 | Quando uma peca precisa de aprovacao, o usuario clica nela e vai para o fluxo existente (/pipeline/{pecaId}/copy, /visual, etc). | Painel do Funil |
| RN-010 | O pipeline-pai (funil) armazena o plano e referencia os sub-pipelines. Ele NAO executa etapas — so orquestra. | Pipeline |
| RN-011 | O funil so e considerado "completo" quando TODAS as pecas estiverem com status "completo". | Pipeline |
| RN-012 | Se o usuario rejeitar o plano, o Funnel Architect recebe o feedback e regenera. | Plano do Funil |
| RN-013 | Cada peca do funil recebe o tema principal + o angulo especifico definido no plano como entrada do strategist. | Pipeline |
| RN-014 | Export gera 1 PDF por peca. Drive salva tudo numa subpasta do funil. | Export |
| RN-015 | O formato de cada peca pode ser diferente (ex: 1 carrossel + 1 post_unico + 1 thumbnail). | Funnel Architect |

---

## 5. Integracoes Externas

| Sistema | Tipo | Finalidade |
|---------|------|-----------|
| Claude API (Anthropic) | API REST | Executar agentes LLM: Funnel Architect, Strategist, Copywriter, Art Director, Content Critic |
| Gemini API (Google) | API REST | Gerar imagens dos slides (image_generator) |
| Google Drive API | API REST (SDK) | Salvar PDFs e PNGs exportados em subpasta do funil |

---

## 6. Requisitos Nao Funcionais

- **Performance:** Polling do painel do funil deve retornar em menos de 500ms. Geracao de pecas em paralelo (max 2 simultaneas) para otimizar tempo total.
- **Seguranca:** Multitenante por tenant_id em toda query. Mesma autenticacao do sistema atual.
- **Escalabilidade:** Limite de 2 sub-pipelines simultaneos por funil para respeitar rate limits das APIs (Claude, Gemini). Fila interna para enfileirar pecas excedentes.
- **Resiliencia:** Se um sub-pipeline falhar, os demais continuam. O usuario pode retomar pecas com erro individualmente.

---

## 7. MVP -- Escopo do Primeiro Lancamento

### 7.1 Backend

1. **Agente Funnel Architect** -- novo agente LLM (agents/funnel_architect.py) com system prompt dedicado
2. **Tabela carrossel.funil** -- armazena plano do funil (pipeline_id pai, plano JSON, status)
3. **Tabela carrossel.funil_peca** -- relaciona funil com sub-pipelines (funil_id, pipeline_id filho, ordem, etapa_funil)
4. **Endpoint POST /api/pipelines/ com modo_funil=true** -- cria pipeline pai + executa Funnel Architect
5. **Endpoint GET /api/pipelines/{id}/funil/plano** -- retorna plano gerado pelo Funnel Architect
6. **Endpoint PUT /api/pipelines/{id}/funil/plano** -- salva plano editado pelo usuario
7. **Endpoint POST /api/pipelines/{id}/funil/plano/aprovar** -- aprova plano e cria N sub-pipelines
8. **Endpoint POST /api/pipelines/{id}/funil/plano/rejeitar** -- rejeita plano com feedback
9. **Endpoint GET /api/pipelines/{id}/funil/status** -- retorna status de todas as pecas (polling unico)
10. **Endpoint POST /api/pipelines/{id}/funil/executar** -- executa proximas etapas pendentes (ate 2 simultaneas)
11. **Endpoint POST /api/pipelines/{id}/funil/exportar** -- gera PDFs de todas as pecas e salva no Drive

### 7.2 Frontend

1. **Home (/?formato=funil)** -- opcao de criar pipeline com modo_funil=true
2. **Tela /pipeline/{id}/funil-plano** -- revisar, editar e aprovar o plano
3. **Tela /pipeline/{id}/funil** -- painel de acompanhamento com cards por peca
4. **Tela /pipeline/{id}/funil-export** -- preview + export de todas as pecas
5. **Navegacao entre painel do funil e telas existentes** -- clicar na peca leva ao /pipeline/{pecaId}/copy etc

### 7.3 Agente: Funnel Architect

**System Prompt** -- gera plano de funil a partir de um tema.

**Saida JSON obrigatoria:**

```json
{
  "plano": {
    "tema_principal": "string -- tema unificador do funil",
    "objetivo_campanha": "string -- o que a campanha como um todo quer alcançar",
    "narrativa_geral": "string -- fio condutor que conecta todas as pecas",
    "pecas": [
      {
        "ordem": 1,
        "titulo": "string -- titulo da peca",
        "etapa_funil": "topo | meio | fundo | conversao",
        "formato": "carrossel | post_unico | thumbnail_youtube | capa_reels",
        "angulo": "string -- abordagem especifica desta peca",
        "resumo": "string -- 1-2 frases sobre o conteudo",
        "gancho": "string -- frase de scroll-stop para esta peca",
        "conexao_anterior": "string | null -- como esta peca conecta com a anterior",
        "cta_para_proxima": "string | null -- como direciona para a proxima peca"
      }
    ]
  }
}
```

**Regras do Funnel Architect:**

1. Gerar entre 3 e 5 pecas por funil
2. Cobrir pelo menos 2 etapas diferentes do funil
3. A primeira peca deve ser topo de funil (atrair atencao)
4. A ultima peca deve ser fundo ou conversao (levar a acao)
5. Variar formatos quando possivel (nao fazer 5 carrosseis)
6. Cada peca deve funcionar sozinha E como parte do funil
7. A narrativa deve ter um fio condutor claro entre as pecas
8. Respeitar identidade da marca (brand context injetado)
9. Tom IT Valley: tecnico + acessivel. NUNCA guru, hack, truque, milagre
10. Responder APENAS em JSON valido, sem texto antes ou depois

---

## 8. Roadmap -- Fora do MVP

1. **Agendamento de publicacao** -- agendar cada peca do funil para dias diferentes (D1, D3, D5...)
2. **Metricas por funil** -- rastrear performance de cada peca e do funil como um todo
3. **Templates de funil** -- funis pre-montados (ex: "Lancamento de curso", "Autoridade rapida", "Engajamento semanal")
4. **Duplicar funil** -- copiar um funil existente para outro tema/marca
5. **A/B testing de pecas** -- gerar 2 versoes de uma peca e testar qual performa melhor
6. **Funil com mais de 5 pecas** -- permitir ate 10 pecas para campanhas longas
7. **Integracao com LinkedIn API** -- publicar pecas diretamente do sistema
8. **Reels/Shorts como formato** -- adicionar video curto como tipo de peca do funil

---

## 9. Duvidas em Aberto

| ID | Duvida | Impacto |
|----|--------|---------|
| DA-001 | O Funnel Architect deve sugerir intervalo de dias entre publicacoes? (ex: "publique peca 1 na segunda, peca 2 na quarta") | Se sim, adicionar campo `dia_sugerido` no plano. Fora do MVP. |
| DA-002 | Quando o usuario remove uma peca do plano, o sistema deve re-gerar a narrativa das restantes para manter coerencia? | Se sim, precisa re-executar Funnel Architect parcialmente. |
| DA-003 | O limite de 2 sub-pipelines simultaneos e suficiente ou o usuario vai querer mais velocidade? | Depende dos rate limits reais da Claude API e Gemini API em producao. |
| DA-004 | O usuario pode adicionar pecas ao plano (alem de remover/editar)? | Adiciona complexidade na UI. Pode ficar para v2. |
| DA-005 | Se uma peca falhar e o usuario cancelar ela, o funil pode ser exportado sem essa peca? | Decisao de negocio: exportar parcial ou exigir todas completas. |

---

## 10. User Stories e Criterios de Aceite

### US-001: Criar funil a partir de um tema

**Como** criador de conteudo,
**Quero** informar um tema e selecionar "Funil" como formato,
**Para que** o sistema gere automaticamente um plano de campanha com multiplas pecas conectadas.

**Criterios de Aceite:**
- [ ] Na Home, existe uma opcao de formato "Funil" ao lado de carrossel, post_unico, etc
- [ ] Ao selecionar Funil + tema + marca e clicar "Criar", o sistema cria um pipeline com modo_funil=true
- [ ] O Funnel Architect e executado automaticamente (primeira etapa do pipeline pai)
- [ ] O usuario e redirecionado para /pipeline/{id}/funil-plano ao criar
- [ ] Se a API falhar, mostra mensagem de erro e permite tentar novamente

---

### US-002: Revisar e editar plano do funil

**Como** criador de conteudo,
**Quero** ver o plano gerado pelo Funnel Architect e poder edita-lo,
**Para que** eu tenha controle total sobre o que sera produzido antes de gastar recursos de API.

**Criterios de Aceite:**
- [ ] A tela /pipeline/{id}/funil-plano mostra o plano com cards para cada peca
- [ ] Cada card mostra: titulo, etapa_funil (badge colorido), formato, angulo, resumo
- [ ] O usuario pode editar inline: titulo, angulo, resumo de cada peca
- [ ] O usuario pode trocar formato via dropdown (carrossel, post_unico, thumbnail_youtube, capa_reels)
- [ ] O usuario pode trocar etapa_funil via dropdown (topo, meio, fundo, conversao)
- [ ] O usuario pode remover uma peca (confirmar com dialog)
- [ ] Minimo de 2 pecas — nao permite remover se restarem apenas 2
- [ ] Mostra narrativa geral do funil no topo da tela
- [ ] Botao "Aprovar Plano" visivel e destacado
- [ ] Botao "Rejeitar e Regenerar" com campo de feedback obrigatorio

---

### US-003: Aprovar plano e iniciar geracao

**Como** criador de conteudo,
**Quero** aprovar o plano revisado para iniciar a producao das pecas,
**Para que** o sistema comece a gerar conteudo de todas as pecas em paralelo.

**Criterios de Aceite:**
- [ ] Ao clicar "Aprovar Plano", o backend cria N sub-pipelines (1 por peca do plano)
- [ ] Cada sub-pipeline recebe: tema (tema_principal + angulo), formato, brand_slug, avatar_mode
- [ ] O usuario e redirecionado para /pipeline/{id}/funil (painel de acompanhamento)
- [ ] Os sub-pipelines comecam a executar automaticamente (ate 2 simultaneos)
- [ ] O plano aprovado fica salvo e nao pode mais ser editado

---

### US-004: Rejeitar plano com feedback

**Como** criador de conteudo,
**Quero** rejeitar o plano e dar feedback sobre o que nao gostei,
**Para que** o Funnel Architect gere um plano melhor na proxima tentativa.

**Criterios de Aceite:**
- [ ] Campo de feedback e obrigatorio ao rejeitar (minimo 10 caracteres)
- [ ] O Funnel Architect recebe o feedback + plano anterior e regenera
- [ ] A tela atualiza com o novo plano
- [ ] O usuario pode rejeitar quantas vezes quiser

---

### US-005: Acompanhar pecas do funil em tempo real

**Como** criador de conteudo,
**Quero** ver o status de todas as pecas do funil em uma unica tela,
**Para que** eu saiba o progresso geral e quais pecas precisam da minha atencao.

**Criterios de Aceite:**
- [ ] A tela /pipeline/{id}/funil mostra cards para cada peca com status visual
- [ ] Status possiveis com cores: pendente (cinza), executando (azul pulsante), aguardando_aprovacao (amarelo), completo (verde), erro (vermelho)
- [ ] Cada card mostra: titulo, formato (icone), etapa_funil (badge), etapa atual do pipeline, progresso de imagem se aplicavel
- [ ] Polling a cada 3 segundos via GET /api/pipelines/{id}/funil/status
- [ ] Header mostra progresso geral: "3 de 5 pecas completas"
- [ ] Pecas com status "aguardando_aprovacao" tem badge piscante de atencao
- [ ] Clicar em uma peca navega para o fluxo existente (/pipeline/{pecaId}/copy, /visual, etc)
- [ ] Botao "Voltar ao Funil" nas telas de aprovacao individual para retornar ao painel

---

### US-006: Aprovar peca individual dentro do funil

**Como** criador de conteudo,
**Quero** aprovar/rejeitar cada peca individualmente usando o mesmo fluxo de hoje,
**Para que** eu mantenha controle sobre a qualidade de cada peca sem mudar o workflow.

**Criterios de Aceite:**
- [ ] Ao clicar na peca no painel do funil, navega para /pipeline/{pecaId}/copy (ou a etapa que precisa aprovacao)
- [ ] O fluxo existente funciona normalmente (aprovar, rejeitar, editar saida)
- [ ] Apos aprovar/rejeitar, o usuario pode voltar ao painel do funil
- [ ] O status da peca no painel atualiza via polling

---

### US-007: Exportar todas as pecas do funil

**Como** criador de conteudo,
**Quero** exportar todas as pecas prontas do funil de uma vez,
**Para que** eu tenha todos os PDFs organizados e salvos no Drive.

**Criterios de Aceite:**
- [ ] A tela /pipeline/{id}/funil-export so fica acessivel quando todas as pecas estao completas
- [ ] Mostra preview miniatura de cada peca (primeiro slide)
- [ ] Botao "Exportar para Drive" salva todos os PDFs + PNGs numa subpasta "{tema} - Funil - {data}"
- [ ] Botao "Download" gera um ZIP com todos os PDFs
- [ ] Cada PDF segue o padrao existente (1 PDF por peca)

---

### US-008: Executar sub-pipelines em paralelo com limite

**Como** sistema,
**Quero** executar ate 2 sub-pipelines simultaneamente,
**Para que** o funil produza mais rapido sem estourar rate limits das APIs.

**Criterios de Aceite:**
- [ ] Ao aprovar plano, o backend inicia execucao dos 2 primeiros sub-pipelines
- [ ] Quando um sub-pipeline completa uma etapa e vai para aguardando_aprovacao ou completa, o backend inicia o proximo sub-pipeline pendente
- [ ] Se um sub-pipeline der erro, os demais continuam executando
- [ ] O usuario pode retomar sub-pipelines com erro individualmente

---

## 11. Modelo de Dados (Novas Tabelas)

### carrossel.funil

| Coluna | Tipo | Descricao |
|--------|------|-----------|
| id | UNIQUEIDENTIFIER | PK |
| tenant_id | VARCHAR(100) | Tenant (obrigatorio) |
| pipeline_id | UNIQUEIDENTIFIER | FK para carrossel.pipeline (pipeline pai) |
| plano | NVARCHAR(MAX) | JSON do plano gerado pelo Funnel Architect |
| plano_aprovado | NVARCHAR(MAX) | JSON do plano aprovado (com edicoes do usuario) |
| status | VARCHAR(50) | pendente_plano, plano_aprovado, executando, completo, cancelado |
| created_at | DATETIME2 | Data de criacao |
| approved_at | DATETIME2 | Data de aprovacao do plano |

### carrossel.funil_peca

| Coluna | Tipo | Descricao |
|--------|------|-----------|
| id | UNIQUEIDENTIFIER | PK |
| funil_id | UNIQUEIDENTIFIER | FK para carrossel.funil |
| pipeline_id | UNIQUEIDENTIFIER | FK para carrossel.pipeline (sub-pipeline da peca) |
| ordem | INT | Posicao da peca no funil (1-5) |
| etapa_funil | VARCHAR(20) | topo, meio, fundo, conversao |
| titulo | NVARCHAR(200) | Titulo da peca |
| formato | VARCHAR(50) | Formato da peca |
| angulo | NVARCHAR(500) | Angulo/abordagem |

---

## 12. Endpoints da API (Resumo)

| Metodo | Rota | Descricao |
|--------|------|-----------|
| POST | /api/pipelines/ | Criar pipeline (modo_funil=true aciona Funnel Architect) |
| GET | /api/pipelines/{id}/funil/plano | Retorna plano gerado |
| PUT | /api/pipelines/{id}/funil/plano | Salva plano editado |
| POST | /api/pipelines/{id}/funil/plano/aprovar | Aprova plano, cria sub-pipelines |
| POST | /api/pipelines/{id}/funil/plano/rejeitar | Rejeita plano com feedback |
| GET | /api/pipelines/{id}/funil/status | Status de todas as pecas (polling) |
| POST | /api/pipelines/{id}/funil/executar | Executa proximas etapas (max 2 simultaneas) |
| POST | /api/pipelines/{id}/funil/exportar | Exporta todos os PDFs + salva no Drive |

---

## 13. Fluxo Completo (Sequencia)

```
1. Home (/?formato=funil)
   Usuario informa tema + seleciona marca + seleciona "Funil"
   → POST /api/pipelines/ {tema, modo_funil: true, brand_slug}
   → Backend cria pipeline pai + executa Funnel Architect

2. /pipeline/{id}/funil-plano
   Usuario ve plano com 3-5 pecas
   → Edita titulos, formatos, angulos, remove pecas
   → Aprova: POST /api/pipelines/{id}/funil/plano/aprovar
   → Backend cria N sub-pipelines + inicia execucao (max 2)

3. /pipeline/{id}/funil
   Painel de acompanhamento com cards por peca
   → Polling: GET /api/pipelines/{id}/funil/status (a cada 3s)
   → Peca precisa aprovacao? Clicar → /pipeline/{pecaId}/copy

4. /pipeline/{pecaId}/copy → /visual → /export (fluxo existente)
   Usuario aprova etapas da peca individual
   → Volta ao painel do funil

5. /pipeline/{id}/funil-export
   Todas as pecas completas
   → Preview + Export Drive + Download ZIP
```

---

*PRD gerado em 2026-04-05 pelo Agente 01 (PRD Analyst) da esteira IT Valley.*
*Fonte de verdade para os proximos agentes: Analista de Tela (02), Arquiteto Backend (03), Arquiteto Frontend (04).*
