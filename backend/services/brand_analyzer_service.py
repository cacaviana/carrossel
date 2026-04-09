import os

from factories.brand_analyzer import BrandAnalyzer
from dtos.brand.analisar_referencias.response import AnalisarReferenciasResponse


class BrandAnalyzerService:

    @staticmethod
    async def analisar(dto, nome_marca: str, descricao: str) -> AnalisarReferenciasResponse:
        """Orquestra analise de referencias visuais. Camada opaca."""
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY nao configurada")

        result = await BrandAnalyzer.analisar(
            imagens_b64=dto,
            nome_marca=nome_marca,
            descricao=descricao,
            api_key=api_key,
        )

        return AnalisarReferenciasResponse(**result)

    @staticmethod
    async def descrever_estilo(imagem_b64: str) -> dict:
        """Extrai TODOS os detalhes visuais de uma imagem usando skill dedicado."""
        api_key = os.getenv("GEMINI_API_KEY", "")
        if not api_key:
            raise ValueError("GEMINI_API_KEY nao configurada")

        from skills.visual_extractor import extrair
        return await extrair(imagem_b64, api_key)
