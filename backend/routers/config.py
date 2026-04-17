import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from middleware.auth import CurrentUser, get_current_user
from middleware.rate_limiter import limiter

from dtos.config.request import SaveConfigRequest
from dtos.config.response import ConfigStatusResponse
from dtos.config.salvar_brand_palette.request import SalvarBrandPaletteRequest
from dtos.config.salvar_brand_palette.response import SalvarBrandPaletteResponse
from dtos.config.buscar_brand_palette.response import BuscarBrandPaletteResponse
from dtos.config.salvar_creator_registry.request import SalvarCreatorRegistryRequest
from dtos.config.salvar_creator_registry.response import SalvarCreatorRegistryResponse
from dtos.config.buscar_creator_registry.response import BuscarCreatorRegistryResponse
from dtos.config.salvar_platform_rules.request import SalvarPlatformRulesRequest
from dtos.config.salvar_platform_rules.response import SalvarPlatformRulesResponse
from dtos.config.buscar_platform_rules.response import BuscarPlatformRulesResponse
from dtos.config.plataformas.request import SalvarPlataformasRequest
from dtos.config.plataformas.response import BuscarPlataformasResponse, SalvarPlataformasResponse
from factories.config_factory import read_env, write_env, update_key
from services.config_service import ConfigService
from services.brand_service import (
    listar_brands as _listar_brands,
    buscar_brand as _buscar_brand,
    criar_brand as _criar_brand,
    atualizar_brand as _atualizar_brand,
    deletar_brand_service as _deletar_brand,
    clonar_brand as _clonar_brand,
    salvar_foto_brand as _salvar_foto_brand,
    buscar_foto_brand as _buscar_foto_brand,
    listar_assets as _listar_assets,
    upload_asset as _upload_asset,
    deletar_asset as _deletar_asset,
    definir_referencia as _definir_referencia,
)
from services.editor_service import (
    salvar_pdf as _salvar_pdf,
    buscar_slides_limpos as _buscar_slides_limpos,
    corrigir_texto as _corrigir_texto,
)
from dtos.brand.analisar_referencias.request import AnalisarReferenciasRequest
from dtos.brand.analisar_referencias.response import AnalisarReferenciasResponse
from services.brand_analyzer_service import BrandAnalyzerService

router = APIRouter(tags=["Configuracoes"])

_config_service = ConfigService()

_TEST_SLIDES_DIR = Path(__file__).resolve().parent.parent.parent / "test_slides"


@router.get("/test-slides")
async def test_slides_gallery(
    current_user: CurrentUser = Depends(get_current_user),
):
    """Galeria dos test_slides (dev only)."""
    if not _TEST_SLIDES_DIR.is_dir():
        raise HTTPException(status_code=404, detail="Pasta test_slides nao encontrada")
    pngs = sorted(_TEST_SLIDES_DIR.glob("*.png"))
    cards = ""
    for p in pngs:
        name = p.stem
        cards += f'<div class="card"><img src="/api/test-slides/{p.name}"><p>{name}</p></div>\n'
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Test Slides</title>
<style>
body{{background:#111;color:#fff;font-family:sans-serif;text-align:center;padding:20px}}
h1{{margin-bottom:30px}}
.grid{{display:flex;flex-wrap:wrap;justify-content:center;gap:20px}}
.card{{background:#222;border-radius:12px;padding:12px}}
.card img{{width:270px;border-radius:8px}}
.card p{{margin-top:8px;font-size:14px;color:#aaa}}
</style></head><body>
<h1>Test Slides — IT Valley</h1>
<div class="grid">{cards}</div>
</body></html>"""
    return HTMLResponse(content=html)


@router.get("/test-slides/{filename}")
async def test_slides_file(
    filename: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Serve arquivo individual de test_slides."""
    path = _TEST_SLIDES_DIR / filename
    if not path.exists() or not path.suffix in (".png", ".jpg", ".jpeg", ".webp"):
        raise HTTPException(status_code=404, detail="Arquivo nao encontrado")
    return FileResponse(path)


# --- API Keys (existente) ---

@router.post("/config")
@limiter.limit("10/minute")
async def salvar_config(
    request: Request,
    req: SaveConfigRequest,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict:
    env = read_env()
    update_key(env, "CLAUDE_API_KEY", req.claude_api_key)
    update_key(env, "OPENAI_API_KEY", req.openai_api_key)
    update_key(env, "GEMINI_API_KEY", req.gemini_api_key)
    update_key(env, "GOOGLE_DRIVE_CREDENTIALS", req.google_drive_credentials)
    update_key(env, "GOOGLE_DRIVE_FOLDER_ID", req.google_drive_folder_id)
    write_env(env)
    return {"ok": True}


@router.get("/config", response_model=ConfigStatusResponse)
async def status_config(
    current_user: CurrentUser = Depends(get_current_user),
) -> ConfigStatusResponse:
    return ConfigStatusResponse(
        claude_api_key_set=bool(os.getenv("CLAUDE_API_KEY")),
        openai_api_key_set=bool(os.getenv("OPENAI_API_KEY")),
        gemini_api_key_set=bool(os.getenv("GEMINI_API_KEY")),
        google_drive_credentials_set=bool(os.getenv("GOOGLE_DRIVE_CREDENTIALS")),
        google_drive_folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID", ""),
    )


# --- Brand Palette (novo) ---

@router.get("/config/brand-palette", response_model=BuscarBrandPaletteResponse)
async def buscar_brand_palette(
    current_user: CurrentUser = Depends(get_current_user),
):
    return await _config_service.buscar_brand_palette(tenant_id=current_user.tenant_id)


@router.put("/config/brand-palette", response_model=SalvarBrandPaletteResponse)
async def salvar_brand_palette(
    dto: SalvarBrandPaletteRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    return await _config_service.salvar_brand_palette(dto, tenant_id=current_user.tenant_id)


# --- Creator Registry (novo) ---

@router.get("/config/creator-registry", response_model=BuscarCreatorRegistryResponse)
async def buscar_creator_registry(
    current_user: CurrentUser = Depends(get_current_user),
):
    return await _config_service.buscar_creator_registry(tenant_id=current_user.tenant_id)


@router.put("/config/creator-registry", response_model=SalvarCreatorRegistryResponse)
async def salvar_creator_registry(
    dto: SalvarCreatorRegistryRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    return await _config_service.salvar_creator_registry(dto, tenant_id=current_user.tenant_id)


# --- Platform Rules (novo) ---

@router.get("/config/platform-rules", response_model=BuscarPlatformRulesResponse)
async def buscar_platform_rules(
    current_user: CurrentUser = Depends(get_current_user),
):
    return await _config_service.buscar_platform_rules(tenant_id=current_user.tenant_id)


@router.put("/config/platform-rules", response_model=SalvarPlatformRulesResponse)
async def salvar_platform_rules(
    dto: SalvarPlatformRulesRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    return await _config_service.salvar_platform_rules(dto, tenant_id=current_user.tenant_id)


# --- Plataformas (unificado: rules + brand palette por plataforma) ---

@router.get("/config/plataformas", response_model=BuscarPlataformasResponse)
async def buscar_plataformas(
    current_user: CurrentUser = Depends(get_current_user),
):
    return await _config_service.buscar_plataformas(tenant_id=current_user.tenant_id)


@router.put("/config/plataformas", response_model=SalvarPlataformasResponse)
async def salvar_plataformas(
    dto: SalvarPlataformasRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    return await _config_service.salvar_plataformas(dto, tenant_id=current_user.tenant_id)


# --- Brands (Design Systems por marca) ---

@router.get("/brands")
async def listar_brands(
    current_user: CurrentUser = Depends(get_current_user),
):
    return _listar_brands()


@router.post("/analisar-referencias", response_model=AnalisarReferenciasResponse)
@limiter.limit("5/minute")
async def analisar_referencias(
    request: Request,
    req: AnalisarReferenciasRequest,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Analisa imagens de referencia via Gemini Vision e extrai brand profile."""
    try:
        return await BrandAnalyzerService.analisar(
            req.imagens, req.nome_marca, req.descricao
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar referencias: {str(e)}")


@router.get("/brands/{slug}")
async def buscar_brand(
    slug: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    brand = _buscar_brand(slug)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Marca '{slug}' nao encontrada")
    return brand


@router.post("/brands", status_code=201)
async def criar_brand(
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    slug = data.get("slug", "")
    if not slug:
        raise HTTPException(status_code=400, detail="slug obrigatorio")
    try:
        return _criar_brand(slug, data)
    except FileExistsError:
        raise HTTPException(status_code=409, detail=f"Marca '{slug}' ja existe")


@router.put("/brands/{slug}")
async def atualizar_brand(
    slug: str,
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    result = _atualizar_brand(slug, data)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Marca '{slug}' nao encontrada")
    return result


@router.delete("/brands/{slug}", status_code=204)
async def deletar_brand(
    slug: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    if not _deletar_brand(slug):
        raise HTTPException(status_code=404, detail=f"Marca '{slug}' nao encontrada")


@router.post("/brands/{slug}/clonar", status_code=201)
async def clonar_brand(
    slug: str,
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Clona marca. Body: {slug_destino, nome_destino}."""
    slug_destino = data.get("slug_destino", "")
    nome_destino = data.get("nome_destino", "")
    if not slug_destino or not nome_destino:
        raise HTTPException(status_code=400, detail="slug_destino e nome_destino obrigatorios")
    try:
        return _clonar_brand(slug, slug_destino, nome_destino)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post("/brands/{slug}/foto")
async def upload_foto_brand(
    slug: str,
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Recebe {"foto": "data:image/jpeg;base64,..."} e salva."""
    foto_data = data.get("foto", "")
    if not foto_data:
        raise HTTPException(status_code=400, detail="Campo 'foto' obrigatorio (base64)")
    return _salvar_foto_brand(slug, foto_data)


@router.put("/brands/{slug}/foto")
async def salvar_foto_brand(
    slug: str,
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Recebe {"foto": "data:image/jpeg;base64,..."} e salva."""
    foto_data = data.get("foto", "")
    if not foto_data:
        raise HTTPException(status_code=400, detail="Campo 'foto' obrigatorio (base64)")
    return _salvar_foto_brand(slug, foto_data)


@router.post("/editor/salvar-pdf")
async def editor_salvar_pdf(
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Recebe slides + logo + posicoes e gera PDF."""
    slides_data = data.get("slides", [])
    logo_data = data.get("logo", "")
    if not slides_data or not logo_data:
        raise HTTPException(status_code=400, detail="slides e logo obrigatorios")
    return _salvar_pdf(slides_data, logo_data, borda_cor_hex=data.get("borda_cor"), formato=data.get("formato", "carrossel"))


@router.get("/editor/slides/{brand}")
async def editor_slides_limpos(
    brand: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Serve imagens limpas (sem overlay) de um brand."""
    result = _buscar_slides_limpos(brand)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Slides limpos de '{brand}' nao encontrados")
    return result


@router.get("/brands/{slug}/foto")
async def buscar_foto_brand(
    slug: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Retorna URL da foto da marca."""
    return _buscar_foto_brand(slug)


@router.get("/brands/{slug}/foto/file")
async def servir_foto_brand(
    slug: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Serve a foto da marca como bytes. Le do MongoDB."""
    from fastapi.responses import Response
    from services.brand_service import buscar_foto_brand_bytes
    result = buscar_foto_brand_bytes(slug)
    if result is None:
        raise HTTPException(status_code=404, detail="Foto nao encontrada")
    data, mime = result
    return Response(content=data, media_type=mime)


@router.get("/brands/{slug}/assets/{nome}/file")
async def servir_asset_brand(
    slug: str,
    nome: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Serve um asset da marca como bytes. Le do MongoDB."""
    from fastapi.responses import Response
    from services.brand_service import buscar_asset_bytes
    result = buscar_asset_bytes(slug, nome)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Asset '{nome}' nao encontrado")
    data, mime = result
    return Response(content=data, media_type=mime)


@router.post("/editor/corrigir-texto")
@limiter.limit("5/minute")
async def editor_corrigir_texto(
    request: Request,
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Corrige texto ou aplica instrucao customizada (ex: remover texto)."""
    image = data.get("image", "")
    instrucao = data.get("instrucao", "")

    if instrucao:
        # Instrucao customizada (ex: remover texto) — envia imagem + instrucao ao Gemini
        from services.editor_service import aplicar_instrucao
        result = await aplicar_instrucao(image, instrucao)
        if result is None:
            raise HTTPException(status_code=500, detail="Falha ao aplicar instrucao")
        return result

    slide = data.get("slide", {})
    result = await _corrigir_texto(image, slide)
    if result is None:
        raise HTTPException(status_code=500, detail="Falha ao corrigir texto")
    return result


@router.post("/editor/ajustar-imagem")
@limiter.limit("10/minute")
async def editor_ajustar_imagem(
    request: Request,
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Recebe imagem existente + feedback e aplica ajuste minimo (image-to-image).
    Body: {imagem: base64, feedback: string, brand_slug?: string}"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY nao configurada")
    imagem = data.get("imagem", "")
    feedback = data.get("feedback", "")
    brand_slug = data.get("brand_slug")
    if not imagem or not feedback:
        raise HTTPException(status_code=400, detail="Campos 'imagem' e 'feedback' obrigatorios")
    try:
        import httpx
        from utils.image_adjuster import ajustar_imagem
        from factories.imagem_factory import _load_all_references
        ref = None
        if brand_slug:
            refs = _load_all_references(brand_slug)
            if refs:
                import random
                ref = random.choice(refs)
        async with httpx.AsyncClient(timeout=120.0) as client:
            result = await ajustar_imagem(client, imagem, feedback, api_key, ref_image_b64=ref)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Brand Assets (banco de imagens da marca) ---

@router.get("/brands/{slug}/assets")
async def listar_assets(
    slug: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Lista assets (imagens) da marca."""
    return _listar_assets(slug)


@router.post("/brands/{slug}/assets")
async def upload_asset(
    slug: str,
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Upload de asset da marca.

    Body:
        nome: str              — nome do asset (prefixo auto-aplicado se `pool` passado)
        imagem: str            — base64 data URI
        pool: str (opcional)   — 'com_avatar' | 'sem_avatar'. Se passado, prefixa
                                 o nome com ref_ca_ ou ref_sa_ automaticamente.
                                 Se omitido, salva com o nome como veio (compat
                                 com upload de avatar/foto).
        layout_tag: str (opcional) — 'texto' | 'lista' | 'comparativo' | 'dados'.
                                     Indica qual tipo de layout visual esta ref exemplifica.
    """
    nome = data.get("nome", "asset")
    imagem = data.get("imagem", "")
    pool = data.get("pool")
    layout_tag = data.get("layout_tag")
    if not imagem:
        raise HTTPException(status_code=400, detail="Campo 'imagem' obrigatorio")
    try:
        return _upload_asset(slug, nome, imagem, pool=pool, layout_tag=layout_tag)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar asset: {str(e)}")


@router.delete("/brands/{slug}/assets/{nome}")
async def deletar_asset(
    slug: str,
    nome: str,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Deleta asset da marca."""
    result = _deletar_asset(slug, nome)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Asset '{nome}' nao encontrado")
    return result


@router.put("/brands/{slug}/referencia")
async def definir_referencia(
    slug: str,
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Define qual asset eh a referencia visual para geracao de imagens.
    Body: {nome: 'asset_name'} ou {nome: null} para remover."""
    nome = data.get("nome")
    result = _definir_referencia(slug, nome)
    if result is None:
        raise HTTPException(status_code=404, detail="Marca ou asset nao encontrado")
    return result


@router.post("/brands/{slug}/dna/regenerate")
@limiter.limit("10/minute")
async def regenerate_dna(
    request: Request,
    slug: str,
    data: dict | None = None,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Gera o DNA da marca (4 linhas: estilo, cores, tipografia, elementos)
    a partir de uma imagem de referencia.

    Body (opcional):
        imagem: base64 — se omitido, usa a primeira ref do brand
                (pool com_avatar preferido, sem_avatar como fallback).

    Returns:
        {slug, dna: {estilo, cores, tipografia, elementos}}
    """
    from services.dna_generator import regenerar_dna

    imagem_b64 = (data or {}).get("imagem") if data else None
    try:
        return await regenerar_dna(slug, imagem_b64)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar DNA: {str(e)}")


@router.post("/descrever-referencia")
@limiter.limit("10/minute")
async def descrever_referencia(
    request: Request,
    data: dict,
    current_user: CurrentUser = Depends(get_current_user),
):
    """Recebe uma imagem base64 e retorna descricao do estilo visual.
    Body: {imagem: 'base64...'}. Usa Gemini Flash (gratis)."""
    imagem = data.get("imagem", "")
    if not imagem:
        raise HTTPException(status_code=400, detail="Campo 'imagem' obrigatorio")
    try:
        result = await BrandAnalyzerService.descrever_estilo(imagem)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao analisar imagem: {str(e)}")
