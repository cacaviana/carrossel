# BANCO DE DADOS -- Modulo Anuncios (Google Ads Display)

Documento produzido pelo Agente 07 (Arquiteto SQL + MongoDB).
Base: PRD (`docs/prd-anuncios.md`) + Arquitetura Backend (`docs/arquitetura-backend-anuncios.md`) + padrao existente (`docs/BANCO.md`) + `CLAUDE.md`.

Fonte de verdade para o Agente 10 (Dev Backend) rodar migrations.

---

## 1. Overview -- Estrategia

### 1.1 SGBD e schema
| Item | Valor |
|------|-------|
| SGBD relacional | Microsoft SQL Server (MSSQL) |
| Schema | `carrossel` (mesmo das demais tabelas) |
| Conexao existente | `backend/services/db_service.py` (pymssql) + `data/connections/database.py` (SQLAlchemy async) |
| NoSQL | **NAO sera usado neste modulo** (ver secao 6) |
| IDs | UNIQUEIDENTIFIER (UUID v4) |
| Tipos JSON | NVARCHAR(MAX) -- parse no Python |
| Timestamps | DATETIME2 em UTC (SYSUTCDATETIME()) |

### 1.2 Decisao AR-01 -- 2 tabelas (`anuncio` + `anuncio_dimensao`)
Decisao ja tomada no Agente 03. Reafirmada aqui pelo Arquiteto SQL:

| Opcao | Vantagem | Desvantagem |
|-------|----------|-------------|
| 1 tabela com JSON (4 URLs) | Simples | **NAO suporta regen individual com estado (retries, brand_gate)**. Queries agregadas dificeis. |
| **2 tabelas (escolhida)** | Estado isolado por dimensao, regen natural (RN-018), parcial natural (RN-019), JOIN direto | 1 JOIN a mais |

### 1.3 Tabelas do modulo
| Tabela | Status | Finalidade |
|--------|--------|-----------|
| `carrossel.anuncio` | **Nova** | 1 linha por anuncio (metadados + copy + status derivado) |
| `carrossel.anuncio_dimensao` | **Nova** | 4 linhas por anuncio (1 por dimensao) -- estado individual de geracao |
| `carrossel.pipeline` | **Alterar** CHECK CONSTRAINT | Aceitar `formato='anuncio'` (ja esta no BANCO.md atual: `('carrossel', 'post_unico', 'thumbnail_youtube', 'capa_reels', 'anuncio')`) -- **verificar se ja foi aplicado** |
| `carrossel.conteudo` | **Alterar** CHECK CONSTRAINT | Mesmo do pipeline (ja esta no BANCO.md: aceita `'anuncio'`) |
| `carrossel.historico` | Sem alteracao | Ja aceita `formato='anuncio'` via coluna existente (VARCHAR(50) sem check) |

### 1.4 Regras globais aplicadas
- RN-009 `tenant_id` em toda tabela e toda query (exceto filha `anuncio_dimensao`, que isola via JOIN com `anuncio` -- mesmo padrao de `pipeline_step`, ver secao 8.6 do BANCO.md).
- RN-013 Soft delete com `deleted_at` na tabela principal. Filha cascateia via `anuncio_id`.
- Cascade em `anuncio_dimensao`: ao hard-deletar `anuncio`, apaga dimensoes. Soft delete nao cascateia fisicamente -- filtro fica no repository.
- FK `pipeline_id` em `anuncio` usa `ON DELETE SET NULL` (mesmo padrao de `conteudo`), preservando o anuncio mesmo se o pipeline for apagado.

---

## 2. Tabela `carrossel.anuncio`

### 2.1 DDL

```sql
-- 008_anuncio.sql
-- Anuncio Google Ads Display -- 1 registro por anuncio, contem 4 dimensoes (filhas).
-- Dependencias: carrossel.pipeline (FK pipeline_id, nullable -- SET NULL no delete).

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'anuncio')
BEGIN
    CREATE TABLE carrossel.anuncio (
        id                     UNIQUEIDENTIFIER    NOT NULL DEFAULT NEWID(),
        tenant_id              VARCHAR(50)         NOT NULL,

        -- Pipeline / funil
        pipeline_id            UNIQUEIDENTIFIER    NULL,
        pipeline_funil_id      UNIQUEIDENTIFIER    NULL,

        -- Metadados
        titulo                 NVARCHAR(200)       NOT NULL,
        etapa_funil            VARCHAR(20)         NULL,            -- topo|meio|fundo|avulso
        tema_ou_briefing       NVARCHAR(MAX)       NULL,
        modo_entrada           VARCHAR(20)         NULL,            -- texto|disciplina
        disciplina             VARCHAR(50)         NULL,
        tecnologia             VARCHAR(100)        NULL,
        foto_criador_id        VARCHAR(100)        NULL,
        criado_por             VARCHAR(100)        NULL,            -- user_id do JWT

        -- Copy (RN-002, RN-003, RN-017)
        headline               NVARCHAR(30)        NULL,            -- max 30 chars Google Ads
        descricao              NVARCHAR(90)        NULL,            -- max 90 chars Google Ads

        -- Status derivado (ver Factory.recalcular_status)
        status                 VARCHAR(20)         NOT NULL DEFAULT 'rascunho',

        -- Export
        drive_folder_id        VARCHAR(100)        NULL,
        drive_folder_link      NVARCHAR(MAX)       NULL,
        last_exported_at       DATETIME2           NULL,

        -- Auditoria
        created_at             DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at             DATETIME2           NULL,
        deleted_at             DATETIME2           NULL,

        CONSTRAINT PK_anuncio PRIMARY KEY (id),
        CONSTRAINT FK_anuncio_pipeline FOREIGN KEY (pipeline_id)
            REFERENCES carrossel.pipeline(id) ON DELETE SET NULL,
        CONSTRAINT CK_anuncio_status CHECK (status IN (
            'rascunho', 'gerando', 'completo', 'parcial', 'erro', 'cancelado'
        )),
        CONSTRAINT CK_anuncio_etapa_funil CHECK (etapa_funil IS NULL OR etapa_funil IN (
            'topo', 'meio', 'fundo', 'avulso'
        )),
        CONSTRAINT CK_anuncio_modo_entrada CHECK (modo_entrada IS NULL OR modo_entrada IN (
            'texto', 'disciplina'
        ))
    );
END
GO
```

### 2.2 Descricao das colunas

| Coluna | Tipo | Nullable | Descricao / RN |
|--------|------|----------|----------------|
| `id` | UNIQUEIDENTIFIER | NOT NULL | PK, UUID gerado no banco |
| `tenant_id` | VARCHAR(50) | NOT NULL | Isolamento multitenant (RN-009) |
| `pipeline_id` | UNIQUEIDENTIFIER | NULL | FK -> `carrossel.pipeline.id`. SET NULL no delete. Opcional para suportar anuncios criados via funil que apontam para `pipeline_funil_id` em vez de pipeline proprio |
| `pipeline_funil_id` | UNIQUEIDENTIFIER | NULL | Apontador solto para o pipeline "mae" do funil (nao tem FK -- funil pode ser deletado antes) |
| `titulo` | NVARCHAR(200) | NOT NULL | Titulo do anuncio. Usado no nome da subpasta Drive (RN-008) |
| `etapa_funil` | VARCHAR(20) | NULL | topo/meio/fundo/avulso (RN-006). Constraint CHECK |
| `tema_ou_briefing` | NVARCHAR(MAX) | NULL | Briefing livre do usuario |
| `modo_entrada` | VARCHAR(20) | NULL | texto ou disciplina |
| `disciplina` | VARCHAR(50) | NULL | D1..D9 quando modo=disciplina |
| `tecnologia` | VARCHAR(100) | NULL | Ex: YOLO, Whisper, XGBoost |
| `foto_criador_id` | VARCHAR(100) | NULL | ID no creator_registry.json |
| `criado_por` | VARCHAR(100) | NULL | user_id extraido do JWT |
| `headline` | NVARCHAR(30) | NULL | Copy Google Ads max 30 chars (RN-002). Nullable ate Copywriter rodar |
| `descricao` | NVARCHAR(90) | NULL | Copy Google Ads max 90 chars (RN-003). Nullable ate Copywriter rodar |
| `status` | VARCHAR(20) | NOT NULL | Estados: rascunho, gerando, completo, parcial, erro, cancelado (RN-019) |
| `drive_folder_id` | VARCHAR(100) | NULL | ID da subpasta Drive criada no export |
| `drive_folder_link` | NVARCHAR(MAX) | NULL | URL publica da pasta Drive |
| `last_exported_at` | DATETIME2 | NULL | Ultimo export feito |
| `created_at` | DATETIME2 | NOT NULL | UTC, DEFAULT SYSUTCDATETIME() |
| `updated_at` | DATETIME2 | NULL | Preenchido pelo ORM em update |
| `deleted_at` | DATETIME2 | NULL | Soft delete (RN-013) |

### 2.3 Observacoes importantes
- **Tamanho de `headline` (30) e `descricao` (90)**: colocado como constraint de coluna apesar do Pydantic validar. Defesa em profundidade -- se algum repository esquecer de validar, o banco rejeita.
- **`status` derivado**: o valor em disco e fonte para queries, mas a Factory recalcula apos cada mudanca de dimensao. O repository deve chamar `AnuncioFactory.recalcular_status(anuncio)` antes de cada UPDATE.
- **Sem UNIQUE em (tenant_id, titulo)**: intencional. Usuario pode criar varios anuncios com o mesmo titulo.

---

## 3. Tabela `carrossel.anuncio_dimensao`

### 3.1 DDL

```sql
-- 009_anuncio_dimensao.sql
-- Uma linha por dimensao do anuncio. Sempre 4 linhas por anuncio no MVP (RN-001).
-- Dependencias: carrossel.anuncio (FK anuncio_id -- CASCADE em hard delete).
-- NAO tem tenant_id proprio: isolamento via JOIN com anuncio (mesmo padrao de pipeline_step).

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'anuncio_dimensao')
BEGIN
    CREATE TABLE carrossel.anuncio_dimensao (
        id                     UNIQUEIDENTIFIER    NOT NULL DEFAULT NEWID(),
        anuncio_id             UNIQUEIDENTIFIER    NOT NULL,

        -- Identidade da dimensao
        dimensao_id            VARCHAR(20)         NOT NULL,        -- 1200x628 | 1080x1080 | 300x600 | 300x250
        ordem                  INT                 NOT NULL,        -- 0..3 (ordem fixa -- ver Factory)
        largura                INT                 NOT NULL,
        altura                 INT                 NOT NULL,

        -- Geracao
        modelo_usado           VARCHAR(50)         NULL,            -- gemini-3-pro-image-preview | gemini-2.5-flash-image
        overlay_aplicado       VARCHAR(20)         NOT NULL DEFAULT 'foto+logo', -- foto+logo | so_logo (RN-016)

        -- Imagem gerada
        imagem_url             NVARCHAR(MAX)       NULL,            -- URL Drive ou data URL
        imagem_base64          NVARCHAR(MAX)       NULL,            -- cache local pre-upload (opcional)

        -- Brand Gate (RN-019, RN-020)
        brand_gate_status      VARCHAR(20)         NOT NULL DEFAULT 'nao_gerada',
        brand_gate_retries     INT                 NOT NULL DEFAULT 0,
        brand_gate_feedback    NVARCHAR(MAX)       NULL,

        -- Timestamps
        created_at             DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
        gerada_em              DATETIME2           NULL,
        updated_at             DATETIME2           NULL,

        CONSTRAINT PK_anuncio_dimensao PRIMARY KEY (id),
        CONSTRAINT FK_anuncio_dimensao_anuncio FOREIGN KEY (anuncio_id)
            REFERENCES carrossel.anuncio(id) ON DELETE CASCADE,
        CONSTRAINT UQ_anuncio_dimensao_unica UNIQUE (anuncio_id, dimensao_id),
        CONSTRAINT CK_anuncio_dimensao_dim CHECK (dimensao_id IN (
            '1200x628', '1080x1080', '300x600', '300x250'
        )),
        CONSTRAINT CK_anuncio_dimensao_overlay CHECK (overlay_aplicado IN (
            'foto+logo', 'so_logo'
        )),
        CONSTRAINT CK_anuncio_dimensao_brand_gate CHECK (brand_gate_status IN (
            'nao_gerada', 'gerando', 'valido', 'revisao_manual', 'falhou'
        )),
        CONSTRAINT CK_anuncio_dimensao_retries CHECK (brand_gate_retries BETWEEN 0 AND 2),
        CONSTRAINT CK_anuncio_dimensao_ordem CHECK (ordem BETWEEN 0 AND 3)
    );
END
GO
```

### 3.2 Descricao das colunas

| Coluna | Tipo | Nullable | Descricao / RN |
|--------|------|----------|----------------|
| `id` | UNIQUEIDENTIFIER | NOT NULL | PK |
| `anuncio_id` | UNIQUEIDENTIFIER | NOT NULL | FK -> `carrossel.anuncio.id` com **CASCADE** (hard delete apaga dimensoes) |
| `dimensao_id` | VARCHAR(20) | NOT NULL | Chave logica da dimensao. CHECK com 4 valores fixos (RN-001) |
| `ordem` | INT | NOT NULL | 0=1200x628, 1=1080x1080, 2=300x600, 3=300x250. Facilita ORDER BY e mapeamento UI |
| `largura` | INT | NOT NULL | Redundante com dimensao_id, mas evita parse na leitura |
| `altura` | INT | NOT NULL | Idem |
| `modelo_usado` | VARCHAR(50) | NULL | Pro na 1200x628, Flash nas 3 menores (RN-015). Null antes da geracao |
| `overlay_aplicado` | VARCHAR(20) | NOT NULL | `foto+logo` nas 2 grandes, `so_logo` nas 2 pequenas (RN-016) |
| `imagem_url` | NVARCHAR(MAX) | NULL | URL final da imagem (Drive ou data URL temporario) |
| `imagem_base64` | NVARCHAR(MAX) | NULL | Cache temporario pre-upload. Pode ser limpo apos upload pro Drive |
| `brand_gate_status` | VARCHAR(20) | NOT NULL | nao_gerada -> gerando -> valido/revisao_manual/falhou (RN-019) |
| `brand_gate_retries` | INT | NOT NULL | 0..2. Passa para `falhou` apos 2 retries ruins (RN-019) |
| `brand_gate_feedback` | NVARCHAR(MAX) | NULL | Feedback do ultimo fail (para debug) |
| `created_at` | DATETIME2 | NOT NULL | DEFAULT SYSUTCDATETIME() |
| `gerada_em` | DATETIME2 | NULL | Timestamp da ultima geracao bem sucedida |
| `updated_at` | DATETIME2 | NULL | Preenchido no ORM |

### 3.3 Por que nao tem `tenant_id`
Segue o mesmo padrao da tabela `pipeline_step` (ver BANCO.md secao 8.6): o isolamento multitenant e garantido via JOIN com a tabela-pai (`anuncio`) que tem `tenant_id`. Todas as queries do `AnuncioRepository` devem fazer JOIN ou WHERE IN (SELECT id FROM anuncio WHERE tenant_id=...). Evita duplicacao e garante consistencia.

### 3.4 Por que nao tem `deleted_at`
Soft delete e feito **somente no anuncio pai**. Se `anuncio.deleted_at IS NOT NULL`, as dimensoes ficam inacessiveis pela aplicacao (query no repository filtra `a.deleted_at IS NULL`). Se um dia precisar hard delete, CASCADE cuida das dimensoes.

---

## 4. Indices e constraints

### 4.1 Indices -- tabela `anuncio`

```sql
-- 808_anuncio_indexes.sql
-- Todos os indices consideram isolamento por tenant_id e soft delete.

-- Listagem principal: por tenant + status + data (tela /anuncios)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_tenant_status_created')
    CREATE INDEX IX_anuncio_tenant_status_created
    ON carrossel.anuncio (tenant_id, status, created_at DESC)
    WHERE deleted_at IS NULL;
GO

-- Filtro por etapa do funil
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_tenant_etapa')
    CREATE INDEX IX_anuncio_tenant_etapa
    ON carrossel.anuncio (tenant_id, etapa_funil)
    WHERE deleted_at IS NULL;
GO

-- Busca por titulo (LIKE). Usado na busca livre da tela.
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_tenant_titulo')
    CREATE INDEX IX_anuncio_tenant_titulo
    ON carrossel.anuncio (tenant_id, titulo)
    WHERE deleted_at IS NULL;
GO

-- JOIN com pipeline (retomar pipeline a partir do anuncio ou vice-versa)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_tenant_pipeline')
    CREATE INDEX IX_anuncio_tenant_pipeline
    ON carrossel.anuncio (tenant_id, pipeline_id)
    WHERE pipeline_id IS NOT NULL AND deleted_at IS NULL;
GO

-- JOIN com funil (listar todos anuncios de um pipeline_funil)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_tenant_funil')
    CREATE INDEX IX_anuncio_tenant_funil
    ON carrossel.anuncio (tenant_id, pipeline_funil_id)
    WHERE pipeline_funil_id IS NOT NULL AND deleted_at IS NULL;
GO

-- Historico unificado (RN-014): buscar por tenant + criado_por + data
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_tenant_criadopor_created')
    CREATE INDEX IX_anuncio_tenant_criadopor_created
    ON carrossel.anuncio (tenant_id, criado_por, created_at DESC)
    WHERE deleted_at IS NULL;
GO
```

### 4.2 Indices -- tabela `anuncio_dimensao`

```sql
-- 809_anuncio_dimensao_indexes.sql

-- JOIN principal: listar dimensoes de um anuncio, ordenadas
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_dim_anuncio_ordem')
    CREATE INDEX IX_anuncio_dim_anuncio_ordem
    ON carrossel.anuncio_dimensao (anuncio_id, ordem);
GO

-- Recalculo de status (contar dimensoes validas por anuncio)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_dim_anuncio_brand_gate')
    CREATE INDEX IX_anuncio_dim_anuncio_brand_gate
    ON carrossel.anuncio_dimensao (anuncio_id, brand_gate_status);
GO

-- Workers de geracao: pegar dimensoes 'gerando' (fila virtual)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_dim_gerando')
    CREATE INDEX IX_anuncio_dim_gerando
    ON carrossel.anuncio_dimensao (brand_gate_status, created_at)
    WHERE brand_gate_status = 'gerando';
GO
```

### 4.3 Constraints -- resumo

| Tabela | Constraint | Tipo | Descricao |
|--------|-----------|------|-----------|
| anuncio | PK_anuncio | PK | id |
| anuncio | FK_anuncio_pipeline | FK | pipeline_id -> pipeline.id, ON DELETE SET NULL |
| anuncio | CK_anuncio_status | CHECK | 6 valores validos de status |
| anuncio | CK_anuncio_etapa_funil | CHECK | topo/meio/fundo/avulso |
| anuncio | CK_anuncio_modo_entrada | CHECK | texto/disciplina |
| anuncio_dimensao | PK_anuncio_dimensao | PK | id |
| anuncio_dimensao | FK_anuncio_dimensao_anuncio | FK | anuncio_id -> anuncio.id, **ON DELETE CASCADE** |
| anuncio_dimensao | UQ_anuncio_dimensao_unica | UNIQUE | (anuncio_id, dimensao_id) -- garante nunca duplicar dimensao |
| anuncio_dimensao | CK_anuncio_dimensao_dim | CHECK | 4 valores fixos de dimensao_id |
| anuncio_dimensao | CK_anuncio_dimensao_overlay | CHECK | foto+logo / so_logo |
| anuncio_dimensao | CK_anuncio_dimensao_brand_gate | CHECK | 5 valores validos |
| anuncio_dimensao | CK_anuncio_dimensao_retries | CHECK | 0..2 |
| anuncio_dimensao | CK_anuncio_dimensao_ordem | CHECK | 0..3 |

---

## 5. Queries criticas

### 5.1 Listar anuncios do tenant com filtros (tela principal)

```sql
-- Filtros: tenant_id obrigatorio + status + etapa_funil + busca por titulo + data range
-- Retorna tambem a thumbnail 1080x1080 (ordem=1) via LEFT JOIN lateral
-- Paginacao: OFFSET/FETCH

DECLARE @tenant_id VARCHAR(50) = 'itvalley';
DECLARE @status VARCHAR(20) = NULL;
DECLARE @etapa VARCHAR(20) = NULL;
DECLARE @busca NVARCHAR(200) = NULL;
DECLARE @data_inicio DATETIME2 = NULL;
DECLARE @data_fim DATETIME2 = NULL;
DECLARE @page INT = 1;
DECLARE @page_size INT = 20;

SELECT
    a.id, a.titulo, a.headline, a.descricao, a.status, a.etapa_funil,
    a.pipeline_id, a.drive_folder_link, a.created_at, a.deleted_at,
    dim.imagem_url AS thumbnail_1080,
    (SELECT COUNT(*) FROM carrossel.anuncio_dimensao d
      WHERE d.anuncio_id = a.id AND d.brand_gate_status = 'valido') AS dimensoes_ok_count
FROM carrossel.anuncio a
OUTER APPLY (
    SELECT TOP 1 imagem_url
    FROM carrossel.anuncio_dimensao d
    WHERE d.anuncio_id = a.id AND d.ordem = 1
) dim
WHERE a.tenant_id = @tenant_id
  AND a.deleted_at IS NULL
  AND (@status IS NULL OR a.status = @status)
  AND (@etapa IS NULL OR a.etapa_funil = @etapa)
  AND (@busca IS NULL OR a.titulo LIKE '%' + @busca + '%')
  AND (@data_inicio IS NULL OR a.created_at >= @data_inicio)
  AND (@data_fim IS NULL OR a.created_at <= @data_fim)
ORDER BY a.created_at DESC
OFFSET (@page - 1) * @page_size ROWS
FETCH NEXT @page_size ROWS ONLY;
```

### 5.2 Obter anuncio com 4 dimensoes hidratadas (tela de detalhe)

```sql
-- Query 1: anuncio
SELECT
    id, tenant_id, pipeline_id, pipeline_funil_id, titulo, etapa_funil,
    headline, descricao, status, drive_folder_id, drive_folder_link,
    foto_criador_id, criado_por, tema_ou_briefing, modo_entrada, disciplina, tecnologia,
    last_exported_at, created_at, updated_at, deleted_at
FROM carrossel.anuncio
WHERE id = @anuncio_id AND tenant_id = @tenant_id AND deleted_at IS NULL;

-- Query 2: dimensoes (ordenadas)
SELECT
    id, anuncio_id, dimensao_id, ordem, largura, altura,
    modelo_usado, overlay_aplicado, imagem_url, imagem_base64,
    brand_gate_status, brand_gate_retries, brand_gate_feedback,
    gerada_em, created_at, updated_at
FROM carrossel.anuncio_dimensao
WHERE anuncio_id = @anuncio_id
ORDER BY ordem ASC;
```

No SQLAlchemy, o `relationship("AnuncioDimensaoModel", order_by="ordem", lazy="selectin")` faz as 2 queries automaticamente. Em codigo manual (repository) basta executar as duas.

### 5.3 Regeneracao individual de 1 dimensao (RN-018)

```sql
-- Marca a dimensao como 'gerando' e zera retries. Isolamento via subquery no anuncio.
UPDATE d
SET d.brand_gate_status = 'gerando',
    d.brand_gate_retries = 0,
    d.brand_gate_feedback = NULL,
    d.updated_at = SYSUTCDATETIME()
FROM carrossel.anuncio_dimensao d
INNER JOIN carrossel.anuncio a ON a.id = d.anuncio_id
WHERE a.id = @anuncio_id
  AND a.tenant_id = @tenant_id
  AND a.deleted_at IS NULL
  AND d.dimensao_id IN ('300x600');  -- ou lista de dimensoes_alvo
```

### 5.4 Atualizar URL de imagem apos Image Generator

```sql
-- Apos image_generator gerar a imagem para uma dimensao:
UPDATE d
SET d.imagem_url = @imagem_url,
    d.modelo_usado = @modelo,
    d.gerada_em = SYSUTCDATETIME(),
    d.updated_at = SYSUTCDATETIME()
FROM carrossel.anuncio_dimensao d
INNER JOIN carrossel.anuncio a ON a.id = d.anuncio_id
WHERE a.id = @anuncio_id
  AND a.tenant_id = @tenant_id
  AND d.dimensao_id = @dimensao_id;
```

### 5.5 Atualizar status do Brand Gate (RN-020)

```sql
-- Brand Gate retornou 'valido' para uma dimensao:
UPDATE d
SET d.brand_gate_status = 'valido',
    d.brand_gate_feedback = NULL,
    d.updated_at = SYSUTCDATETIME()
FROM carrossel.anuncio_dimensao d
INNER JOIN carrossel.anuncio a ON a.id = d.anuncio_id
WHERE a.id = @anuncio_id
  AND a.tenant_id = @tenant_id
  AND d.dimensao_id = @dimensao_id;

-- Brand Gate retornou 'revisao_manual' com retries disponiveis:
UPDATE d
SET d.brand_gate_status = 'revisao_manual',
    d.brand_gate_retries = d.brand_gate_retries + 1,
    d.brand_gate_feedback = @feedback,
    d.updated_at = SYSUTCDATETIME()
FROM carrossel.anuncio_dimensao d
INNER JOIN carrossel.anuncio a ON a.id = d.anuncio_id
WHERE a.id = @anuncio_id
  AND a.tenant_id = @tenant_id
  AND d.dimensao_id = @dimensao_id
  AND d.brand_gate_retries < 2;

-- Brand Gate falhou definitivo apos 2 retries (RN-019):
UPDATE d
SET d.brand_gate_status = 'falhou',
    d.brand_gate_feedback = @feedback,
    d.updated_at = SYSUTCDATETIME()
FROM carrossel.anuncio_dimensao d
INNER JOIN carrossel.anuncio a ON a.id = d.anuncio_id
WHERE a.id = @anuncio_id
  AND a.tenant_id = @tenant_id
  AND d.dimensao_id = @dimensao_id
  AND d.brand_gate_retries >= 2;
```

### 5.6 Recalcular status do anuncio a partir das dimensoes

```sql
-- Conta dimensoes em cada estado para decidir status do anuncio
SELECT
    SUM(CASE WHEN brand_gate_status = 'valido'   THEN 1 ELSE 0 END) AS validas,
    SUM(CASE WHEN brand_gate_status = 'falhou'   THEN 1 ELSE 0 END) AS falhadas,
    SUM(CASE WHEN brand_gate_status IN ('nao_gerada','gerando','revisao_manual') THEN 1 ELSE 0 END) AS pendentes,
    COUNT(*) AS total
FROM carrossel.anuncio_dimensao
WHERE anuncio_id = @anuncio_id;

-- Aplicacao decide (na Factory):
--   validas=4                       -> 'completo'
--   pendentes>0                     -> 'gerando'
--   validas>=1 AND pendentes=0      -> 'parcial'
--   validas=0 AND falhadas=total    -> 'erro'

-- Grava resultado (feito pela Factory na propriedade status)
UPDATE carrossel.anuncio
SET status = @novo_status,
    updated_at = SYSUTCDATETIME()
WHERE id = @anuncio_id AND tenant_id = @tenant_id;
```

### 5.7 Soft delete (RN-013)

```sql
-- Soft delete so no anuncio. Dimensoes ficam "orfas logicamente" mas CASCADE fisico
-- dispara se algum dia rodar hard delete.
UPDATE carrossel.anuncio
SET deleted_at = SYSUTCDATETIME(),
    status = 'cancelado',
    updated_at = SYSUTCDATETIME()
WHERE id = @anuncio_id
  AND tenant_id = @tenant_id
  AND deleted_at IS NULL;
```

### 5.8 Historico unificado (RN-014)

O historico e consultado na tabela existente `carrossel.historico` (ja aceita `formato='anuncio'`). Nao ha tabela separada de historico de anuncios. A query padrao do historico unificado ja funciona sem alteracao:

```sql
SELECT id, titulo, formato, status, final_score, criado_em, google_drive_link
FROM carrossel.historico
WHERE tenant_id = @tenant_id
  AND deleted_at IS NULL
  AND (@formato_filtro IS NULL OR formato = @formato_filtro)
ORDER BY criado_em DESC;
```

Obs: a insercao no `historico` continua sendo feita pelo handler de "conteudo concluido" ja existente -- basta o `anuncio_service` chamar `historico_repository.create()` no final do pipeline com `formato='anuncio'`.

### 5.9 Agregacao para o card do Kanban (RN-021)

O Kanban usa MongoDB (`kanban_cards`). O card do Kanban aponta para `pipeline_id`. Para buscar o anuncio de um card:

```sql
SELECT a.id, a.titulo, a.status, a.headline, a.descricao,
       (SELECT imagem_url FROM carrossel.anuncio_dimensao WHERE anuncio_id = a.id AND ordem = 1) AS thumb
FROM carrossel.anuncio a
WHERE a.tenant_id = @tenant_id
  AND a.pipeline_id = @pipeline_id
  AND a.deleted_at IS NULL;
```

---

## 6. Decisao sobre MongoDB

### 6.1 Avaliacao
Foram consideradas 3 possiveis coletas para Mongo:

| Candidato | Justificativa | Decisao |
|-----------|---------------|---------|
| Historico de regeneracao por dimensao | Cada anuncio gera ~4-12 eventos de geracao/brand gate. Append-only, polimorfico | **NAO** -- o `pipeline_step` ja loga tudo em MSSQL (`entrada`/`saida` JSON). Duplicar no Mongo so criaria 2 fontes de verdade |
| Cache de prompts por dimensao | Art Director gera 1 prompt base + 4 adaptacoes. Tamanho medio 2-5 KB | **NAO** -- cabe em `pipeline_step.entrada` (NVARCHAR(MAX)) |
| Brand Gate feedback estruturado | JSON com regras violadas, scores por regra | **NAO** -- cabe em `anuncio_dimensao.brand_gate_feedback` (NVARCHAR(MAX)) |

### 6.2 Conclusao -- somente SQL
O modulo Anuncios usa **apenas MSSQL**. Motivos:

1. Todas as entidades tem estado bem definido e relacional (anuncio 1:N dimensoes 1:1 pipeline).
2. Logs de execucao ja sao capturados pela tabela `pipeline_step` existente.
3. Nao ha alta volumetria que justifique NoSQL (estimativa: <1000 anuncios/mes por tenant).
4. Manter 1 banco por modulo reduz complexidade operacional.
5. O Kanban usa Mongo por motivos diferentes (documentos com colunas aninhadas, audit log append-only, TTL de convites) -- nada disso se aplica a Anuncios.

**Se no futuro precisar:** cache de imagens geradas com dedup por prompt hash (para reaproveitamento), ou telemetria detalhada do Content Critic/Brand Gate, sera reavaliado. Por enquanto, **SQL puro**.

---

## 7. Script de migration completo (pronto para rodar)

### 7.1 Arquivo: `backend/db/sql/anuncios_migration.sql`

```sql
-- ============================================================================
-- MIGRATION: Modulo Anuncios (Google Ads Display)
-- Autor: Agente 07 (Arquiteto SQL + MongoDB)
-- Base: PRD Anuncios + Arquitetura Backend Anuncios
-- ============================================================================
-- Idempotente: pode ser executado multiplas vezes sem efeitos colaterais.
-- Dependencia: schema 'carrossel' e tabela 'carrossel.pipeline' devem existir.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1. PRE-REQUISITOS (verifica dependencias antes de prosseguir)
-- ---------------------------------------------------------------------------

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'carrossel')
BEGIN
    RAISERROR('Schema "carrossel" nao existe. Execute 000_init.sql primeiro.', 16, 1);
    RETURN;
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'pipeline')
BEGIN
    RAISERROR('Tabela "carrossel.pipeline" nao existe. Execute 001_pipeline.sql primeiro.', 16, 1);
    RETURN;
END
GO

-- ---------------------------------------------------------------------------
-- 2. GARANTIR que carrossel.pipeline aceita formato='anuncio'
-- (Reaplica CHECK constraint se necessario.)
-- ---------------------------------------------------------------------------

-- Verifica se ja existe CK com 'anuncio' ou precisa recriar
IF EXISTS (
    SELECT 1 FROM sys.check_constraints cc
    INNER JOIN sys.objects o ON o.object_id = cc.parent_object_id
    WHERE cc.name = 'CK_pipeline_formato'
      AND o.name = 'pipeline'
      AND cc.definition NOT LIKE '%anuncio%'
)
BEGIN
    ALTER TABLE carrossel.pipeline DROP CONSTRAINT CK_pipeline_formato;
    ALTER TABLE carrossel.pipeline
        ADD CONSTRAINT CK_pipeline_formato CHECK (
            formato IN ('carrossel', 'post_unico', 'thumbnail_youtube', 'capa_reels', 'anuncio')
        );
END
GO

-- Mesmo para carrossel.conteudo (se a tabela existir)
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA='carrossel' AND TABLE_NAME='conteudo')
AND EXISTS (
    SELECT 1 FROM sys.check_constraints cc
    INNER JOIN sys.objects o ON o.object_id = cc.parent_object_id
    WHERE cc.name = 'CK_conteudo_formato'
      AND o.name = 'conteudo'
      AND cc.definition NOT LIKE '%anuncio%'
)
BEGIN
    ALTER TABLE carrossel.conteudo DROP CONSTRAINT CK_conteudo_formato;
    ALTER TABLE carrossel.conteudo
        ADD CONSTRAINT CK_conteudo_formato CHECK (
            formato IN ('carrossel', 'post_unico', 'thumbnail_youtube', 'capa_reels', 'anuncio')
        );
END
GO

-- ---------------------------------------------------------------------------
-- 3. CRIAR TABELA carrossel.anuncio
-- ---------------------------------------------------------------------------

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'anuncio')
BEGIN
    CREATE TABLE carrossel.anuncio (
        id                     UNIQUEIDENTIFIER    NOT NULL DEFAULT NEWID(),
        tenant_id              VARCHAR(50)         NOT NULL,
        pipeline_id            UNIQUEIDENTIFIER    NULL,
        pipeline_funil_id      UNIQUEIDENTIFIER    NULL,
        titulo                 NVARCHAR(200)       NOT NULL,
        etapa_funil            VARCHAR(20)         NULL,
        tema_ou_briefing       NVARCHAR(MAX)       NULL,
        modo_entrada           VARCHAR(20)         NULL,
        disciplina             VARCHAR(50)         NULL,
        tecnologia             VARCHAR(100)        NULL,
        foto_criador_id        VARCHAR(100)        NULL,
        criado_por             VARCHAR(100)        NULL,
        headline               NVARCHAR(30)        NULL,
        descricao              NVARCHAR(90)        NULL,
        status                 VARCHAR(20)         NOT NULL DEFAULT 'rascunho',
        drive_folder_id        VARCHAR(100)        NULL,
        drive_folder_link      NVARCHAR(MAX)       NULL,
        last_exported_at       DATETIME2           NULL,
        created_at             DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at             DATETIME2           NULL,
        deleted_at             DATETIME2           NULL,

        CONSTRAINT PK_anuncio PRIMARY KEY (id),
        CONSTRAINT FK_anuncio_pipeline FOREIGN KEY (pipeline_id)
            REFERENCES carrossel.pipeline(id) ON DELETE SET NULL,
        CONSTRAINT CK_anuncio_status CHECK (status IN (
            'rascunho', 'gerando', 'completo', 'parcial', 'erro', 'cancelado'
        )),
        CONSTRAINT CK_anuncio_etapa_funil CHECK (etapa_funil IS NULL OR etapa_funil IN (
            'topo', 'meio', 'fundo', 'avulso'
        )),
        CONSTRAINT CK_anuncio_modo_entrada CHECK (modo_entrada IS NULL OR modo_entrada IN (
            'texto', 'disciplina'
        ))
    );
END
GO

-- ---------------------------------------------------------------------------
-- 4. CRIAR TABELA carrossel.anuncio_dimensao
-- ---------------------------------------------------------------------------

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'anuncio_dimensao')
BEGIN
    CREATE TABLE carrossel.anuncio_dimensao (
        id                     UNIQUEIDENTIFIER    NOT NULL DEFAULT NEWID(),
        anuncio_id             UNIQUEIDENTIFIER    NOT NULL,
        dimensao_id            VARCHAR(20)         NOT NULL,
        ordem                  INT                 NOT NULL,
        largura                INT                 NOT NULL,
        altura                 INT                 NOT NULL,
        modelo_usado           VARCHAR(50)         NULL,
        overlay_aplicado       VARCHAR(20)         NOT NULL DEFAULT 'foto+logo',
        imagem_url             NVARCHAR(MAX)       NULL,
        imagem_base64          NVARCHAR(MAX)       NULL,
        brand_gate_status      VARCHAR(20)         NOT NULL DEFAULT 'nao_gerada',
        brand_gate_retries     INT                 NOT NULL DEFAULT 0,
        brand_gate_feedback    NVARCHAR(MAX)       NULL,
        created_at             DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
        gerada_em              DATETIME2           NULL,
        updated_at             DATETIME2           NULL,

        CONSTRAINT PK_anuncio_dimensao PRIMARY KEY (id),
        CONSTRAINT FK_anuncio_dimensao_anuncio FOREIGN KEY (anuncio_id)
            REFERENCES carrossel.anuncio(id) ON DELETE CASCADE,
        CONSTRAINT UQ_anuncio_dimensao_unica UNIQUE (anuncio_id, dimensao_id),
        CONSTRAINT CK_anuncio_dimensao_dim CHECK (dimensao_id IN (
            '1200x628', '1080x1080', '300x600', '300x250'
        )),
        CONSTRAINT CK_anuncio_dimensao_overlay CHECK (overlay_aplicado IN (
            'foto+logo', 'so_logo'
        )),
        CONSTRAINT CK_anuncio_dimensao_brand_gate CHECK (brand_gate_status IN (
            'nao_gerada', 'gerando', 'valido', 'revisao_manual', 'falhou'
        )),
        CONSTRAINT CK_anuncio_dimensao_retries CHECK (brand_gate_retries BETWEEN 0 AND 2),
        CONSTRAINT CK_anuncio_dimensao_ordem CHECK (ordem BETWEEN 0 AND 3)
    );
END
GO

-- ---------------------------------------------------------------------------
-- 5. INDICES DA TABELA anuncio
-- ---------------------------------------------------------------------------

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_tenant_status_created')
    CREATE INDEX IX_anuncio_tenant_status_created
    ON carrossel.anuncio (tenant_id, status, created_at DESC)
    WHERE deleted_at IS NULL;
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_tenant_etapa')
    CREATE INDEX IX_anuncio_tenant_etapa
    ON carrossel.anuncio (tenant_id, etapa_funil)
    WHERE deleted_at IS NULL;
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_tenant_titulo')
    CREATE INDEX IX_anuncio_tenant_titulo
    ON carrossel.anuncio (tenant_id, titulo)
    WHERE deleted_at IS NULL;
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_tenant_pipeline')
    CREATE INDEX IX_anuncio_tenant_pipeline
    ON carrossel.anuncio (tenant_id, pipeline_id)
    WHERE pipeline_id IS NOT NULL AND deleted_at IS NULL;
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_tenant_funil')
    CREATE INDEX IX_anuncio_tenant_funil
    ON carrossel.anuncio (tenant_id, pipeline_funil_id)
    WHERE pipeline_funil_id IS NOT NULL AND deleted_at IS NULL;
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_tenant_criadopor_created')
    CREATE INDEX IX_anuncio_tenant_criadopor_created
    ON carrossel.anuncio (tenant_id, criado_por, created_at DESC)
    WHERE deleted_at IS NULL;
GO

-- ---------------------------------------------------------------------------
-- 6. INDICES DA TABELA anuncio_dimensao
-- ---------------------------------------------------------------------------

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_dim_anuncio_ordem')
    CREATE INDEX IX_anuncio_dim_anuncio_ordem
    ON carrossel.anuncio_dimensao (anuncio_id, ordem);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_dim_anuncio_brand_gate')
    CREATE INDEX IX_anuncio_dim_anuncio_brand_gate
    ON carrossel.anuncio_dimensao (anuncio_id, brand_gate_status);
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_dim_gerando')
    CREATE INDEX IX_anuncio_dim_gerando
    ON carrossel.anuncio_dimensao (brand_gate_status, created_at)
    WHERE brand_gate_status = 'gerando';
GO

-- ---------------------------------------------------------------------------
-- 7. VALIDACAO FINAL
-- ---------------------------------------------------------------------------

DECLARE @msg NVARCHAR(500);
SET @msg = 'Migration Anuncios OK -- tabelas: ' +
    CAST((SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
          WHERE TABLE_SCHEMA='carrossel' AND TABLE_NAME IN ('anuncio','anuncio_dimensao')) AS VARCHAR) +
    '/2, indices: ' +
    CAST((SELECT COUNT(*) FROM sys.indexes WHERE name LIKE 'IX_anuncio%') AS VARCHAR);
PRINT @msg;
GO
```

### 7.2 Organizacao em arquivos separados (padrao BANCO.md)

Segue a mesma nomenclatura numerica do projeto:

```text
backend/db/sql/
  tables/
    008_anuncio.sql              # corpo da tabela principal
    009_anuncio_dimensao.sql     # corpo da tabela filha
  indexes/
    808_anuncio_indexes.sql      # indices da tabela principal
    809_anuncio_dimensao_indexes.sql # indices da filha
  alters/
    008a_pipeline_checks.sql     # garante 'anuncio' no CHECK do pipeline/conteudo
  run/
    run_sql_order.txt            # atualizar com os novos arquivos
```

### 7.3 Atualizacao do `run_sql_order.txt`

```
# Ordem de execucao -- modulo Anuncios (incremento ao BANCO.md existente)

# Ja executados previamente:
# 000_init.sql, 001_pipeline.sql, 002_pipeline_step.sql, 003_conteudo.sql,
# 004_imagem.sql, 005_score.sql, 006_visual_preference.sql, 007_historico_alter.sql

# Novos para modulo Anuncios:
008a_pipeline_checks.sql
008_anuncio.sql
009_anuncio_dimensao.sql
808_anuncio_indexes.sql
809_anuncio_dimensao_indexes.sql
```

---

## 8. Impactos em tabelas existentes

### 8.1 `carrossel.pipeline` -- CHECK constraint
Ja foi atualizado no BANCO.md v3 atual para aceitar `'anuncio'` (ver linha 133 de `BANCO.md`). **Verificar se o script ja rodou em producao.** Caso nao, o script `008a_pipeline_checks.sql` da secao 7.1 garante idempotentemente.

### 8.2 `carrossel.conteudo` -- CHECK constraint
Mesma situacao do `pipeline`. Valor `'anuncio'` ja listado no CHECK do BANCO.md atual (linha 214). Script `008a` cobre.

### 8.3 `carrossel.historico` -- sem alteracao
Coluna `formato VARCHAR(50)` ja aceita qualquer string (nao tem CHECK). Anuncios entram no historico unificado sem DDL adicional. O `anuncio_service` insere registro ao finalizar pipeline.

### 8.4 `carrossel.imagem` -- nao sera usada para anuncios
Decisao: **nao reutilizar** a tabela `imagem` para anuncios. Motivos:
- `imagem` foi desenhada para carrossel (slide_index 1..10, variacao 1..3). O modelo nao casa (dimensao nao cabe em `slide_index`).
- Duplicar logica de brand gate entre `imagem` e `anuncio_dimensao` seria pior que ter a coluna propria na dimensao.
- Se um dia precisar unificar, criar view `vw_imagens_todas` no futuro.

### 8.5 Mongo `kanban_cards`
Cards de Kanban armazenam `pipeline_id` (ja existe, ver `scripts-mongodb-kanban.md`). Para recuperar o anuncio de um card, faz-se JOIN logico no app: Mongo -> pipeline_id -> `carrossel.anuncio` WHERE pipeline_id=X. **Nenhuma alteracao no schema Mongo** do Kanban e necessaria.

---

## 9. Duvidas em aberto

Nenhuma duvida de modelagem em aberto. Todas as decisoes ja foram tomadas no PRD (DA-001 a DA-010) ou no Agente 03 (AR-01).

Duvidas possiveis que **nao bloqueiam** a migration, mas podem ser revisitadas no futuro:

1. **Retencao de `imagem_base64` apos upload pro Drive**: atualmente a coluna existe para cache pre-upload. Apos upload bem sucedido, o Drive tem a fonte da verdade. Recomendacao do Arquiteto SQL: `AnuncioRepository` deve limpar (`SET imagem_base64 = NULL`) apos upload. Decisao final fica com o Dev Backend.

2. **Indice FULLTEXT em `titulo`**: hoje a busca usa `LIKE '%x%'` (scan). Se a base crescer >10k anuncios por tenant, avaliar `CREATE FULLTEXT INDEX`. Fora do MVP.

3. **Tabela de audit_log para regeneracoes**: cada regen individual (RN-018) hoje e rastreavel via `pipeline_step` (criado novo step). Se o Funil precisar de visao agregada das regeneracoes, considerar tabela `anuncio_regeneracao_log` futuramente.

---

## 10. Compatibilidade com SQLAlchemy Models

| Model Python (Agente 03) | Tabela SQL | Compativel |
|--------------------------|-----------|-----------|
| `AnuncioModel(TenantMixin, Base)` | `carrossel.anuncio` | Sim |
| `AnuncioDimensaoModel(Base)` -- sem TenantMixin | `carrossel.anuncio_dimensao` | Sim |

Tipos mapeados (mesmo padrao do BANCO.md secao 9):
- `Column(String(N))` -> `VARCHAR(N)` / `NVARCHAR(N)`
- `Column(Text)` -> `NVARCHAR(MAX)`
- `Column(UNIQUEIDENTIFIER)` -> `UNIQUEIDENTIFIER`
- `Column(DateTime)` -> `DATETIME2`
- `Column(Integer)` -> `INT`
- `ForeignKey(... ondelete="SET NULL")` -> `ON DELETE SET NULL`
- `ForeignKey(... ondelete="CASCADE")` -> `ON DELETE CASCADE`

O ORM usa `relationship("AnuncioDimensaoModel", back_populates="anuncio", cascade="all, delete-orphan", order_by="ordem")` para carregar as 4 dimensoes em 1 call (selectin loading). Nao e necessaria nenhuma view.

---

## 11. Resumo executivo -- checklist para o Dev Backend

- [ ] Rodar `008a_pipeline_checks.sql` (garantir formato='anuncio' nos CHECKs existentes)
- [ ] Rodar `008_anuncio.sql` (criar tabela principal)
- [ ] Rodar `009_anuncio_dimensao.sql` (criar tabela filha)
- [ ] Rodar `808_anuncio_indexes.sql`
- [ ] Rodar `809_anuncio_dimensao_indexes.sql`
- [ ] Validar com: `SELECT COUNT(*) FROM carrossel.anuncio` e `SELECT COUNT(*) FROM carrossel.anuncio_dimensao` (devem retornar 0)
- [ ] Confirmar FK: tentar deletar um pipeline que tenha anuncio vinculado e verificar que o anuncio persiste com `pipeline_id = NULL`
- [ ] Confirmar CASCADE: deletar um anuncio e verificar que as 4 dimensoes sao removidas fisicamente (use hard delete em ambiente de teste)

---

*Documento gerado pelo Agente 07 (Arquiteto SQL + MongoDB) da esteira IT Valley.*
*Entrada: `docs/prd-anuncios.md` + `docs/arquitetura-backend-anuncios.md` + `docs/BANCO.md`.*
*Proximo: Agente 08 (P.O. / Gerente de Projetos) + Agente 10 (Dev Backend).*
