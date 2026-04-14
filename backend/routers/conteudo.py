import os

from fastapi import APIRouter, HTTPException, Request

from dtos.conteudo.gerar_conteudo.request import GerarConteudoRequest
from dtos.conteudo.gerar_conteudo.response import GerarConteudoResponse
from services.conteudo_service import gerar_conteudo
from services.conteudo_openai_service import gerar_conteudo_openai
from services.conteudo_cli_service import gerar_conteudo_cli
from middleware.rate_limiter import limiter

router = APIRouter()


@router.post("/gerar-conteudo", response_model=GerarConteudoResponse)
@limiter.limit("5/minute")
async def api_gerar_conteudo(request: Request, req: GerarConteudoRequest):
    claude_key = os.getenv("CLAUDE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    if not claude_key and not openai_key:
        raise HTTPException(status_code=400, detail="Nenhuma API key configurada (CLAUDE_API_KEY ou OPENAI_API_KEY). Acesse /configuracoes.")
    try:
        total = 1 if req.tipo_carrossel == "infografico" else req.total_slides
        if claude_key:
            result = await gerar_conteudo(
                claude_api_key=claude_key,
                disciplina=req.disciplina,
                tecnologia=req.tecnologia,
                tema_custom=req.tema_custom,
                texto_livre=req.texto_livre,
                total_slides=total,
                tipo_carrossel=req.tipo_carrossel,
            )
        else:
            result = await gerar_conteudo_openai(
                openai_api_key=openai_key,
                disciplina=req.disciplina,
                tecnologia=req.tecnologia,
                tema_custom=req.tema_custom,
                texto_livre=req.texto_livre,
                total_slides=total,
                tipo_carrossel=req.tipo_carrossel,
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/gerar-conteudo-cli", response_model=GerarConteudoResponse)
@limiter.limit("5/minute")
async def api_gerar_conteudo_cli(request: Request, req: GerarConteudoRequest):
    try:
        total = 1 if req.tipo_carrossel == "infografico" else req.total_slides
        result = await gerar_conteudo_cli(
            disciplina=req.disciplina,
            tecnologia=req.tecnologia,
            tema_custom=req.tema_custom,
            texto_livre=req.texto_livre,
            total_slides=total,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
