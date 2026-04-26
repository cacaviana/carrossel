-- 808_anuncio_indexes.sql
-- Indices para queries da tabela carrossel.anuncio

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
