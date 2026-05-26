"""Testes unitarios — mappers/historico_mapper.py.

Mapper e PURO: so converte Model -> DTO, sem validar nem chamar banco.
Cobre os 3 formatos (PostUnico, Reels, Thumbnail) — comportamento deve ser
identico pra todos, pois o model e polimorfico.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from mappers.historico_mapper import HistoricoMapper
from models.historico import HistoricoModel
from dtos.historico.listar_historico.response import HistoricoItem
from dtos.historico.buscar_historico.response import BuscarHistoricoResponse


def _make_model(**kwargs):
    """Constroi um HistoricoModel em memoria (sem banco) pros testes de mapper."""
    defaults = {
        "id": uuid4(),
        "tenant_id": "t1",
        "titulo": "Titulo teste",
        "formato": "carrossel",
        "status": "completo",
        "disciplina": "D1",
        "tecnologia_principal": "YOLO",
        "tipo_carrossel": "texto",
        "total_slides": 10,
        "final_score": 8.5,
        "legenda_linkedin": "legenda completa",
        "google_drive_link": "https://drive.google.com/x",
        "google_drive_folder_name": "YOLO - 2025-04-17",
        "pipeline_id": "pipe-1",
        "created_at": datetime.now(timezone.utc),
    }
    defaults.update(kwargs)
    return HistoricoModel(**defaults)


class TestToItem:
    def test_retorna_historico_item(self):
        m = _make_model()
        item = HistoricoMapper.to_item(m)
        assert isinstance(item, HistoricoItem)
        assert item.titulo == "Titulo teste"

    def test_converte_todos_campos(self):
        m = _make_model()
        item = HistoricoMapper.to_item(m)
        assert item.id == m.id
        assert item.formato == m.formato
        assert item.status == m.status
        assert item.disciplina == m.disciplina
        assert item.tecnologia_principal == m.tecnologia_principal
        assert item.tipo_carrossel == m.tipo_carrossel
        assert item.total_slides == m.total_slides
        assert item.final_score == m.final_score
        assert item.google_drive_link == m.google_drive_link
        assert item.google_drive_folder_name == m.google_drive_folder_name
        assert item.pipeline_id == m.pipeline_id
        assert item.created_at == m.created_at

    def test_nao_inclui_legenda_linkedin(self):
        """Listar nao deve expor legenda_linkedin (apenas o 'obter' expoe)."""
        m = _make_model()
        item = HistoricoMapper.to_item(m)
        assert not hasattr(item, "legenda_linkedin") or getattr(item, "legenda_linkedin", None) is None

    def test_nao_inclui_tenant_id(self):
        """Listar nao expoe tenant_id — sao detalhes internos."""
        m = _make_model()
        item = HistoricoMapper.to_item(m)
        assert not hasattr(item, "tenant_id")


class TestToList:
    def test_lista_vazia(self):
        assert HistoricoMapper.to_list([]) == []

    def test_converte_varios_items(self):
        models = [
            _make_model(titulo="a", formato="post_unico"),
            _make_model(titulo="b", formato="capa_reels"),
            _make_model(titulo="c", formato="thumbnail_youtube"),
        ]
        items = HistoricoMapper.to_list(models)
        assert len(items) == 3
        assert items[0].formato == "post_unico"
        assert items[1].formato == "capa_reels"
        assert items[2].formato == "thumbnail_youtube"


class TestToBuscarResponse:
    def test_retorna_buscar_response(self):
        m = _make_model()
        resp = HistoricoMapper.to_buscar_response(m)
        assert isinstance(resp, BuscarHistoricoResponse)
        assert resp.titulo == "Titulo teste"

    def test_inclui_legenda_linkedin(self):
        """Obter expoe legenda_linkedin (diferente de Listar)."""
        m = _make_model(legenda_linkedin="minha legenda completa aqui")
        resp = HistoricoMapper.to_buscar_response(m)
        assert resp.legenda_linkedin == "minha legenda completa aqui"

    def test_converte_todos_campos(self):
        m = _make_model()
        resp = HistoricoMapper.to_buscar_response(m)
        assert resp.id == m.id
        assert resp.formato == m.formato
        assert resp.legenda_linkedin == m.legenda_linkedin
        assert resp.pipeline_id == m.pipeline_id


# =============================================================================
# Parametrizacao por formato (Obter PostUnico / CapaReels / Thumbnail)
# =============================================================================
@pytest.mark.parametrize("formato,total_slides", [
    ("post_unico", 1),
    ("capa_reels", 1),
    ("thumbnail_youtube", 1),
    ("carrossel", 10),
])
class TestMapperPorFormato:
    def test_to_item_preserva_formato(self, formato, total_slides):
        m = _make_model(formato=formato, total_slides=total_slides)
        item = HistoricoMapper.to_item(m)
        assert item.formato == formato
        assert item.total_slides == total_slides

    def test_to_buscar_response_preserva_formato(self, formato, total_slides):
        m = _make_model(formato=formato, total_slides=total_slides)
        resp = HistoricoMapper.to_buscar_response(m)
        assert resp.formato == formato
        assert resp.total_slides == total_slides


class TestMapperNaoValida:
    """Mapper NAO valida — se o model vem com titulo vazio, passa adiante."""

    def test_model_sem_campos_opcionais_mapa_ok(self):
        m = _make_model(
            disciplina=None,
            tecnologia_principal=None,
            tipo_carrossel=None,
            total_slides=None,
            final_score=None,
            legenda_linkedin=None,
            google_drive_link=None,
            google_drive_folder_name=None,
            pipeline_id=None,
        )
        item = HistoricoMapper.to_item(m)
        resp = HistoricoMapper.to_buscar_response(m)
        assert item.disciplina is None
        assert resp.legenda_linkedin is None
