-- 008_anuncio.sql
-- Tabela de anuncios (pos-pivot 2026-04-23): 1 formato 1080x1350 com copy de venda.

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

        -- Copy de venda (RN-017)
        headline               NVARCHAR(40)        NULL,
        descricao              NVARCHAR(125)       NULL,
        cta                    NVARCHAR(30)        NULL,

        -- Imagem final (1 unica)
        image_url              NVARCHAR(2048)      NULL,

        -- Brand Gate
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
