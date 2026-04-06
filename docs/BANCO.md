# BANCO DE DADOS -- Content Factory v3

Documento de modelagem SQL (MSSQL) gerado pelo Agente 07 (Arquiteto SQL + MongoDB).
Base: ARQUITETURA_BACKEND.md (models SQLAlchemy) + PRD.md + db_service.py existente.

---

## 1. Visao Geral

| Item | Valor |
|------|-------|
| SGBD | Microsoft SQL Server (MSSQL) |
| Schema | `carrossel` |
| Conexao existente | `backend/services/db_service.py` (pymssql, MSSQL_URL) |
| Tabela existente | `carrossel.historico` (sera alterada, nao recriada) |
| Multitenancia | Preparada (tenant_id em toda tabela e toda query) |
| Soft delete | `deleted_at` em todas as tabelas |
| IDs | UNIQUEIDENTIFIER (UUID v4) |

### Decisao: somente SQL

O projeto usa MSSQL como banco unico. Nao ha necessidade de MongoDB neste momento:
- Logs de pipeline ficam em `pipeline_step` (entrada/saida como TEXT/JSON).
- Historico fica em tabela SQL (ja existe).
- Preferencias visuais ficam em `visual_preference` com campo `contexto` TEXT (JSON).
- Configs (brand_palette, creator_registry, platform_rules) ficam em arquivos JSON no disco (`backend/configs/`), conforme definido no PRD (RN-014: "Configs sao JSON puro, sem logica de negocio").

Se no futuro houver necessidade de colecoes MongoDB (ex: logs de alta volumetria, cache do trend_scanner), o Agente 07 sera re-executado.

---

## 2. Mapa de Entidades e Tabelas

| Entidade (PRD) | Tabela SQL | Status |
|----------------|-----------|--------|
| Pipeline | `carrossel.pipeline` | Nova |
| PipelineStep | `carrossel.pipeline_step` | Nova |
| Conteudo | `carrossel.conteudo` | Nova |
| Imagem | `carrossel.imagem` | Nova |
| Score | `carrossel.score` | Nova |
| VisualPreference | `carrossel.visual_preference` | Nova |
| Historico | `carrossel.historico` | Existente (alterar) |

### Entidades que NAO viram tabela

| Entidade (PRD) | Motivo | Onde fica |
|----------------|--------|-----------|
| CreatorEntry | Config JSON puro (RN-014) | `backend/configs/creator_registry.json` |
| BrandPalette | Config JSON puro (RN-014) | `backend/configs/brand_palette.json` |
| PlatformRules | Config JSON puro (RN-014) | `backend/configs/platform_rules.json` |
| Dimensions | Config JSON puro (RN-014) | `backend/configs/dimensions.json` |
| Templates | Config JSON puro (RN-014) | `backend/configs/templates.json` |

---

## 3. Dependencias entre Tabelas

```
carrossel.pipeline
    |
    +--- carrossel.pipeline_step  (FK: pipeline_id -> pipeline.id)
    |
    +--- carrossel.conteudo       (FK: pipeline_id -> pipeline.id, nullable)
              |
              +--- carrossel.imagem  (FK: conteudo_id -> conteudo.id)
              |
              +--- carrossel.score   (FK: conteudo_id -> conteudo.id)

carrossel.visual_preference       (sem FK, independente)

carrossel.historico               (sem FK, independente, ja existe)
```

**Ordem de criacao obrigatoria:**
1. Schema `carrossel` (se nao existir)
2. `pipeline` (sem dependencias)
3. `pipeline_step` (depende de pipeline)
4. `conteudo` (depende de pipeline)
5. `imagem` (depende de conteudo)
6. `score` (depende de conteudo)
7. `visual_preference` (independente)
8. `historico` (ALTER, ja existe)

---

## 4. Scripts SQL

### 4.1 Inicializacao do Schema

```sql
-- 000_init.sql
-- Cria schema carrossel se nao existir.
-- Executar primeiro, antes de qualquer tabela.

IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'carrossel')
BEGIN
    EXEC('CREATE SCHEMA carrossel')
END
GO
```

---

### 4.2 Tabela: pipeline

```sql
-- 001_pipeline.sql
-- Tabela principal do pipeline de geracao de conteudo.
-- Cada execucao do pipeline (tema + formato) gera 1 registro.
-- Dependencias: nenhuma (tabela raiz).

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'pipeline')
BEGIN
    CREATE TABLE carrossel.pipeline (
        id                  UNIQUEIDENTIFIER    NOT NULL DEFAULT NEWID(),
        tenant_id           VARCHAR(50)         NOT NULL,
        tema                NVARCHAR(MAX)       NOT NULL,
        formato             VARCHAR(50)         NOT NULL,       -- carrossel, post_unico, thumbnail_youtube
        modo_funil          BIT                 NOT NULL DEFAULT 0,
        status              VARCHAR(30)         NOT NULL DEFAULT 'pendente',
        -- Status possiveis: pendente, em_execucao, aguardando_aprovacao, completo, cancelado, erro
        etapa_atual         VARCHAR(50)         NULL,
        modo_entrada        VARCHAR(20)         NULL,           -- texto, disciplina
        disciplina          VARCHAR(50)         NULL,
        tecnologia          VARCHAR(100)        NULL,
        foto_criador        NVARCHAR(MAX)       NULL,           -- URL ou base64

        created_at          DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at          DATETIME2           NULL,
        deleted_at          DATETIME2           NULL,

        CONSTRAINT PK_pipeline PRIMARY KEY (id),
        CONSTRAINT CK_pipeline_formato CHECK (formato IN ('carrossel', 'post_unico', 'thumbnail_youtube', 'capa_reels', 'anuncio')),
        CONSTRAINT CK_pipeline_status CHECK (status IN ('pendente', 'em_execucao', 'aguardando_aprovacao', 'completo', 'cancelado', 'erro')),
        CONSTRAINT CK_pipeline_modo_entrada CHECK (modo_entrada IS NULL OR modo_entrada IN ('texto', 'disciplina'))
    );
END
GO
```

---

### 4.3 Tabela: pipeline_step

```sql
-- 002_pipeline_step.sql
-- Cada etapa do pipeline (1 por agente/skill executado).
-- Dependencias: carrossel.pipeline (FK pipeline_id).

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'pipeline_step')
BEGIN
    CREATE TABLE carrossel.pipeline_step (
        id                  UNIQUEIDENTIFIER    NOT NULL DEFAULT NEWID(),
        pipeline_id         UNIQUEIDENTIFIER    NOT NULL,
        agente              VARCHAR(50)         NOT NULL,
        -- Agentes: strategist, copywriter, hook_specialist, art_director,
        --          image_generator, brand_gate, content_critic
        ordem               INT                 NOT NULL,
        entrada             NVARCHAR(MAX)       NULL,           -- JSON serializado
        saida               NVARCHAR(MAX)       NULL,           -- JSON serializado
        status              VARCHAR(30)         NOT NULL DEFAULT 'pendente',
        -- Status: pendente, em_execucao, aguardando_aprovacao, aprovado, rejeitado, erro
        erro_mensagem       NVARCHAR(MAX)       NULL,
        aprovado_por        VARCHAR(100)        NULL,
        approved_at         DATETIME2           NULL,
        started_at          DATETIME2           NULL,
        finished_at         DATETIME2           NULL,

        created_at          DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),

        CONSTRAINT PK_pipeline_step PRIMARY KEY (id),
        CONSTRAINT FK_pipeline_step_pipeline FOREIGN KEY (pipeline_id)
            REFERENCES carrossel.pipeline(id) ON DELETE CASCADE,
        CONSTRAINT CK_pipeline_step_status CHECK (status IN ('pendente', 'em_execucao', 'aguardando_aprovacao', 'aprovado', 'rejeitado', 'erro'))
    );
END
GO
```

---

### 4.4 Tabela: conteudo

```sql
-- 003_conteudo.sql
-- Conteudo final gerado (texto + metadados).
-- Um pipeline pode gerar 1 conteudo. Conteudos legados podem nao ter pipeline_id.
-- Dependencias: carrossel.pipeline (FK pipeline_id, nullable).

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'conteudo')
BEGIN
    CREATE TABLE carrossel.conteudo (
        id                      UNIQUEIDENTIFIER    NOT NULL DEFAULT NEWID(),
        tenant_id               VARCHAR(50)         NOT NULL,
        pipeline_id             UNIQUEIDENTIFIER    NULL,           -- NULL para conteudos legados
        formato                 VARCHAR(50)         NOT NULL,       -- carrossel, post_unico, thumbnail_youtube
        titulo                  NVARCHAR(500)       NOT NULL,
        headline                NVARCHAR(MAX)       NULL,
        narrativa               NVARCHAR(MAX)       NULL,
        hook                    NVARCHAR(MAX)       NULL,
        cta                     NVARCHAR(MAX)       NULL,
        copy_completa           NVARCHAR(MAX)       NULL,           -- JSON com sequencia de slides
        legenda_linkedin        NVARCHAR(MAX)       NULL,
        disciplina              VARCHAR(50)         NULL,
        tecnologia_principal    VARCHAR(100)        NULL,

        created_at              DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at              DATETIME2           NULL,
        deleted_at              DATETIME2           NULL,

        CONSTRAINT PK_conteudo PRIMARY KEY (id),
        CONSTRAINT FK_conteudo_pipeline FOREIGN KEY (pipeline_id)
            REFERENCES carrossel.pipeline(id) ON DELETE SET NULL,
        CONSTRAINT CK_conteudo_formato CHECK (formato IN ('carrossel', 'post_unico', 'thumbnail_youtube', 'capa_reels', 'anuncio'))
    );
END
GO
```

---

### 4.5 Tabela: imagem

```sql
-- 004_imagem.sql
-- Imagem gerada por slide/campo. Cada conteudo pode ter N imagens (slides x variacoes).
-- Dependencias: carrossel.conteudo (FK conteudo_id).

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'imagem')
BEGIN
    CREATE TABLE carrossel.imagem (
        id                      UNIQUEIDENTIFIER    NOT NULL DEFAULT NEWID(),
        tenant_id               VARCHAR(50)         NOT NULL,
        conteudo_id             UNIQUEIDENTIFIER    NOT NULL,
        slide_index             INT                 NOT NULL,
        variacao                INT                 NOT NULL,       -- 1, 2 ou 3
        url_drive               NVARCHAR(MAX)       NULL,
        image_base64            NVARCHAR(MAX)       NULL,
        modelo_gemini           VARCHAR(50)         NULL,           -- gemini-3-pro, gemini-2.5-flash
        brand_gate_status       VARCHAR(30)         NULL,           -- valido, invalido, revisao_manual
        brand_gate_retries      INT                 NOT NULL DEFAULT 0,
        selecionada             BIT                 NOT NULL DEFAULT 0,

        created_at              DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at              DATETIME2           NULL,
        deleted_at              DATETIME2           NULL,

        CONSTRAINT PK_imagem PRIMARY KEY (id),
        CONSTRAINT FK_imagem_conteudo FOREIGN KEY (conteudo_id)
            REFERENCES carrossel.conteudo(id) ON DELETE CASCADE,
        CONSTRAINT CK_imagem_variacao CHECK (variacao BETWEEN 1 AND 3),
        CONSTRAINT CK_imagem_brand_gate CHECK (brand_gate_status IS NULL OR brand_gate_status IN ('valido', 'invalido', 'revisao_manual'))
    );
END
GO
```

---

### 4.6 Tabela: score

```sql
-- 005_score.sql
-- Score do Content Critic. 1 score por conteudo.
-- Dependencias: carrossel.conteudo (FK conteudo_id).

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'score')
BEGIN
    CREATE TABLE carrossel.score (
        id                  UNIQUEIDENTIFIER    NOT NULL DEFAULT NEWID(),
        tenant_id           VARCHAR(50)         NOT NULL,
        conteudo_id         UNIQUEIDENTIFIER    NOT NULL,
        clarity             FLOAT               NOT NULL,
        impact              FLOAT               NOT NULL,
        originality         FLOAT               NOT NULL,
        scroll_stop         FLOAT               NOT NULL,
        cta_strength        FLOAT               NOT NULL,
        final_score         FLOAT               NOT NULL,
        decision            VARCHAR(30)         NOT NULL,       -- approved, needs_revision
        best_variation      VARCHAR(10)         NULL,
        feedback            NVARCHAR(MAX)       NULL,

        created_at          DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at          DATETIME2           NULL,
        deleted_at          DATETIME2           NULL,

        CONSTRAINT PK_score PRIMARY KEY (id),
        CONSTRAINT FK_score_conteudo FOREIGN KEY (conteudo_id)
            REFERENCES carrossel.conteudo(id) ON DELETE CASCADE,
        CONSTRAINT CK_score_decision CHECK (decision IN ('approved', 'needs_revision')),
        CONSTRAINT CK_score_final_range CHECK (final_score BETWEEN 0 AND 10)
    );
END
GO
```

---

### 4.7 Tabela: visual_preference

```sql
-- 006_visual_preference.sql
-- Preferencias visuais do usuario. Alimenta o Art Director em futuras geracoes.
-- Dependencias: nenhuma (tabela independente).

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'visual_preference')
BEGIN
    CREATE TABLE carrossel.visual_preference (
        id                  UNIQUEIDENTIFIER    NOT NULL DEFAULT NEWID(),
        tenant_id           VARCHAR(50)         NOT NULL,
        estilo              NVARCHAR(200)       NOT NULL,       -- descricao do estilo
        aprovado            BIT                 NOT NULL,       -- 1 = aprovado, 0 = rejeitado
        contexto            NVARCHAR(MAX)       NULL,           -- JSON: formato, tema, agente, etc.

        created_at          DATETIME2           NOT NULL DEFAULT SYSUTCDATETIME(),
        updated_at          DATETIME2           NULL,
        deleted_at          DATETIME2           NULL,

        CONSTRAINT PK_visual_preference PRIMARY KEY (id)
    );
END
GO
```

---

### 4.8 Tabela: historico (ALTER -- ja existe)

```sql
-- 007_historico_alter.sql
-- A tabela carrossel.historico JA EXISTE no banco.
-- Colunas existentes: id, titulo, disciplina, tecnologia_principal, tipo_carrossel,
--                     total_slides, legenda_linkedin, google_drive_link,
--                     google_drive_folder_name, criado_em
-- Este script adiciona colunas da v3 sem destruir dados existentes.
-- Dependencias: nenhuma.

-- Adicionar tenant_id (obrigatorio IT Valley)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'historico' AND COLUMN_NAME = 'tenant_id')
BEGIN
    ALTER TABLE carrossel.historico ADD tenant_id VARCHAR(50) NOT NULL DEFAULT 'itvalley';
END
GO

-- Adicionar formato (v3: multi-formato)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'historico' AND COLUMN_NAME = 'formato')
BEGIN
    ALTER TABLE carrossel.historico ADD formato VARCHAR(50) NULL DEFAULT 'carrossel';
END
GO

-- Adicionar status
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'historico' AND COLUMN_NAME = 'status')
BEGIN
    ALTER TABLE carrossel.historico ADD status VARCHAR(30) NULL DEFAULT 'completo';
END
GO

-- Adicionar final_score (score do Content Critic)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'historico' AND COLUMN_NAME = 'final_score')
BEGIN
    ALTER TABLE carrossel.historico ADD final_score FLOAT NULL;
END
GO

-- Adicionar pipeline_id (referencia ao pipeline v3)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'historico' AND COLUMN_NAME = 'pipeline_id')
BEGIN
    ALTER TABLE carrossel.historico ADD pipeline_id VARCHAR(36) NULL;
END
GO

-- Adicionar updated_at
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'historico' AND COLUMN_NAME = 'updated_at')
BEGIN
    ALTER TABLE carrossel.historico ADD updated_at DATETIME2 NULL;
END
GO

-- Adicionar deleted_at (soft delete)
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'historico' AND COLUMN_NAME = 'deleted_at')
BEGIN
    ALTER TABLE carrossel.historico ADD deleted_at DATETIME2 NULL;
END
GO
```

---

## 5. Indices

### 5.1 Indices da tabela pipeline

```sql
-- 801_pipeline_indexes.sql
-- Todos os indices consideram isolamento por tenant_id.

-- Busca por tenant + status (listar pipelines ativos)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_pipeline_tenant_status')
    CREATE INDEX IX_pipeline_tenant_status
    ON carrossel.pipeline (tenant_id, status)
    WHERE deleted_at IS NULL;
GO

-- Busca por tenant + formato (filtrar por tipo de conteudo)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_pipeline_tenant_formato')
    CREATE INDEX IX_pipeline_tenant_formato
    ON carrossel.pipeline (tenant_id, formato)
    WHERE deleted_at IS NULL;
GO

-- Listagem ordenada por data (mais recentes primeiro)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_pipeline_tenant_created')
    CREATE INDEX IX_pipeline_tenant_created
    ON carrossel.pipeline (tenant_id, created_at DESC)
    WHERE deleted_at IS NULL;
GO
```

### 5.2 Indices da tabela pipeline_step

```sql
-- 802_pipeline_step_indexes.sql

-- Busca de etapas por pipeline (sempre consultadas juntas)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_pipeline_step_pipeline_ordem')
    CREATE INDEX IX_pipeline_step_pipeline_ordem
    ON carrossel.pipeline_step (pipeline_id, ordem);
GO

-- Busca de etapas aguardando aprovacao
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_pipeline_step_status')
    CREATE INDEX IX_pipeline_step_status
    ON carrossel.pipeline_step (status)
    WHERE status = 'aguardando_aprovacao';
GO
```

### 5.3 Indices da tabela conteudo

```sql
-- 803_conteudo_indexes.sql

-- Busca por tenant + formato
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_conteudo_tenant_formato')
    CREATE INDEX IX_conteudo_tenant_formato
    ON carrossel.conteudo (tenant_id, formato)
    WHERE deleted_at IS NULL;
GO

-- Busca por pipeline_id
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_conteudo_pipeline')
    CREATE INDEX IX_conteudo_pipeline
    ON carrossel.conteudo (pipeline_id)
    WHERE pipeline_id IS NOT NULL;
GO

-- Listagem por data
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_conteudo_tenant_created')
    CREATE INDEX IX_conteudo_tenant_created
    ON carrossel.conteudo (tenant_id, created_at DESC)
    WHERE deleted_at IS NULL;
GO
```

### 5.4 Indices da tabela imagem

```sql
-- 804_imagem_indexes.sql

-- Busca de imagens por conteudo (sempre consultadas juntas)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_imagem_conteudo')
    CREATE INDEX IX_imagem_conteudo
    ON carrossel.imagem (conteudo_id, slide_index, variacao)
    WHERE deleted_at IS NULL;
GO

-- Filtrar imagens selecionadas
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_imagem_selecionada')
    CREATE INDEX IX_imagem_selecionada
    ON carrossel.imagem (conteudo_id)
    WHERE selecionada = 1 AND deleted_at IS NULL;
GO
```

### 5.5 Indices da tabela score

```sql
-- 805_score_indexes.sql

-- Busca de score por conteudo (1:1)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_score_conteudo')
    CREATE UNIQUE INDEX IX_score_conteudo
    ON carrossel.score (conteudo_id)
    WHERE deleted_at IS NULL;
GO

-- Busca por tenant + final_score (ranking de qualidade)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_score_tenant_final')
    CREATE INDEX IX_score_tenant_final
    ON carrossel.score (tenant_id, final_score DESC)
    WHERE deleted_at IS NULL;
GO
```

### 5.6 Indices da tabela visual_preference

```sql
-- 806_visual_preference_indexes.sql

-- Busca por tenant (listar preferencias do usuario)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_visual_preference_tenant')
    CREATE INDEX IX_visual_preference_tenant
    ON carrossel.visual_preference (tenant_id, created_at DESC)
    WHERE deleted_at IS NULL;
GO

-- Busca por tenant + aprovado (so aprovadas, para alimentar Art Director)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_visual_preference_tenant_aprovado')
    CREATE INDEX IX_visual_preference_tenant_aprovado
    ON carrossel.visual_preference (tenant_id)
    WHERE aprovado = 1 AND deleted_at IS NULL;
GO
```

### 5.7 Indices da tabela historico (novas colunas)

```sql
-- 807_historico_indexes.sql
-- Indices para as novas colunas adicionadas na v3.
-- O indice existente sobre criado_em provavelmente ja existe.

-- Busca por tenant_id (obrigatorio IT Valley)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_historico_tenant')
    CREATE INDEX IX_historico_tenant
    ON carrossel.historico (tenant_id)
    WHERE deleted_at IS NULL;
GO

-- Busca por tenant + formato (v3: multi-formato)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_historico_tenant_formato')
    CREATE INDEX IX_historico_tenant_formato
    ON carrossel.historico (tenant_id, formato)
    WHERE deleted_at IS NULL;
GO
```

---

## 6. Seed de Dados

```sql
-- 901_seed_tenant_default.sql
-- Cria tenant padrao para modo single-user.
-- NAO insere dados em nenhuma tabela de negocio (pipelines, conteudos, etc.).
-- Os dados de historico ja existem no banco.

-- Nenhuma tabela de tenants separada existe (tenant_id e apenas uma coluna).
-- Este script serve como referencia do valor padrao usado em todo o sistema.

-- Valor padrao do tenant_id: 'itvalley'
-- Usado em: toda query, todo INSERT, todo filtro.

PRINT 'Tenant padrao: itvalley'
PRINT 'Nao ha tabela de tenants separada. tenant_id e coluna em cada tabela.'
GO
```

---

## 7. Ordem de Execucao

### run_sql_order.txt

```
# Ordem de execucao dos scripts SQL -- Content Factory v3
# Executar na ordem listada. Cada script e idempotente (IF NOT EXISTS).

# 1. Schema
000_init.sql

# 2. Tabelas (ordem de dependencia)
001_pipeline.sql
002_pipeline_step.sql
003_conteudo.sql
004_imagem.sql
005_score.sql
006_visual_preference.sql
007_historico_alter.sql

# 3. Indices
801_pipeline_indexes.sql
802_pipeline_step_indexes.sql
803_conteudo_indexes.sql
804_imagem_indexes.sql
805_score_indexes.sql
806_visual_preference_indexes.sql
807_historico_indexes.sql

# 4. Seeds
901_seed_tenant_default.sql
```

---

## 8. Observacoes Importantes

### 8.1 Tabela historico existente

A tabela `carrossel.historico` ja existe com dados em producao. O script `007_historico_alter.sql` faz somente ALTER TABLE ADD COLUMN, nunca DROP ou RECREATE. Os dados existentes serao preservados. A coluna `tenant_id` recebe DEFAULT 'itvalley' para preencher registros antigos automaticamente.

### 8.2 Campos JSON como TEXT

Os campos `entrada`, `saida`, `copy_completa` e `contexto` armazenam JSON como NVARCHAR(MAX). O MSSQL suporta funcoes JSON nativas (`JSON_VALUE`, `OPENJSON`) para consultas, mas a aplicacao faz parse no Python (via `json.loads`). Nao ha necessidade de tipo JSON nativo.

### 8.3 Soft delete

Todas as tabelas possuem `deleted_at`. Toda query de listagem deve filtrar `WHERE deleted_at IS NULL`. Os indices filtrados ja consideram essa coluna. A aplicacao nunca faz DELETE fisico, sempre UPDATE SET deleted_at = SYSUTCDATETIME().

### 8.4 Isolamento por tenant

Mesmo em modo single-user (tenant_id = 'itvalley'), toda query deve incluir `WHERE tenant_id = @tenant_id`. Isso garante que a migracao para multitenancia sera transparente.

### 8.5 Cascade deletes

- `pipeline_step` CASCADE de `pipeline` (deletar pipeline remove etapas).
- `imagem` e `score` CASCADE de `conteudo` (deletar conteudo remove imagens e scores).
- `conteudo` SET NULL de `pipeline` (deletar pipeline nao remove conteudo, apenas desvincula).

### 8.6 PipelineStep sem tenant_id

A tabela `pipeline_step` nao possui `tenant_id` proprio. O isolamento e garantido via JOIN com `pipeline` (que tem `tenant_id`). Isso evita duplicacao e mantem consistencia.

### 8.7 Configs fora do banco

Brand palette, creator registry, platform rules, dimensions e templates sao arquivos JSON na pasta `backend/configs/`. Conforme PRD RN-014: "Configs sao JSON puro, sem logica de negocio". Nao ha tabelas para essas entidades.

---

## 9. Compatibilidade com SQLAlchemy Models

Os scripts acima geram exatamente as tabelas esperadas pelos models definidos em `ARQUITETURA_BACKEND.md` secao 5:

| Model (Python) | Tabela SQL | Compativel |
|----------------|-----------|------------|
| `PipelineModel(TenantMixin, Base)` | `carrossel.pipeline` | Sim |
| `PipelineStepModel(Base)` | `carrossel.pipeline_step` | Sim |
| `ConteudoModel(TenantMixin, Base)` | `carrossel.conteudo` | Sim |
| `ImagemModel(TenantMixin, Base)` | `carrossel.imagem` | Sim |
| `ScoreModel(TenantMixin, Base)` | `carrossel.score` | Sim |
| `HistoricoModel(TenantMixin, Base)` | `carrossel.historico` | Sim (apos ALTER) |
| `VisualPreferenceModel(TenantMixin, Base)` | `carrossel.visual_preference` | Sim |

Tipos mapeados:
- `Column(Text)` / `Column(String)` -> `NVARCHAR(MAX)` / `VARCHAR(N)`
- `Column(UNIQUEIDENTIFIER)` -> `UNIQUEIDENTIFIER`
- `Column(DateTime)` -> `DATETIME2`
- `Column(Boolean)` -> `BIT`
- `Column(Integer)` -> `INT`
- `Column(Float)` -> `FLOAT`

---

*Documento gerado pelo Agente 07 (Arquiteto SQL + MongoDB) da esteira IT Valley.*
*Entrada: ARQUITETURA_BACKEND.md (Agente 03) + PRD.md (Agente 01).*
*Proximo: Agente 08 (P.O. / Gerente de Projetos).*
