import os

from fastapi import APIRouter, HTTPException, Request
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
)
from services.editor_service import (
    salvar_pdf as _salvar_pdf,
    buscar_slides_limpos as _buscar_slides_limpos,
    corrigir_texto as _corrigir_texto,
)

router = APIRouter(tags=["Configuracoes"])

_config_service = ConfigService()


# --- API Keys (existente) ---

@router.post("/config")
@limiter.limit("10/minute")
async def salvar_config(request: Request, req: SaveConfigRequest) -> dict:
    env = read_env()
    update_key(env, "CLAUDE_API_KEY", req.claude_api_key)
    update_key(env, "OPENAI_API_KEY", req.openai_api_key)
    update_key(env, "GEMINI_API_KEY", req.gemini_api_key)
    update_key(env, "GOOGLE_DRIVE_CREDENTIALS", req.google_drive_credentials)
    update_key(env, "GOOGLE_DRIVE_FOLDER_ID", req.google_drive_folder_id)
    write_env(env)
    return {"ok": True}


@router.get("/config", response_model=ConfigStatusResponse)
async def status_config() -> ConfigStatusResponse:
    return ConfigStatusResponse(
        claude_api_key_set=bool(os.getenv("CLAUDE_API_KEY")),
        openai_api_key_set=bool(os.getenv("OPENAI_API_KEY")),
        gemini_api_key_set=bool(os.getenv("GEMINI_API_KEY")),
        google_drive_credentials_set=bool(os.getenv("GOOGLE_DRIVE_CREDENTIALS")),
        google_drive_folder_id=os.getenv("GOOGLE_DRIVE_FOLDER_ID", ""),
    )


# --- Brand Palette (novo) ---

@router.get("/config/brand-palette", response_model=BuscarBrandPaletteResponse)
async def buscar_brand_palette():
    return await _config_service.buscar_brand_palette()


@router.put("/config/brand-palette", response_model=SalvarBrandPaletteResponse)
async def salvar_brand_palette(dto: SalvarBrandPaletteRequest):
    return await _config_service.salvar_brand_palette(dto)


# --- Creator Registry (novo) ---

@router.get("/config/creator-registry", response_model=BuscarCreatorRegistryResponse)
async def buscar_creator_registry():
    return await _config_service.buscar_creator_registry()


@router.put("/config/creator-registry", response_model=SalvarCreatorRegistryResponse)
async def salvar_creator_registry(dto: SalvarCreatorRegistryRequest):
    return await _config_service.salvar_creator_registry(dto)


# --- Platform Rules (novo) ---

@router.get("/config/platform-rules", response_model=BuscarPlatformRulesResponse)
async def buscar_platform_rules():
    return await _config_service.buscar_platform_rules()


@router.put("/config/platform-rules", response_model=SalvarPlatformRulesResponse)
async def salvar_platform_rules(dto: SalvarPlatformRulesRequest):
    return await _config_service.salvar_platform_rules(dto)


# --- Plataformas (unificado: rules + brand palette por plataforma) ---

@router.get("/config/plataformas", response_model=BuscarPlataformasResponse)
async def buscar_plataformas():
    return await _config_service.buscar_plataformas()


@router.put("/config/plataformas", response_model=SalvarPlataformasResponse)
async def salvar_plataformas(dto: SalvarPlataformasRequest):
    return await _config_service.salvar_plataformas(dto)


# --- Brands (Design Systems por marca) ---

@router.get("/brands")
async def listar_brands():
    return _listar_brands()


@router.get("/brands/{slug}")
async def buscar_brand(slug: str):
    brand = _buscar_brand(slug)
    if not brand:
        raise HTTPException(status_code=404, detail=f"Marca '{slug}' nao encontrada")
    return brand


@router.post("/brands", status_code=201)
async def criar_brand(data: dict):
    slug = data.get("slug", "")
    if not slug:
        raise HTTPException(status_code=400, detail="slug obrigatorio")
    try:
        return _criar_brand(slug, data)
    except FileExistsError:
        raise HTTPException(status_code=409, detail=f"Marca '{slug}' ja existe")


@router.put("/brands/{slug}")
async def atualizar_brand(slug: str, data: dict):
    result = _atualizar_brand(slug, data)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Marca '{slug}' nao encontrada")
    return result


@router.delete("/brands/{slug}", status_code=204)
async def deletar_brand(slug: str):
    if not _deletar_brand(slug):
        raise HTTPException(status_code=404, detail=f"Marca '{slug}' nao encontrada")


@router.post("/brands/{slug}/clonar", status_code=201)
async def clonar_brand(slug: str, data: dict):
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
async def upload_foto_brand(slug: str, data: dict):
    """Recebe {"foto": "data:image/jpeg;base64,..."} e salva."""
    foto_data = data.get("foto", "")
    if not foto_data:
        raise HTTPException(status_code=400, detail="Campo 'foto' obrigatorio (base64)")
    return _salvar_foto_brand(slug, foto_data)


@router.put("/brands/{slug}/foto")
async def salvar_foto_brand(slug: str, data: dict):
    """Recebe {"foto": "data:image/jpeg;base64,..."} e salva."""
    foto_data = data.get("foto", "")
    if not foto_data:
        raise HTTPException(status_code=400, detail="Campo 'foto' obrigatorio (base64)")
    return _salvar_foto_brand(slug, foto_data)


@router.post("/editor/salvar-pdf")
async def editor_salvar_pdf(data: dict):
    """Recebe slides + logo + posicoes e gera PDF."""
    slides_data = data.get("slides", [])
    logo_data = data.get("logo", "")
    if not slides_data or not logo_data:
        raise HTTPException(status_code=400, detail="slides e logo obrigatorios")
    return _salvar_pdf(slides_data, logo_data, borda_cor_hex=data.get("borda_cor"), formato=data.get("formato", "carrossel"))


@router.get("/editor/slides/{brand}")
async def editor_slides_limpos(brand: str):
    """Serve imagens limpas (sem overlay) de um brand."""
    result = _buscar_slides_limpos(brand)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Slides limpos de '{brand}' nao encontrados")
    return result


@router.get("/brands/{slug}/foto")
async def buscar_foto_brand(slug: str):
    """Retorna foto da marca como base64."""
    return _buscar_foto_brand(slug)


@router.post("/editor/corrigir-texto")
@limiter.limit("2/minute")
async def editor_corrigir_texto(request: Request, data: dict):
    """Tenta corrigir texto ate 3x com OCR verificando."""
    image = data.get("image", "")
    slide = data.get("slide", {})
    result = await _corrigir_texto(image, slide)
    if result is None:
        raise HTTPException(status_code=500, detail="Falha ao corrigir texto")
    return result


# --- Brand Assets (banco de imagens da marca) ---

@router.get("/brands/{slug}/assets")
async def listar_assets(slug: str):
    """Lista assets (imagens) da marca."""
    return _listar_assets(slug)


@router.post("/brands/{slug}/assets")
async def upload_asset(slug: str, data: dict):
    """Upload de asset da marca. Body: {nome, imagem: base64}."""
    nome = data.get("nome", "asset")
    imagem = data.get("imagem", "")
    if not imagem:
        raise HTTPException(status_code=400, detail="Campo 'imagem' obrigatorio")
    return _upload_asset(slug, nome, imagem)


@router.delete("/brands/{slug}/assets/{nome}")
async def deletar_asset(slug: str, nome: str):
    """Deleta asset da marca."""
    result = _deletar_asset(slug, nome)
    if result is None:
        raise HTTPException(status_code=404, detail=f"Asset '{nome}' nao encontrado")
    return result
