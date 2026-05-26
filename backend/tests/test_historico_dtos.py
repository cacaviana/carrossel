"""Testes unitarios — DTOs do dominio Historico (modelo polimorfico).

Os 3 formatos (PostUnico, Reels, Thumbnail) + carrossel compartilham o mesmo DTO —
o campo 'formato' identifica qual o tipo do artefato.

Casos de uso cobertos:
 - Listar (PostsUnicos, CapasReels, Thumbnails) via filtro formato
 - Obter (PostUnico, CapaReels, Thumbnail) via BuscarHistoricoResponse
"""

import sys
from datetime import datetime, date, timezone
from pathlib import Path
from uuid import uuid4

import pytest
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dtos.historico.listar_historico.request import ListarHistoricoFiltros
from dtos.historico.listar_historico.response import HistoricoItem, ListarHistoricoResponse
from dtos.historico.buscar_historico.response import BuscarHistoricoResponse
from dtos.historico.base import HistoricoItemBase


# =============================================================================
# ListarHistoricoFiltros — request de listagem
# =============================================================================
class TestListarHistoricoFiltros:
    def test_defaults(self):
        f = ListarHistoricoFiltros()
        assert f.limit == 50
        assert f.offset == 0
        assert f.texto is None
        assert f.formato is None
        assert f.status is None
        assert f.data_inicio is None

    @pytest.mark.parametrize("formato", ["post_unico", "capa_reels", "thumbnail_youtube", "carrossel"])
    def test_aceita_filtro_por_formato(self, formato):
        f = ListarHistoricoFiltros(formato=formato)
        assert f.formato == formato

    def test_aceita_filtro_por_texto(self):
        f = ListarHistoricoFiltros(texto="YOLO")
        assert f.texto == "YOLO"

    def test_aceita_filtro_por_status(self):
        f = ListarHistoricoFiltros(status="completo")
        assert f.status == "completo"

    def test_aceita_intervalo_de_datas(self):
        f = ListarHistoricoFiltros(
            data_inicio=date(2025, 1, 1),
            data_fim=date(2025, 12, 31),
        )
        assert f.data_inicio.year == 2025

    def test_paginacao_customizada(self):
        f = ListarHistoricoFiltros(limit=10, offset=20)
        assert f.limit == 10
        assert f.offset == 20


# =============================================================================
# HistoricoItem (item da listagem)
# =============================================================================
class TestHistoricoItem:
    def _base(self):
        return {
            "id": uuid4(),
            "titulo": "Item teste",
        }

    def test_campos_minimos(self):
        data = self._base()
        item = HistoricoItem(**data)
        assert item.titulo == "Item teste"
        assert item.formato is None
        assert item.total_slides is None

    def test_rejeita_sem_titulo(self):
        with pytest.raises(ValidationError):
            HistoricoItem(id=uuid4())

    def test_rejeita_sem_id(self):
        with pytest.raises(ValidationError):
            HistoricoItem(titulo="x")

    @pytest.mark.parametrize("formato,total", [
        ("post_unico", 1),
        ("capa_reels", 1),
        ("thumbnail_youtube", 1),
        ("carrossel", 10),
    ])
    def test_campos_populados_por_formato(self, formato, total):
        data = self._base()
        data.update(formato=formato, total_slides=total, pipeline_id="pipe-1")
        item = HistoricoItem(**data)
        assert item.formato == formato
        assert item.total_slides == total
        assert item.pipeline_id == "pipe-1"

    def test_aceita_drive_link_e_folder_name(self):
        data = self._base()
        data.update(
            google_drive_link="https://drive.google.com/drive/folders/abc",
            google_drive_folder_name="YOLO - 2025-04-17",
        )
        item = HistoricoItem(**data)
        assert "drive.google.com" in item.google_drive_link


# =============================================================================
# ListarHistoricoResponse
# =============================================================================
class TestListarHistoricoResponse:
    def test_lista_vazia(self):
        resp = ListarHistoricoResponse(items=[], total=0)
        assert resp.total == 0
        assert resp.items == []

    def test_lista_com_items_dos_3_formatos(self):
        items = [
            HistoricoItem(id=uuid4(), titulo="Post unico 1", formato="post_unico"),
            HistoricoItem(id=uuid4(), titulo="Reels 1", formato="capa_reels"),
            HistoricoItem(id=uuid4(), titulo="Thumb 1", formato="thumbnail_youtube"),
        ]
        resp = ListarHistoricoResponse(items=items, total=len(items))
        assert resp.total == 3
        formatos = [i.formato for i in resp.items]
        assert set(formatos) == {"post_unico", "capa_reels", "thumbnail_youtube"}


# =============================================================================
# BuscarHistoricoResponse — Obter {Formato}
# =============================================================================
class TestBuscarHistoricoResponse:
    @pytest.mark.parametrize("formato", ["post_unico", "capa_reels", "thumbnail_youtube"])
    def test_obter_por_formato(self, formato):
        resp = BuscarHistoricoResponse(
            id=uuid4(),
            titulo=f"Item {formato}",
            formato=formato,
            total_slides=1,
            legenda_linkedin="Legenda de teste",
            google_drive_link="https://drive.google.com/x",
        )
        assert resp.formato == formato
        assert resp.total_slides == 1
        assert resp.legenda_linkedin == "Legenda de teste"

    def test_inclui_legenda_linkedin_que_listar_nao_tem(self):
        """BuscarHistoricoResponse inclui legenda_linkedin; HistoricoItem nao."""
        resp = BuscarHistoricoResponse(
            id=uuid4(), titulo="x", legenda_linkedin="uma legenda longa"
        )
        # Garantir que o campo existe no schema da resposta de obter
        assert hasattr(resp, "legenda_linkedin")
        assert resp.legenda_linkedin == "uma legenda longa"

    def test_campos_opcionais_podem_ser_none(self):
        resp = BuscarHistoricoResponse(id=uuid4(), titulo="x")
        assert resp.formato is None
        assert resp.legenda_linkedin is None
        assert resp.final_score is None


# =============================================================================
# HistoricoItemBase — base compartilhada
# =============================================================================
class TestHistoricoItemBase:
    def test_titulo_obrigatorio(self):
        with pytest.raises(ValidationError):
            HistoricoItemBase()

    def test_aceita_campos_opcionais(self):
        b = HistoricoItemBase(
            titulo="x",
            formato="post_unico",
            status="completo",
            final_score=8.5,
            created_at=datetime.now(timezone.utc),
        )
        assert b.final_score == 8.5
