-- ============================================================================
-- MIGRATION: Modulo Anuncios (pos-pivot 2026-04-23)
-- ============================================================================
-- Idempotente. Anuncio = 1 formato 1080x1350 com copy de venda.
-- Dependencia: schema 'carrossel' e tabela 'carrossel.pipeline' devem existir.
-- ============================================================================

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

-- ---- 1. ALTERs em pipeline/conteudo (garantir formato='anuncio') ----
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

-- ---- 2. CREATE TABLE carrossel.anuncio ----
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

        headline               NVARCHAR(40)        NULL,
        descricao              NVARCHAR(125)       NULL,
        cta                    NVARCHAR(30)        NULL,

        image_url              NVARCHAR(2048)      NULL,

        brand_gate_score       FLOAT               NULL,
        brand_gate_feedback    NVARCHAR(MAX)       NULL,
        tentativas             INT                 NOT NULL DEFAULT 0,

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
            'rascunho', 'gerando', 'completo', 'erro', 'cancelado'
        )),
        CONSTRAINT CK_anuncio_etapa_funil CHECK (etapa_funil IS NULL OR etapa_funil IN (
            'topo', 'meio', 'fundo', 'avulso'
        )),
        CONSTRAINT CK_anuncio_modo_entrada CHECK (modo_entrada IS NULL OR modo_entrada IN (
            'texto', 'disciplina', 'texto_pronto', 'ideia'
        ))
    );
END
GO

-- ---- 3. INDEXES anuncio ----

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

-- ---- 4. VALIDACAO ----
DECLARE @msg NVARCHAR(500);
SET @msg = 'Migration Anuncios OK -- tabelas: ' +
    CAST((SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES
          WHERE TABLE_SCHEMA='carrossel' AND TABLE_NAME = 'anuncio') AS VARCHAR) +
    '/1, indices: ' +
    CAST((SELECT COUNT(*) FROM sys.indexes WHERE name LIKE 'IX_anuncio%') AS VARCHAR);
PRINT @msg;
GO
