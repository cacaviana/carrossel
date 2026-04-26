-- 008a_pipeline_checks.sql
-- Garante que carrossel.pipeline e carrossel.conteudo aceitam formato='anuncio'

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
