# PRD -- Modulo Anuncios (Post 1080x1350 + Copy de Venda)

> **PIVOT 2026-04-23:** PRD simplificado apos validacao visual no mockado. A proposta original de 4 dimensoes Google Ads Display foi **abandonada** porque ficou overkill. O modulo agora e um formato de **1080x1350 (mesma dimensao do post unico)** com **copy de venda diferenciada** (headline + descricao + CTA). Ver secao 10 (Historico de Decisoes) para detalhes da pivot.

## 1. Visao Geral

**Problema:** O sistema de Carrosseis IT Valley cobre bem formatos de conteudo organico (carrossel, post unico educacional, capa de Reels), mas nao tem um formato dedicado a **anuncio pago** com **copy de venda** (headline impactante + descricao de conversao + CTA). Carlos Viana precisa gerar anuncios da IT Valley School com o mesmo visual dark mode premium dos posts organicos, mas com uma estrutura de copy diferente: foco em conversao, CTA explicito, pitch de venda.

**Solucao:** Um novo modulo `/anuncios` que adiciona **Anuncio** como mais um formato suportado pelo sistema (ao lado de carrossel, post unico, capa de Reels). Anuncio tem **a mesma dimensao do post unico (1080x1350)** -- o que diferencia e a **copy** (headline de venda curta + descricao persuasiva + CTA como botao) e o **historico/gestao proprios** (pra nao misturar anuncios com conteudo organico). O formato participa do mesmo pipeline de 6 agentes existente; a unica diferenca e que o Copywriter roda com prompt de venda (nao educacional) e o usuario escolhe/digita um CTA.

**Usuarios-alvo:** Equipe de marketing da IT Valley School (Carlos Viana + operadores do sistema), mesmo publico dos demais formatos.

**Multitenante:** Sim. Segue o padrao do sistema -- `tenant_id` em toda tabela e toda query, mesmo em modo single-user.

---

## 2. Perfis de Usuario (ACL)

Herda os perfis ja definidos no PRD base do sistema. Nenhum perfil novo e criado para o modulo Anuncios.

| Perfil | Descricao | Permissoes Principais no modulo Anuncios |
|--------|-----------|-------------------------------------------|
| Marketing | Equipe de marketing da IT Valley | Criar, listar, obter, editar e excluir anuncios. Executar pipeline, aprovar etapas, escolher variacoes, exportar para Drive. |
| Admin | Carlos Viana ou responsavel tecnico | Tudo do Marketing + configurar chaves de API, gerenciar brand palette usada pelos anuncios. |

---

## 3. Modulos do Sistema

### Modulo Anuncios (novo -- rota `/anuncios`)

- **Descricao:** Nova area do sistema dedicada a criacao e gestao de anuncios com copy de venda. Formato 1080x1350 (mesma dimensao do post unico), mas com copy orientada a conversao (headline + descricao + CTA). Segue o mesmo padrao das rotas `/carrossel` e `/kanban`.
- **Perfis com acesso:** Marketing, Admin
- **Funcionalidades (CRUD -- "nivel 5" Dominio Anuncio):**
  - **CriarAnuncio** -- iniciar criacao de um novo anuncio a partir de tema/briefing
  - **ListarAnuncios** -- listar todos os anuncios do tenant com filtros (data, status, etapa do funil)
  - **ObterAnuncio** -- retornar detalhes de um anuncio especifico (copy + imagem + status + link Drive)
  - **EditarAnuncio** -- editar metadados e copy do anuncio existente (headline, descricao, CTA)
  - **ExcluirAnuncio** -- excluir anuncio (soft delete)

### Formato Anuncio dentro do Pipeline existente

- **Descricao:** Anuncio e um novo **formato** que participa do pipeline de 6 agentes ja existente (Strategist -> Copywriter -> Hook Specialist -> Art Director -> Image Generator -> Content Critic) com o Brand Gate. Nao e um pipeline novo -- e uma nova config de formato.
- **Perfis com acesso:** Marketing, Admin (via pipeline)
- **O que muda em relacao aos outros formatos:**
  - **Copy de venda:** Copywriter roda com prompt de conversao (nao educacional). Gera headline curta de impacto, descricao persuasiva e CTA (texto do botao). Post unico usa prompt educacional/autoridade; anuncio usa prompt de pitch.
  - **Campo CTA obrigatorio:** anuncio tem 1 campo a mais que o post unico -- o CTA (ex: "Inscreva-se", "Saiba mais", "Matricule-se", "Comece agora")
  - **Modelo de imagem:** Gemini **Pro** sempre (anuncio exige mais qualidade visual do que post organico)
  - **Dimensao:** 1080x1350 (mesma do post unico)

### Modulo Funil (existente -- Anuncio entra como novo formato possivel)

- **Descricao:** O Funnel Architect agora pode escolher `anuncio` como um dos formatos das pecas do funil (junto com carrossel, post_unico, thumbnail_youtube, capa_reels).
- **Perfis com acesso:** Marketing, Admin
- **Funcionalidades afetadas:**
  - Funnel Architect passa a considerar `anuncio` como formato valido para pecas de fundo de funil e conversao
  - Plano do funil pode listar pecas do tipo `anuncio`

### Modulo Historico (existente -- extendido)

- **Descricao:** Anuncios aparecem no mesmo historico dos demais formatos (nao tem tela separada), filtrados por `formato = anuncio`.
- **Perfis com acesso:** Marketing, Admin
- **Funcionalidades:**
  - Listar anuncios ao lado dos demais conteudos
  - Filtro por formato para ver so anuncios
  - Reabrir pipeline de um anuncio anterior

### Modulo Export (existente -- extendido)

- **Descricao:** Export ganha comportamento especifico para formato Anuncio -- salva PNG individual + `copy.txt` (com headline, descricao e CTA) na subpasta Drive.
- **Perfis com acesso:** Marketing, Admin
- **Funcionalidades:**
  - Exportar anuncio para subpasta Drive `"{titulo} - {YYYY-MM-DD}"` contendo:
    - `anuncio.png` (1080x1350)
    - `copy.txt` com headline + descricao + CTA

### Modulo Marca (existente -- extendido)

- **Descricao:** Brand ganha campo opcional `cta_anuncio` -- texto de CTA default pra usar quando o anuncio for gerado em modo "ideia livre" (sem usuario digitar CTA manualmente).
- **Perfis com acesso:** Marketing, Admin
- **Funcionalidades:**
  - Novo campo `cta_anuncio` (string opcional) em cada marca
  - Configurado na tela de marcas
  - Usado pelo Copywriter quando anuncio e criado via modo `ideia` e nao tem CTA explicito

---

## 4. Regras de Negocio

| ID | Regra | Modulo |
|----|-------|--------|
| RN-001 | Todo anuncio gera **1 imagem 1080x1350** (mesma dimensao do post unico). | Anuncios |
| RN-002 | Headline do anuncio tem **maximo 40 caracteres** (curta e impactante, estilo de venda). O Copywriter valida esse limite. | Anuncios / Agentes |
| RN-003 | Descricao do anuncio tem **maximo 125 caracteres** (persuasiva). O Copywriter valida esse limite. | Anuncios / Agentes |
| RN-004 | Anuncio e um **formato** que entra no pipeline existente -- NAO e um pipeline novo. Passa pelas mesmas 6 etapas (Strategist, Copywriter, Hook Specialist, Art Director, Image Generator, Content Critic). | Pipeline |
| RN-005 | O Image Generator gera 1 imagem 1080x1350 para o anuncio. O Brand Gate valida do mesmo jeito que post unico. | Pipeline / Imagem |
| RN-006 | Anuncio participa do funil como qualquer outro formato. O Funnel Architect pode incluir pecas `anuncio` no plano do funil (tipicamente em fundo/conversao). | Funil |
| RN-007 | Export de anuncio NAO gera PDF. Salva no Drive subpasta com 1 PNG + `copy.txt` (headline + descricao + CTA). | Export |
| RN-008 | Nome da subpasta Drive segue o padrao existente: `"{titulo} - {YYYY-MM-DD}"`. Mesmo scope `https://www.googleapis.com/auth/drive`. | Export |
| RN-009 | `tenant_id` presente em toda tabela e toda query do modulo Anuncios, mesmo em modo single-user. | Todos |
| RN-010 | CRUD do dominio Anuncio segue a arquitetura IT Valley: DTOs por caso de uso (CriarAnuncio, ListarAnuncios, ObterAnuncio, EditarAnuncio, ExcluirAnuncio), Factory com regras, Service/Router como camadas opacas. | Anuncios |
| RN-011 | Dimensao do formato Anuncio em `dimensions.json` e `{ w: 1080, h: 1350 }` -- mesma estrutura do post_unico. | Configuracoes |
| RN-012 | O brand palette usado pelos anuncios e o mesmo dark mode premium dos demais formatos -- mesma identidade visual. | Anuncios / Skills |
| RN-013 | ExcluirAnuncio e **soft delete** -- mantem registro com `deleted_at` preenchido. Historico continua acessivel via filtro. | Anuncios |
| RN-014 | O historico e **unificado** com os demais formatos -- anuncios aparecem na mesma lista, filtraveis por `formato = anuncio`. Nao existe rota `/historico/anuncios` separada. | Historico |
| RN-015 | **Gemini Pro sempre pra anuncio.** Diferente dos outros formatos (Flash na maioria dos casos), anuncio exige qualidade visual maxima -- entao usa Gemini Pro sempre. Custo ~R$0,30 por anuncio. | Imagem / Custo |
| RN-016 | **Brand overlay igual post unico** (foto+logo). Sem regras especiais de aspect ratio. | Skills / brand_overlay |
| RN-017 | **Copy de venda com 3 campos obrigatorios:** headline (max 40), descricao (max 125), CTA (texto do botao, max 30 chars). | Anuncios / Copy |
| RN-018 | **EditarAnuncio permite editar copy** (headline, descricao, CTA) e regenerar imagem. Nao ha regeneracao "por dimensao" ja que so existe 1 imagem. | Anuncios |
| RN-019 | **Fallback em caso de falha da imagem:** se a geracao falhar apos 2 retries, o anuncio fica em status `erro` e o usuario pode regenerar via EditarAnuncio. | Pipeline |
| RN-020 | **Brand Gate igual post unico** -- mesmo validador, mesmas regras. Sem adaptacao especial. | Skills / Brand Gate |
| RN-021 | **Anuncio participa do Kanban** igual os demais formatos. Card entra na coluna inicial "A fazer" quando criado. | Kanban |
| RN-022 | **Perfis de acesso** herdam do sistema atual: Marketing e Admin podem criar, listar, obter, editar e excluir anuncios. Nenhuma restricao adicional no MVP. | ACL |
| RN-023 | **CTA via modo de entrada:** modo "texto pronto" o usuario digita o CTA. Modo "ideia livre" o Copywriter usa `brand.cta_anuncio` se existir; se nao existir na marca, o Copywriter inventa um CTA contextual apropriado. | Anuncios / Copy / Marca |
| RN-024 | **Campo `cta_anuncio` na Brand:** marca ganha campo opcional `cta_anuncio` (string, max 30 chars) que serve como CTA default quando anuncio e gerado sem CTA explicito. | Marca |
| RN-025 | **Copywriter roda com prompt de venda** (nao educacional) quando formato=anuncio. Foco em conversao, urgencia, beneficio concreto. | Agentes / Copywriter |

---

## 5. Integracoes Externas

Nenhuma integracao nova no MVP. Usa as integracoes ja existentes do sistema:

| Sistema | Tipo | Finalidade |
|---------|------|-----------|
| Claude API (Anthropic) | API REST | LLM dos agentes textuais do pipeline com Copywriter em modo venda (headline 40 / descricao 125 / CTA 30) |
| Gemini API (Google) | API REST | Geracao de 1 imagem 1080x1350 do anuncio. **Pro** sempre (RN-015). |
| Google Drive API | API REST (service account) | Salvar anuncio (1 PNG + copy.txt) em subpasta automatica |
| MSSQL | SQLAlchemy | Persistencia do dominio Anuncio (tabela `anuncio` + relacao com `pipeline`) |

---

## 6. Requisitos Nao Funcionais

- **Performance:** Geracao de 1 imagem em ate 60s (mesmo SLA do post_unico). Validacao dos limites de caracteres em menos de 500ms.
- **Seguranca:** `tenant_id` em toda tabela e query. Chaves de API no `.env` do backend, nunca expostas ao frontend. Mesma autenticacao do sistema atual.
- **Custo:** ~R$0,30 por anuncio (1 Gemini Pro), conforme RN-015.
- **Resiliencia:** Retry automatico ate 2x se a geracao da imagem falhar. Em caso de falha persistente, status = erro e o usuario regenera manualmente.
- **Observabilidade:** Logs estruturados por execucao de pipeline. Historico de scores do Content Critic por anuncio.

---

## 7. MVP -- Escopo do Primeiro Lancamento

### Backend
- DTOs por caso de uso: `CriarAnuncio`, `ListarAnuncios`, `ObterAnuncio`, `EditarAnuncio`, `ExcluirAnuncio` em `backend/dtos/anuncio/`
- `AnuncioFactory` com regras de negocio (limites de caracteres headline/descricao/CTA, validacao de CTA vs brand.cta_anuncio)
- `AnuncioService` como camada opaca orquestrando Factory + Mapper + Repository
- `AnuncioRouter` expondo `/api/anuncios/` (POST, GET list, GET by id, PUT, DELETE)
- Model SQLAlchemy `anuncio` (tabela unica, sem tabela filha de dimensoes) com `tenant_id`, titulo, headline, descricao, cta, pipeline_id, status, drive_folder_link, image_url (1 URL), created_at, updated_at, deleted_at
- Integracao do formato `anuncio` no pipeline existente (adicionar em `dimensions.json`, `formatos.json`, `platform_rules.json`, `templates.json`)
- Copywriter com branch `formato=anuncio` usando prompt de venda + limites 40/125/30
- Export handler especifico: 1 PNG + copy.txt (sem PDF, sem ZIP)
- Brand DTO + tabela `brand` ganham campo opcional `cta_anuncio` (string, max 30 chars)

### Frontend
- Nova rota `/anuncios` com lista de anuncios (CRUD)
- Entrada de criacao unificada via `/?formato=anuncio` (mesmo wizard dos demais formatos)
- Tela de detalhe do anuncio mostrando a imagem 1080x1350 + headline + descricao + CTA
- Integracao do formato `anuncio` no seletor de formato da Home, Kanban, Historico, Pipeline Export
- Tela de configuracao de marca ganha campo "CTA padrao de anuncio"
- Historico unificado com filtro por formato

### Configs
- `dimensions.json` atualizado com formato `anuncio` = `{ w: 1080, h: 1350 }` (objeto unico, mesma estrutura de post_unico)
- `platform_rules.json` atualizado com regras de anuncio (headline 40, descricao 125, CTA 30)
- `templates.json` atualizado com template do formato anuncio
- `formatos.json` atualizado com objeto `anuncio`

### Infraestrutura
- Brand Gate aplicado igual post unico (1 validacao)
- Retry automatico 2x (mesmo limite do sistema)

---

## 8. Roadmap -- Fora do MVP

| Item | Descricao | Prioridade |
|------|-----------|------------|
| Multiplas dimensoes de anuncio | Suportar outras dimensoes (1200x628, 1080x1080, 300x600, 300x250) pra campanhas Google Ads Display | Media |
| Integracao Meta Ads / Google Ads Manager API | Upload direto pra plataformas sem baixar/subir manualmente | Alta |
| Variacoes de copy | Gerar 3 pares headline+descricao+CTA por anuncio e usuario escolhe o melhor | Media |
| A/B testing de anuncios | Gerar 2 versoes da imagem com mesma copy e comparar | Media |
| Metricas de performance | Integrar com APIs externas para trazer CTR/CPC de volta pro sistema | Baixa |
| Biblioteca de CTAs | Sugestoes inteligentes de CTA baseadas em objetivo (leads, vendas, autoridade) | Baixa |
| Geracao em lote | Gerar N anuncios de uma vez para uma campanha completa | Media |

---

## 9. Decisoes Atuais (pos-pivot 2026-04-23)

| ID | Decisao | RN |
|----|---------|-----|
| DA-001 | Gemini **Pro sempre** (1 imagem por anuncio, ~R$0,30). | RN-015 |
| DA-002 | EditarAnuncio permite **editar copy + regerar imagem inteira**. Sem regeneracao "por dimensao" (so tem 1 imagem). | RN-018 |
| DA-003 | Historico **unificado** com filtro por formato. | RN-014 |
| DA-004 | Perfis: **herda Marketing + Admin** do sistema atual. | RN-022 |
| DA-005 | Anuncio **entra no Kanban** igual os outros formatos. | RN-021 |
| DA-006 | Integracao Meta/Google Ads API fica no **roadmap**. | Roadmap |
| DA-007 | Copy com **3 campos** fixos: headline (40), descricao (125), CTA (30). | RN-017 |
| DA-008 | Brand Gate **igual post unico** -- sem logica especial. | RN-020 |
| DA-009 | **Falha de imagem** apos 2 retries -> status=erro. Usuario regenera manualmente. | RN-019 |
| DA-010 | Brand overlay **igual post unico** (foto+logo). Sem logica por dimensao. | RN-016 |
| DA-011 | **CTA por modo de entrada:** modo `texto_pronto` -> usuario digita; modo `ideia` -> pega `brand.cta_anuncio` se existir, senao Copywriter inventa. | RN-023 |
| DA-012 | **Marca ganha campo `cta_anuncio`** opcional (max 30 chars). Configuravel na tela de marca. | RN-024 |
| DA-013 | **Copywriter em modo venda** pra formato=anuncio (prompt de conversao, nao educacional). | RN-025 |

Nenhuma duvida em aberto.

---

## 10. Historico de Decisoes (Pivots)

### Pivot 1 -- 2026-04-23 -- De "Google Ads 4 dimensoes" pra "Post de venda 1080x1350"

**Contexto:** O PRD original propunha anuncio como formato Google Ads Display com 4 dimensoes (1200x628, 1080x1080, 300x600, 300x250), grid 2x2 no detalhe, regeneracao individual por dimensao, status parcial (3 de 4 completos), Gemini Pro+Flash hibrido, export ZIP com 4 PNGs, Brand Gate adaptado por aspect ratio, foto do Carlos so nas grandes.

**Gatilho:** Apos agentes 01-07 completos e mockado clicavel validado visualmente, o designer apontou que todo o trabalho visual (inclusive mockups de referencia) foi feito em 1080x1350. Tentar gerar 4 dimensoes diferentes exigia criar novos templates visuais, reescrever o brand_overlay e validar cada aspect ratio separadamente -- muito esforco pra ROI baixo, dado que o uso real e 95% social (Meta Ads).

**Decisao:** O modulo Anuncios passa a ser **1 formato 1080x1350** (mesma dimensao do post unico) que se diferencia pela **copy de venda** (headline impactante + descricao persuasiva + CTA como botao). Mantem o modulo separado porque copy de venda e diferente de copy educacional (post_unico), tem historico proprio pra nao misturar com conteudo organico, e tem regras visuais sutis diferentes (template orientado a conversao).

**O que foi descartado:**
- 4 dimensoes -> 1 dimensao
- Grid 2x2 -> 1 imagem simples
- Regeneracao individual por dimensao -> regeneracao da imagem inteira
- Status parcial -> completo/erro simples
- Gemini Pro/Flash hibrido -> Pro sempre
- ZIP multi-arquivo -> 1 PNG + copy.txt no Drive
- Brand Gate adaptado por aspect ratio -> igual post unico
- Tabela `anuncio_dimensao` separada -> campos diretos na `anuncio`

**O que foi ganho:**
- Campo CTA obrigatorio (3 campos de copy: headline, descricao, CTA)
- Brand.cta_anuncio como fallback pro modo "ideia livre"
- Copywriter em modo venda (prompt de conversao)
- Limites de copy ajustados (40/125/30 em vez de 30/90)

**Impacto nos artefatos existentes:**
- `docs/prd-anuncios.md` -- este documento atualizado
- `docs/telas-anuncios.md` -- precisa simplificacao: remover grid 2x2, modal regenerar dimensao
- `docs/arquitetura-backend-anuncios.md` -- remover tabela `anuncio_dimensao`, endpoint regenerar-dimensao, logica parcial
- `docs/arquitetura-frontend-anuncios.md` -- remover componentes DimensoesGrid, DimensaoCard, RegenerarModal
- `docs/design-anuncios.md` -- simplificar: grid 2x2 some, badge "Parcial N/4" some
- `docs/banco-anuncios.md` -- remover tabela `anuncio_dimensao`; adicionar `image_url` e `cta` direto na `anuncio`; Brand ganha `cta_anuncio`
- Frontend (componentes + rotas) -- simplificar, adicionar CTA
- Backend (model + migration + copywriter + brand) -- simplificar, adicionar CTA

---

*PRD gerado pelo Agente 01 (PRD Analyst) da esteira IT Valley.*
*Fonte de verdade para os proximos agentes: Analista de Tela (02), Arquiteto Backend (03), Arquiteto Frontend (04), Arquiteto Designer (05).*
