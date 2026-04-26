-- ============================================================================
-- PIVOT MIGRATION: Anuncios 4 dimensoes -> 1 formato 1080x1350
-- ============================================================================
-- Transacao unica. Preserva dados existentes da tabela anuncio.
-- Dropa tabela anuncio_dimensao. Adiciona colunas novas em anuncio.
-- Ajusta CHECK de status (remove 'parcial').
-- ============================================================================

SET XACT_ABORT ON;
BEGIN TRANSACTION;

-- ---- 1. Normalizar linhas com status='parcial' antes do novo CHECK ----
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'anuncio')
BEGIN
    UPDATE carrossel.anuncio SET status = 'erro' WHERE status = 'parcial';
END

-- ---- 2. Drop FK + table anuncio_dimensao ----
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'anuncio_dimensao')
BEGIN
    -- Drop indices relacionados (se existirem)
    IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_dim_anuncio_ordem')
        DROP INDEX IX_anuncio_dim_anuncio_ordem ON carrossel.anuncio_dimensao;
    IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_dim_anuncio_brand_gate')
        DROP INDEX IX_anuncio_dim_anuncio_brand_gate ON carrossel.anuncio_dimensao;
    IF EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_anuncio_dim_gerando')
        DROP INDEX IX_anuncio_dim_gerando ON carrossel.anuncio_dimensao;

    DROP TABLE carrossel.anuncio_dimensao;
END

-- ---- 3. Adicionar colunas novas em anuncio (image_url, cta, brand_gate, tentativas) ----
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = 'carrossel' AND TABLE_NAME = 'anuncio')
BEGIN
    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('carrossel.anuncio') AND name = 'image_url')
        ALTER TABLE carrossel.anuncio ADD image_url NVARCHAR(2048) NULL;

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('carrossel.anuncio') AND name = 'cta')
        ALTER TABLE carrossel.anuncio ADD cta NVARCHAR(30) NULL;

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('carrossel.anuncio') AND name = 'brand_gate_score')
        ALTER TABLE carrossel.anuncio ADD brand_gate_score FLOAT NULL;

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('carrossel.anuncio') AND name = 'brand_gate_feedback')
        ALTER TABLE carrossel.anuncio ADD brand_gate_feedback NVARCHAR(MAX) NULL;

    IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('carrossel.anuncio') AND name = 'tentativas')
        ALTER TABLE carrossel.anuncio ADD tentativas INT NOT NULL CONSTRAINT DF_anuncio_tentativas DEFAULT 0;
END

-- ---- 4. Alargar colunas de copy (headline 30->40, descricao 90->125) ----
IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('carrossel.anuncio') AND name = 'headline' AND max_length <> 80)
BEGIN
    -- max_length em NVARCHAR vem em bytes*2; 80 bytes = 40 chars
    ALTER TABLE carrossel.anuncio ALTER COLUMN headline NVARCHAR(40) NULL;
END

IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('carrossel.anuncio') AND name = 'descricao' AND max_length <> 250)
BEGIN
    -- 250 bytes = 125 chars
    ALTER TABLE carrossel.anuncio ALTER COLUMN descricao NVARCHAR(125) NULL;
END

-- ---- 5. Trocar CK_anuncio_status (remover 'parcial') ----
IF EXISTS (
    SELECT 1 FROM sys.check_constraints cc
    INNER JOIN sys.objects o ON o.object_id = cc.parent_object_id
    WHERE cc.name = 'CK_anuncio_status' AND o.name = 'anuncio'
)
BEGIN
    ALTER TABLE carrossel.anuncio DROP CONSTRAINT CK_anuncio_status;
END
ALTER TABLE carrossel.anuncio
    ADD CONSTRAINT CK_anuncio_status CHECK (status IN (
        'rascunho', 'gerando', 'completo', 'erro', 'cancelado'
    ));

-- ---- 5b. Trocar CK_anuncio_modo_entrada (adicionar texto_pronto / ideia) ----
IF EXISTS (
    SELECT 1 FROM sys.check_constraints cc
    INNER JOIN sys.objects o ON o.object_id = cc.parent_object_id
    WHERE cc.name = 'CK_anuncio_modo_entrada' AND o.name = 'anuncio'
)
BEGIN
    ALTER TABLE carrossel.anuncio DROP CONSTRAINT CK_anuncio_modo_entrada;
END
ALTER TABLE carrossel.anuncio
    ADD CONSTRAINT CK_anuncio_modo_entrada CHECK (
        modo_entrada IS NULL OR modo_entrada IN ('texto', 'disciplina', 'texto_pronto', 'ideia')
    );

-- ---- 6. Remover indice IX_anuncio_tenant_funil obsoleto? Nao, so pra referencia ----
-- Indices de anuncio continuam validos pois dependem so de tenant_id/status/etc.

PRINT 'Pivot migration Anuncios OK (4 dimensoes -> 1 formato 1080x1350)';

COMMIT TRANSACTION;
GO
