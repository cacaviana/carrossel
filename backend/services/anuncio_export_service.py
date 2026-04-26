"""Export service do dominio Anuncio (pos-pivot 2026-04-23).

Gera 2 destinos:
- PNG: retorna image_base64 (1 imagem 1080x1350)
- Drive: salva 1 PNG + copy.txt em subpasta "{titulo} - {YYYY-MM-DD}"
"""
import base64
from datetime import datetime, timezone
from typing import Optional

import httpx

from models.anuncio import AnuncioModel


NOME_ARQUIVO_PNG = "anuncio.png"


class AnuncioExportService:

    # -------- COPY.TXT --------
    @staticmethod
    def montar_copy_txt(anuncio: AnuncioModel) -> str:
        headline = anuncio.headline or ""
        descricao = anuncio.descricao or ""
        cta = anuncio.cta or ""
        titulo = anuncio.titulo or ""
        linhas = [
            f"TITULO: {titulo}",
            "",
            "HEADLINE (ate 40 chars):",
            headline,
            "",
            "DESCRICAO (ate 125 chars):",
            descricao,
            "",
            "CTA (ate 30 chars):",
            cta,
            "",
        ]
        return "\n".join(linhas) + "\n"

    # -------- INTERNO --------
    @staticmethod
    async def _obter_bytes_imagem(anuncio: AnuncioModel) -> tuple[Optional[bytes], Optional[str]]:
        """Retorna (bytes, warning). bytes=None se nao ha imagem ou erro."""
        image_url = anuncio.image_url or ""
        if not image_url:
            return None, "Imagem do anuncio ainda nao foi gerada"

        # data URI
        if image_url.startswith("data:"):
            try:
                b64 = image_url.split(",", 1)[1]
                return base64.b64decode(b64), None
            except Exception as e:
                return None, f"Imagem corrompida (data URI): {e}"

        # URL HTTP
        if image_url.startswith(("http://", "https://")):
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    res = await client.get(image_url)
                    res.raise_for_status()
                    return res.content, None
            except Exception as e:
                return None, f"Falha baixando imagem: {e}"

        # Base64 cru
        try:
            return base64.b64decode(image_url), None
        except Exception as e:
            return None, f"Formato de imagem desconhecido: {e}"

    # -------- PNG --------
    @staticmethod
    async def build_png(anuncio: AnuncioModel) -> tuple[Optional[str], Optional[str]]:
        """Retorna (image_base64_data_uri, warning)."""
        conteudo, warning = await AnuncioExportService._obter_bytes_imagem(anuncio)
        if not conteudo:
            return None, warning
        b64 = base64.b64encode(conteudo).decode("utf-8")
        return f"data:image/png;base64,{b64}", None

    # -------- DRIVE --------
    @staticmethod
    async def salvar_drive(
        anuncio: AnuncioModel,
        credentials_json: str,
        parent_folder_id: str,
    ) -> tuple[str, str, list[str], Optional[str]]:
        """Salva 1 PNG + copy.txt em subpasta Drive.
        Retorna (folder_id, folder_link, arquivos, warning).
        """
        from services.drive_service import salvar_anuncio_drive

        conteudo, warning = await AnuncioExportService._obter_bytes_imagem(anuncio)
        copy_txt = AnuncioExportService.montar_copy_txt(anuncio)

        data_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        titulo = anuncio.titulo or "Anuncio"

        arquivos_drive: list[dict] = []
        if conteudo:
            arquivos_drive.append({"nome_arquivo": NOME_ARQUIVO_PNG, "imagem_bytes": conteudo})

        result = await salvar_anuncio_drive(
            credentials_json=credentials_json,
            parent_folder_id=parent_folder_id,
            title=titulo,
            data_str=data_str,
            dimensoes=arquivos_drive,       # reutiliza assinatura existente (so 1 item)
            copy_txt_content=copy_txt,
        )

        arquivos = [NOME_ARQUIVO_PNG] if conteudo else []
        arquivos.append("copy.txt")
        return (
            result.get("folder_id", ""),
            result.get("folder_link", ""),
            arquivos,
            warning,
        )
