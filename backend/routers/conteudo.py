import os

from fastapi import APIRouter, HTTPException

from dtos.conteudo.gerar_conteudo.request import GerarConteudoRequest
from dtos.conteudo.gerar_conteudo.response import GerarConteudoResponse
from services.conteudo_service import gerar_conteudo
from services.conteudo_cli_service import gerar_conteudo_cli

router = APIRouter()


@router.post("/gerar-conteudo", response_model=GerarConteudoResponse)
async def api_gerar_conteudo(req: GerarConteudoRequest):
    api_key = os.getenv("CLAUDE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="CLAUDE_API_KEY não configurada. Acesse /configuracoes.")
    try:
        result = await gerar_conteudo(
            claude_api_key=api_key,
            disciplina=req.disciplina,
            tecnologia=req.tecnologia,
            tema_custom=req.tema_custom,
            texto_livre=req.texto_livre,
            total_slides=req.total_slides,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gerar-conteudo-cli", response_model=GerarConteudoResponse)
async def api_gerar_conteudo_cli(req: GerarConteudoRequest):
    try:
        result = await gerar_conteudo_cli(
            disciplina=req.disciplina,
            tecnologia=req.tecnologia,
            tema_custom=req.tema_custom,
            texto_livre=req.texto_livre,
            total_slides=req.total_slides,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
