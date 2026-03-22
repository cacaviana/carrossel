from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

AGENTS_PATH = Path(__file__).parent.parent.parent / "agents"

AGENTES_META = [
    {
        "slug": "gerador-conteudo",
        "nome": "Agente 1 — Gerador de Conteúdo",
        "descricao": "Geração de conteúdo técnico real para LinkedIn. Cria o roteiro dos slides — Carlos Viana / IT Valley School.",
        "arquivo": "anti-bel-pesce.md",
    },
    {
        "slug": "gerador-imagens",
        "nome": "Agente 2 — Gerador de Imagens",
        "descricao": "Geração visual dos slides via Gemini Image API. Define prompts e lógica de imagem por tipo de slide.",
        "arquivo": "nano-banana-carrossel.md",
    },
]


class AgenteResponse(BaseModel):
    slug: str
    nome: str
    descricao: str
    conteudo: str


@router.get("/agentes")
async def listar_agentes() -> list[AgenteResponse]:
    result = []
    for meta in AGENTES_META:
        path = AGENTS_PATH / meta["arquivo"]
        conteudo = path.read_text(encoding="utf-8") if path.exists() else "Arquivo não encontrado."
        result.append(AgenteResponse(
            slug=meta["slug"],
            nome=meta["nome"],
            descricao=meta["descricao"],
            conteudo=conteudo,
        ))
    return result
